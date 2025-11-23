"""
Dynamic Position Sizing module.
Adjusts position sizes based on win streaks and market volatility.
"""

from typing import Optional
from config.config import Config
from core.logger import get_logger


class DynamicPositionSizer:
    """
    Calculates optimal position sizes using Kelly Criterion-inspired approach.
    
    Features:
    - Increases size during winning streaks
    - Decreases size during losing streaks
    - Adjusts for market volatility (ATR)
    - Enforces safety limits
    """
    
    def __init__(self):
        """Initialize position sizer."""
        self.logger = get_logger(__name__)
        
        # Configuration
        self.enabled = Config.ENABLE_DYNAMIC_SIZING if hasattr(Config, 'ENABLE_DYNAMIC_SIZING') else False
        self.win_streak_threshold = Config.SIZING_WIN_STREAK_THRESHOLD if hasattr(Config, 'SIZING_WIN_STREAK_THRESHOLD') else 3
        self.win_multiplier = Config.SIZING_WIN_MULTIPLIER if hasattr(Config, 'SIZING_WIN_MULTIPLIER') else 1.2
        self.loss_multiplier = Config.SIZING_LOSS_MULTIPLIER if hasattr(Config, 'SIZING_LOSS_MULTIPLIER') else 0.8
        self.volatility_threshold = Config.SIZING_VOLATILITY_THRESHOLD if hasattr(Config, 'SIZING_VOLATILITY_THRESHOLD') else 1.5
        self.max_multiplier = Config.SIZING_MAX_MULTIPLIER if hasattr(Config, 'SIZING_MAX_MULTIPLIER') else 1.5
        self.min_multiplier = Config.SIZING_MIN_MULTIPLIER if hasattr(Config, 'SIZING_MIN_MULTIPLIER') else 0.5
        
        if self.enabled:
            self.logger.info(
                f"Dynamic Position Sizing enabled - "
                f"Win threshold: {self.win_streak_threshold}, "
                f"Win multiplier: {self.win_multiplier}x, "
                f"Loss multiplier: {self.loss_multiplier}x"
            )
        else:
            self.logger.info("Dynamic Position Sizing disabled")
    
    def calculate_position_size(
        self,
        base_size: float,
        win_streak: int,
        current_volatility: Optional[float] = None,
        avg_volatility: Optional[float] = None
    ) -> float:
        """
        Calculate optimal position size based on momentum and volatility.
        
        Args:
            base_size: Base position size (e.g., $10,000)
            win_streak: Current win streak
                       Positive = consecutive wins (e.g., 3 = 3 wins in a row)
                       Negative = consecutive losses (e.g., -2 = 2 losses in a row)
            current_volatility: Current market volatility (ATR)
            avg_volatility: Average volatility for normalization
            
        Returns:
            Adjusted position size
        """
        if not self.enabled:
            return base_size
        
        multiplier = 1.0
        adjustments = []
        
        # 1. Win Streak Adjustment (Kelly Criterion inspired)
        if win_streak >= self.win_streak_threshold:
            multiplier *= self.win_multiplier
            adjustments.append(f"win_streak_+{win_streak}")
        elif win_streak <= -2:  # 2 or more losses
            multiplier *= self.loss_multiplier
            adjustments.append(f"loss_streak_{win_streak}")
        
        # 2. Volatility Adjustment
        if current_volatility is not None and avg_volatility is not None and avg_volatility > 0:
            volatility_ratio = current_volatility / avg_volatility
            
            if volatility_ratio > self.volatility_threshold:
                # High volatility -> reduce size
                vol_multiplier = 0.9
                multiplier *= vol_multiplier
                adjustments.append(f"high_vol_{volatility_ratio:.2f}x")
        
        # 3. Enforce Safety Limits
        multiplier = max(self.min_multiplier, min(self.max_multiplier, multiplier))
        
        # Calculate final size
        adjusted_size = base_size * multiplier
        
        # Log adjustment
        if adjustments:
            self.logger.info(
                f"Position sizing: ${base_size:.0f} → ${adjusted_size:.0f} "
                f"(multiplier: {multiplier:.2f}, adjustments: {', '.join(adjustments)})"
            )
        
        return adjusted_size
    
    def get_status(self) -> dict:
        """
        Get current position sizer configuration.
        
        Returns:
            Dict with configuration
        """
        return {
            'enabled': self.enabled,
            'config': {
                'win_streak_threshold': self.win_streak_threshold,
                'win_multiplier': self.win_multiplier,
                'loss_multiplier': self.loss_multiplier,
                'volatility_threshold': self.volatility_threshold,
                'max_multiplier': self.max_multiplier,
                'min_multiplier': self.min_multiplier
            }
        }
