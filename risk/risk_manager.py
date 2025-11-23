"""
Risk management module.
Handles position sizing, risk validation, and risk limits.
"""

from typing import Dict, Optional
from config.config import Config
from core.logger import get_logger


class RiskManager:
    """
    Manages risk for trading operations.
    """
    
    def __init__(self, initial_capital: float = None):
        """
        Initialize risk manager.
        
        Args:
            initial_capital: Starting capital. If None, uses Config.INITIAL_CAPITAL
        """
        self.logger = get_logger(__name__)
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL
        self.current_capital = self.initial_capital
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Kill switch tracking
        self.consecutive_losses = 0
        self.peak_capital = self.initial_capital
        self.kill_switch_active = False
        self.kill_switch_activated_time = None
    
    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss_price: Optional[float] = None,
        risk_percent: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on risk parameters.
        
        Args:
            symbol: Trading pair
            entry_price: Entry price for the position
            stop_loss_price: Stop loss price. If None, uses Config.STOP_LOSS_PERCENT
            risk_percent: Risk percentage. If None, uses Config.RISK_PER_TRADE
        
        Returns:
            Position size (amount of base currency to buy)
        """
        if risk_percent is None:
            risk_percent = Config.RISK_PER_TRADE
        
        # Calculate risk amount in quote currency
        risk_amount = self.current_capital * (risk_percent / 100)
        
        # Calculate stop loss price if not provided
        if stop_loss_price is None:
            # For long positions, stop loss is below entry
            stop_loss_price = entry_price * (1 - Config.STOP_LOSS_PERCENT / 100)
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit == 0:
            self.logger.warning("Risk per unit is 0, using default position size")
            return (risk_amount / entry_price)
        
        # Calculate position size
        position_size = risk_amount / risk_per_unit
        
        # Cap position size for scalping to avoid over-leveraging
        max_position_value = self.current_capital * 0.25  # Max 25% of capital per trade
        max_position_size = max_position_value / entry_price
        
        if position_size > max_position_size:
            self.logger.debug(f"Capping position size from {position_size:.6f} to {max_position_size:.6f}")
            position_size = max_position_size
        
        self.logger.debug(
            f"Position size calculation: "
            f"capital=${self.current_capital:.2f}, "
            f"risk={risk_percent}%, "
            f"entry=${entry_price:.2f}, "
            f"stop=${stop_loss_price:.2f}, "
            f"size={position_size:.6f}"
        )
        
        return position_size
    
    def validate_trade(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        open_positions_count: int
    ) -> tuple[bool, str]:
        """
        Validate if a trade should be executed based on risk parameters.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Position size
            price: Entry price
            open_positions_count: Number of currently open positions
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check max positions
        if open_positions_count >= Config.MAX_POSITIONS:
            return False, f"Max positions limit reached ({Config.MAX_POSITIONS})"
        
        # Calculate position value
        position_value = amount * price
        
        # Check if we have enough capital
        if position_value > self.current_capital:
            return False, f"Insufficient capital (need ${position_value:.2f}, have ${self.current_capital:.2f})"
        
        # Check max portfolio exposure
        exposure_percent = (position_value / self.initial_capital) * 100
        if exposure_percent > Config.MAX_PORTFOLIO_EXPOSURE:
            return False, f"Position exceeds max exposure ({exposure_percent:.1f}% > {Config.MAX_PORTFOLIO_EXPOSURE}%)"
        
        # Check minimum position size (to avoid dust trades)
        if position_value < 10:  # Minimum $10 position
            return False, f"Position too small (${position_value:.2f})"
        
        return True, "Trade validated"
    
    def update_capital(self, pnl: float) -> None:
        """
        Update current capital after a trade.
        
        Args:
            pnl: Profit or loss from the trade
        """
        self.current_capital += pnl
        self.total_trades += 1
        
        if pnl > 0:
            self.winning_trades += 1
            self.consecutive_losses = 0  # Reset on win
            # Update peak capital
            if self.current_capital > self.peak_capital:
                self.peak_capital = self.current_capital
        elif pnl < 0:
            self.losing_trades += 1
            self.consecutive_losses += 1
        
        self.logger.info(
            f"Capital updated: ${self.current_capital:.2f} "
            f"(PnL: ${pnl:+.2f}, Consecutive losses: {self.consecutive_losses})"
        )
    
    def get_stop_loss_price(self, entry_price: float, side: str, strategy_type: str = 'normal') -> float:
        """
        Calculate stop loss price based on strategy type.
        
        Args:
            entry_price: Entry price
            side: 'buy' or 'sell'
            strategy_type: 'normal' or 'scalp'
        
        Returns:
            Stop loss price
        """
        # Use scalping stop loss if strategy is scalp
        if strategy_type == 'scalp':
            sl_percent = Config.SCALP_STOP_LOSS_PERCENT
        else:
            sl_percent = Config.STOP_LOSS_PERCENT
        
        if side.lower() == 'buy':
            # For long positions, stop loss is below entry
            stop_loss = entry_price * (1 - sl_percent / 100)
        else:
            # For short positions, stop loss is above entry
            stop_loss = entry_price * (1 + sl_percent / 100)
        
        return stop_loss
    
    def get_take_profit_price(self, entry_price: float, side: str, strategy_type: str = 'normal') -> float:
        """
        Calculate take profit price based on strategy type.
        
        Args:
            entry_price: Entry price
            side: 'buy' or 'sell'
            strategy_type: 'normal' or 'scalp'
        
        Returns:
            Take profit price
        """
        # Use scalping take profit if strategy is scalp
        if strategy_type == 'scalp':
            tp_percent = Config.SCALP_TAKE_PROFIT_PERCENT
        else:
            tp_percent = Config.TAKE_PROFIT_PERCENT
        
        if side.lower() == 'buy':
            # For long positions, take profit is above entry
            take_profit = entry_price * (1 + tp_percent / 100)
        else:
            # For short positions, take profit is below entry
            take_profit = entry_price * (1 - tp_percent / 100)
        
        return take_profit
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Get risk and performance statistics.
        
        Returns:
            Dictionary with statistics
        """
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        total_return = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'total_return_pct': total_return,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate_pct': win_rate
        }
    
    def get_current_drawdown(self) -> float:
        """
        Calculate current drawdown percentage.
        
        Returns:
            Drawdown percentage (positive number)
        """
        if self.peak_capital == 0:
            return 0
        drawdown = ((self.peak_capital - self.current_capital) / self.peak_capital) * 100
        return max(0, drawdown)
    
    def should_halt_trading(self) -> tuple[bool, str]:
        """
        Check if kill switch should activate.
        
        Returns:
            Tuple of (should_halt, reason)
        """
        if not Config.ENABLE_KILL_SWITCH:
            return False, ""
        
        # Check drawdown
        current_drawdown = self.get_current_drawdown()
        if current_drawdown >= Config.MAX_DRAWDOWN_PERCENT:
            reason = f"Maximum drawdown exceeded: {current_drawdown:.2f}% >= {Config.MAX_DRAWDOWN_PERCENT}%"
            self.logger.critical(f"🚨 KILL SWITCH ACTIVATED: {reason}")
            self.kill_switch_active = True
            return True, reason
        
        # Check consecutive losses
        if self.consecutive_losses >= Config.MAX_CONSECUTIVE_LOSSES:
            reason = f"Maximum consecutive losses exceeded: {self.consecutive_losses} >= {Config.MAX_CONSECUTIVE_LOSSES}"
            self.logger.critical(f"🚨 KILL SWITCH ACTIVATED: {reason}")
            self.kill_switch_active = True
            return True, reason
        
        return False, ""
    
    def reset(self) -> None:
        """Reset risk manager to initial state."""
        self.current_capital = self.initial_capital
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.consecutive_losses = 0
        self.peak_capital = self.initial_capital
        self.kill_switch_active = False
        self.kill_switch_activated_time = None
        self.logger.info("Risk manager reset")
