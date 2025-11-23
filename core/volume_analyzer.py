"""
Volume analysis module for detecting significant volume patterns.
Provides tools for identifying volume spikes, trends, and validating trade signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from core.logger import get_logger


class VolumeAnalyzer:
    """
    Analyzes volume patterns to validate trading signals and detect market activity.
    """
    
    def __init__(self, spike_threshold: float = 2.0):
        """
        Initialize volume analyzer.
        
        Args:
            spike_threshold: Multiplier for detecting volume spikes (e.g., 2.0 = 2x average)
        """
        self.logger = get_logger(__name__)
        self.spike_threshold = spike_threshold
        self.logger.info(f"VolumeAnalyzer initialized with spike threshold: {spike_threshold}x")
    
    def is_volume_spike(self, df: pd.DataFrame, threshold: float = None) -> bool:
        """
        Check if current volume is significantly above average.
        
        Args:
            df: DataFrame with volume data
            threshold: Custom threshold multiplier (uses default if None)
            
        Returns:
            True if volume spike detected
        """
        if len(df) < 20:
            return False
        
        threshold = threshold or self.spike_threshold
        current_volume = df.iloc[-1]['volume']
        avg_volume = df['volume_sma'].iloc[-1] if 'volume_sma' in df.columns else df['volume'].rolling(20).mean().iloc[-1]
        
        return current_volume >= (avg_volume * threshold)
    
    def get_volume_ratio(self, df: pd.DataFrame) -> float:
        """
        Get ratio of current volume to average volume.
        
        Args:
            df: DataFrame with volume data
            
        Returns:
            Volume ratio (e.g., 2.5 means 2.5x average)
        """
        if len(df) < 20:
            return 1.0
        
        current_volume = df.iloc[-1]['volume']
        avg_volume = df['volume_sma'].iloc[-1] if 'volume_sma' in df.columns else df['volume'].rolling(20).mean().iloc[-1]
        
        if avg_volume == 0:
            return 1.0
        
        return current_volume / avg_volume
    
    def get_obv_trend(self, df: pd.DataFrame, period: int = 14) -> str:
        """
        Determine OBV (On-Balance Volume) trend.
        
        Args:
            df: DataFrame with OBV data
            period: Period for OBV moving average
            
        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        if 'obv' not in df.columns or len(df) < period + 5:
            return 'neutral'
        
        # Calculate OBV moving average
        obv_ma = df['obv'].rolling(window=period).mean()
        
        if len(obv_ma) < 2:
            return 'neutral'
        
        current_obv = df['obv'].iloc[-1]
        current_obv_ma = obv_ma.iloc[-1]
        prev_obv_ma = obv_ma.iloc[-2]
        
        # OBV above rising MA = bullish
        if current_obv > current_obv_ma and current_obv_ma > prev_obv_ma:
            return 'bullish'
        # OBV below falling MA = bearish
        elif current_obv < current_obv_ma and current_obv_ma < prev_obv_ma:
            return 'bearish'
        else:
            return 'neutral'
    
    def validate_signal_with_volume(
        self,
        signal: str,
        df: pd.DataFrame,
        require_spike: bool = True,
        require_obv_confirmation: bool = False
    ) -> tuple[bool, str]:
        """
        Validate a trading signal using volume analysis.
        
        Args:
            signal: 'buy' or 'sell'
            df: DataFrame with volume and price data
            require_spike: Require volume spike for validation
            require_obv_confirmation: Require OBV trend to match signal
            
        Returns:
            Tuple of (is_valid, reason)
        """
        validations = []
        
        # Check volume spike
        if require_spike:
            has_spike = self.is_volume_spike(df)
            volume_ratio = self.get_volume_ratio(df)
            
            if not has_spike:
                return False, f"Low volume (ratio: {volume_ratio:.2f}x)"
            
            validations.append(f"Volume spike: {volume_ratio:.2f}x")
        
        # Check OBV trend
        if require_obv_confirmation:
            obv_trend = self.get_obv_trend(df)
            
            if signal == 'buy' and obv_trend == 'bearish':
                return False, f"OBV bearish contradicts buy signal"
            elif signal == 'sell' and obv_trend == 'bullish':
                return False, f"OBV bullish contradicts sell signal"
            
            validations.append(f"OBV: {obv_trend}")
        
        reason = " | ".join(validations) if validations else "Volume OK"
        return True, reason
    
    def get_vwap_position(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze price position relative to VWAP.
        
        Args:
            df: DataFrame with VWAP data
            
        Returns:
            Dictionary with VWAP analysis
        """
        if 'vwap' not in df.columns or len(df) < 2:
            return {'position': 'unknown', 'distance_percent': 0}
        
        current_price = df.iloc[-1]['close']
        vwap = df.iloc[-1]['vwap']
        
        distance_percent = ((current_price - vwap) / vwap) * 100
        
        if current_price > vwap:
            position = 'above'
        elif current_price < vwap:
            position = 'below'
        else:
            position = 'at'
        
        return {
            'position': position,
            'vwap': vwap,
            'price': current_price,
            'distance_percent': distance_percent
        }
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive volume analysis.
        
        Args:
            df: DataFrame with volume and price data
            
        Returns:
            Dictionary with complete volume analysis
        """
        analysis = {
            'volume_spike': self.is_volume_spike(df),
            'volume_ratio': self.get_volume_ratio(df),
            'obv_trend': self.get_obv_trend(df),
            'vwap_position': self.get_vwap_position(df)
        }
        
        return analysis
    
    def get_strength_score(self, df: pd.DataFrame, signal: str) -> float:
        """
        Calculate signal strength score based on volume (0-100).
        
        Args:
            df: DataFrame with volume data
            signal: 'buy' or 'sell'
            
        Returns:
            Strength score (0-100)
        """
        score = 50.0  # Base score
        
        # Volume spike adds points
        volume_ratio = self.get_volume_ratio(df)
        if volume_ratio >= 3.0:
            score += 30
        elif volume_ratio >= 2.0:
            score += 20
        elif volume_ratio >= 1.5:
            score += 10
        
        # OBV confirmation adds points
        obv_trend = self.get_obv_trend(df)
        if (signal == 'buy' and obv_trend == 'bullish') or \
           (signal == 'sell' and obv_trend == 'bearish'):
            score += 20
        elif obv_trend == 'neutral':
            score += 0
        else:
            score -= 20  # Contradictory trend
        
        return max(0, min(100, score))
