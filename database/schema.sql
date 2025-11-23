-- Trading Bot Database Schema
-- SQLite database for storing historical trading data

-- =====================================================
-- TABLE: trades
-- Stores complete history of closed trades
-- =====================================================
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT UNIQUE NOT NULL,
    timestamp DATETIME NOT NULL,
    symbol TEXT NOT NULL,
    strategy TEXT NOT NULL,
    side TEXT NOT NULL,  -- 'LONG' or 'SHORT'
    entry_price REAL NOT NULL,
    exit_price REAL,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    amount REAL NOT NULL,
    pnl REAL,
    pnl_percent REAL,
    fees REAL DEFAULT 0,
    exit_reason TEXT,  -- 'take_profit', 'stop_loss', 'manual', 'signal', 'timeout'
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy);
CREATE INDEX IF NOT EXISTS idx_trades_exit_reason ON trades(exit_reason);

-- =====================================================
-- TABLE: positions
-- Current snapshot of open positions
-- =====================================================
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    strategy TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL,
    current_price REAL,
    amount REAL NOT NULL,
    entry_time DATETIME NOT NULL,
    stop_loss REAL,
    take_profit REAL,
    unrealized_pnl REAL,
    pnl_percent REAL,
    status TEXT DEFAULT 'OPEN',  -- 'OPEN', 'CLOSED'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);

-- =====================================================
-- TABLE: market_data
-- Cache of OHLCV data to reduce API calls
-- =====================================================
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_market_data_symbol_tf ON market_data(symbol, timeframe);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);

-- =====================================================
-- TABLE: signals
-- Record of ALL trading signals (taken or not)
-- =====================================================
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    symbol TEXT NOT NULL,
    strategy TEXT NOT NULL,
    signal_type TEXT NOT NULL,  -- 'BUY', 'SELL', 'CLOSE'
    price REAL NOT NULL,
    strength REAL,  -- Confidence: 0-1
    taken BOOLEAN DEFAULT 0,
    reason_not_taken TEXT,  -- e.g., 'max_positions', 'insufficient_capital', 'risk_limit'
    indicators TEXT,  -- JSON with indicator values
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_signals_taken ON signals(taken);
CREATE INDEX IF NOT EXISTS idx_signals_strategy ON signals(strategy);

-- =====================================================
-- TABLE: performance_metrics
-- Daily snapshot of bot performance metrics
-- =====================================================
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    capital REAL NOT NULL,
    total_return REAL,
    daily_return REAL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate REAL,
    profit_factor REAL,
    max_drawdown REAL,
    sharpe_ratio REAL,
    open_positions INTEGER DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metrics_date ON performance_metrics(date);
