"""
Order management module for the trading bot.
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime
import csv
from pathlib import Path

from core.exchange_connector import ExchangeConnector
from core.logger import get_logger
from config.config import Config


class OrderManager:
    """
    Manages order creation, tracking, and execution.
    """
    
    def __init__(self, exchange: ExchangeConnector):
        """
        Initialize order manager.
        
        Args:
            exchange: ExchangeConnector instance
        """
        self.exchange = exchange
        self.logger = get_logger(__name__)
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.trades_log_file = Config.RESULTS_DIR / f"trades_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Initialize trades log CSV
        self._init_trades_log()
    
    def _init_trades_log(self) -> None:
        """Initialize trades log CSV file."""
        if not self.trades_log_file.exists():
            with open(self.trades_log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'symbol',
                    'side',
                    'order_type',
                    'price',
                    'amount',
                    'filled',
                    'status',
                    'order_id',
                    'commission',
                    'notes'
                ])
            self.logger.info(f"Initialized trades log: {self.trades_log_file}")
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        notes: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Create a market order.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Amount to trade
            notes: Optional notes for the trade
        
        Returns:
            Order information or None if failed
        """
        try:
            self.logger.info(f"Creating market {side} order: {amount} {symbol}")
            
            order = self.exchange.create_market_order(symbol, side, amount)
            
            # Store order
            self.orders[order['id']] = order
            
            # Log to CSV
            self._log_trade(
                symbol=symbol,
                side=side,
                order_type='market',
                price=order.get('price', 0),
                amount=amount,
                filled=order.get('filled', amount),
                status=order.get('status', 'simulated'),
                order_id=order['id'],
                commission=0,
                notes=notes
            )
            
            return order
        
        except Exception as e:
            self.logger.error(f"Error creating market order: {e}")
            return None
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        notes: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Create a limit order.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Limit price
            notes: Optional notes
        
        Returns:
            Order information or None if failed
        """
        try:
            self.logger.info(f"Creating limit {side} order: {amount} {symbol} @ {price}")
            
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            
            # Store order
            self.orders[order['id']] = order
            
            # Log to CSV
            self._log_trade(
                symbol=symbol,
                side=side,
                order_type='limit',
                price=price,
                amount=amount,
                filled=order.get('filled', 0),
                status=order.get('status', 'pending'),
                order_id=order['id'],
                commission=0,
                notes=notes
            )
            
            return order
        
        except Exception as e:
            self.logger.error(f"Error creating limit order: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading pair
        
        Returns:
            True if successful
        """
        try:
            self.exchange.cancel_order(order_id, symbol)
            
            if order_id in self.orders:
                self.orders[order_id]['status'] = 'cancelled'
            
            self.logger.info(f"Cancelled order: {order_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get status of an order.
        
        Args:
            order_id: Order ID
            symbol: Trading pair
        
        Returns:
            Order status or None
        """
        try:
            order = self.exchange.get_order_status(order_id, symbol)
            
            # Update stored order
            if order_id in self.orders:
                self.orders[order_id].update(order)
            
            return order
        
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            return None
    
    def _log_trade(
        self,
        symbol: str,
        side: str,
        order_type: str,
        price: float,
        amount: float,
        filled: float,
        status: str,
        order_id: str,
        commission: float,
        notes: str
    ) -> None:
        """Log trade to CSV file."""
        try:
            with open(self.trades_log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    symbol,
                    side,
                    order_type,
                    price,
                    amount,
                    filled,
                    status,
                    order_id,
                    commission,
                    notes
                ])
        except Exception as e:
            self.logger.error(f"Error logging trade to CSV: {e}")
    
    def get_open_orders(self, symbol: str = None) -> list:
        """
        Get open orders.
        
        Args:
            symbol: Optional symbol filter
        
        Returns:
            List of open orders
        """
        try:
            orders = self.exchange.get_open_orders(symbol)
            return orders
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            return []
