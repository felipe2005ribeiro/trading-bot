"""
Market data module for fetching and processing market data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import ta
from core.exchange_connector import ExchangeConnector
from core.logger import get_logger
from config.config import Config


class MarketData:
    """
    Handles fetching and processing of market data.
    """
    
    def __init__(self, exchange: ExchangeConnector):
        """
        Initialize market data handler.
        
        Args:
            exchange: ExchangeConnector instance
        """
        self.exchange = exchange
        self.logger = get_logger(__name__)
        self.data_cache: Dict[str, pd.DataFrame] = {}
    
    def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str,
        days: int = 90,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (e.g., '1h', '4h', '1d')
            days: Number of days of historical data
            limit: Maximum candles per request
        
        Returns:
            DataFrame with OHLCV data and timestamp index
        """
        self.logger.info(f"Fetching {days} days of {timeframe} data for {symbol}")
        
        try:
            # Calculate since timestamp
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            all_data = []
            
            while True:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe=timeframe,
                    since=since,
                    limit=limit
                )
                
                if not ohlcv:
                    break
                
                all_data.extend(ohlcv)
                
                # Update since to last timestamp + 1ms
                since = ohlcv[-1][0] + 1
                
                # Break if we have enough data or reached current time
                if len(ohlcv) < limit:
                    break
            
            # Convert to DataFrame
            df = pd.DataFrame(
                all_data,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Ensure numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            self.logger.info(f"Fetched {len(df)} candles for {symbol}")
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to the DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicators
        """
        try:
            # SMA indicators
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['sma_200'] = ta.trend.sma_indicator(df['close'], window=200)
            
            # EMA indicators
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
            
            # EMA for scalping
            df['ema_8'] = ta.trend.ema_indicator(df['close'], window=8)
            df['ema_21'] = ta.trend.ema_indicator(df['close'], window=21)
            
            # RSI
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_diff'] = macd.macd_diff()
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(df['close'])
            df['bb_high'] = bollinger.bollinger_hband()
            df['bb_mid'] = bollinger.bollinger_mavg()
            df['bb_low'] = bollinger.bollinger_lband()
            
            # ATR (Average True Range)
            df['atr'] = ta.volatility.average_true_range(
                df['high'], df['low'], df['close'], window=14
            )
            
            # Volume indicators
            df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
            
            # OBV (On-Balance Volume)
            df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
            
            # VWAP (Volume Weighted Average Price)
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            
            self.logger.debug("Added technical indicators to DataFrame")
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error adding technical indicators: {e}")
            raise
    
    def get_latest_data(
        self,
        symbol: str,
        timeframe: str,
        lookback: int = 200
    ) -> pd.DataFrame:
        """
        Get latest market data with indicators.
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            lookback: Number of candles to fetch
        
        Returns:
            DataFrame with OHLCV data and indicators
        """
        cache_key = f"{symbol}_{timeframe}"
        
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=lookback
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            #Ensure numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Add technical indicators
            df = self.add_technical_indicators(df)
            
            # Update cache
            self.data_cache[cache_key] = df
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error getting latest data for {symbol}: {e}")
            # Return cached data if available
            if cache_key in self.data_cache:
                self.logger.warning("Returning cached data due to error")
                return self.data_cache[cache_key]
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Trading pair
        
        Returns:
            Current price
        """
        try:
            ticker = self.exchange.get_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            self.logger.error(f"Error getting current price for {symbol}: {e}")
            raise
    
    def clear_cache(self) -> None:
        """Clear the data cache."""
        self.data_cache.clear()
        self.logger.info("Data cache cleared")
