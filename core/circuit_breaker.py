"""
Circuit Breaker system to pause trading during extreme market conditions.
Monitors volatility, volume, and spread to protect against tail risks.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
from datetime import datetime, timedelta
from config.config import Config
from core.logger import get_logger


class CircuitBreaker:
    """
    Monitors market conditions and pauses trading when thresholds are exceeded.
    
    Features:
    - Volatility monitoring (>5x normal → pause)
    - Volume monitoring (<20% average → pause)
    - Spread monitoring (>0.5% → pause)
    """
    
    def __init__(self):
        """Initialize circuit breaker."""
        self.logger = get_logger(__name__)
        self.paused_symbols = {}  # {symbol: (timestamp, reason)}
        self.historical_volatility = {}  # {symbol: rolling volatility}
        self.historical_volume = {}  # {symbol: rolling volume}
        
        # Configuration
        self.volatility_threshold = Config.VOLATILITY_THRESHOLD if hasattr(Config, 'VOLATILITY_THRESHOLD') else 5.0
        self.volume_threshold = Config.VOLUME_THRESHOLD if hasattr(Config, 'VOLUME_THRESHOLD') else 0.2
        self.spread_threshold = Config.SPREAD_THRESHOLD if hasattr(Config, 'SPREAD_THRESHOLD') else 0.5
        self.cooldown_minutes = 30  # Resume after cooldown
        
        self.logger.info(f"Circuit Breaker initialized - Volatility: {self.volatility_threshold}x, "
                        f"Volume: {self.volume_threshold*100}%, Spread: {self.spread_threshold}%")
    
    def check_volatility(self, symbol: str, current_price: float, historical_data: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Check if current volatility exceeds threshold.
        
        Args:
            symbol: Trading pair symbol
            current_price: Current market price
            historical_data: DataFrame with 'close' prices
            
        Returns:
            (is_extreme, reason) - True if volatility is extreme
        """
        if historical_data is None or len(historical_data) < 20:
            return False, None
        
        try:
            # Calculate rolling volatility (standard deviation of returns)
            returns = historical_data['close'].pct_change().dropna()
            rolling_vol = returns.rolling(window=20).std()
            
            # Store baseline volatility
            if symbol not in self.historical_volatility:
                self.historical_volatility[symbol] = rolling_vol.mean()
            
            # Calculate current volatility
            recent_returns = returns.tail(5)
            current_vol = recent_returns.std()
            
            # Check if current volatility exceeds threshold
            baseline_vol = self.historical_volatility[symbol]
            
            if baseline_vol > 0 and current_vol > baseline_vol * self.volatility_threshold:
                reason = f"Extreme volatility: {current_vol:.4f} (>{self.volatility_threshold}x baseline {baseline_vol:.4f})"
                self.logger.warning(f"{symbol}: {reason}")
                return True, reason
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Error checking volatility for {symbol}: {e}")
            return False, None
    
    def check_volume(self, symbol: str, current_volume: float, historical_data: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Check if current volume is abnormally low (low liquidity).
        
        Args:
            symbol: Trading pair symbol
            current_volume: Current trading volume
            historical_data: DataFrame with 'volume' data
            
        Returns:
            (is_low, reason) - True if volume is too low
        """
        if historical_data is None or len(historical_data) < 20:
            return False, None
        
        try:
            # Calculate average volume
            avg_volume = historical_data['volume'].tail(100).mean()
            
            # Store baseline volume
            if symbol not in self.historical_volume:
                self.historical_volume[symbol] = avg_volume
            
            # Check if current volume is too low
            if avg_volume > 0 and current_volume < avg_volume * self.volume_threshold:
                reason = f"Low volume: {current_volume:.0f} (<{self.volume_threshold*100}% of avg {avg_volume:.0f})"
                self.logger.warning(f"{symbol}: {reason}")
                return True, reason
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Error checking volume for {symbol}: {e}")
            return False, None
    
    def check_spread(self, symbol: str, bid: float, ask: float) -> Tuple[bool, Optional[str]]:
        """
        Check if bid-ask spread is abnormally high.
        
        Args:
            symbol: Trading pair symbol
            bid: Current bid price
            ask: Current ask price
            
        Returns:
            (is_high, reason) - True if spread is too high
        """
        if bid <= 0 or ask <= 0:
            return False, None
        
        try:
            # Calculate spread percentage
            mid_price = (bid + ask) / 2
            spread_pct = ((ask - bid) / mid_price) * 100
            
            # Check if spread exceeds threshold
            if spread_pct > self.spread_threshold:
                reason = f"High spread: {spread_pct:.2f}% (>{self.spread_threshold}%)"
                self.logger.warning(f"{symbol}: {reason}")
                return True, reason
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Error checking spread for {symbol}: {e}")
            return False, None
    
    def should_pause_trading(self, symbol: str, current_data: dict) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive check - should trading be paused for this symbol?
        
        Args:
            symbol: Trading pair symbol
            current_data: Dict with 'price', 'volume', 'bid', 'ask', 'historical_df'
            
        Returns:
            (should_pause, reason) - True if trading should pause
        """
        # Check if already paused and cooldown period hasn't expired
        if symbol in self.paused_symbols:
            pause_time, pause_reason = self.paused_symbols[symbol]
            elapsed = (datetime.now() - pause_time).total_seconds() / 60
            
            if elapsed < self.cooldown_minutes:
                return True, f"Still in cooldown ({self.cooldown_minutes - elapsed:.0f}min remaining): {pause_reason}"
            else:
                # Cooldown expired, remove from paused
                del self.paused_symbols[symbol]
                self.logger.info(f"{symbol}: Cooldown expired, resuming monitoring")
        
        # Check volatility
        if 'price' in current_data and 'historical_df' in current_data:
            is_extreme, reason = self.check_volatility(
                symbol,
                current_data['price'],
                current_data['historical_df']
            )
            if is_extreme:
                self.paused_symbols[symbol] = (datetime.now(), reason)
                return True, reason
        
        # Check volume
        if 'volume' in current_data and 'historical_df' in current_data:
            is_low, reason = self.check_volume(
                symbol,
                current_data['volume'],
                current_data['historical_df']
            )
            if is_low:
                self.paused_symbols[symbol] = (datetime.now(), reason)
                return True, reason
        
        # Check spread
        if 'bid' in current_data and 'ask' in current_data:
            is_high, reason = self.check_spread(
                symbol,
                current_data['bid'],
                current_data['ask']
            )
            if is_high:
                self.paused_symbols[symbol] = (datetime.now(), reason)
                return True, reason
        
        return False, None
    
    def get_status(self) -> dict:
        """
        Get current circuit breaker status.
        
        Returns:
            Dict with paused symbols and reasons
        """
        return {
            'paused_symbols': {
                symbol: {
                    'reason': reason,
                    'since': timestamp.isoformat(),
                    'minutes_ago': (datetime.now() - timestamp).total_seconds() / 60
                }
                for symbol, (timestamp, reason) in self.paused_symbols.items()
            },
            'config': {
                'volatility_threshold': self.volatility_threshold,
                'volume_threshold': self.volume_threshold,
                'spread_threshold': self.spread_threshold,
                'cooldown_minutes': self.cooldown_minutes
            }
        }
