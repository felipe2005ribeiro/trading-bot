#!/usr/bin/env python3
"""
Database Contents Checker

This script checks and displays all data stored in the trading bot database.
Useful for verifying that trades, positions, and metrics are being saved correctly.

Usage:
    python scripts/check_database.py

What it shows:
    - Total trades in database
    - Recent trade details
    - Open positions
    - Performance statistics
    - Stats by symbol
    - Stats by strategy

Requirements:
    - Database must exist (data/bot.db)
    - Bot must have run at least once
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_manager import DatabaseManager

def check_database():
    """Check what data was saved to database."""
    
    print("="*70)
    print("Database Contents Check")
    print("="*70)
    
    db = DatabaseManager("data/bot.db")
    
    # 1. Check trades
    print("\n1. TRADES")
    print("-" * 70)
    trades = db.get_trades(limit=100)
    print(f"Total trades in database: {len(trades)}")
    
    if trades:
        print("\nRecent trades:")
        for i, trade in enumerate(trades[:10], 1):
            print(f"\n  Trade {i}:")
            print(f"    Symbol: {trade['symbol']}")
            print(f"    Strategy: {trade['strategy']}")
            print(f"    Side: {trade['side']}")
            print(f"    Entry: ${trade['entry_price']:.2f}")
            print(f"    Exit: ${trade['exit_price']:.2f}" if trade['exit_price'] else "    Exit: N/A")
            print(f"    PnL: ${trade['pnl']:.2f}" if trade['pnl'] else "    PnL: N/A")
            print(f"    PnL%: {trade['pnl_percent']:.2f}%" if trade['pnl_percent'] else "    PnL%: N/A")
            print(f"    Exit Reason: {trade['exit_reason']}")
            print(f"    Timestamp: {trade['timestamp']}")
    else:
        print("  No trades recorded yet.")
    
    # 2. Check positions
    print("\n2. OPEN POSITIONS")
    print("-" * 70)
    positions = db.get_open_positions()
    print(f"Currently open positions: {len(positions)}")
    
    if positions:
        print("\nOpen positions:")
        for i, pos in enumerate(positions, 1):
            print(f"\n  Position {i}:")
            print(f"    Symbol: {pos['symbol']}")
            print(f"    Strategy: {pos['strategy']}")
            print(f"    Side: {pos['side']}")
            print(f"    Entry: ${pos['entry_price']:.2f}")
            print(f"    Current: ${pos['current_price']:.2f}" if pos['current_price'] else "    Current: N/A")
            print(f"    Amount: {pos['amount']}")
            print(f"    Unrealized PnL: ${pos['unrealized_pnl']:.2f}" if pos['unrealized_pnl'] else "    Unrealized PnL: N/A")
            print(f"    PnL%: {pos['pnl_percent']:.2f}%" if pos['pnl_percent'] else "    PnL%: N/A")
            print(f"    Entry Time: {pos['entry_time']}")
            print(f"    Updated: {pos['updated_at']}")
    else:
        print("  No open positions.")
    
    # 3. Performance stats
    print("\n3. PERFORMANCE STATISTICS")
    print("-" * 70)
    stats = db.get_performance_stats()
    
    if stats.get('total_trades', 0) > 0:
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Winning Trades: {stats['winning_trades']}")
        print(f"  Losing Trades: {stats['losing_trades']}")
        print(f"  Win Rate: {stats['win_rate']:.2f}%")
        print(f"  Total PnL: ${stats['total_pnl']:.2f}")
        print(f"  Average PnL: ${stats['avg_pnl']:.2f}")
        print(f"  Best Trade: ${stats['best_trade']:.2f}")
        print(f"  Worst Trade: ${stats['worst_trade']:.2f}")
        print(f"  Profit Factor: {stats['profit_factor']:.2f}")
        print(f"  First Trade: {stats['first_trade']}")
        print(f"  Last Trade: {stats['last_trade']}")
    else:
        print("  No trade statistics available yet.")
    
    # 4. Stats by symbol
    print("\n4. PERFORMANCE BY SYMBOL")
    print("-" * 70)
    by_symbol = db.get_stats_by_symbol()
    
    if by_symbol:
        for symbol, sym_stats in by_symbol.items():
            print(f"\n  {symbol}:")
            print(f"    Trades: {sym_stats['total_trades']}")
            print(f"    Win Rate: {sym_stats['win_rate']:.2f}%")
            print(f"    Total PnL: ${sym_stats['total_pnl']:.2f}")
            print(f"    Avg PnL: ${sym_stats['avg_pnl']:.2f}")
            print(f"    Best: ${sym_stats['best_trade']:.2f}")
            print(f"    Worst: ${sym_stats['worst_trade']:.2f}")
    else:
        print("  No symbol-specific data yet.")
    
    # 5. Stats by strategy
    print("\n5. PERFORMANCE BY STRATEGY")
    print("-" * 70)
    by_strategy = db.get_stats_by_strategy()
    
    if by_strategy:
        for strategy, strat_stats in by_strategy.items():
            print(f"\n  {strategy}:")
            print(f"    Trades: {strat_stats['total_trades']}")
            print(f"    Win Rate: {strat_stats['win_rate']:.2f}%")
            print(f"    Total PnL: ${strat_stats['total_pnl']:.2f}")
            print(f"    Avg PnL: ${strat_stats['avg_pnl']:.2f}")
    else:
        print("  No strategy-specific data yet.")
    
    print("\n" + "="*70)
    print("Database check complete!")
    print("="*70)

if __name__ == "__main__":
    check_database()
