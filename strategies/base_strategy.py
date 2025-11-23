"""
Base strategy class.
All trading strategies should inherit from this class.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional
from core.logger import get_logger


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
            parameters: Strategy parameters
        """
        self.name = name
        self.parameters = parameters or {}
        self.logger = get_logger(__name__)
    
    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze market data and add signal columns.
        
        Args:
            df: DataFrame with OHLCV and indicator data
        
        Returns:
            DataFrame with added signal columns
        """
        pass
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[str]:
        """
        Generate trading signal based on latest data.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            symbol: Trading pair
        
        Returns:
            'buy', 'sell', or None
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters."""
        return self.parameters.copy()
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set strategy parameters."""
        self.parameters.update(parameters)
    
    def __str__(self) -> str:
        """String representation of strategy."""
        return f"{self.name}({self.parameters})"
