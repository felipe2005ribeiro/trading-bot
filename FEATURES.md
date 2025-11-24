# 🎯 Features Overview - Trading Bot

**Complete feature breakdown with usage examples and configuration.**

---

## 📊 Core Trading Features

### 1. Automated Trading

**What it does:**
- Monitors markets 24/7
- Analyzes price data and indicators
- Generates trading signals
- Executes orders automatically
- Manages open positions

**Configuration:**
```ini
UPDATE_INTERVAL=60  # Check markets every 60 seconds
SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT
TIMEFRAME=1h
```

**Usage:**
```bash
python scripts/run_bot.py
```

---

### 2. Multi-Symbol Support

**What it does:**
- Trade multiple cryptocurrency pairs simultaneously
- Independent analysis for each symbol
- Different strategies per symbol
- Parallel position management

**Configuration:**
```ini
SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT,ADAUSDT
MAX_POSITIONS=5  # Maximum concurrent positions
```

**Assign strategies per symbol:**
```ini
# In config.py
SYMBOL_STRATEGIES = {
    'BTCUSDT': 'SMA_CROSS',
    'ETHUSDT': 'EMA_SCALP',
    'SOLUSDT': 'EMA_SCALP',
}
```

---

## 🔬 Strategies

### 1. SMA Crossover Strategy

**Description:** Classic trend-following strategy using Simple Moving Averages.

**Signals:**
- **BUY:** SMA20 crosses above SMA50 (Golden Cross)
- **SELL:** SMA20 crosses below SMA50 (Death Cross)

**Best for:** Medium to long-term trends, lower frequency trading

**Configuration:**
```ini
DEFAULT_STRATEGY=SMA_CROSS
SMA_SHORT_PERIOD=20
SMA_LONG_PERIOD=50
```

**Performance (Backtest 180 days):**
- Win Rate: ~52%
- Best for: BTC (trending markets)

---

### 2. RSI + Bollinger Bands

**Description:** Mean reversion strategy combining momentum and volatility.

**Signals:**
- **BUY:** RSI < 30 AND price touches lower Bollinger Band
- **SELL:** RSI > 70 AND price touches upper Bollinger Band

**Best for:** Range-bound markets, counter-trend trading

**Configuration:**
```ini
DEFAULT_STRATEGY=RSI_BB
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
BB_PERIOD=20
BB_STD=2
```

---

### 3. EMA Scalping Strategy

**Description:** Fast-paced strategy using Exponential Moving Averages with volume confirmation.

**Signals:**
- **BUY:** EMA8 crosses above EMA21 + volume spike (>1.5x average)
- **SELL:** EMA8 crosses below EMA21

**Best for:** Active markets with high volume

**Configuration:**
```ini
DEFAULT_STRATEGY=EMA_SCALP
EMA_FAST=8
EMA_SLOW=21
VOLUME_SPIKE_THRESHOLD=1.5
```

**Performance (Backtest 180 days):**
- Win Rate: ~57%
- Best for: ETH, SOL (volatile markets)

---

### 4. Multi-Timeframe Filter

**Description:** Confirms trend on higher timeframe before executing trades.

**How it works:**
1. Analyze trend on 4h timeframe (EMA200)
2. Only take 1h signals that align with 4h trend
3. Skip counter-trend signals

**Configuration:**
```ini
ENABLE_MTF_FILTER=true
MTF_SYMBOLS=SOLUSDT  # Apply only to specific symbols
TREND_TIMEFRAME=4h
TREND_EMA_PERIOD=200
```

**Performance improvement:**
- SOLUSDT: +0.56% better with MTF
- Reduces false signals in choppy markets

---

## 🛡️ Risk Management

### 1. Position Sizing

**Method:** Percentage of capital per trade

**Configuration:**
```ini
RISK_PER_TRADE=2  # Risk 2% of capital per trade
INITIAL_CAPITAL=10000  # Starting capital
```

**Example:**
- Capital: $10,000
- Risk: 2% = $200
- Entry: $50,000
- Stop Loss: 2% below = $49,000
- Position size: $200 / ($50,000 - $49,000) = 0.004 BTC

---

### 2. Stop Loss & Take Profit

**Automatic exit points:**

```ini
STOP_LOSS_PERCENT=2    # Exit if price drops 2%
TAKE_PROFIT_PERCENT=4  # Exit if price rises 4%
```

**Dynamic adjustment:** Based on volatility (ATR-based - planned feature)

---

### 3. Trailing Stop Loss

**Description:** Lock in profits as price moves favorably.

**Configuration:**
```ini
ENABLE_TRAILING_STOP=true
TRAILING_STOP_ACTIVATION=2.0   # Activate when +2% profit
TRAILING_STOP_CALLBACK=1.0     # Trail 1% below peak
```

