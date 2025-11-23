"""
Auto-Recovery system for handling API failures and connection issues.
Provides retry logic with exponential backoff and state persistence.
"""

import time
import json
import pickle
from pathlib import Path
from typing import Any, Callable, Optional
from functools import wraps
from datetime import datetime
from config.config import Config
from core.logger import get_logger


class AutoRecovery:
    """
    Handles automatic recovery from connection failures and errors.
    
    Features:
    - Exponential backoff retry (3 attempts)
    - State persistence
    - Error logging and alerts
    """
    
    logger = get_logger(__name__)
    state_file = Config.DATA_DIR / 'bot_state.pkl'
    max_retries = 3
    base_delay = 1  # seconds
    
    @classmethod
    def retry_with_backoff(cls, max_retries: int = None):
        """
        Decorator to retry a function with exponential backoff.
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Usage:
            @AutoRecovery.retry_with_backoff(max_retries=3)
            def risky_operation():
                # code that might fail
        """
        if max_retries is None:
            max_retries = cls.max_retries
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        if attempt < max_retries - 1:
                            # Calculate backoff delay (exponential)
                            delay = cls.base_delay * (2 ** attempt)
                            cls.logger.warning(
                                f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                                f"Retrying in {delay}s..."
                            )
                            time.sleep(delay)
                        else:
                            cls.logger.error(
                                f"All {max_retries} attempts failed for {func.__name__}: {e}"
                            )
                
                # All retries exhausted
                raise last_exception
            
            return wrapper
        return decorator
    
    @classmethod
    def save_state(cls, state_dict: dict) -> None:
        """
        Save bot state to disk for recovery.
        
        Args:
            state_dict: Dictionary containing bot state
        """
        try:
            # Ensure data directory exists
            Config.DATA_DIR.mkdir(exist_ok=True)
            
            # Add timestamp
            state_dict['timestamp'] = datetime.now().isoformat()
            
            #  Save as pickle for complex objects
            with open(cls.state_file, 'wb') as f:
                pickle.dump(state_dict, f)
            
            cls.logger.debug(f"State saved successfully at {datetime.now()}")
            
        except Exception as e:
            cls.logger.error(f"Failed to save state: {e}")
    
    @classmethod
    def restore_state(cls) -> Optional[dict]:
        """
        Restore bot state from disk.
        
        Returns:
            State dictionary or None if no state found
        """
        if not cls.state_file.exists():
            cls.logger.info("No saved state found")
            return None
        
        try:
            with open(cls.state_file, 'rb') as f:
                state = pickle.load(f)
            
            timestamp = state.get('timestamp', 'unknown')
            cls.logger.info(f"State restored from {timestamp}")
            return state
            
        except Exception as e:
            cls.logger.error(f"Failed to restore state: {e}")
            return None
    
    @classmethod
    def handle_connection_error(cls, error: Exception, context: str = "") -> None:
        """
        Handle connection errors and attempt recovery.
        
        Args:
            error: The exception that occurred
            context: Optional context string
        """
        cls.logger.error(f"Connection error{' in ' + context if context else ''}: {error}")
        
        # Log detailed error info
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        # Save error log
        error_log_file = Config.DATA_DIR / 'error_log.json'
        try:
            existing_errors = []
            if error_log_file.exists():
                with open(error_log_file, 'r') as f:
                    existing_errors = json.load(f)
            
            existing_errors.append(error_info)
            
            # Keep only last 100 errors
            existing_errors = existing_errors[-100:]
            
            with open(error_log_file, 'w') as f:
                json.dump(existing_errors, f, indent=2)
                
        except Exception as e:
            cls.logger.error(f"Failed to log error: {e}")
    
    @classmethod
    def clear_state(cls) -> None:
        """Clear saved state file."""
        if cls.state_file.exists():
            cls.state_file.unlink()
            cls.logger.info("Saved state cleared")
    
    @classmethod
    def get_error_summary(cls) -> dict:
        """
        Get summary of recent errors.
        
        Returns:
            Dict with error statistics
        """
        error_log_file = Config.DATA_DIR / 'error_log.json'
        
        if not error_log_file.exists():
            return {'total_errors': 0, 'recent_errors': []}
        
        try:
            with open(error_log_file, 'r') as f:
                errors = json.load(f)
            
            # Group by error type
            error_types = {}
            for error in errors:
                error_type = error.get('error_type', 'Unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            return {
                'total_errors': len(errors),
                'error_types': error_types,
                'recent_errors': errors[-10:]  # Last 10 errors
            }
            
        except Exception as e:
            cls.logger.error(f"Failed to get error summary: {e}")
            return {'total_errors': 0, 'error': str(e)}
