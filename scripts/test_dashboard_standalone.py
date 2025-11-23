"""
Standalone dashboard server for testing.
Run this to test dashboard without full bot.
"""

import sys
import os

# Add parent directory to path to import dashboard module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dashboard.server import DashboardServer

if __name__ == '__main__':
    print("=" * 50)
    print("TRADING BOT DASHBOARD - TEST MODE")
    print("=" * 50)
    print("\nDashboard URL: http://localhost:5000")
    print("Mode: MOCK DATA (no bot connected)")
    print("\nPress Ctrl+C to stop\n")
    
    # Create dashboard without bot instance (will use mock data)
    dashboard = DashboardServer(bot_instance=None)
    
    try:
        # Run Flask server
        dashboard.app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Disable debug to reduce output
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\nDashboard stopped")
        sys.exit(0)
