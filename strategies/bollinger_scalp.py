"""
Bollinger Bands Scalping Strategy.
Mean reversion scalping using Bollinger Bands bounces with volume confirmation.
"""

import pandas as pd
from typing import Optional
from strategies.base_strategy import BaseStrategy
from config.config import Config
from core.logger import get_logger


class BollingerScalpStrategy(BaseStrategy):
    """
    Bollinger Bands scalping strategy for quick reversals.
    
    Entry signals:
    - BUY: Price touches lower BB + RSI oversold + volume spike
    - SELL: Price touches upper BB + RSI overbought + volume spike
    
    Designed for mean reversion in ranging markets.
    """
    
    def __init__(
        self,
        bb_period: int = None,
        bb_std: float = None,
        rsi_period: int = None,
        rsi_oversold: float = None,
        rsi_overbought: float = None,
        volume_threshold: float = None
    ):
        """
        Initialize Bollinger scalping strategy.
        
        Args:
            bb_period: Bollinger Bands period (default: 20)
            bb_std: BB standard deviation (default: 2.0)
            rsi_period: RSI period (default: 14)
            rsi_oversold: RSI oversold level (default: 30)
            rsi_overbought: RSI overbought level (default: 70)
            volume_threshold: Volume spike threshold (default: 1.5x)
        """
        # Strategy parameters
        self.bb_period = bb_period or getattr(Config, 'BB_PERIOD', 20)
        self.bb_std = bb_std or getattr(Config, 'BB_STD', 2.0)
        self.rsi_period = rsi_period or getattr(Config, 'RSI_PERIOD', 14)
        self.rsi_oversold = rsi_oversold or getattr(Config, 'RSI_OVERSOLD', 30)
        self.rsi_overbought = rsi_overbought or getattr(Config, 'RSI_OVERBOUGHT', 70)
        self.volume_threshold = volume_threshold or getattr(Config, 'VOLUME_SPIKE_THRESHOLD', 1.5)
        
        # Initialize parent
        super().__init__(name="BB_SCALP")
        self.logger = get_logger(__name__)
        
        self.logger.info(
            f"Bollinger Scalp Strategy initialized -"
            f"BB{self.bb_period}({self.bb_std}σ), "
            f"RSI{self.rsi_period} ({self.rsi_oversold}/{self.rsi_overbought}), "
            f"Volume: {self.volume_threshold}x"
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
        Generate scalping signal based on Bollinger Bands bounces.
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Trading pair symbol
            
        Returns:
            'buy', 'sell', or None
        """
        if len(data) < max(self.bb_period, self.rsi_period):
            return None
        
        # Get current values
        current = data.iloc[-1]
        price = current['close']
        rsi = current['rsi']
        bb_upper = current['bb_high']
        bb_lower = current['bb_low']
        
        # Check volume
        volume_ratio = current['volume'] / current['volume_sma'] if current['volume_sma'] > 0 else 1.0
        has_volume = volume_ratio >= self.volume_threshold
        
        # Tolerance for "touching" bands (within 0.3%)
        lower_touch = price <= bb_lower * 1.003
        upper_touch = price >= bb_upper * 0.997
        
        # BUY Signal: Price at lower BB + oversold + volume
        if lower_touch and rsi < self.rsi_oversold:
            if has_volume:
                self.logger.info(
                    f"{symbol} BB SCALP BUY - "
                    f"Price ${price:.2f} at lower BB (${bb_lower:.2f}), "
                    f"RSI: {rsi:.1f}, Volume: {volume_ratio:.2f}x"
                )
                return 'buy'
            else:
                self.logger.debug(
                    f"{symbol} BB bounce signal but volume too low ({volume_ratio:.2f}x)"
                )
        
        # SELL Signal: Price at upper BB + overbought + volume
        elif upper_touch and rsi > self.rsi_overbought:
            if has_volume:
                self.logger.info(
                    f"{symbol} BB SCALP SELL - "
                    f"Price ${price:.2f} at upper BB (${bb_upper:.2f}), "
                    f"RSI: {rsi:.1f}, Volume: {volume_ratio:.2f}x"
                )
                return 'sell'
            else:
                self.logger.debug(
                    f"{symbol} BB bounce signal but volume too low ({volume_ratio:.2f}x)"
                )
        
        return None
    
    def get_trend(self, data: pd.DataFrame) -> str:
        """
        Determine current trend based on BB position.
        
        Args:
            data: DataFrame with indicators
            
        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        if len(data) < self.bb_period:
            return 'unknown'
        
        price = data.iloc[-1]['close']
        bb_mid = data.iloc[-1]['bb_mid']
        bb_upper = data.iloc[-1]['bb_high']
        bb_lower = data.iloc[-1]['bb_low']
        
        # Position relative to bands
        if price >= bb_upper * 0.995:
            return 'overbought'
        elif price <= bb_lower * 1.005:
            return 'oversold'
        elif price > bb_mid:
            return 'bullish'
        elif price < bb_mid:
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
            'bb_period': self.bb_period,
            'bb_std': self.bb_std,
            'rsi_period': self.rsi_period,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'volume_threshold': self.volume_threshold
        }
