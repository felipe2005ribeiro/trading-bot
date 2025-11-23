"""
Dashboard diagnostic script - captures all errors
"""

import sys
import os
import traceback

print("=" * 60)
print("DASHBOARD DIAGNOSTIC MODE")
print("=" * 60)

try:
    print("\n[1/5] Adding parent directory to Python path...")
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    print("      OK - Path added")
    
    print("\n[2/5] Importing DashboardServer...")
    from dashboard.server import DashboardServer
    print("      OK - Import successful")
    
    print("\n[3/5] Creating DashboardServer instance...")
    dashboard = DashboardServer(bot_instance=None)
    print("      OK - Instance created")
    
    print("\n[4/5] Checking Flask app...")
    print(f"      Flask app: {dashboard.app}")
    print(f"      Routes: {list(dashboard.app.url_map.iter_rules())[:5]}")
    
    print("\n[5/5] Starting Flask server...")
    print("\n" + "=" * 60)
    print("Dashboard URL: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    dashboard.app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )
    
except ImportError as e:
    print(f"\n[ERROR] Import failed: {e}")
    print("\nMissing module. Install with:")
    print("  pip install flask flask-cors")
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)
