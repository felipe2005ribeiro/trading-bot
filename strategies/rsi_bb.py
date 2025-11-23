"""
RSI + Bollinger Bands Strategy.
Mean reversion strategy for sideways/ranging markets.
"""

import pandas as pd
from typing import Optional
from strategies.base_strategy import BaseStrategy
from config.config import Config
from core.logger import get_logger


class RSIBollingerStrategy(BaseStrategy):
    """
    RSI + Bollinger Bands strategy for mean reversion trading.
    
    Buy signals:
    - RSI < 30 (oversold) AND price touches lower Bollinger Band
    
    Sell signals:
    - RSI > 70 (overbought) AND price touches upper Bollinger Band
    """
    
    def __init__(
        self,
        rsi_period: int = None,
        rsi_oversold: float = None,
        rsi_overbought: float = None,
        bb_period: int = None,
        bb_std: float = None
    ):
        """
        Initialize RSI + Bollinger Bands strategy.
        
        Args:
            rsi_period: RSI period
            rsi_oversold: RSI oversold threshold
            rsi_overbought: RSI overbought threshold
            bb_period: Bollinger Bands period
            bb_std: Bollinger Bands standard deviation
        """
        # Strategy parameters
        self.rsi_period = rsi_period or getattr(Config, 'RSI_PERIOD', 14)
        self.rsi_oversold = rsi_oversold or getattr(Config, 'RSI_OVERSOLD', 30)
        self.rsi_overbought = rsi_overbought or getattr(Config, 'RSI_OVERBOUGHT', 70)
        self.bb_period = bb_period or getattr(Config, 'BB_PERIOD', 20)
        self.bb_std = bb_std or getattr(Config, 'BB_STD', 2.0)
        
        # Initialize parent with name
        super().__init__(name="RSI_BB")
        self.logger = get_logger(__name__)
        
        self.logger.info(
            f"RSI+BB Strategy initialized - "
            f"RSI: {self.rsi_period} period, "
            f"Oversold: {self.rsi_oversold}, Overbought: {self.rsi_overbought}, "
            f"BB: {self.bb_period} period, {self.bb_std} std"
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
        Generate trading signal based on RSI and Bollinger Bands.
        
        Args:
            data: DataFrame with OHLCV and indicators
            symbol: Trading pair symbol
            
        Returns:
            'buy', 'sell', or None
        """
        if len(data) < max(self.rsi_period, self.bb_period):
            return None
        
        # Get last values
        current_price = data.iloc[-1]['close']
        rsi = data.iloc[-1]['rsi']
        bb_upper = data.iloc[-1]['bb_high']
        bb_lower = data.iloc[-1]['bb_low']
        
        # BUY Signal: Oversold RSI + Price at lower BB
        is_oversold = rsi < self.rsi_oversold
        touches_lower_bb = current_price <= bb_lower * 1.002  # Within 0.2%
        
        if is_oversold and touches_lower_bb:
            self.logger.info(
                f"{symbol} RSI+BB BUY signal - "
                f"RSI: {rsi:.1f} (oversold), "
                f"Price: ${current_price:.2f} at lower BB (${bb_lower:.2f})"
            )
            return 'buy'
        
        # SELL Signal: Overbought RSI + Price at upper BB
        is_overbought = rsi > self.rsi_overbought
        touches_upper_bb = current_price >= bb_upper * 0.998  # Within 0.2%
        
        if is_overbought and touches_upper_bb:
            self.logger.info(
                f"{symbol} RSI+BB SELL signal - "
                f"RSI: {rsi:.1f} (overbought), "
                f"Price: ${current_price:.2f} at upper BB (${bb_upper:.2f})"
            )
            return 'sell'
        
        return None
    
    def get_trend(self, data: pd.DataFrame) -> str:
        """
        Determine current trend based on RSI and BB position.
        
        Args:
            data: DataFrame with indicators
            
        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        if len(data) < max(self.rsi_period, self.bb_period):
            return 'unknown'
        
        rsi = data.iloc[-1]['rsi']
        current_price = data.iloc[-1]['close']
        bb_middle = data.iloc[-1]['bb_mid']
        
        # Strong signals
        if rsi > 70 and current_price > bb_middle:
            return 'overbought'
        elif rsi < 30 and current_price < bb_middle:
            return 'oversold'
        # Moderate signals
        elif rsi > 60:
            return 'bullish'
        elif rsi < 40:
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
            'rsi_period': self.rsi_period,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'bb_period': self.bb_period,
            'bb_std': self.bb_std
        }
