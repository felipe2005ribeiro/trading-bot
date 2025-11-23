"""
SMA Crossover Strategy.
Golden Cross (buy) and Death Cross (sell) based on SMA crossovers.
"""

import pandas as pd
from typing import Optional
from strategies.base_strategy import BaseStrategy
from config.config import Config


class SMACrossStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.
    
    Signals:
    - BUY (Golden Cross): When short SMA crosses above long SMA
    - SELL (Death Cross): When short SMA crosses below long SMA
    """
    
    def __init__(
        self,
        short_period: int = None,
        long_period: int = None
    ):
        """
        Initialize SMA Cross strategy.
        
        Args:
            short_period: Period for short SMA (default from config)
            long_period: Period for long SMA (default from config)
        """
        parameters = {
            'short_period': short_period or Config.SMA_SHORT_PERIOD,
            'long_period': long_period or Config.SMA_LONG_PERIOD
        }
        super().__init__("SMA_Cross", parameters)
        
        self.short_period = parameters['short_period']
        self.long_period = parameters['long_period']
    
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze data and add signal columns.
        
        Args:
            df: DataFrame with OHLCV data and indicators
        
        Returns:
            DataFrame with signal columns added
        """
        # Ensure we have the required SMAs
        if f'sma_{self.short_period}' not in df.columns:
            df[f'sma_{self.short_period}'] = df['close'].rolling(
                window=self.short_period
            ).mean()
        
        if f'sma_{self.long_period}' not in df.columns:
            df[f'sma_{self.long_period}'] = df['close'].rolling(
                window=self.long_period
            ).mean()
        
        # Calculate crossover signals
        df['sma_short'] = df[f'sma_{self.short_period}']
        df['sma_long'] = df[f'sma_{self.long_period}']
        
        # Identify crossovers
        df['sma_position'] = 0
        df.loc[df['sma_short'] > df['sma_long'], 'sma_position'] = 1
        df.loc[df['sma_short'] < df['sma_long'], 'sma_position'] = -1
        
        # Detect crossover points
        df['sma_crossover'] = df['sma_position'].diff()
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['sma_crossover'] == 2, 'signal'] = 1  # Golden Cross (buy)
        df.loc[df['sma_crossover'] == -2, 'signal'] = -1  # Death Cross (sell)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[str]:
        """
        Generate trading signal for the latest data point.
        
        Args:
            df: DataFrame with OHLCV and indicator data
            symbol: Trading pair
        
        Returns:
            'buy', 'sell', or None
        """
        # Analyze the data
        df = self.analyze(df)
        
        # Check if we have enough data
        if len(df) < self.long_period + 5:
            self.logger.warning(
                f"Not enough data for {symbol}. "
                f"Need at least {self.long_period + 5} candles, have {len(df)}"
            )
            return None
        
        # Get the last few rows to detect crossover
        recent = df.tail(3)
        
        # Check for Golden Cross (buy signal)
        # SMA short crosses above SMA long
        if recent['signal'].iloc[-1] == 1:
            self.logger.info(
                f"[{symbol}] Golden Cross detected! "
                f"SMA{self.short_period} ({recent['sma_short'].iloc[-1]:.2f}) "
                f"crossed above SMA{self.long_period} ({recent['sma_long'].iloc[-1]:.2f})"
            )
            return 'buy'
        
        # Check for Death Cross (sell signal)
        # SMA short crosses below SMA long
        elif recent['signal'].iloc[-1] == -1:
            self.logger.info(
                f"[{symbol}] Death Cross detected! "
                f"SMA{self.short_period} ({recent['sma_short'].iloc[-1]:.2f}) "
                f"crossed below SMA{self.long_period} ({recent['sma_long'].iloc[-1]:.2f})"
            )
            return 'sell'
        
        # No signal
        return None
    
    def get_trend(self, df: pd.DataFrame) -> str:
        """
        Get current trend based on SMA position.
        
        Args:
            df: DataFrame with analyzed data
        
        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        df = self.analyze(df)
        
        if len(df) < self.long_period:
            return 'neutral'
        
        last_position = df['sma_position'].iloc[-1]
        
        if last_position == 1:
            return 'bullish'
        elif last_position == -1:
            return 'bearish'
        else:
            return 'neutral'
