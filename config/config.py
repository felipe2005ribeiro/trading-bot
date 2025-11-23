"""
Configuration module for the trading bot.
Loads all settings from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """
    Centralized configuration class.
    All configuration values are loaded from environment variables.
    """
    
    # ===================================
    # BINANCE API CONFIGURATION
    # ===================================
    BINANCE_TESTNET_API_KEY = os.getenv('BINANCE_TESTNET_API_KEY', '')
    BINANCE_TESTNET_API_SECRET = os.getenv('BINANCE_TESTNET_API_SECRET', '')
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    
    # Exchange settings
    EXCHANGE = os.getenv('EXCHANGE', 'binance')
    USE_TESTNET = os.getenv('TESTNET', 'true').lower() == 'true'
    
    # Backtest-specific: Use production data for historical backtesting (read-only)
    BACKTEST_USE_PRODUCTION_DATA = os.getenv('BACKTEST_USE_PRODUCTION_DATA', 'false').lower() == 'true'
    
    # ===================================
    # TRADING CONFIGURATION
    # ===================================
    SYMBOLS = os.getenv('SYMBOLS', 'BTC/USDT,ETH/USDT').split(',')
    TIMEFRAME = os.getenv('TIMEFRAME', '1h')
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '10000'))
    
    # ===================================
    # RISK MANAGEMENT
    # ===================================
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', '2'))
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '3'))
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '2'))
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '4'))
    MAX_PORTFOLIO_EXPOSURE = float(os.getenv('MAX_PORTFOLIO_EXPOSURE', '50'))
    
    # ===================================
    # STRATEGY CONFIGURATION
    # ===================================
    STRATEGY = os.getenv('STRATEGY', 'SMA_CROSS').upper()  # SMA_CROSS, RSI_BB, or BOTH
    SMA_SHORT_PERIOD = int(os.getenv('SMA_SHORT_PERIOD', '20'))
    SMA_LONG_PERIOD = int(os.getenv('SMA_LONG_PERIOD', '50'))
    
    # RSI + Bollinger Bands parameters
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD = float(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = float(os.getenv('RSI_OVERBOUGHT', '70'))
    BB_PERIOD = int(os.getenv('BB_PERIOD', '20'))
    BB_STD = float(os.getenv('BB_STD', '2.0'))
    
    
    # ===================================
    # EXECUTION MODE
    # ===================================
    EXECUTE_REAL = os.getenv('EXECUTE_REAL', 'false').lower() == 'true'
    
    # ===================================
    # BOT CONFIGURATION
    # ===================================
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '300'))
    
    # ===================================
    # KILL SWITCH (Risk Protection)
    # ===================================
    ENABLE_KILL_SWITCH = os.getenv('ENABLE_KILL_SWITCH', 'true').lower() == 'true'
    MAX_DRAWDOWN_PERCENT = float(os.getenv('MAX_DRAWDOWN_PERCENT', '10'))
    MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', '5'))
    KILL_SWITCH_COOLDOWN_MINUTES = int(os.getenv('KILL_SWITCH_COOLDOWN_MINUTES', '60'))
    
    
    # ===================================
    # BACKTESTING CONFIGURATION
    # ===================================
    COMMISSION_RATE = float(os.getenv('COMMISSION_RATE', '0.1'))
    SLIPPAGE_RATE = float(os.getenv('SLIPPAGE_RATE', '0.05'))
    
    # ===================================
    # LOGGING
    # ===================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
    LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'
    
    # ===================================
    # SCALPING CONFIGURATION
    # ===================================
    ENABLE_SCALPING = os.getenv('ENABLE_SCALPING', 'false').lower() == 'true'
    SCALPING_TIMEFRAMES = os.getenv('SCALPING_TIMEFRAMES', '5m,15m').split(',')
    SCALP_STOP_LOSS_PERCENT = float(os.getenv('SCALP_STOP_LOSS_PERCENT', '0.6'))
    SCALP_TAKE_PROFIT_PERCENT = float(os.getenv('SCALP_TAKE_PROFIT_PERCENT', '1.0'))
    
    # EMA Scalping
    EMA_FAST_PERIOD = int(os.getenv('EMA_FAST_PERIOD', '8'))
    EMA_SLOW_PERIOD = int(os.getenv('EMA_SLOW_PERIOD', '21'))
    
    # Volume Analysis
    VOLUME_SPIKE_THRESHOLD = float(os.getenv('VOLUME_SPIKE_THRESHOLD', '1.5'))
    ENABLE_VOLUME_FILTER = os.getenv('ENABLE_VOLUME_FILTER', 'true').lower() == 'true'
    
    # ===================================
    # TRAILING STOP CONFIGURATION
    # ===================================
    # DISABLED: Real 180-day data shows trailing stops hurt performance
    # BTC: -$468, ETH: -$730, SOL: no effect
    ENABLE_TRAILING_STOP = os.getenv('ENABLE_TRAILING_STOP', 'false').lower() == 'true'
    TRAILING_ACTIVATION_PERCENT = float(os.getenv('TRAILING_ACTIVATION_PERCENT', '1.5'))
    TRAILING_DISTANCE_PERCENT = float(os.getenv('TRAILING_DISTANCE_PERCENT', '0.8'))
    
    # Disabled - no symbols use trailing stops based on real data
    TRAILING_SYMBOLS = []  # Empty list
    
    # ===================================
    # TELEGRAM NOTIFICATIONS
    # ===================================
    TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # ===================================
    # SYMBOL-SPECIFIC STRATEGY CONFIGURATION
    # ===================================
    # Each symbol uses its optimal strategy based on 180-day REAL data analysis (production)
    # BTC: SMA_CROSS (+4.20%), ETH: EMA_SCALP (+10.58%), SOL: EMA_SCALP (+3.59%)
    # NOTE: Previous testnet data (18 days) gave incorrect results - this is validated
    # ONLY validated symbols included - BNB/ADA/DOT removed until validated
    SYMBOL_STRATEGIES = {
        'BTCUSDT': 'SMA_CROSS',   # Real data validated: +4.20% vs EMA_SCALP +1.07%
        'ETHUSDT': 'EMA_SCALP',   # Real data validated: +10.58% vs RSI_BB -33.60%
        'SOLUSDT': 'EMA_SCALP',   # Real data validated: +3.59% vs others negative
    }
    
    # Fallback strategy for symbols not in mapping
    DEFAULT_STRATEGY = STRATEGY
    
    # ===================================
    # MULTI-TIMEFRAME (MTF) ANALYSIS
    # ===================================
    # Filter trades based on higher timeframe trend
    ENABLE_MTF_FILTER = os.getenv('ENABLE_MTF_FILTER', 'true').lower() == 'true'
    TREND_TIMEFRAME = os.getenv('TREND_TIMEFRAME', '4h')  # Higher timeframe
    TREND_EMA_PERIOD = int(os.getenv('TREND_EMA_PERIOD', '200'))  # Trend definition
    
    # Selective MTF - only enable for symbols that benefit (based on real 180-day data)
    # ETH: +29% improvement (+$305), SOL: +48% improvement (+$173), BTC: hurts performance
    MTF_SYMBOLS = ['ETHUSDT', 'SOLUSDT']  # BTC excluded - MTF hurts its performance
    
    
    # ===================================
    # CIRCUIT BREAKER CONFIGURATION
    # ===================================
    # Protects against extreme market conditions with minimal profit impact (<0.5%)
    ENABLE_CIRCUIT_BREAKER = os.getenv('ENABLE_CIRCUIT_BREAKER', 'true').lower() == 'true'
    VOLATILITY_THRESHOLD = float(os.getenv('VOLATILITY_THRESHOLD', '5.0'))  # 5x normal volatility
    VOLUME_THRESHOLD = float(os.getenv('VOLUME_THRESHOLD', '0.2'))  # 20% of average volume
    SPREAD_THRESHOLD = float(os.getenv('SPREAD_THRESHOLD', '0.5'))  # 0.5% spread
    
    # ===================================
    # DYNAMIC POSITION SIZING (TIER 2)
    # ===================================
    # Adjusts position sizes based on win streaks and volatility
    ENABLE_DYNAMIC_SIZING = os.getenv('ENABLE_DYNAMIC_SIZING', 'true').lower() == 'true'
    SIZING_WIN_STREAK_THRESHOLD = int(os.getenv('SIZING_WIN_STREAK_THRESHOLD', '3'))  # 3 wins
    SIZING_WIN_MULTIPLIER = float(os.getenv('SIZING_WIN_MULTIPLIER', '1.2'))  # +20%
    SIZING_LOSS_MULTIPLIER = float(os.getenv('SIZING_LOSS_MULTIPLIER', '0.8'))  # -20%
    SIZING_VOLATILITY_THRESHOLD = float(os.getenv('SIZING_VOLATILITY_THRESHOLD', '1.5'))  # 1.5x ATR
    SIZING_MAX_MULTIPLIER = float(os.getenv('SIZING_MAX_MULTIPLIER', '1.5'))  # Max 150%
    SIZING_MIN_MULTIPLIER = float(os.getenv('SIZING_MIN_MULTIPLIER', '0.5'))  # Min 50%
    
    # ===================================
    # ATR-BASED STOP LOSS (TIER 2)
    # ===================================
    # Adaptive stop losses based on market volatility
    ENABLE_ATR_STOPS = os.getenv('ENABLE_ATR_STOPS', 'true').lower() == 'true'
    ATR_PERIOD = int(os.getenv('ATR_PERIOD', '14'))  # 14 candles for ATR calculation
    ATR_MIN_STOP_PCT = float(os.getenv('ATR_MIN_STOP_PCT', '1.0'))  # 1% minimum
    ATR_MAX_STOP_PCT = float(os.getenv('ATR_MAX_STOP_PCT', '5.0'))  # 5% maximum
    
    # Symbol-specific ATR multipliers
    ATR_MULTIPLIERS = {
        'BTCUSDT': 1.5,  # Less volatile
        'ETHUSDT': 2.0,  # Medium volatility
        'SOLUSDT': 2.5   # High volatility
    }
    
    # WEB DASHBOARD
    ENABLE_DASHBOARD = os.getenv('ENABLE_DASHBOARD', 'true').lower() == 'true'
    DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '5000'))
    
    # ===================================
    # DIRECTORIES
    # ===================================
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    RESULTS_DIR = BASE_DIR / 'results'
    
    @classmethod
    def get_api_credentials(cls) -> tuple:
        """
        Get the appropriate API credentials based on USE_TESTNET setting.
        
        Returns:
            tuple: (api_key, api_secret, is_testnet)
        """
        if cls.USE_TESTNET:
            return (cls.BINANCE_TESTNET_API_KEY, cls.BINANCE_TESTNET_API_SECRET, True)
        else:
            return (cls.BINANCE_API_KEY, cls.BINANCE_API_SECRET, False)
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate that all required configuration values are set.
        Raises ValueError if any required values are missing.
        """
        api_key, api_secret, is_testnet = cls.get_api_credentials()
        
        if not api_key or not api_secret:
            env_type = "testnet" if is_testnet else "production"
            raise ValueError(
                f"Missing Binance {env_type} API credentials. "
                f"Please set BINANCE_{'TESTNET_' if is_testnet else ''}API_KEY "
                f"and BINANCE_{'TESTNET_' if is_testnet else ''}API_SECRET in .env file"
            )
        
        if not cls.SYMBOLS:
            raise ValueError("No trading symbols configured. Set SYMBOLS in .env file")
        
        if cls.INITIAL_CAPITAL <= 0:
            raise ValueError("INITIAL_CAPITAL must be greater than 0")
        
        if cls.RISK_PER_TRADE <= 0 or cls.RISK_PER_TRADE > 100:
            raise ValueError("RISK_PER_TRADE must be between 0 and 100")
        
        if cls.MAX_POSITIONS <= 0:
            raise ValueError("MAX_POSITIONS must be greater than 0")
        
        # Create directories if they don't exist
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.RESULTS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (without sensitive data)."""
        print("=" * 50)
        print("TRADING BOT CONFIGURATION")
        print("=" * 50)
        print(f"Mode: {'TESTNET' if cls.USE_TESTNET else 'PRODUCTION'}")
        print(f"Execute Real Orders: {cls.EXECUTE_REAL}")
        print(f"Symbols: {', '.join(cls.SYMBOLS)}")
        print(f"Timeframe: {cls.TIMEFRAME}")
        print(f"Initial Capital: ${cls.INITIAL_CAPITAL:,.2f}")
        print(f"Risk per Trade: {cls.RISK_PER_TRADE}%")
        print(f"Max Positions: {cls.MAX_POSITIONS}")
        print(f"Stop Loss: {cls.STOP_LOSS_PERCENT}%")
        print(f"Take Profit: {cls.TAKE_PROFIT_PERCENT}%")
        print(f"SMA Strategy: {cls.SMA_SHORT_PERIOD}/{cls.SMA_LONG_PERIOD}")
        print(f"Update Interval: {cls.UPDATE_INTERVAL}s")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("=" * 50)
