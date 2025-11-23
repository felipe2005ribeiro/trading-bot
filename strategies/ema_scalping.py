"""
EMA Crossover Scalping Strategy.
Fast scalping strategy using 8/21 EMA crossovers with volume confirmation.
"""

import pandas as pd
from typing import Optional
from strategies.base_strategy import BaseStrategy
from config.config import Config
from core.logger import get_logger


class EMAScalpingStrategy(BaseStrategy):
    """
    EMA crossover scalping strategy for short timeframes (5m/15m).
    
    Entry signals:
    - BUY: EMA8 crosses above EMA21 + volume spike
    - SELL: EMA8 crosses below EMA21 + volume spike
    
    Designed for quick trades with tight stop losses.
    """
    
    def __init__(
        self,
        fast_period: int = None,
        slow_period: int = None,
        volume_threshold: float = None
    ):
        """
        Initialize EMA scalping strategy.
        
        Args:
            fast_period: Fast EMA period (default: 8)
            slow_period: Slow EMA period (default: 21)
            volume_threshold: Volume spike threshold (default: 1.5x)
        """
        # Strategy parameters
        self.fast_period = fast_period or getattr(Config, 'EMA_FAST_PERIOD', 8)
        self.slow_period = slow_period or getattr(Config, 'EMA_SLOW_PERIOD', 21)
        self.volume_threshold = volume_threshold or getattr(Config, 'VOLUME_SPIKE_THRESHOLD', 1.5)
        
        # Initialize parent
        super().__init__(name="EMA_SCALP")
        self.logger = get_logger(__name__)
        
        self.logger.info(
            f"EMA Scalping Strategy initialized - "
            f"EMA{self.fast_period}/{self.slow_period}, "
            f"Volume threshold: {self.volume_threshold}x"
        )
    
    def analyze(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze market data with indicators.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators
        """
        # Indicators are already added by market_data.add_technical_indicators()
        return data
    
    def generate_signal(self, data: pd.DataFrame, symbol: str = "") -> Optional[str]:
        """
        Generate scalping signal based on EMA crossover.
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Trading pair symbol
            
        Returns:
            'buy', 'sell', or None
        """
        if len(data) < max(self.fast_period, self.slow_period) + 2:
            return None
        
        # Get current and previous values
        current = data.iloc[-1]
        previous = data.iloc[-2]
        
        ema_fast_current = current[f'ema_{self.fast_period}']
        ema_slow_current = current[f'ema_{self.slow_period}']
        ema_fast_prev = previous[f'ema_{self.fast_period}']
        ema_slow_prev = previous[f'ema_{self.slow_period}']
        
        # Check volume
        volume_ratio = current['volume'] / current['volume_sma'] if current['volume_sma'] > 0 else 1.0
        has_volume = volume_ratio >= self.volume_threshold
        
        # Bullish crossover: EMA8 crosses above EMA21
        if ema_fast_prev <= ema_slow_prev and ema_fast_current > ema_slow_current:
            if has_volume:
                self.logger.info(
                    f"{symbol} EMA SCALP BUY - "
                    f"EMA{self.fast_period} crossed above EMA{self.slow_period}, "
                    f"Price: ${current['close']:.2f}, Volume: {volume_ratio:.2f}x"
                )
                return 'buy'
            else:
                self.logger.debug(
                    f"{symbol} EMA crossover detected but volume too low ({volume_ratio:.2f}x)"
                )
        
        # Bearish crossover: EMA8 crosses below EMA21
        elif ema_fast_prev >= ema_slow_prev and ema_fast_current < ema_slow_current:
            if has_volume:
                self.logger.info(
                    f"{symbol} EMA SCALP SELL - "
                    f"EMA{self.fast_period} crossed below EMA{self.slow_period}, "
                    f"Price: ${current['close']:.2f}, Volume: {volume_ratio:.2f}x"
                )
                return 'sell'
            else:
                self.logger.debug(
                    f"{symbol} EMA crossover detected but volume too low ({volume_ratio:.2f}x)"
                )
        
        return None
    
    def get_trend(self, data: pd.DataFrame) -> str:
        """
        Determine current trend based on EMA position.
        
        Args:
            data: DataFrame with indicators
            
        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        if len(data) < max(self.fast_period, self.slow_period):
            return 'unknown'
        
        ema_fast = data.iloc[-1][f'ema_{self.fast_period}']
        ema_slow = data.iloc[-1][f'ema_{self.slow_period}']
        
        if ema_fast > ema_slow * 1.002:  # 0.2% above
            return 'bullish'
        elif ema_fast < ema_slow * 0.998:  # 0.2% below
            return 'bearish'
        else:
            return 'neutral'
    
    def get_parameters(self) -> dict:
        """
        Get strategy parameters.
        
        Returns:
            Dictionary with strategy configuration
        """
        return {
            'name': self.name,
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'volume_threshold': self.volume_threshold
        }