**Example:**
- Entry: $50,000
- Price hits $51,000 (+2%) → Trailing activates
- Price climbs to $52,000 → Stop trails to $51,480 (-1%)
- If price drops to $51,480 → Position closes with +2.96% profit

---

### 4. Kill Switch

**Description:** Auto-halt trading on extreme losses.

**Triggers:**
- Max drawdown exceeded
- Consecutive losses limit reached

**Configuration:**
```ini
MAX_DRAWDOWN_PERCENT=10          # Stop if down 10%
CONSECUTIVE_LOSSES_LIMIT=5       # Stop after 5 losses in a row
```

**Behavior:**
- Bot stops opening new positions
- Existing positions remain open
- Sends Telegram alert
- Logs critical warning

---

### 5. Circuit Breaker

**Description:** Halt trading during extreme market conditions.

**Triggers:**
- Extreme volatility (>5x normal)
- Volume spike (>20x normal)
- Wide spread (>0.5%)

**Configuration:**
```ini
ENABLE_CIRCUIT_BREAKER=true
CIRCUIT_BREAKER_VOLATILITY_THRESHOLD=5.0
CIRCUIT_BREAKER_VOLUME_SPIKE=20.0
CIRCUIT_BREAKER_SPREAD_THRESHOLD=0.5
```

**Use case:** Prevents trading during flash crashes or anomalies

---

### 6. Position Limits

**Description:** Control portfolio exposure.

**Configuration:**
```ini
MAX_POSITIONS=5              # Max 5 open positions
MAX_PORTFOLIO_EXPOSURE=50    # Max 50% of capital deployed
```

**Example:**
- Capital: $10,000
- Max exposure: $5,000
- 3 positions open worth $3,500
- Can only open positions worth max $1,500 more

---

## 📈 Backtesting

### Features

- Historical simulation with real market data
- Configurable date ranges
- Commission and slippage modeling
- Comprehensive metrics calculation
- Equity curve visualization
- Trade-by-trade logging

### Usage

```bash
# Basic backtest
python scripts/run_backtest.py --symbols BTCUSDT --days 90

# Custom date range
python scripts/run_backtest.py \
    --symbols BTCUSDT,ETHUSDT \
    --start 2024-01-01 \
    --end 2024-12-31 \
    --timeframe 1h

# Multiple symbols
python scripts/run_backtest.py \
    --symbols BTCUSDT,ETHUSDT,SOLUSDT \
    --days 180
```

### Metrics Provided

**Performance:**
- Total Return (%)
- Win Rate (%)
- Profit Factor
- Average Trade Return

**Risk:**
- Max Drawdown (%)
- Max Drawdown Duration
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio

**Trading:**
- Total Trades
- Winning / Losing Trades
- Avg Win / Avg Loss
- Largest Win / Largest Loss

---

## 🖥️ Dashboard

### Real-Time Monitoring

**URL:** `http://localhost:5000` (or your server IP)

**Features:**
- Equity curve (live)
- Current capital
- Open positions table
- Trade history
- Performance metrics
- Market prices

**Access:**
- Locally: `http://localhost:5000`
- Remote: `http://YOUR_SERVER_IP:5000`

**Configuration:**
```ini
ENABLE_DASHBOARD=true
DASHBOARD_HOST=0.0.0.0  # Listen on all interfaces
DASHBOARD_PORT=5000
```

---

## 🗄️ Database

### SQLite Persistence

**What's stored:**
- All closed trades
- Position snapshots (updated every iteration)
- Performance metrics
- Market data cache (optional)
- Trading signals (optional)

**Tables:**
1. `trades` - Complete trade history
2. `positions` - Current/historical positions
3. `market_data` - OHLCV cache
4. `signals` - All signals (taken or ignored)
5. `performance_metrics` - Daily snapshots

**Usage:**
```bash
# View database contents
python scripts/check_database.py

# Query trades
from database.db_manager import DatabaseManager
db = DatabaseManager()
trades = db.get_trades(limit=50)
stats = db.get_performance_stats()
```

**Benefits:**
- Data persists across bot restarts
- Fast queries (10-100x faster than CSV)
- Analytics and reporting
- Historical analysis

---

## 📱 Telegram Notifications

### Real-Time Alerts

**What you receive:**
- Bot startup/shutdown
- Trade execution (buy/sell)
- Position closed (with PnL)
- Take profit / Stop loss hit
- Trailing stop activation
- Error alerts
- Daily summary

