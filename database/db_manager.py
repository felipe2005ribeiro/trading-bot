"""
Database Manager for Trading Bot.
Handles all database operations using SQLite.
"""

import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Any
import json
from contextlib import contextmanager
import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """
    Manages all database operations for the trading bot.
    Uses SQLite for lightweight, serverless database.
    """
    
    def __init__(self, db_path: str = "data/bot.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing database at {self.db_path}")
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Ensures proper connection handling and rollback on errors.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database with schema if not exists."""
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        try:
            with self.get_connection() as conn:
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # =========================================================================
    # TRADES - Complete history of closed trades
    # =========================================================================
    
    def insert_trade(self, trade_data: Dict[str, Any]):
        """
        Insert a new completed trade.
        
        Args:
            trade_data: Dictionary with trade information
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO trades (
                        trade_id, timestamp, symbol, strategy, side,
                        entry_price, exit_price, entry_time, exit_time,
                        amount, pnl, pnl_percent, fees, exit_reason, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade_data.get('trade_id'),
                    trade_data.get('timestamp'),
                    trade_data.get('symbol'),
                    trade_data.get('strategy'),
                    trade_data.get('side'),
                    trade_data.get('entry_price'),
                    trade_data.get('exit_price'),
                    trade_data.get('entry_time'),
                    trade_data.get('exit_time'),
                    trade_data.get('amount'),
                    trade_data.get('pnl'),
                    trade_data.get('pnl_percent'),
                    trade_data.get('fees', 0),
                    trade_data.get('exit_reason'),
                    trade_data.get('notes')
                ))
            logger.info(f"Trade saved: {trade_data.get('symbol')} {trade_data.get('side')} PnL: {trade_data.get('pnl')}")
        except Exception as e:
            logger.error(f"Error inserting trade: {e}")
            raise
    
    def get_trades(self, symbol: Optional[str] = None, 
                   strategy: Optional[str] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[Dict]:
        """
        Get trade history with optional filters.
        
        Args:
            symbol: Filter by symbol (optional)
            strategy: Filter by strategy (optional)
            limit: Maximum number of trades to return
            offset: Pagination offset
            
        Returns:
            List of trade dictionaries
        """
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []
    
    def get_trade_count(self) -> int:
        """Get total number of trades."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM trades")
                return cursor.fetchone()['count']
        except Exception as e:
            logger.error(f"Error getting trade count: {e}")
            return 0
    
    # =========================================================================
    # POSITIONS - Current open positions snapshot
    # =========================================================================
    
    def upsert_position(self, position_data: Dict[str, Any]):
        """
        Insert or update a position.
        
        Args:
            position_data: Dictionary with position information
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO positions (
                        position_id, symbol, strategy, side, entry_price,
                        current_price, amount, entry_time, stop_loss,
                        take_profit, unrealized_pnl, pnl_percent, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(position_id) DO UPDATE SET
                        current_price = excluded.current_price,
                        unrealized_pnl = excluded.unrealized_pnl,
                        pnl_percent = excluded.pnl_percent,
                        status = excluded.status,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    position_data.get('position_id'),
                    position_data.get('symbol'),
                    position_data.get('strategy'),
                    position_data.get('side'),
                    position_data.get('entry_price'),
                    position_data.get('current_price'),
                    position_data.get('amount'),
                    position_data.get('entry_time'),
                    position_data.get('stop_loss'),
                    position_data.get('take_profit'),
                    position_data.get('unrealized_pnl'),
                    position_data.get('pnl_percent'),
                    position_data.get('status', 'OPEN')
                ))
        except Exception as e:
            logger.error(f"Error upserting position: {e}")
            raise
    
    def get_open_positions(self) -> List[Dict]:
        """
        Get all currently open positions.
        
        Returns:
            List of position dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM positions WHERE status = 'OPEN' ORDER BY entry_time DESC"
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return []
    
    def close_position(self, position_id: str):
        """
        Mark a position as closed.
        
        Args:
            position_id: ID of position to close
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE positions 
                    SET status = 'CLOSED', updated_at = CURRENT_TIMESTAMP
                    WHERE position_id = ?
                """, (position_id,))
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            raise
    
    # =========================================================================
    # SIGNALS - Record of all trading signals
    # =========================================================================
    
    def insert_signal(self, signal_data: Dict[str, Any]):
        """
        Record a trading signal (taken or not).
        
        Args:
            signal_data: Dictionary with signal information
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO signals (
                        timestamp, symbol, strategy, signal_type, price,
                        strength, taken, reason_not_taken, indicators
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal_data.get('timestamp'),
                    signal_data.get('symbol'),
                    signal_data.get('strategy'),
                    signal_data.get('signal_type'),
                    signal_data.get('price'),
                    signal_data.get('strength'),
                    signal_data.get('taken', False),
                    signal_data.get('reason_not_taken'),
                    json.dumps(signal_data.get('indicators', {}))
                ))
        except Exception as e:
            logger.error(f"Error inserting signal: {e}")
            # Don't raise - signal logging shouldn't break trading
    
    def get_signals(self, symbol: Optional[str] = None,
                    taken_only: bool = False,
                    limit: int = 100) -> List[Dict]:
        """
        Get recorded signals.
        
        Args:
            symbol: Filter by symbol (optional)
            taken_only: Only return signals that were taken
            limit: Maximum number of signals
            
        Returns:
            List of signal dictionaries
        """
        query = "SELECT * FROM signals WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if taken_only:
            query += " AND taken = 1"
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                signals = [dict(row) for row in cursor.fetchall()]
                # Parse JSON indicators
                for signal in signals:
                    if signal.get('indicators'):
                        signal['indicators'] = json.loads(signal['indicators'])
                return signals
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return []
    
    # =========================================================================
    # MARKET DATA - OHLCV cache
    # =========================================================================
    
    def insert_market_data(self, data: Dict[str, Any]):
        """
        Insert OHLCV market data for caching.
        
        Args:
            data: Dictionary with OHLCV data
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO market_data (
                        symbol, timeframe, timestamp, open, high, low, close, volume
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('symbol'),
                    data.get('timeframe'),
                    data.get('timestamp'),
                    data.get('open'),
                    data.get('high'),
                    data.get('low'),
                    data.get('close'),
                    data.get('volume')
                ))
        except Exception as e:
            logger.error(f"Error inserting market data: {e}")
    
    def get_market_data(self, symbol: str, timeframe: str,
                        start_time: Optional[str] = None,
                        limit: int = 100) -> List[Dict]:
        """
        Get cached market data.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (e.g., '1h', '4h')
            start_time: Optional start timestamp
            limit: Maximum number of candles
            
        Returns:
            List of OHLCV dictionaries
        """
        query = """
            SELECT * FROM market_data 
            WHERE symbol = ? AND timeframe = ?
        """
        params = [symbol, timeframe]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return []
    
    # =========================================================================
    # PERFORMANCE METRICS - Daily snapshots
    # =========================================================================
    
    def insert_daily_metrics(self, metrics_data: Dict[str, Any]):
        """
        Insert or update daily performance metrics.
        
        Args:
            metrics_data: Dictionary with performance metrics
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO performance_metrics (
                        date, capital, total_return, daily_return,
                        total_trades, winning_trades, losing_trades,
                        win_rate, profit_factor, max_drawdown,
                        sharpe_ratio, open_positions, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics_data.get('date'),
                    metrics_data.get('capital'),
                    metrics_data.get('total_return'),
                    metrics_data.get('daily_return'),
                    metrics_data.get('total_trades', 0),
                    metrics_data.get('winning_trades', 0),
                    metrics_data.get('losing_trades', 0),
                    metrics_data.get('win_rate'),
                    metrics_data.get('profit_factor'),
                    metrics_data.get('max_drawdown'),
                    metrics_data.get('sharpe_ratio'),
                    metrics_data.get('open_positions', 0),
                    metrics_data.get('notes')
                ))
            logger.info(f"Metrics saved for {metrics_data.get('date')}")
        except Exception as e:
            logger.error(f"Error inserting daily metrics: {e}")
            raise
    
    def get_metrics_history(self, days: int = 30) -> List[Dict]:
        """
        Get performance metrics history.
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of metrics dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM performance_metrics
                    WHERE date >= date('now', '-' || ? || ' days')
                    ORDER BY date DESC
                """, (days,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting metrics history: {e}")
            return []
    
    # =========================================================================
    # ANALYTICS - Aggregated statistics
    # =========================================================================
    
    def get_performance_stats(self, days: Optional[int] = None) -> Dict:
        """
        Get aggregated performance statistics.
        
        Args:
            days: Optional number of days to analyze (None = all time)
            
        Returns:
            Dictionary with performance stats
        """
        query = """
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                AVG(pnl) as avg_pnl,
                SUM(pnl) as total_pnl,
                MIN(pnl) as worst_trade,
                MAX(pnl) as best_trade,
                MIN(timestamp) as first_trade,
                MAX(timestamp) as last_trade
            FROM trades
        """
        params = []
        
        if days:
            query += " WHERE timestamp >= datetime('now', '-' || ? || ' days')"
            params.append(days)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                stats = dict(cursor.fetchone())
                
                # Calculate win rate and profit factor
                if stats['total_trades'] > 0:
                    stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100
                    
                    # Profit factor = gross profit / gross loss
                    cursor = conn.execute("""
                        SELECT 
                            SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) as gross_profit,
                            ABS(SUM(CASE WHEN pnl < 0 THEN pnl ELSE 0 END)) as gross_loss
                        FROM trades
                    """ + (" WHERE timestamp >= datetime('now', '-' || ? || ' days')" if days else ""),
                    params)
                    pf_data = dict(cursor.fetchone())
                    
                    if pf_data['gross_loss'] > 0:
                        stats['profit_factor'] = pf_data['gross_profit'] / pf_data['gross_loss']
                    else:
                        stats['profit_factor'] = float('inf') if pf_data['gross_profit'] > 0 else 0
                else:
                    stats['win_rate'] = 0
                    stats['profit_factor'] = 0
                
                return stats
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}
    
    def get_stats_by_symbol(self) -> Dict[str, Dict]:
        """
        Get performance statistics broken down by symbol.
        
        Returns:
            Dictionary mapping symbol to stats
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT
                        symbol,
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                        SUM(pnl) as total_pnl,
                        AVG(pnl) as avg_pnl,
                        MAX(pnl) as best_trade,
                        MIN(pnl) as worst_trade
                    FROM trades
                    GROUP BY symbol
                    ORDER BY total_pnl DESC
                """)
                
                results = {}
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    symbol = row_dict.pop('symbol')
                    
                    # Calculate win rate
                    if row_dict['total_trades'] > 0:
                        row_dict['win_rate'] = (row_dict['winning_trades'] / row_dict['total_trades']) * 100
                    else:
                        row_dict['win_rate'] = 0
                    
                    results[symbol] = row_dict
                
                return results
        except Exception as e:
            logger.error(f"Error getting stats by symbol: {e}")
            return {}
    
    def get_stats_by_strategy(self) -> Dict[str, Dict]:
        """
        Get performance statistics broken down by strategy.
        
        Returns:
            Dictionary mapping strategy to stats
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT
                        strategy,
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                        SUM(pnl) as total_pnl,
                        AVG(pnl) as avg_pnl
                    FROM trades
                    GROUP BY strategy
                    ORDER BY total_pnl DESC
                """)
                
                results = {}
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    strategy = row_dict.pop('strategy')
                    
                    # Calculate win rate
                    if row_dict['total_trades'] > 0:
                        row_dict['win_rate'] = (row_dict['winning_trades'] / row_dict['total_trades']) * 100
                    else:
                        row_dict['win_rate'] = 0
                    
                    results[strategy] = row_dict
                
                return results
        except Exception as e:
            logger.error(f"Error getting stats by strategy: {e}")
            return {}
