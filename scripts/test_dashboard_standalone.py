"""
Standalone dashboard server for testing.
Run this to test dashboard without full bot.
"""

from dashboard.server import DashboardServer
import sys

if __name__ == '__main__':
    print("🚀 Starting Dashboard Server...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("⚠️  Running in MOCK DATA mode (no bot connected)")
    print("\n💡 Press Ctrl+C to stop\n")
    
    # Create dashboard without bot instance (will use mock data)
    dashboard = DashboardServer(bot_instance=None)
    
    try:
        # Run Flask server
        dashboard.app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid double startup
        )
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped")
        sys.exit(0)
