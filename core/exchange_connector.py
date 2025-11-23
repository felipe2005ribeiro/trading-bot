"""
Exchange connector module using ccxt library.
Handles connection to Binance (testnet and production).
"""

import ccxt
import time
from typing import Dict, List, Optional, Any
from config.config import Config
from core.logger import get_logger


class ExchangeConnector:
    """
    Wrapper for ccxt exchange connection with error handling and rate limiting.
    """
    
    def __init__(self):
        """Initialize exchange connection."""
        self.logger = get_logger(__name__)
        self.exchange = None
        self.is_testnet = Config.USE_TESTNET
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to the exchange."""
        # For backtesting with production data, we don't need API keys (public data only)
        if Config.BACKTEST_USE_PRODUCTION_DATA:
            try:
                self.exchange = ccxt.binance({
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot',
                    }
                })
                # No API keys needed for public data
                # No sandbox mode - use production endpoints
                self.is_testnet = False
                self.logger.info("Connected to Binance PRODUCTION (Read-Only for Backtesting)")
                
                # Load markets
                self.exchange.load_markets()
                self.logger.info(f"Loaded {len(self.exchange.markets)} markets")
                return
            except Exception as e:
                self.logger.error(f"Failed to connect to production for backtesting: {e}")
                raise
        
        # Normal flow with API keys
        api_key, api_secret, is_testnet = Config.get_api_credentials()
        
        try:
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,  # Auto rate limiting
                'options': {
                    'defaultType': 'spot',
                }
            })
            
            if is_testnet:
                # Set testnet URLs
                self.exchange.set_sandbox_mode(True)
                self.logger.info("Connected to Binance TESTNET")
            else:
                self.logger.warning("Connected to Binance PRODUCTION")
            
            # Load markets
            self.exchange.load_markets()
            self.logger.info(f"Loaded {len(self.exchange.markets)} markets")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to exchange: {e}")
            raise
    
    def reconnect(self) -> None:
        """Attempt to reconnect to the exchange."""
        self.logger.info("Attempting to reconnect...")
        max_retries = 5
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                self._connect()
                self.logger.info("Reconnection successful")
                return
            except Exception as e:
                self.logger.warning(
                    f"Reconnection attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error("Max reconnection attempts reached")
                    raise
    
    def get_balance(self, currency: str = None) -> Dict[str, float]:
        """
        Get account balance.
        
        Args:
            currency: Specific currency to check (e.g., 'USDT'). If None, returns all.
        
        Returns:
            Dictionary with balance information
        """
        try:
            balance = self.exchange.fetch_balance()
            
            if currency:
                return {
                    'free': balance['free'].get(currency, 0),
                    'used': balance['used'].get(currency, 0),
                    'total': balance['total'].get(currency, 0)
                }
            
            return balance
        
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            self.reconnect()
            raise
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get ticker information for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
        
        Returns:
            Dictionary with ticker data
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        
        except Exception as e:
            self.logger.error(f"Error fetching ticker for {symbol}: {e}")
            self.reconnect()
            raise
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        since: int = None,
        limit: int = 500
    ) -> List[List]:
        """
        Fetch OHLCV (candlestick) data.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (e.g., '1m', '5m', '1h', '1d')
            since: Timestamp in milliseconds to fetch from
            limit: Number of candles to fetch (max 1000)
        
        Returns:
            List of OHLCV data [timestamp, open, high, low, close, volume]
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                since=since,
                limit=limit
            )
            return ohlcv
        
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            self.reconnect()
            raise
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Create a market order.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Amount to trade
        
        Returns:
            Order information
        """
        try:
            if not Config.EXECUTE_REAL:
                self.logger.info(
                    f"[SIMULATION] Market {side} order: {amount} {symbol}"
                )
                return {
                    'id': f'sim_{int(time.time() * 1000)}',
                    'symbol': symbol,
                    'type': 'market',
                    'side': side,
                    'amount': amount,
                    'status': 'simulated'
                }
            
            order = self.exchange.create_market_order(symbol, side, amount)
            self.logger.info(f"Created market {side} order: {order['id']}")
            return order
        
        except Exception as e:
            self.logger.error(f"Error creating market order: {e}")
            raise
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float
    ) -> Dict[str, Any]:
        """
        Create a limit order.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Limit price
        
        Returns:
            Order information
        """
        try:
            if not Config.EXECUTE_REAL:
                self.logger.info(
                    f"[SIMULATION] Limit {side} order: {amount} {symbol} @ {price}"
                )
                return {
                    'id': f'sim_{int(time.time() * 1000)}',
                    'symbol': symbol,
                    'type': 'limit',
                    'side': side,
                    'amount': amount,
                    'price': price,
                    'status': 'simulated'
                }
            
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            self.logger.info(f"Created limit {side} order: {order['id']}")
            return order
        
        except Exception as e:
            self.logger.error(f"Error creating limit order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            order_id: ID of the order to cancel
            symbol: Trading pair
        
        Returns:
            Cancellation result
        """
        try:
            if not Config.EXECUTE_REAL:
                self.logger.info(f"[SIMULATION] Cancelled order: {order_id}")
                return {'id': order_id, 'status': 'cancelled'}
            
            result = self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"Cancelled order: {order_id}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def get_open_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Get open orders.
        
        Args:
            symbol: Trading pair. If None, returns all open orders.
        
        Returns:
            List of open orders
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        
        except Exception as e:
            self.logger.error(f"Error fetching open orders: {e}")
            raise
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get status of an order.
        
        Args:
            order_id: Order ID
            symbol: Trading pair
        
        Returns:
            Order status information
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        
        except Exception as e:
            self.logger.error(f"Error fetching order status: {e}")
            raise
