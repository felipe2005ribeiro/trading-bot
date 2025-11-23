"""
Simple test script to verify database functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_manager import DatabaseManager
from datetime import datetime

def test_database():
    """Test database operations."""
    print("="*60)
    print("Database Test Script")
    print("="*60)
    
    # Initialize database
    print("\n1. Initializing database...")
    db = DatabaseManager("data/test.db")
    print("   OK - Database initialized")
    
    # Test inserting a trade
    print("\n2. Testing trade insertion...")
    trade_data = {
        'trade_id': 'test_001',
        'timestamp': datetime.now().isoformat(),
        'symbol': 'BTCUSDT',
        'strategy': 'SMA_CROSS',
        'side': 'LONG',
        'entry_price': 50000.0,
        'exit_price': 51000.0,
        'entry_time': datetime.now().isoformat(),
        'exit_time': datetime.now().isoformat(),
        'amount': 0.01,
        'pnl': 10.0,
        'pnl_percent': 2.0,
        'exit_reason': 'take_profit'
    }
    db.insert_trade(trade_data)
    print("   OK - Trade inserted")
    
    # Test querying trades
    print("\n3. Testing trade query...")
    trades = db.get_trades(limit=10)
    print(f"   OK - Retrieved {len(trades)} trade(s)")
    
    # Test position upsert
    print("\n4. Testing position upsert...")
    position_data = {
        'position_id': 'pos_001',
        'symbol': 'ETHUSDT',
        'strategy': 'EMA_SCALP',
        'side': 'LONG',
        'entry_price': 2000.0,
        'current_price': 2050.0,
        'amount': 1.0,
        'entry_time': datetime.now().isoformat(),
        'unrealized_pnl': 50.0,
        'pnl_percent': 2.5,
        'status': 'OPEN'
    }
    db.upsert_position(position_data)
    print("   OK - Position inserted/updated")
    
    # Test getting open positions
    print("\n5. Testing open positions query...")
    positions = db.get_open_positions()
    print(f"   OK - Retrieved {len(positions)} open position(s)")
    
    # Test performance stats
    print("\n6. Testing performance stats...")
    stats = db.get_performance_stats()
    print(f"   OK - Stats retrieved:")
    print(f"      Total trades: {stats.get('total_trades', 0)}")
    print(f"      Total PnL: ${stats.get('total_pnl', 0):.2f}")
    
    print("\n" + "="*60)
    print("All tests passed!")
    print("="*60)

if __name__ == "__main__":
    test_database()
