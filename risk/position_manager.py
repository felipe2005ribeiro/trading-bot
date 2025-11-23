"""
Position management module.
Tracks open positions and calculates P&L.
"""

from typing import Dict, List, Optional
from datetime import datetime
from core.logger import get_logger


class Position:
    """Represents a single trading position."""
    
    def __init__(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        amount: float,
        stop_loss: float = None,
        take_profit: float = None,
        entry_time: datetime = None
    ):
        """
        Initialize a position.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            entry_price: Entry price
            amount: Position size
            stop_loss: Stop loss price
            take_profit: Take profit price
            entry_time: Entry timestamp
        """
        self.symbol = symbol
        self.side = side
        self.entry_price = entry_price
        self.amount = amount
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_time = entry_time or datetime.now()
        self.exit_price = None
        self.exit_time = None
        self.pnl = 0.0
        self.pnl_percent = 0.0
        
        # Trailing stop fields
        self.trailing_stop_active = False
        self.highest_price = entry_price  # For buy positions
        self.lowest_price = entry_price   # For sell positions
        self.trailing_stop_price = None
    
    def calculate_pnl(self, current_price: float) -> tuple[float, float]:
        """
        Calculate current profit/loss.
        
        Args:
            current_price: Current market price
        
        Returns:
            Tuple of (pnl_amount, pnl_percent)
        """
        if self.side.lower() == 'buy':
            pnl = (current_price - self.entry_price) * self.amount
        else:
            pnl = (self.entry_price - current_price) * self.amount
        
        pnl_percent = (pnl / (self.entry_price * self.amount)) * 100
        
        return pnl, pnl_percent
    
    def should_close(self, current_price: float) -> tuple[bool, str]:
        """
        Check if position should be closed based on stop loss or take profit.
        
        Args:
            current_price: Current market price
        
        Returns:
            Tuple of (should_close, reason)
        """
        # PRIORITY 1: Check trailing stop if active
        if self.trailing_stop_active and self.trailing_stop_price:
            if self.side.lower() == 'buy':
                if current_price <= self.trailing_stop_price:
                    return True, "trailing_stop"
            else:  # sell position
                if current_price >= self.trailing_stop_price:
                    return True, "trailing_stop"
        
        # PRIORITY 2: Check regular stop loss
        if self.stop_loss and self.side.lower() == 'buy':
            if current_price <= self.stop_loss:
                return True, "stop_loss"
        elif self.stop_loss and self.side.lower() == 'sell':
            if current_price >= self.stop_loss:
                return True, "stop_loss"
        
        # PRIORITY 3: Check take profit
        if self.take_profit and self.side.lower() == 'buy':
            if current_price >= self.take_profit:
                return True, "take_profit"
        elif self.take_profit and self.side.lower() == 'sell':
            if current_price <= self.take_profit:
                return True, "take_profit"
        
        return False, ""
    
    def update_trailing_stop(self, current_price: float, config) -> bool:
        """
        Update trailing stop based on current price and configuration.
        
        Args:
            current_price: Current market price
            config: Configuration object with trailing stop parameters
        
        Returns:
            True if trailing stop was updated, False otherwise
        """
        if not config.ENABLE_TRAILING_STOP:
            return False
        
        # Calculate current unrealized profit percentage
        pnl, pnl_percent = self.calculate_pnl(current_price)
        
        # Check if we should activate trailing stop
        if not self.trailing_stop_active:
            if pnl_percent >= config.TRAILING_ACTIVATION_PERCENT:
                self.trailing_stop_active = True
                self.highest_price = current_price if self.side.lower() == 'buy' else self.entry_price
                self.lowest_price = self.entry_price if self.side.lower() == 'buy' else current_price
                
                # Calculate initial trailing stop price
                if self.side.lower() == 'buy':
                    self.trailing_stop_price = current_price * (1 - config.TRAILING_DISTANCE_PERCENT / 100)
                else:
                    self.trailing_stop_price = current_price * (1 + config.TRAILING_DISTANCE_PERCENT / 100)
                
                return True  # Trailing stop just activated
        
        # If already active, update highest/lowest and trailing stop
        if self.trailing_stop_active:
            updated = False
            
            if self.side.lower() == 'buy':
                # For buy positions, track highest price
                if current_price > self.highest_price:
                    self.highest_price = current_price
                    new_trailing_stop = current_price * (1 - config.TRAILING_DISTANCE_PERCENT / 100)
                    
                    # Only move trailing stop up, never down
                    if new_trailing_stop > self.trailing_stop_price:
                        self.trailing_stop_price = new_trailing_stop
                        updated = True
            else:
                # For sell positions, track lowest price
                if current_price < self.lowest_price:
                    self.lowest_price = current_price
                    new_trailing_stop = current_price * (1 + config.TRAILING_DISTANCE_PERCENT / 100)
                    
                    # Only move trailing stop down, never up
                    if new_trailing_stop < self.trailing_stop_price:
                        self.trailing_stop_price = new_trailing_stop
                        updated = True
            
            return updated
        
        return False
    
    def close(self, exit_price: float, exit_time: datetime = None) -> None:
        """
        Close the position.
        
        Args:
            exit_price: Exit price
            exit_time: Exit timestamp
        """
        self.exit_price = exit_price
        self.exit_time = exit_time or datetime.now()
        self.pnl, self.pnl_percent = self.calculate_pnl(exit_price)
    
    def to_dict(self) -> Dict:
        """Convert position to dictionary."""
        return {
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'amount': self.amount,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_price': self.exit_price,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent
        }


