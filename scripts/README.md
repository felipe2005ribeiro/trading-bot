# Testing Scripts

This directory contains testing and utility scripts for the trading bot.

## Available Scripts

### 1. check_database.py

**Purpose:** Check database contents and verify data is being saved.

**Usage:**
```bash
python scripts/check_database.py
```

**What it shows:**
- Total trades in database
- Recent trade details (symbol, entry/exit, PnL, strategy)
- Open positions with unrealized PnL
- Overall performance statistics
- Performance breakdown by symbol
- Performance breakdown by strategy

**When to use:**
- After running the bot to verify trades saved
- Before/after database migrations
- To analyze trading performance
- Troubleshooting data persistence issues

---

### 2. simulate_trade.py

**Purpose:** Simulate a complete trade to test database integration.

**Usage:**
```bash
python scripts/simulate_trade.py
```

**What it does:**
1. Creates a simulated BTC position (entry at $50,000)
2. Saves position snapshot to database
3. Simulates position close (exit at $51,500)
4. Calculates and saves PnL (+$150, +3%)
5. Verifies data was saved correctly
6. Shows statistics

**When to use:**
- First time setup to test database
- After database schema changes
- Before running live bot
- Verify complete trade lifecycle works

**Output:**
```
1. Simulating Trade Entry...
2. Creating Position Snapshot...
   [OK] Position snapshot saved
3. Simulating Position Close...
   [OK] Position marked as closed
4. Saving Completed Trade...
   [OK] Trade saved to database
5. Verifying Saved Data...
   Trades in DB: 1
   Performance Stats: Win Rate: 100%
```

---

### 3. test_integration.py

**Purpose:** Integration test to verify all components work together.

**Usage:**
```bash
python scripts/test_integration.py
```

**What it tests:**
1. ✅ DatabaseManager initialization
2. ✅ TradingBot initialization with database
3. ✅ Database tables accessible
4. ✅ Component connectivity

**Exit codes:**
- `0` - All tests passed ✅
- `1` - One or more tests failed ❌

**When to use:**
- Before first bot run
- After code changes
- Before deployment
- Troubleshooting initialization issues

**Example output:**
```
1. Testing DatabaseManager initialization...
   [OK] DatabaseManager initialized successfully

2. Testing TradingBot initialization with database...
   [OK] TradingBot initialized successfully
   [OK] Database manager available: True
   [OK] Database path: data\bot.db

3. Checking database tables...
   [OK] Trades table accessible (currently 0 trades)
   [OK] Positions table accessible (currently 0 open)

All database integration tests passed!
```

---

## Common Testing Workflow

### First Time Setup

```bash
# 1. Run integration test
python scripts/test_integration.py

# 2. Simulate a trade
python scripts/simulate_trade.py

# 3. Check database contents
python scripts/check_database.py

# 4. Run bot
python scripts/run_bot.py
```

### After Running Bot

```bash
# Check what trades were executed
python scripts/check_database.py
```

### Troubleshooting

```bash
# If bot crashes or data not saving:
python scripts/test_integration.py  # Verify components work

# If database seems empty:
python scripts/simulate_trade.py    # Test database manually
python scripts/check_database.py    # Verify simulated trade saved
```

---

## Requirements

All scripts require:
- Virtual environment activated
- Dependencies installed (`pip install -r requirements.txt`)
- Proper `.env` configuration (for TradingBot tests)

---

## Database Location

Scripts use `data/bot.db` by default.

Test scripts may use `data/test.db` to avoid conflicting with production data.

---

## Tips

1. **Run tests before deployment** - Catch issues early
2. **Simulate trades** - Test database without market risk
3. **Check database regularly** - Verify data persistence
4. **Use for debugging** - Identify integration problems

---

## Need Help?

- Check main [README.md](../README.md)
- See [FEATURES.md](../FEATURES.md) for full feature list
- Review database [schema.sql](../database/schema.sql)
- Open issue on GitHub if problems persist
