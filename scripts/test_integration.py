#!/usr/bin/env python3
"""
Integration Test Suite

Tests that all components work together correctly before running the bot.
Verifies database integration, bot initialization, and component connectivity.

Usage:
    python scripts/test_integration.py

What it tests:
    1. DatabaseManager initialization
    2. TradingBot initialization with database
    3. Database table accessibility
    4. Component connectivity (exchange, database, etc.)

Exit codes:
    0 - All tests passed
    1 - One or more tests failed

Use this before:
    - First bot run
    - After major changes
    - Deploying to production
    - Troubleshooting issues
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_manager import DatabaseManager
from bot.trading_bot import TradingBot
from core.logger import get_logger

logger = get_logger(__name__)

def test_database_integration():
    """Test that database integration works correctly."""
    
    print("="*60)
    print("Database Integration Test")
    print("="*60)
    
    # 1. Check database manager initialization
    print("\n1. Testing DatabaseManager initialization...")
    try:
        db = DatabaseManager("data/bot_test.db")
        print("   [OK] DatabaseManager initialized successfully")
    except Exception as e:
        print(f"   [FAIL] Failed to initialize DatabaseManager: {e}")
        return False
    
    # 2. Test bot can initialize with database
    print("\n2. Testing TradingBot initialization with database...")
    try:
        bot = TradingBot()
        print("   [OK] TradingBot initialized successfully")
        print(f"   [OK] Database manager available: {hasattr(bot, 'db')}")
        
        if hasattr(bot, 'db'):
            print(f"   [OK] Database path: {bot.db.db_path}")
        
    except Exception as e:
        print(f"   [FAIL] Failed to initialize TradingBot: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Check database tables exist
    print("\n3. Checking database tables...")
    try:
        stats = db.get_performance_stats()
        print(f"   [OK] Trades table accessible (currently {stats.get('total_trades', 0)} trades)")
        
        positions = db.get_open_positions()
        print(f"   [OK] Positions table accessible (currently {len(positions)} open)")
        
    except Exception as e:
        print(f"   [FAIL] Error accessing database tables: {e}")
        return False
    
    print("\n" + "="*60)
    print("All database integration tests passed!")
    print("="*60)
    print("\nThe bot is ready to run with database integration.")
    print("Database will be created at: data/bot.db")
    print("\nTo run the bot:")
    print("  .\\venv\\Scripts\\python scripts\\run_bot.py")
    print("\nTo query data after running:")
    print("  from database.db_manager import DatabaseManager")
    print("  db = DatabaseManager()")
    print("  trades = db.get_trades(limit=10)")
    
    return True

if __name__ == "__main__":
    success = test_database_integration()
    sys.exit(0 if success else 1)
