"""
ATR-based Stop Loss Calculator.
Calculates adaptive stop losses based on market volatility (ATR).
"""

import ta
import pandas as pd
from typing import Optional
from config.config import Config
from core.logger import get_logger


class ATRStopCalculator:
    """
    Calculates stop losses based on Average True Range (ATR).
    
    Adjusts stop distance based on symbol's natural volatility,
    preventing premature stops in volatile markets and tighter
    stops in stable markets.
    """
    
    def __init__(self):
        """Initialize ATR calculator."""
        self.logger = get_logger(__name__)
        
        # Configuration
        self.enabled = Config.ENABLE_ATR_STOPS if hasattr(Config, 'ENABLE_ATR_STOPS') else False
        self.atr_period = Config.ATR_PERIOD if hasattr(Config, 'ATR_PERIOD') else 14
        self.min_stop_pct = Config.ATR_MIN_STOP_PCT if hasattr(Config, 'ATR_MIN_STOP_PCT') else 1.0
        self.max_stop_pct = Config.ATR_MAX_STOP_PCT if hasattr(Config, 'ATR_MAX_STOP_PCT') else 5.0
        
        # Symbol-specific multipliers
        self.atr_multipliers = {
            'BTCUSDT': 1.5,  # Less volatile, tighter stops
            'ETHUSDT': 2.0,  # Medium volatility
            'SOLUSDT': 2.5,  # High volatility, wider stops
        }
        
        if hasattr(Config, 'ATR_MULTIPLIERS'):
            self.atr_multipliers.update(Config.ATR_MULTIPLIERS)
        
        if self.enabled:
            self.logger.info(
                f"ATR-based Stop Loss enabled - "
                f"Period: {self.atr_period}, "
                f"Limits: {self.min_stop_pct}%-{self.max_stop_pct}%"
            )
        else:
            self.logger.info("ATR-based Stop Loss disabled (using fixed stops)")
    
    def calculate_atr(self, df: pd.DataFrame) -> Optional[float]:
        """
        Calculate ATR from price data.
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            
        Returns:
            ATR value or None if insufficient data
        """
        if df is None or len(df) < self.atr_period:
            return None
        
        try:
            atr_series = ta.volatility.average_true_range(
                df['high'],
                df['low'],
                df['close'],
                window=self.atr_period
            )
            
            return atr_series.iloc[-1]
            
        except Exception as e:
            self.logger.error(f"Failed to calculate ATR: {e}")
            return None
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        symbol: str,
        is_long: bool = True
    ) -> float:
        """
        Calculate ATR-based stop loss price.
        
        Args:
            entry_price: Entry price
            atr: Current ATR value
            symbol: Trading symbol
            is_long: True for long position, False for short
            
        Returns:
            Stop loss price
        """
        if not self.enabled or atr is None or atr <= 0:
            # Fallback to fixed percentage
            if is_long:
                return entry_price * (1 - Config.STOP_LOSS_PCT / 100)
            else:
                return entry_price * (1 + Config.STOP_LOSS_PCT / 100)
        
        # Get symbol-specific multiplier
        multiplier = self.atr_multipliers.get(symbol, 2.0)
        
        # Calculate stop distance in price units
        stop_distance = atr * multiplier
        
        # Convert to percentage
        stop_pct = (stop_distance / entry_price) * 100
        
        # Enforce safety limits
        stop_pct = max(self.min_stop_pct, min(self.max_stop_pct, stop_pct))
        
        # Calculate stop loss price
        if is_long:
            stop_loss = entry_price * (1 - stop_pct / 100)
        else:
            stop_loss = entry_price * (1 + stop_pct / 100)
        
        self.logger.debug(
            f"ATR Stop: {symbol} @ ${entry_price:.2f}, "
            f"ATR={atr:.2f}, multiplier={multiplier}x, "
            f"stop={stop_pct:.2f}% → ${stop_loss:.2f}"
        )
        
        return stop_loss
    
    def get_status(self) -> dict:
        """
        Get current ATR calculator configuration.
        
        Returns:
            Dict with configuration
        """
        return {
            'enabled': self.enabled,
            'config': {
                'atr_period': self.atr_period,
                'min_stop_pct': self.min_stop_pct,
                'max_stop_pct': self.max_stop_pct,
                'multipliers': self.atr_multipliers
            }
        }
