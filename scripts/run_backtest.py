#!/usr/bin/env python3
"""
Script to run backtesting on historical data.
"""

import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.config import Config
from core.exchange_connector import ExchangeConnector
from core.market_data import MarketData
from strategies.sma_cross import SMACrossStrategy
from strategies.rsi_bb import RSIBollingerStrategy
from strategies.ema_scalping import EMAScalpingStrategy
from strategies.bollinger_scalp import BollingerScalpStrategy
from backtesting.backtester import Backtester
from backtesting.metrics import calculate_metrics, print_metrics
from backtesting.equity_curve import generate_equity_curve
from core.logger import setup_logger


def main():
    """Main function to run backtest."""
    parser = argparse.ArgumentParser(description='Run strategy backtesting')
    parser.add_argument('--symbols', type=str, default=None,
                        help='Comma-separated symbols to backtest (default: from config)')
    parser.add_argument('--start', type=str, default=None,
                        help='Start date (YYYY-MM-DD), default: 90 days ago')
    parser.add_argument('--end', type=str, default=None,
                        help='End date (YYYY-MM-DD), default: today')
    parser.add_argument('--timeframe', type=str, default=None,
                        help='Timeframe (1m, 5m, 1h, 1d), default: from config')
    parser.add_argument('--days', type=int, default=90,
                        help='Number of days of historical data (default: 90)')
    parser.add_argument('--capital', type=float, default=None,
                        help='Initial capital (default: from config)')
    parser.add_argument('--strategy', type=str, default=None,
                        help='Strategy to test: SMA_CROSS, RSI_BB, or BOTH (default: from config)')
    parser.add_argument('--no-plot', action='store_true',
                        help='Skip equity curve plot generation')
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger('backtest_runner', 'backtest.log')
    
    logger.info("=" * 60)
    logger.info("STARTING BACKTEST")
    logger.info("=" * 60)
    
    try:
        # Validate config
        Config.validate()
        
        # Parse arguments
        symbols = args.symbols.split(',') if args.symbols else Config.SYMBOLS
        timeframe = args.timeframe or Config.TIMEFRAME
        initial_capital = args.capital or Config.INITIAL_CAPITAL
        
        # Calculate date range
        if args.end:
            end_date = args.end
        else:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if args.start:
            start_date = args.start
        else:
            start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
        
        logger.info(f"Symbols: {', '.join(symbols)}")
        logger.info(f"Timeframe: {timeframe}")
        logger.info(f"Date Range: {start_date} to {end_date}")
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        
        # Initialize components
        logger.info("\nInitializing components...")
        exchange = ExchangeConnector()
        market_data = MarketData(exchange)
        
        # Initialize strategy based on config or argument
        strategy_name = args.strategy or Config.STRATEGY
        logger.info(f"Strategy selection: {strategy_name}")
        
        if strategy_name == 'SMA_CROSS':
            strategy = SMACrossStrategy()
        elif strategy_name == 'RSI_BB':
            strategy = RSIBollingerStrategy()
        elif strategy_name == 'EMA_SCALP':
            strategy = EMAScalpingStrategy()
            logger.info("Using EMA Scalping strategy for backtest")
        elif strategy_name == 'BB_SCALP':
            strategy = BollingerScalpStrategy()
            logger.info("Using Bollinger Scalp strategy for backtest")
        elif strategy_name == 'BOTH':
            # For BOTH, default to SMA for backtest (backtester doesn't support multi-strategy yet)
            logger.warning("BOTH strategy selected - using SMA Cross for backtest")
            logger.warning("(Multi-strategy backtest support coming soon)")
            strategy = SMACrossStrategy()
        else:
            logger.error(f"Unknown strategy: {strategy_name}")
            logger.error("Valid strategies: SMA_CROSS, RSI_BB, EMA_SCALP, BB_SCALP, BOTH")
            return 1
        
        logger.info(f"Strategy: {strategy}")
        
        # Fetch historical data
        logger.info("\nFetching historical data...")
        data = {}
        for symbol in symbols:
            logger.info(f"Fetching data for {symbol}...")
            df = market_data.fetch_historical_data(
                symbol,
                timeframe,
                days=args.days
            )
            df = market_data.add_technical_indicators(df)
            data[symbol] = df
            logger.info(f"Loaded {len(df)} candles for {symbol} (from {df.index[0]} to {df.index[-1]})")
        
        # Initialize backtester
        logger.info("\nInitializing backtester...")
        backtester = Backtester(
            strategy=strategy,
            initial_capital=initial_capital
        )
        
        # Run backtest
        logger.info("\nRunning backtest...")
        results = backtester.run(data, start_date, end_date)
        
        # Calculate metrics
        logger.info("\nCalculating metrics...")
        metrics = calculate_metrics(
            results['equity_curve'],
            results['trades'],
            initial_capital
        )
        
        # Print results
        print_metrics(metrics)
        
        # Export results
        logger.info("\nExporting results...")
        trades_file = backtester.export_trades()
        equity_file = backtester.export_equity_curve()
        
        logger.info(f"Trades exported to: {trades_file}")
        logger.info(f"Equity curve exported to: {equity_file}")
        
        # Generate equity curve plot
        if not args.no_plot:
            logger.info("\nGenerating equity curve plot...")
            plot_file = generate_equity_curve(
                results['equity_curve'],
                results['trades'],
                show=False
            )
            if plot_file:
                logger.info(f"Equity curve plot saved to: {plot_file}")
        
        logger.info("\n" + "=" * 60)
        logger.info("BACKTEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
