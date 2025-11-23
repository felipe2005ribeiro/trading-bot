#!/usr/bin/env python3
"""
Script to run the trading bot with integrated dashboard.
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
        
        # Start dashboard server in separate thread (if enabled)
        dashboard_thread = None
        if Config.ENABLE_DASHBOARD:
            try:
                from dashboard.server import DashboardServer
                import threading
                
                logger.info("Starting dashboard server...")
                dashboard = DashboardServer(bot_instance=bot)
                
                def run_dashboard():
                    """Run dashboard in separate thread."""
                    dashboard.app.run(
                        host=Config.DASHBOARD_HOST,
                        port=Config.DASHBOARD_PORT,
                        debug=False,
                        use_reloader=False
                    )
                
                dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
                dashboard_thread.start()
                logger.info(f"Dashboard available at http://{Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
                
            except Exception as e:
                logger.warning(f"Dashboard failed to start: {e}")
                logger.info("Bot will continue without dashboard")
        
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
