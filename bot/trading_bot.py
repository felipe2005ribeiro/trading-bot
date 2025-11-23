"""
Main trading bot module.
Runs 24/7 monitoring markets and executing trades.
"""

import time
import signal
import sys
import threading
from datetime import datetime
from typing import Dict
import ta

from core.exchange_connector import ExchangeConnector
from core.market_data import MarketData
from core.logger import get_logger
from core.circuit_breaker import CircuitBreaker
from core.auto_recovery import AutoRecovery
from risk.risk_manager import RiskManager
from risk.position_manager import PositionManager
from strategies.sma_cross import SMACrossStrategy
from strategies.rsi_bb import RSIBollingerStrategy
from strategies.ema_scalping import EMAScalpingStrategy
from bot.order_manager import OrderManager
from notifications.telegram_notifier import TelegramNotifier
from core.volume_analyzer import VolumeAnalyzer
from dashboard.server import DashboardServer
from config.config import Config


class TradingBot:
    """
    Main trading bot that runs continuously.
    """
    
    def __init__(self):
        """Initialize the trading bot."""
        self.logger = get_logger(__name__)
        self.running = False
        
        # Initialize components
        self.logger.info("Initializing trading bot...")
        
        try:
            self.exchange = ExchangeConnector()
            self.market_data = MarketData(self.exchange)
            self.order_manager = OrderManager(self.exchange)
            self.risk_manager = RiskManager()
            self.position_manager = PositionManager()
            
            # Initialize Telegram notifier
            self.telegram = TelegramNotifier()
            
            # Set telegram notifier in position manager for trailing stop notifications
            self.position_manager.set_telegram_notifier(self.telegram)
            
            # Initialize Volume Analyzer
            self.volume_analyzer = VolumeAnalyzer(spike_threshold=Config.VOLUME_SPIKE_THRESHOLD)
            
            # Initialize Circuit Breaker
            if Config.ENABLE_CIRCUIT_BREAKER:
                self.circuit_breaker = CircuitBreaker()
                self.logger.info("Circuit Breaker enabled")
            else:
                self.circuit_breaker = None
                self.logger.info("Circuit Breaker disabled")
            
            # Initialize symbol-specific strategies
            self.symbol_strategies = {}
            self.logger.info("Initializing symbol-specific strategies...")
            
            for symbol in Config.SYMBOLS:
                # Get strategy name for this symbol
                strategy_name = Config.SYMBOL_STRATEGIES.get(symbol, Config.DEFAULT_STRATEGY)
                
                # Create strategy instance based on name
                if strategy_name == 'SMA_CROSS':
                    strategy = SMACrossStrategy()
                elif strategy_name == 'RSI_BB':
                    strategy = RSIBollingerStrategy()
                elif strategy_name == 'EMA_SCALP':
                    strategy = EMAScalpingStrategy()
                elif strategy_name == 'BOTH':
                    # For BOTH, we'll use a list of strategies (backward compatibility)
                    self.symbol_strategies[symbol] = [SMACrossStrategy(), RSIBollingerStrategy()]
                    self.logger.info(f"{symbol}: Using BOTH strategies (SMA_CROSS + RSI_BB)")
                    continue
                else:
                    # Fallback to EMA_SCALP as default
                    self.logger.warning(f"Unknown strategy '{strategy_name}' for {symbol}, using EMA_SCALP")
                    strategy = EMAScalpingStrategy()
                
                self.symbol_strategies[symbol] = strategy
                self.logger.info(f"{symbol}: {strategy_name} strategy assigned")
            
            if not self.symbol_strategies:
                raise ValueError("No strategies initialized for any symbols")
            
            # Initialize dashboard server in background thread
            self.logger.info("Starting dashboard server...")
            self.dashboard = DashboardServer(bot_instance=self)
            self.dashboard_thread = threading.Thread(
                target=self.dashboard.run,
                kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False},
                daemon=True,
                name="DashboardThread"
            )
            self.dashboard_thread.start()
            self.logger.info("Dashboard server started on http://localhost:5000")
            
            # Handle shutdown signals
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.logger.info("Trading bot initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize trading bot: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info("Shutdown signal received. Stopping bot...")
        self.stop()
    
    def start(self) -> None:
        """Start the trading bot main loop."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING TRADING BOT")
        self.logger.info("=" * 60)
        
        Config.print_config()
        
        if not Config.EXECUTE_REAL:
            self.logger.warning("*** RUNNING IN SIMULATION MODE ***")
            self.logger.warning("*** Orders will NOT be executed on the exchange ***")
        else:
            self.logger.warning("*** RUNNING IN LIVE MODE ***")
            self.logger.warning("*** Real orders WILL be executed ***")
        
        # Fetch actual balance and send correct Telegram startup message
        try:
            balance = self.exchange.get_balance('USDT')
            actual_capital = balance['total']
            if actual_capital > 0:
                self.risk_manager.current_capital = actual_capital
                # Send Telegram message with actual capital
                self.telegram._send_startup_message(actual_capital)
        except Exception as e:
            self.logger.warning(f"Could not fetch balance for startup message: {e}")
        
        self.running = True
        iteration = 0
        
        try:
            while self.running:
                iteration += 1
                self.logger.info(f"\n--- Iteration {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
                
                # Run trading logic
                self._trading_loop()
                
                # Wait for next iteration (check every second for shutdown signal)
                self.logger.info(f"Waiting {Config.UPDATE_INTERVAL} seconds until next update...")
                for _ in range(Config.UPDATE_INTERVAL):
                    if not self.running:
                        break
                    time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
            self.stop()
        
        finally:
            self._cleanup()
    
    def _trading_loop(self) -> None:
        """Execute one iteration of the trading logic."""
        try:
            # Check balance
            self._check_balance()
            
            # Check kill switch BEFORE trading
            should_halt, halt_reason = self.risk_manager.should_halt_trading()
            if should_halt:
                self.logger.critical(f"🚨 KILL SWITCH ACTIVE: {halt_reason}")
                self.logger.critical("Trading halted. Bot will continue monitoring but NOT execute new trades.")
                self.logger.critical(f"Current Drawdown: {self.risk_manager.get_current_drawdown():.2f}%")
                self.logger.critical(f"Consecutive Losses: {self.risk_manager.consecutive_losses}")
                
                # Send Telegram alert
                self.telegram.send_kill_switch_alert(
                    halt_reason,
                    self.risk_manager.get_current_drawdown(),
                    self.risk_manager.consecutive_losses
                )
                
                # Still update positions but don't open new ones
                self._update_positions()
                self._print_statistics()
                return
            
            # Update positions with current prices
            self._update_positions()
            
            # Analyze markets and generate signals
            for symbol in Config.SYMBOLS:
                self._process_symbol(symbol)
            
            # Print statistics
            self._print_statistics()
            
        except Exception as e:
            self.logger.error(f"Error in trading loop: {e}", exc_info=True)
    
    def _check_balance(self) -> None:
        """Check account balance."""
        try:
            balance = self.exchange.get_balance('USDT')
            self.logger.info(f"Account Balance - Free: ${balance['free']:.2f}, Used: ${balance['used']:.2f}, Total: ${balance['total']:.2f}")
            
            # Update risk manager capital if needed
            if balance['total'] > 0:
                self.risk_manager.current_capital = balance['total']
                
        except Exception as e:
            self.logger.warning(f"Could not fetch balance: {e}")
    
    def _update_positions(self) -> None:
        """Update all open positions and check for exit conditions."""
        if self.position_manager.get_open_positions_count() == 0:
            return
        
        try:
            # Get current prices
            current_prices = {}
            for symbol in Config.SYMBOLS:
                try:
                    current_prices[symbol] = self.market_data.get_current_price(symbol)
                except:
                    continue
            
            # Check positions
            positions_to_close = self.position_manager.update_positions(current_prices)
            
            # Close positions that hit SL/TP
            for symbol, reason in positions_to_close:
                self.logger.info(f"Closing position for {symbol} - Reason: {reason}")
                self._close_position(symbol, reason)
                
        except Exception as e:
            self.logger.error(f"Error updating positions: {e}")
    
    def _process_symbol(self, symbol: str) -> None:
        """
        Process a single symbol: fetch data, generate signal, execute if valid.
        
        Args:
            symbol: Trading pair to process
        """
        try:
            # Skip if we already have a position
            if self.position_manager.has_position(symbol):
                position = self.position_manager.get_position(symbol)
                current_price = self.market_data.get_current_price(symbol)
                pnl, pnl_pct = position.calculate_pnl(current_price)
                self.logger.info(
                    f"{symbol}: Open {position.side} position - "
                    f"Entry: ${position.entry_price:.2f}, Current: ${current_price:.2f}, "
                    f"PnL: ${pnl:+.2f} ({pnl_pct:+.2f}%)"
                )
                return
            
            # Fetch latest market data
            df = self.market_data.get_latest_data(
                symbol,
                Config.TIMEFRAME,
                lookback=max(Config.SMA_LONG_PERIOD, Config.BB_PERIOD) + 50
            )
            
            # Circuit Breaker Check - pause trading if extreme conditions detected
            if self.circuit_breaker:
                try:
                    # Get current market data for circuit breaker
                    ticker = self.exchange.exchange.fetch_ticker(symbol)
                    current_data = {
                        'price': ticker.get('last', 0),
                        'volume': ticker.get('baseVolume', 0),
                        'bid': ticker.get('bid', 0),
                        'ask': ticker.get('ask', 0),
                        'historical_df': df
                    }
                    
                    should_pause, reason = self.circuit_breaker.should_pause_trading(symbol, current_data)
                    if should_pause:
                        self.logger.warning(f"{symbol}: Circuit breaker activated - {reason}")
                        if self.telegram:
                            self.telegram.send_message(f"⚠️ Circuit Breaker: {symbol}\n{reason}")
                        return
                except Exception as e:
                    self.logger.error(f"Circuit breaker check failed for {symbol}: {e}")
            
            # Get symbol-specific strategy
            strategy = self.symbol_strategies.get(symbol)
            if not strategy:
                self.logger.warning(f"No strategy configured for {symbol}, skipping")
                return
            
            # Handle BOTH strategy case (list of strategies)
            signal = None
            active_strategy = None
            
            if isinstance(strategy, list):
                # Multiple strategies for this symbol
                for strat in strategy:
                    s = strat.generate_signal(df, symbol)
                    if s:
                        signal = s
                        active_strategy = strat.name
                        break
            else:
                # Single strategy for this symbol
                signal = strategy.generate_signal(df, symbol)
                if signal:
                    active_strategy = strategy.name
            
            if signal:
                self.logger.info(f"{symbol}: Signal detected from {active_strategy} - {signal.upper()}")
                
                # Multi-Timeframe (MTF) Trend Filter - Only for selected symbols
                if Config.ENABLE_MTF_FILTER and symbol in Config.MTF_SYMBOLS:
                    try:
                        # Fetch trend data (e.g., 4h)
                        trend_df = self.market_data.get_latest_data(
                            symbol, 
                            Config.TREND_TIMEFRAME, 
                            lookback=Config.TREND_EMA_PERIOD + 50
                        )
                        
                        if not trend_df.empty:
                            # Calculate Trend EMA
                            trend_ema = ta.trend.ema_indicator(
                                trend_df['close'], 
                                window=Config.TREND_EMA_PERIOD
                            ).iloc[-1]
                            
                            trend_price = trend_df['close'].iloc[-1]
                            is_bullish = trend_price > trend_ema
                            
                            trend_str = "BULLISH" if is_bullish else "BEARISH"
                            self.logger.info(f"{symbol}: {Config.TREND_TIMEFRAME} Trend is {trend_str} (Price: ${trend_price:.2f}, EMA{Config.TREND_EMA_PERIOD}: ${trend_ema:.2f})")
                            
                            # Filter Logic
                            if signal == 'buy' and not is_bullish:
                                self.logger.warning(f"MTF Filter: Skipping BUY signal for {symbol} (Counter-trend)")
                                return
                            
                            if signal == 'sell' and is_bullish:
                                self.logger.warning(f"MTF Filter: Skipping SELL signal for {symbol} (Counter-trend)")
                                return
                    except Exception as e:
                        self.logger.error(f"Error in MTF filter: {e}")
                        # On error, we default to allowing the trade (fail-open) or blocking (fail-close)
                        # Here we allow it but log error
                
                # Send signal notification
                current_price = df.iloc[-1]['close']
                sl_price = self.risk_manager.get_stop_loss_price(current_price, signal)
                tp_price = self.risk_manager.get_take_profit_price(current_price, signal)
                self.telegram.send_signal(
                    symbol, signal, active_strategy,
                    current_price, sl_price, tp_price
                )
                
                self._execute_signal(symbol, signal, df, active_strategy)
            else:
                # Log current status from this symbol's strategy
                # Use the symbol-specific strategy for trend detection
                if isinstance(strategy, list):
                    log_strategy = strategy[0]  # Use first strategy if multiple
                else:
                    log_strategy = strategy
                
                trend = log_strategy.get_trend(df)
                current_price = df.iloc[-1]['close']
                
                # Get relevant indicators based on strategy type
                if isinstance(log_strategy, SMACrossStrategy):
                    sma_short = df.iloc[-1][f'sma_{Config.SMA_SHORT_PERIOD}']
                    sma_long = df.iloc[-1][f'sma_{Config.SMA_LONG_PERIOD}']
                    self.logger.info(
                        f"{symbol}: No signal - Trend: {trend}, "
                        f"Price: ${current_price:.2f}, "
                        f"SMA{Config.SMA_SHORT_PERIOD}: ${sma_short:.2f}, "
                        f"SMA{Config.SMA_LONG_PERIOD}: ${sma_long:.2f}"
                    )
                else:  # RSI_BB
                    rsi = df.iloc[-1]['rsi']
                    bb_upper = df.iloc[-1]['bb_high']
                    bb_lower = df.iloc[-1]['bb_low']
                    self.logger.info(
                        f"{symbol}: No signal - Trend: {trend}, "
                        f"Price: ${current_price:.2f}, "
                        f"RSI: {rsi:.1f}, BB: ${bb_lower:.2f}-${bb_upper:.2f}"
                    )
                
        except Exception as e:
            self.logger.error(f"Error processing {symbol}: {e}")
    
    def _execute_signal(self, symbol: str, signal: str, df, strategy_name: str = "Unknown") -> None:
        """
        Execute a trading signal.
        
        Args:
            symbol: Trading pair
            signal: 'buy' or 'sell'
            df: Market data DataFrame
            strategy_name: Name of strategy that generated the signal
        """
        try:
            current_price = df.iloc[-1]['close']
            
            # Calculate position size
            stop_loss_price = self.risk_manager.get_stop_loss_price(current_price, signal)
            position_size = self.risk_manager.calculate_position_size(
                symbol,
                current_price,
                stop_loss_price
            )
            
            # Validate trade
            is_valid, reason = self.risk_manager.validate_trade(
                symbol,
                signal,
                position_size,
                current_price,
                self.position_manager.get_open_positions_count()
            )
            
            if not is_valid:
                self.logger.warning(f"Trade rejected for {symbol}: {reason}")
                return
            
            # Execute order
            order = self.order_manager.create_market_order(
                symbol,
                signal,
                position_size,
                notes=f"{strategy_name} signal"
            )
            
            if order:
                # Open position in position manager
                take_profit_price = self.risk_manager.get_take_profit_price(current_price, signal)
                
                self.position_manager.open_position(
                    symbol,
                    signal,
                    current_price,
                    position_size,
                    stop_loss_price,
                    take_profit_price
                )
                
                # Send order executed notification
                position_value = position_size * current_price
                self.telegram.send_order_executed(
                    symbol, signal, position_size,
                    current_price, position_value,
                    order.get('id')
                )
                
                self.logger.info(
                    f"Successfully executed {signal} for {symbol}: "
                    f"{position_size} @ ${current_price:.2f}"
                )
            else:
                self.logger.error(f"Failed to execute order for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error executing signal for {symbol}: {e}")
    
    def _close_position(self, symbol: str, reason: str) -> None:
        """
        Close a position.
        
        Args:
            symbol: Trading pair
            reason: Reason for closing
        """
        try:
            position = self.position_manager.get_position(symbol)
            if not position:
                return
            
            # Determine exit side (opposite of entry)
            exit_side = 'sell' if position.side == 'buy' else 'buy'
            
            # Execute exit order
            current_price = self.market_data.get_current_price(symbol)
            order = self.order_manager.create_market_order(
                symbol,
                exit_side,
                position.amount,
                notes=f"Close position - {reason}"
            )
            
            if order:
                # Close position in position manager
                closed_position = self.position_manager.close_position(
                    symbol,
                    current_price,
                    reason
                )
                
                if closed_position:
                    # Update risk manager
                    self.risk_manager.update_capital(closed_position.pnl)
                    
                    # Calculate duration
                    if closed_position.exit_time and closed_position.entry_time:
                        duration = closed_position.exit_time - closed_position.entry_time
                        hours = duration.total_seconds() / 3600
                        duration_str = f"{int(hours)}h {int((hours % 1) * 60)}m"
                    else:
                        duration_str = None
                    
                    # Send position closed notification
                    self.telegram.send_position_closed(
                        symbol, closed_position.side,
                        closed_position.pnl, closed_position.pnl_percent,
                        reason, duration_str
                    )
                    
                    self.logger.info(
                        f"Position closed for {symbol} - "
                        f"PnL: ${closed_position.pnl:+.2f} ({closed_position.pnl_percent:+.2f}%)"
                    )
            else:
                self.logger.error(f"Failed to close position for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error closing position for {symbol}: {e}")
    
    def _print_statistics(self) -> None:
        """Print current bot statistics."""
        stats = self.risk_manager.get_statistics()
        
        self.logger.info("\n--- Current Statistics ---")
        self.logger.info(f"Capital: ${stats['current_capital']:.2f}")
        self.logger.info(f"Total Return: {stats['total_return_pct']:+.2f}%")
        self.logger.info(f"Total Trades: {stats['total_trades']}")
        self.logger.info(f"Win Rate: {stats['win_rate_pct']:.1f}%")
        self.logger.info(f"Open Positions: {self.position_manager.get_open_positions_count()}")
    
    def stop(self) -> None:
        """Stop the trading bot."""
        self.logger.info("Stopping trading bot...")
        self.running = False
    
    def _cleanup(self) -> None:
        """Cleanup before shutdown."""
        self.logger.info("Performing cleanup...")
        
        # Close all open positions before shutdown (optional)
        if self.position_manager.get_open_positions_count() > 0:
            self.logger.warning(
                f"Bot stopping with {self.position_manager.get_open_positions_count()} open positions"
            )
            # Uncomment to auto-close on shutdown:
            # for symbol in list(self.position_manager.open_positions.keys()):
            #     self._close_position(symbol, "bot_shutdown")
        
        self.logger.info("=" * 60)
        self.logger.info("TRADING BOT STOPPED")
        self.logger.info("=" * 60)


# Import pandas for type hints
import pandas as pd
