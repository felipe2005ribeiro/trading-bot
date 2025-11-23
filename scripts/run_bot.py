#!/usr/bin/env python3
"""
Script to run the trading bot.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.config import Config
from bot.trading_bot import TradingBot
from core.logger import setup_logger


def main():
    """Main function to run the trading bot."""
    # Setup logger
    logger = setup_logger('bot_runner', 'trading_bot.log')
    
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Config.validate()
        
        # Create and start bot
        logger.info("Creating trading bot instance...")
        bot = TradingBot()
        
        logger.info("Starting trading bot...")
        bot.start()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
        return 0
        
    except Exception as e:
        logger.error(f"Bot failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