**Setup:**
1. Create bot with [@BotFather](https://t.me/BotFather)
2. Get bot token
3. Get your Chat ID
4. Add to `.env`

**Configuration:**
```ini
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Message Examples:**
```
🚀 Bot Started
Capital: $10,000
Mode: TESTNET
Symbols: BTC, ETH, SOL

📈 Buy Signal Executed
Symbol: BTCUSDT
Price: $50,000
Amount: 0.1 BTC
Value: $5,000

🎯 Position Closed - Take Profit
Symbol: BTCUSDT
PnL: +$200 (+4.00%)
Duration: 2h 30m
```

See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) for full guide.

---

## 🚀 Deployment

### Supported Platforms

**Cloud (Recommended):**
- Railway - Quick deploy, $0-5/month
- Oracle Cloud - Free forever
- DigitalOcean - $4/month VPS

**Self-Hosted:**
- Raspberry Pi - One-time cost
- Home server - Use existing hardware

**Containerized:**
- Docker - Any platform
- Kubernetes - Enterprise scale

### Auto-Restart

**systemd (Linux):**
```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

**Railway/Cloud:**
- Auto-restart on crash
- Auto-deploy on Git push

**Docker:**
```bash
docker run -d --restart=always trading-bot
```

---

## 🔒 Security Features

### 1. Environment Variables

**All sensitive data in `.env`:**
- API keys
- Secrets
- Passwords

**Never in code:**
```python
# ❌ BAD
api_key = "abc123"

# ✅ GOOD
api_key = os.getenv('BINANCE_API_KEY')
```

---

### 2. API Key Restrictions

**Binance API settings:**
- ✅ Enable trading
- ✅ Enable reading
- ❌ Disable withdrawals
- ✅ IP whitelist (if VPS has static IP)

---

### 3. Testnet/Production Separation

```ini
# Testnet (safe)
USE_TESTNET=true
BINANCE_TESTNET_API_KEY=...
BINANCE_TESTNET_API_SECRET=...

# Production (real money)
USE_TESTNET=false
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
```

---

### 4. Order Validation

**Before executing:**
- ✅ Check position limits
- ✅ Verify capital available
- ✅ Validate order size
- ✅ Check market conditions
- ✅ Confirm strategy signal

---

### 5. Logging

**Complete audit trail:**
- All trades logged
- Errors captured
- API calls recorded
- Position changes tracked

**Log files:**
```
logs/
├── trading_bot.log          # Main log
├── trading_bot_20241123.log # Daily rotation
└── balance.log              # Balance checks
```

---

## 📊 Performance Tracking

### Metrics Calculated

**Real-time:**
- Current capital
- Open positions
- Unrealized PnL
- Total return %

**Historical:**
- Total trades
- Win rate
- Profit factor
- Max drawdown
- Sharpe ratio

**Per Symbol:**
- Trades executed
- Win rate
- Total PnL
- Best/worst trade

**Per Strategy:**
- Strategy performance
- Signal accuracy
- Average holding time

---

## 🔄 Auto-Recovery

### Built-in Resilience

**Connection errors:**
- Auto-reconnect to exchange
- Retry failed API calls
- Maintain state during disconnection

**Bot crashes:**
- Restart policies (systemd/Docker)
- Resume from last state
- No position data loss

**Exchange downtime:**
- Detect unavailability
- Pause trading
- Resume when online

---

## ⚙️ Advanced Configuration

### Custom Strategy Parameters

Each strategy has configurable parameters:

**SMA:**
```ini
SMA_SHORT_PERIOD=20
SMA_LONG_PERIOD=50
```

**RSI:**
```ini
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
```

**Bollinger Bands:**
```ini
BB_PERIOD=20
BB_STD=2.0
```

**EMA:**
```ini
EMA_FAST=8
EMA_SLOW=21
```

### Volume Analysis

```ini
VOLUME_SPIKE_THRESHOLD=1.5  # 1.5x average volume
ENABLE_VOLUME_FILTER=true
```

### Update Frequency

```ini
UPDATE_INTERVAL=60  # Check markets every 60 seconds
```

⚠️ Lower values = more API calls = higher costs  
⚠️ Higher values = slower response to signals

---

## 📚 Documentation

**Guides:**
- [README.md](README.md) - Main overview
- [INSTALL.md](INSTALL.md) - Installation
- [CONFIGURATION.md](CONFIGURATION.md) - All settings
- [DEPLOYMENT.md](DEPLOYMENT.md) - Cloud deployment
- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Notifications

**Deployment Guides:**
- Railway - Quick cloud deploy
- Oracle Cloud - Free forever option
- Docker - Containerized deployment

---

## 🎓 Learning Resources

**Understand before using:**
- Technical analysis basics
- Trading terminology
- Risk management principles
- Market behavior

**Recommended reading:**
- Strategy documentation
- Backtest results
- Code comments
- Logs and metrics

---

**Complete feature set designed for reliability, performance, and ease of use.**

**Questions? Check the documentation or open an issue on GitHub.**