class PositionManager:
    """Manages all trading positions."""
    
    def __init__(self):
        """Initialize position manager."""
        self.logger = get_logger(__name__)
        self.open_positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        self._telegram_notifier = None  # Will be set by trading bot
    
    def set_telegram_notifier(self, telegram_notifier):
        """Set telegram notifier instance for notifications."""
        self._telegram_notifier = telegram_notifier
    
    def open_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        amount: float,
        stop_loss: float = None,
        take_profit: float = None
    ) -> Position:
        """
        Open a new position.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            entry_price: Entry price
            amount: Position size
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            Opened position
        """
        position = Position(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            amount=amount,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        self.open_positions[symbol] = position
        
        self.logger.info(
            f"Opened {side} position: {amount} {symbol} @ ${entry_price:.2f} "
            f"(SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})"
        )
        
        return position
    
    def close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: str = ""
    ) -> Optional[Position]:
        """
        Close a position.
        
        Args:
            symbol: Trading pair
            exit_price: Exit price
            reason: Reason for closing
        
        Returns:
            Closed position or None if not found
        """
        if symbol not in self.open_positions:
            self.logger.warning(f"No open position found for {symbol}")
            return None
        
        position = self.open_positions.pop(symbol)
        position.close(exit_price)
        
        self.closed_positions.append(position)
        
        self.logger.info(
            f"Closed {position.side} position: {position.amount} {symbol} "
            f"@ ${exit_price:.2f} | PnL: ${position.pnl:+.2f} ({position.pnl_percent:+.2f}%) "
            f"| Reason: {reason}"
        )
        
        return position
    
    def has_position(self, symbol: str) -> bool:
        """
        Check if there's an open position for a symbol.
        
        Args:
            symbol: Trading pair
        
        Returns:
            True if position exists
        """
        return symbol in self.open_positions
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get open position for a symbol.
        
        Args:
            symbol: Trading pair
        
        Returns:
            Position or None
        """
        return self.open_positions.get(symbol)
    
    def get_all_open_positions(self) -> List[Position]:
        """Get all open positions."""
        return list(self.open_positions.values())
    
    def get_open_positions_count(self) -> int:
        """Get count of open positions."""
        return len(self.open_positions)
    
    def update_positions(self, current_prices: Dict[str, float]) -> List[tuple[str, str]]:
        """
        Update all positions and check for stop loss/take profit triggers.
        
        Args:
            current_prices: Dictionary of symbol: current_price
        
        Returns:
            List of (symbol, reason) tuples for positions that should be closed
        """
        positions_to_close = []
        
        for symbol, position in self.open_positions.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            
            # Update trailing stop only for symbols that benefit from it
            from config.config import Config
            
            # Track if this is first activation for notification
            was_active_before = position.trailing_stop_active
            trailing_updated = False
            
            # Only update trailing stop for selected symbols
            if Config.ENABLE_TRAILING_STOP and symbol in Config.TRAILING_SYMBOLS:
                trailing_updated = position.update_trailing_stop(current_price, Config)
            
            if trailing_updated:
                if position.trailing_stop_active and position.trailing_stop_price:
                    # Log the update
                    self.logger.info(
                        f"{symbol}: Trailing stop {'activated' if not was_active_before else 'updated'} "
                        f"at ${position.trailing_stop_price:.2f} (Current: ${current_price:.2f})"
                    )
                    
                    # Send Telegram notification only on first activation
                    if not was_active_before and self._telegram_notifier is not None:
                        pnl, pnl_percent = position.calculate_pnl(current_price)
                        self._telegram_notifier.send_trailing_stop_activated(
                            symbol, current_price, position.trailing_stop_price, pnl_percent
                        )
            
            # Check exit conditions (includes trailing stop, SL, TP)
            should_close, reason = position.should_close(current_price)
            
            if should_close:
                positions_to_close.append((symbol, reason))
        
        return positions_to_close
    
    def get_total_pnl(self, current_prices: Dict[str, float] = None) -> float:
        """
        Get total P&L from all positions.
        
        Args:
            current_prices: Current prices for open positions. If None, only closed positions PnL.
        
        Returns:
            Total P&L
        """
        total_pnl = sum(pos.pnl for pos in self.closed_positions)
        
        if current_prices:
            for symbol, position in self.open_positions.items():
                if symbol in current_prices:
                    pnl, _ = position.calculate_pnl(current_prices[symbol])
                    total_pnl += pnl
        
        return total_pnl
    
    def get_statistics(self) -> Dict:
        """Get position statistics."""
        total_closed = len(self.closed_positions)
        winning = sum(1 for pos in self.closed_positions if pos.pnl > 0)
        losing = sum(1 for pos in self.closed_positions if pos.pnl < 0)
        
        total_pnl = sum(pos.pnl for pos in self.closed_positions)
        avg_win = sum(pos.pnl for pos in self.closed_positions if pos.pnl > 0) / winning if winning > 0 else 0
        avg_loss = sum(pos.pnl for pos in self.closed_positions if pos.pnl < 0) / losing if losing > 0 else 0
        
        return {
            'total_positions': total_closed,
            'winning_positions': winning,
            'losing_positions': losing,
            'win_rate': (winning / total_closed * 100) if total_closed > 0 else 0,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0
        }
    
    def clear_closed_positions(self) -> None:
        """Clear closed positions history."""
        self.closed_positions.clear()
        self.logger.info("Cleared closed positions history")
