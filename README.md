# 🤖 Advanced Crypto Trading Bot

> **Professional-grade automated trading system for cryptocurrencies with advanced features, real-time monitoring, and production-ready deployment options.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Binance](https://img.shields.io/badge/Exchange-Binance-yellow.svg)](https://www.binance.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ⚠️ **DISCLAIMER**

**This software is for educational and research purposes only. Cryptocurrency trading carries significant risks and may result in total capital loss. Use this bot at your own risk.**

- ❌ **NO profitability guarantees**
- ❌ **NO liability for losses**
- ✅ **Always start with testnet**
- ✅ **Fully understand before using real money**

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Deployment](#-deployment)
- [Architecture](#-architecture)
- [Strategies](#-strategies)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🤖 **Automated Trading**
- ✅ 24/7 market monitoring and analysis
- ✅ Automatic signal execution
- ✅ Real-time position management
- ✅ Auto-restart on failure
- ✅ Multi-symbol support (BTC, ETH, SOL, etc.)

### 📊 **Advanced Backtesting**
- ✅ Historical simulation with real market data
- ✅ Configurable commissions and slippage
- ✅ Complete metrics: Sharpe, Sortino, Calmar ratios
- ✅ Drawdown analysis and win rate tracking
- ✅ Equity curve visualization
- ✅ CSV export for further analysis

### 📈 **Trading Strategies**
- ✅ **SMA Crossover** - Golden/Death Cross signals
- ✅ **RSI + Bollinger Bands** - Oversold/overbought detection
- ✅ **EMA Scalping** - Fast/Slow EMA with volume confirmation
- ✅ **Multi-Timeframe Analysis** - Trend confirmation (4h → 1h)
- ✅ Easily extensible for custom strategies

### 🛡️ **Risk Management**
- ✅ **Position Sizing** - Percentage-based capital allocation
- ✅ **Stop Loss & Take Profit** - Automatic exit points
- ✅ **Trailing Stop** - Lock in profits dynamically
- ✅ **Kill Switch** - Auto-halt on max drawdown
- ✅ **Circuit Breaker** - Halt on extreme volatility/volume
- ✅ **Max Positions Limit** - Control portfolio exposure
- ✅ **Consecutive Loss Protection** - Stop after X losses

### 🖥️ **Real-Time Dashboard**
- ✅ Live trading statistics
- ✅ Equity curve visualization
- ✅ Open positions tracking
- ✅ Trade history
- ✅ Real-time market data
- ✅ Performance metrics

### 🗄️ **Database Integration**
- ✅ SQLite persistence
- ✅ Automatic trade logging
- ✅ Position snapshots
- ✅ Historical data storage
- ✅ Performance analytics
- ✅ Query capabilities for analysis

### 📱 **Telegram Notifications**
- ✅ Real-time trade alerts
- ✅ Position updates
- ✅ Error notifications
- ✅ Daily performance summaries
- ✅ Bot status updates

### 🚀 **Deployment Ready**
- ✅ Railway (PaaS) - Quick deploy
- ✅ Oracle Cloud - Free forever option
- ✅ Docker support
- ✅ Systemd service configuration
- ✅ Auto-restart policies
- ✅ Environment-based configuration

### 🔒 **Security**
- ✅ API keys in environment variables
- ✅ Testnet/Production separation
- ✅ Order validation before execution
- ✅ Auto-recovery from connection errors
- ✅ Comprehensive logging
- ✅ No hardcoded credentials

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Astolfu/trading-bot.git
cd trading-bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run backtest
python scripts/run_backtest.py --symbols BTCUSDT --days 90

# 6. Run bot (testnet)
python scripts/run_bot.py
```

Access dashboard at: `http://localhost:5000`

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- Binance account (for API keys)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Astolfu/trading-bot.git
   cd trading-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Get Binance API Keys**
   - **Testnet:** [testnet.binance.vision](https://testnet.binance.vision/)
   - **Production:** [binance.com](https://www.binance.com/) → Account → API Management

5. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys and preferences.

6. **Setup Telegram (Optional)**
   - Create bot with [@BotFather](https://t.me/BotFather)
   - Get your Chat ID
   - Add to `.env`
   
   See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) for detailed guide.

---

## ⚙️ Configuration

### Essential Settings

```ini
# Exchange API
BINANCE_TESTNET_API_KEY=your_testnet_key
BINANCE_TESTNET_API_SECRET=your_testnet_secret
USE_TESTNET=true

# Trading
EXECUTE_REAL=true  # true = execute orders, false = simulation only
SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT
TIMEFRAME=1h
INITIAL_CAPITAL=10000

# Risk Management
RISK_PER_TRADE=2  # 2% of capital per trade
MAX_POSITIONS=5
STOP_LOSS_PERCENT=2
TAKE_PROFIT_PERCENT=4
MAX_DRAWDOWN_PERCENT=10

# Strategies
DEFAULT_STRATEGY=EMA_SCALP  # SMA_CROSS, RSI_BB, EMA_SCALP
```

See [CONFIGURATION.md](CONFIGURATION.md) for all options.

---

## 📖 Usage

### Backtesting

```bash
# Basic backtest
python scripts/run_backtest.py --symbols BTCUSDT --days 90

# Multi-symbol backtest
python scripts/run_backtest.py --symbols BTCUSDT,ETHUSDT,SOLUSDT --days 180

# Custom date range
python scripts/run_backtest.py \
    --symbols BTCUSDT \
    --start 2024-01-01 \
    --end 2024-12-31 \
    --timeframe 1h
```

### Running the Bot

```bash
# Start bot (testnet recommended)
python scripts/run_bot.py

# Bot will:
# - Connect to Binance
# - Initialize database
# - Start dashboard on port 5000
# - Begin monitoring markets
# - Execute trades based on signals
```

### Dashboard Access

Open browser: `http://localhost:5000`

Features:
- Real-time equity curve
- Active positions
- Trade history
- Performance metrics

### Database Queries

```bash
# Check database contents
python scripts/check_database.py

# Simulate a test trade
python scripts/simulate_trade.py
```

---

## 🌐 Deployment

### Option 1: Railway (Fastest)

1. Sign up at [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add environment variables
4. Deploy!

**Cost:** $0-5/month (Free tier included)

See [railway_deployment_guide.md](docs/railway_deployment_guide.md)

### Option 2: Oracle Cloud (Free Forever)

1. Create Oracle Cloud account
2. Launch VM instance
3. Setup bot with systemd
4. Configure firewall

**Cost:** $0/month (Always Free tier)

See [oracle_cloud_deployment_guide.md](docs/oracle_cloud_deployment_guide.md)

### Option 3: Docker (Any Platform)

```bash
# Build image
docker build -t trading-bot .

# Run container
docker run -d --env-file .env -p 5000:5000 trading-bot
```

---

## 🏗️ Architecture

```
trading-bot/
├── bot/                    # Main trading bot
│   ├── trading_bot.py      # Core bot logic
│   └── order_manager.py    # Order execution
├── strategies/             # Trading strategies
│   ├── sma_cross.py        # SMA Crossover
│   ├── rsi_bb.py           # RSI + Bollinger Bands
│   └── ema_scalping.py     # EMA Scalping
├── risk/                   # Risk management
│   ├── risk_manager.py     # Position sizing
│   └── position_manager.py # Position tracking
├── database/               # Data persistence
│   ├── db_manager.py       # SQLite manager
│   └── schema.sql          # Database schema
├── dashboard/              # Web dashboard
│   ├── server.py           # Flask server
│   └── templates/          # HTML templates
├── core/                   # Core utilities
│   ├── exchange_connector.py
│   ├── market_data.py
│   └── logger.py
├── notifications/          # Alerts
│   └── telegram_notifier.py
├── backtesting/            # Backtest engine
│   ├── backtester.py
│   └── metrics.py
└── scripts/                # Executable scripts
    ├── run_bot.py
    └── run_backtest.py
```

---

## 📊 Strategies

### 1. SMA Crossover

**Signals:**
- **Buy:** SMA20 crosses above SMA50 (Golden Cross)
- **Sell:** SMA20 crosses below SMA50 (Death Cross)

**Best for:** Medium to long-term trends

### 2. RSI + Bollinger Bands

**Signals:**
- **Buy:** RSI < 30 AND price touches lower BB
- **Sell:** RSI > 70 AND price touches upper BB

**Best for:** Range-bound markets

### 3. EMA Scalping

**Signals:**
- **Buy:** EMA8 crosses above EMA21 + volume spike
- **Sell:** EMA8 crosses below EMA21

**Best for:** Active markets with good volume

### Multi-Timeframe Filter

Confirms trend on higher timeframe (4h) before executing 1h signals.

**Configurable per symbol.**

---

## 🔐 Security

### API Key Protection

✅ **Never hardcode keys** - Use environment variables  
✅ **Testnet first** - Validate before production  
✅ **Read-only keys** - Disable withdrawals  
✅ **IP Whitelist** - Restrict API access  
✅ **Git ignored** - `.env` never committed  

### Trading Safety

✅ **Kill Switch** - Auto-stop on max drawdown  
✅ **Circuit Breaker** - Halt on extreme volatility  
✅ **Position Limits** - Max concurrent positions  
✅ **Order Validation** - Verify before execution  
✅ **Logs** - Complete audit trail  

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .

# Lint
flake8
```

---

## 📝 Documentation

- **[INSTALL.md](INSTALL.md)** - Detailed installation guide
- **[CONFIGURATION.md](CONFIGURATION.md)** - All configuration options
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - VPS deployment guide
- **[TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)** - Telegram bot configuration
- **[Deployment Guides](docs/)** - Railway, Oracle Cloud, Docker

---

## 📈 Performance

**Backtested Results (180 days, BTCUSDT/ETHUSDT/SOLUSDT):**

- **Total Return:** +7.72%
- **Win Rate:** 55.26%
- **Max Drawdown:** -3.12%
- **Sharpe Ratio:** 0.89
- **Profit Factor:** 1.28

*Past performance does not guarantee future results.*

---

## 🛣️ Roadmap

### Planned Features

- [ ] Additional exchanges (Bybit, Kucoin)
- [ ] Advanced ML strategies
- [ ] Portfolio optimization
- [ ] Mobile app
- [ ] Advanced analytics dashboard
- [ ] Backtesting optimization (grid search)
- [ ] Social trading features

See [improvement_roadmap.md](docs/improvement_roadmap.md) for details.

---

## 📜 License

This project is open source under the MIT License -

 see [LICENSE](LICENSE) file.

**Use at your own risk. No warranties provided.**

---

## 🙏 Acknowledgments

Built with:
- [ccxt](https://github.com/ccxt/ccxt) - Cryptocurrency exchange library
- [pandas](https://pandas.pydata.org/) - Data analysis
- [ta](https://github.com/bukosabino/ta) - Technical analysis
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Chart.js](https://www.chartjs.org/) - Dashboard charts

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Astolfu/trading-bot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Astolfu/trading-bot/discussions)
- **Documentation:** Check `/docs` folder

---

## ⚡ Quick Links

- [Features Overview](#-features)
- [Installation Guide](#-installation)
- [Configuration Guide](CONFIGURATION.md)
- [Deployment Options](#-deployment)
- [Telegram Setup](TELEGRAM_SETUP.md)
- [Contribution Guidelines](#-contributing)

---

**Happy Trading! 📈🚀**

*Remember: Trade responsibly. Only invest what you can afford to lose.*

---

**Star ⭐ this repo if you find it useful!**
