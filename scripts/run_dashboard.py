"""
Start the trading bot dashboard web server.
Provides real-time monitoring interface for the bot.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dashboard.server import DashboardServer
from core.logger import get_logger

def main():
    """Start the dashboard server."""
    logger = get_logger(__name__)
    
    print("=" * 60)
    print("TRADING BOT DASHBOARD")
    print("=" * 60)
    print()
    print("Starting dashboard server...")
    print()
    print("Dashboard URL: http://localhost:5000")
    print("Auto-refresh: Every 5 seconds")
    print("Status: Ready")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Create and run dashboard server
    # Note: For full integration, pass bot instance here
    # Example: server = DashboardServer(bot_instance=your_bot)
    server = DashboardServer()
    
    try:
        server.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n Dashboard stopped by user")
        logger.info("Dashboard server shut down")
    except Exception as e:
        print(f"\n\nDashboard error: {e}")
        logger.error(f"Dashboard server error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
