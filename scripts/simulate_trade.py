#!/usr/bin/env python3
"""
Trade Simulator for Database Testing

This script simulates a complete trade lifecycle to test database integration.
Creates fake trades and position snapshots to verify data is saved correctly.

Usage:
    python scripts/simulate_trade.py

What it does:
    1. Creates a simulated open position
    2. Saves position snapshot to database
    3. Simulates position close
    4. Saves completed trade with PnL
    5. Verifies all data was saved correctly

Use this to:
    - Test database integration without running live bot
    - Verify trade logging works
    - Check database schema is correct
    - Test performance analytics

Output:
    Shows step-by-step progress and final statistics
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_manager import DatabaseManager

def simulate_trade():
    """Simulate a complete trade lifecycle."""
    
    print("="*70)
    print("Simulating Trade for Database Test")
    print("="*70)
    
    db = DatabaseManager("data/bot.db")
    
    # Simulate trade parameters
    symbol = "BTCUSDT"
    strategy = "SMA_CROSS"
    entry_price = 50000.00
    exit_price = 51500.00  # Profitable trade
    amount = 0.1
    
    # Calculate PnL
    pnl = (exit_price - entry_price) * amount
    pnl_percent = ((exit_price - entry_price) / entry_price) * 100
    
    # Generate timestamps
    entry_time = datetime.now() - timedelta(hours=2, minutes=30)
    exit_time = datetime.now()
    
    # Trade data
    trade_data = {
        'trade_id': f"trade_{symbol}_{int(entry_time.timestamp())}",
        'timestamp': exit_time.isoformat(),
        'symbol': symbol,
        'strategy': strategy,
        'side': 'LONG',
        'entry_price': entry_price,
        'exit_price': exit_price,
        'entry_time': entry_time.isoformat(),
        'exit_time': exit_time.isoformat(),
        'amount': amount,
        'pnl': pnl,
        'pnl_percent': pnl_percent,
        'fees': 0.1,  # $0.10 in fees
        'exit_reason': 'take_profit',
        'notes': 'Simulated trade for testing database'
    }
    
    print("\n1. Simulating Trade Entry...")
    print(f"   Symbol: {symbol}")
    print(f"   Strategy: {strategy}")
    print(f"   Side: LONG")
    print(f"   Entry Price: ${entry_price:,.2f}")
    print(f"   Amount: {amount} BTC")
    print(f"   Entry Time: {entry_time}")
    
    # First, insert a position snapshot (simulating an open position)
    print("\n2. Creating Position Snapshot...")
    position_data = {
        'position_id': f"pos_{symbol}_{int(entry_time.timestamp())}",
        'symbol': symbol,
        'strategy': strategy,
        'side': 'LONG',
        'entry_price': entry_price,
        'current_price': 50750.00,  # Mid-way price
        'amount': amount,
        'entry_time': entry_time.isoformat(),
        'stop_loss': 49000.00,
        'take_profit': 52000.00,
        'unrealized_pnl': (50750.00 - entry_price) * amount,
        'pnl_percent': ((50750.00 - entry_price) / entry_price) * 100,
        'status': 'OPEN'
    }
    
    try:
        db.upsert_position(position_data)
        print("   [OK] Position snapshot saved")
        print(f"   Unrealized PnL: ${position_data['unrealized_pnl']:,.2f}")
    except Exception as e:
        print(f"   [FAIL] Error saving position: {e}")
        return False
    
    # Now close the position by marking it closed and inserting the trade
    print("\n3. Simulating Position Close...")
    print(f"   Exit Price: ${exit_price:,.2f}")
    print(f"   Exit Time: {exit_time}")
    print(f"   Duration: 2 hours 30 minutes")
    print(f"   Exit Reason: take_profit")
    
    try:
        # Mark position as closed
        position_data['status'] = 'CLOSED'
        position_data['current_price'] = exit_price
        position_data['unrealized_pnl'] = pnl
        position_data['pnl_percent'] = pnl_percent
        db.upsert_position(position_data)
        print("   [OK] Position marked as closed")
    except Exception as e:
        print(f"   [FAIL] Error closing position: {e}")
        return False
    
    # Insert the completed trade
    print("\n4. Saving Completed Trade...")
    print(f"   PnL: ${pnl:,.2f} ({pnl_percent:+.2f}%)")
    print(f"   Fees: ${trade_data['fees']:.2f}")
    print(f"   Net PnL: ${pnl - trade_data['fees']:,.2f}")
    
    try:
        db.insert_trade(trade_data)
        print("   [OK] Trade saved to database")
    except Exception as e:
        print(f"   [FAIL] Error saving trade: {e}")
        return False
    
    # Verify data was saved
    print("\n5. Verifying Saved Data...")
    
    # Check trades
    trades = db.get_trades(limit=5)
    print(f"   Trades in DB: {len(trades)}")
    
    if trades:
        latest_trade = trades[0]
        print(f"   Latest trade: {latest_trade['symbol']} - ${latest_trade['pnl']:.2f}")
    
    # Check positions
    positions = db.get_open_positions()
    print(f"   Open positions: {len(positions)}")
    
    # Get stats
    stats = db.get_performance_stats()
    print(f"\n   Performance Stats:")
    print(f"     Total Trades: {stats.get('total_trades', 0)}")
    print(f"     Win Rate: {stats.get('win_rate', 0):.2f}%")
    print(f"     Total PnL: ${stats.get('total_pnl', 0):,.2f}")
    print(f"     Profit Factor: {stats.get('profit_factor', 0):.2f}")
    
    print("\n" + "="*70)
    print("Trade Simulation Complete!")
    print("="*70)
    print("\nYou can now run: python scripts/check_database.py")
    print("to see all the saved data in detail.")
    
    return True

if __name__ == "__main__":
    success = simulate_trade()
    sys.exit(0 if success else 1)
