"""
Dashboard Test Data Injector
Populates the trading bot with simulated data to test the dashboard.
"""

import sys
import os
from datetime import datetime, timedelta
import random
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.trading_bot import TradingBot
from risk.position_manager import Position
from core.logger import get_logger

logger = get_logger(__name__)


def inject_test_data(bot):
    """Inject test trading data into the bot for dashboard testing."""
    
    print("\n" + "="*60)
    print("INJECTING TEST DATA FOR DASHBOARD")
    print("="*60 + "\n")
    
    # 1. Inject closed trades (trade history)
    print("Creating trade history...")
    
    closed_trades_data = [
        # Winning trades
        ('BTC/USDT', 95000.0, 95950.0, 0.1),
        ('ETH/USDT', 2800.0, 2912.0, 3.5),
        ('BNB/USDT', 630.0, 636.3, 1.5),
        # Losing trades
        ('SOL/USDT', 230.0, 228.62, 4.0),
        ('ADA/USDT', 0.62, 0.607, 1500.0),
        ('DOT/USDT', 7.50, 7.41, 120.0),
    ]
    
    # Inject closed positions as Position objects
    total_pnl = 0
    for i,  (symbol, entry, exit_pr, amount) in enumerate(closed_trades_data):
        # Calculate SL/TP
        if exit_pr > entry:
            sl = entry * 0.98
            tp = exit_pr
        else:
            sl = exit_pr
            tp = entry * 1.02
        
        position = Position(
            symbol=symbol,
            side='buy',
            entry_price=entry,
            amount=amount,
            stop_loss=sl,
            take_profit=tp,
            entry_time=datetime.now() - timedelta(hours=8-i)
        )
        # Close the position
        position.close(exit_price=exit_pr, exit_time=datetime.now() - timedelta(hours=7-i))
        
        # Add to closed positions
        bot.position_manager.closed_positions.append(position)
        
        # Update risk manager stats
        if position.pnl > 0:
            bot.risk_manager.winning_trades += 1
        else:
            bot.risk_manager.losing_trades += 1
        
        bot.risk_manager.total_trades += 1
        total_pnl += position.pnl
    
    # Update capital based on trades
    bot.risk_manager.current_capital += total_pnl
    
    print(f"  ✓ Created {len(closed_trades_data)} closed trades")
    print(f"  ✓ Total PnL: ${total_pnl:.2f}")
    print(f"  ✓ Win Rate: {bot.risk_manager.winning_trades}/{bot.risk_manager.total_trades}")
    print(f"  ✓ New Capital: ${bot.risk_manager.current_capital:.2f}")
    
    # 2. Inject open positions
    print("\nCreating open positions...")
    
    open_positions_data = [
        ('BTC/USDT', 95280.0, 0.08),
        ('ETH/USDT', 2770.0, 3.0),
    ]
    
    # Inject open positions
    for symbol, entry, amount in open_positions_data:
        position = Position(
            symbol=symbol,
            side='buy',
            entry_price=entry,
            amount=amount,
            stop_loss=entry * 0.994,  # -0.6% for scalping
            take_profit=entry * 1.01,  # +1.0% for scalping
            entry_time=datetime.now() - timedelta(minutes=random.randint(20, 45))
        )
        bot.position_manager.open_positions[symbol] = position
        
        # Calculate unrealized PnL with slight price движение
        current_price = entry * random.uniform(1.001, 1.005)
        unrealized_pnl, _ = position.calculate_pnl(current_price)
        print(f"    - {symbol}: ${unrealized_pnl:+.2f} unrealized PnL")
    
    print(f"  ✓ Created {len(open_positions_data)} open positions")
    
    # 3. Populate equity history in dashboard
    print("\nPopulating equity curve...")
    
    # Create equity history for the last 2 hours
    base_capital = bot.risk_manager.initial_capital
    current_time = datetime.now()
    
    # Simulate equity growth over 2 hours (every 5 minutes)
    for minutes_ago in range(120, 0, -5):
        timestamp = current_time - timedelta(minutes=minutes_ago)
        # Simulate some volatility
        progress = 1 - (minutes_ago / 120)
        growth = total_pnl * progress
        noise = random.uniform(-50, 50)
        capital_at_time = base_capital + growth + noise
        
        bot.dashboard.equity_history.append((timestamp, capital_at_time))
    
    # Add current capital
    bot.dashboard.equity_history.append((current_time, bot.risk_manager.current_capital))
    bot.dashboard.last_equity_update = current_time
    
    print(f"  ✓ Created equity history with {len(bot.dashboard.equity_history)} data points")
    
    print("\n" + "="*60)
    print("TEST DATA INJECTION COMPLETE!")
    print("="*60)
    print()
    print("Dashboard should now show:")
    print(f"  • Capital: ${bot.risk_manager.current_capital:.2f}")
    print(f"  • Total Trades: {bot.risk_manager.total_trades}")
    print(f"  • Win Rate: {(bot.risk_manager.winning_trades/bot.risk_manager.total_trades*100):.1f}%")
    print(f"  • Open Positions: {len(bot.position_manager.open_positions)}")
    print(f"  • Equity Curve: {len(bot.dashboard.equity_history)} points")
    print()
    print("Open dashboard: http://localhost:5000")
    print()


def main():
    """Create bot with test data and keep it running."""
    
    print("\nStarting Trading Bot in TEST MODE...")
    print("This will populate the dashboard with sample data.\n")
    
    try:
        # Initialize bot
        bot = TradingBot()
        
        # Wait for dashboard to start
        time.sleep(2)
        
        # Inject test data
        inject_test_data(bot)
        
        # Keep bot running so dashboard stays accessible
        # Don't call bot.start() because it will execute trades and overwrite test data
        print("Bot is running with test data...")
        print("Dashboard: http://localhost:5000")
        print("Press Ctrl+C to stop\n")
        
        # Keep script alive so dashboard stays accessible
        while True:
            time.sleep(10)
        
        
    except KeyboardInterrupt:
        print("\n\nTest bot stopped by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        logger.error(f"Test bot error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
