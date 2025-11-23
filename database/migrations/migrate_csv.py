"""
Migration script to migrate data from CSV files to SQLite database.
Run this once to populate the database with historical data.
"""

import csv
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.db_manager import DatabaseManager
from core.logger import get_logger

logger = get_logger(__name__)


def migrate_trades(db: DatabaseManager, csv_path: Path) -> int:
    """
    Migrate trades from CSV to database.
    
    Args:
        db: DatabaseManager instance
        csv_path: Path to trades.csv file
        
    Returns:
        Number of trades migrated
    """
    if not csv_path.exists():
        logger.warning(f"⚠️  {csv_path} not found, skipping trades migration")
        return 0
    
    count = 0
    skipped = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Generate unique trade ID
                    trade_id = row.get('id')
                    if not trade_id:
                        timestamp = row.get('timestamp', row.get('exit_time', ''))
                        trade_id = f"trade_{row['symbol']}_{timestamp}".replace(' ', '_').replace(':', '')
                    
                    trade_data = {
                        'trade_id': trade_id,
                        'timestamp': row.get('timestamp', row.get('exit_time')),
                        'symbol': row['symbol'],
                        'strategy': row.get('strategy', 'UNKNOWN'),
                        'side': row['side'],
                        'entry_price': float(row['entry_price']),
                        'exit_price': float(row.get('exit_price', 0)) if row.get('exit_price') else None,
                        'entry_time': row.get('entry_time', row.get('timestamp')),
                        'exit_time': row.get('exit_time'),
                        'amount': float(row.get('amount', 0)),
                        'pnl': float(row.get('pnl', 0)) if row.get('pnl') else None,
                        'pnl_percent': float(row.get('pnl_percent', 0)) if row.get('pnl_percent') else None,
                        'fees': float(row.get('fees', 0)) if row.get('fees') else 0,
                        'exit_reason': row.get('reason', row.get('exit_reason', 'unknown'))
                    }
                    
                    db.insert_trade(trade_data)
                    count += 1
                    
                    if count % 10 == 0:
                        logger.info(f"Migrated {count} trades...")
                        
                except Exception as e:
                    logger.error(f"Error migrating trade row: {e} | Row: {row}")
                    skipped += 1
        
        logger.info(f"✅ Successfully migrated {count} trades, skipped {skipped}")
        return count
        
    except Exception as e:
        logger.error(f"Error reading trades CSV: {e}")
        return count


def migrate_positions(db: DatabaseManager, csv_path: Path) -> int:
    """
    Migrate positions from CSV to database.
    
    Args:
        db: DatabaseManager instance
        csv_path: Path to positions.csv file
        
    Returns:
        Number of positions migrated
    """
    if not csv_path.exists():
        logger.warning(f"⚠️  {csv_path} not found, skipping positions migration")
        return 0
    
    count = 0
    skipped = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Generate unique position ID
                    position_id = row.get('id')
                    if not position_id:
                        entry_time = row.get('entry_time', '')
                        position_id = f"pos_{row['symbol']}_{entry_time}".replace(' ', '_').replace(':', '')
                    
                    position_data = {
                        'position_id': position_id,
                        'symbol': row['symbol'],
                        'strategy': row.get('strategy', 'UNKNOWN'),
                        'side': row.get('side', 'LONG'),
                        'entry_price': float(row['entry_price']),
                        'current_price': float(row.get('current_price', row['entry_price'])),
                        'amount': float(row.get('amount', 0)),
                        'entry_time': row.get('entry_time'),
                        'stop_loss': float(row.get('stop_loss', 0)) if row.get('stop_loss') else None,
                        'take_profit': float(row.get('take_profit', 0)) if row.get('take_profit') else None,
                        'unrealized_pnl': float(row.get('unrealized_pnl', 0)) if row.get('unrealized_pnl') else None,
                        'pnl_percent': float(row.get('pnl_percent', 0)) if row.get('pnl_percent') else None,
                        'status': row.get('status', 'CLOSED')  # Old positions are likely closed
                    }
                    
                    db.upsert_position(position_data)
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Error migrating position row: {e} | Row: {row}")
                    skipped += 1
        
        logger.info(f"✅ Successfully migrated {count} positions, skipped {skipped}")
        return count
        
    except Exception as e:
        logger.error(f"Error reading positions CSV: {e}")
        return count


def main():
    """Main migration function."""
    print("\n" + "="*60)
    print("🚀 Trading Bot - Database Migration Script")
    print("="*60 + "\n")
    
    # Initialize database
    print("📊 Initializing database...")
    db = DatabaseManager()
    print("✅ Database initialized\n")
    
    # Path to data directory
    data_dir = Path("data")
    
    if not data_dir.exists():
        print(f"⚠️  Data directory not found: {data_dir}")
        print("Creating data directory...")
        data_dir.mkdir(exist_ok=True)
    
    # Migrate trades
    print("\n📈 Migrating trades...")
    trades_csv = data_dir / "trades.csv"
    trades_count = migrate_trades(db, trades_csv)
    
    # Migrate positions
    print("\n📌 Migrating positions...")
    positions_csv = data_dir / "positions.csv"
    positions_count = migrate_positions(db, positions_csv)
    
    # Summary
    print("\n" + "="*60)
    print("✅ Migration Complete!")
    print("="*60)
    print(f"📈 Trades migrated: {trades_count}")
    print(f"📌 Positions migrated: {positions_count}")
    
    # Get some stats
    stats = db.get_performance_stats()
    if stats and stats.get('total_trades', 0) > 0:
        print("\n📊 Quick Stats:")
        print(f"   - Total trades: {stats['total_trades']}")
        print(f"   - Winning trades: {stats['winning_trades']}")
        print(f"   - Win rate: {stats.get('win_rate', 0):.2f}%")
        print(f"   - Total PnL: ${stats.get('total_pnl', 0):.2f}")
        print(f"   - Profit factor: {stats.get('profit_factor', 0):.2f}")
    
    print("\n✅ Database ready to use!")
    print(f"   Location: {db.db_path.absolute()}\n")


if __name__ == "__main__":
    main()
