import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import ta

from strategies.base_strategy import BaseStrategy
from risk.risk_manager import RiskManager
from risk.position_manager import PositionManager
from config.config import Config
from core.logger import get_logger


class Backtester:
    """
    Backtesting engine for evaluating trading strategies.
    """
    
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = None,
        commission_rate: float = None,
        slippage_rate: float = None
    ):
        """
        Initialize backtester.
        
        Args:
            strategy: Trading strategy to backtest
            initial_capital: Starting capital
            commission_rate: Commission rate (percentage)
            slippage_rate: Slippage rate (percentage)
        """
        self.strategy = strategy
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL
        self.commission_rate = commission_rate or Config.COMMISSION_RATE
        self.slippage_rate = slippage_rate or Config.SLIPPAGE_RATE
        
        self.logger = get_logger(__name__)
        self.risk_manager = RiskManager(self.initial_capital)
        self.position_manager = PositionManager()
        
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []
        
        self.logger.info(
            f"Initialized backtester with strategy: {strategy.name}, "
            f"capital: ${self.initial_capital:,.2f}, "
            f"commission: {self.commission_rate}%, "
            f"slippage: {self.slippage_rate}%"
        )
    
    def run(
        self,
        data: Dict[str, pd.DataFrame],
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data.
        
        Args:
            data: Dictionary of symbol -> DataFrame with OHLCV data
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)
        
        Returns:
            Dictionary with backtest results
        """
        self.logger.info(f"Starting backtest from {start_date} to {end_date}")
        
        # Filter data by date range
        if start_date or end_date:
            data = self._filter_by_date(data, start_date, end_date)
        
        # Analyze data with strategy
        analyzed_data = {}
        for symbol, df in data.items():
            analyzed_data[symbol] = self.strategy.analyze(df)
        
        # Get all timestamps (use first symbol as reference)
        timestamps = analyzed_data[list(data.keys())[0]].index
        
        # Initialize equity tracking
        current_equity = self.initial_capital
        
        # Iterate through time
        for i, timestamp in enumerate(timestamps):
            # Get current data for all symbols
            current_data = {}
            for symbol, df in analyzed_data.items():
                if timestamp in df.index:
                    current_data[symbol] = df.loc[:timestamp]
            
            # Check existing positions for stop loss / take profit
            current_prices = {
                symbol: df.loc[timestamp, 'close']
                for symbol, df in analyzed_data.items()
                if timestamp in df.index
            }
            
            positions_to_close = self.position_manager.update_positions(current_prices)
            
            for symbol, reason in positions_to_close:
                exit_price = current_prices[symbol]
                position = self.position_manager.close_position(
                    symbol,
                    exit_price,
                    reason
                )
                
                if position:
                    # Calculate commission and slippage
                    exit_value = position.amount * exit_price
                    commission = exit_value * (self.commission_rate / 100)
                    slippage = exit_value * (self.slippage_rate / 100)
                    
                    # Adjust PnL
                    adjusted_pnl = position.pnl - commission - slippage
                    
                    # Update capital
                    self.risk_manager.update_capital(adjusted_pnl)
                    
                    # Record trade
                    self.trades.append({
                        'entry_time': position.entry_time,
                        'exit_time': timestamp,
                        'symbol': symbol,
                        'side': position.side,
                        'entry_price': position.entry_price,
                        'exit_price': exit_price,
                        'amount': position.amount,
                        'pnl': adjusted_pnl,
                        'pnl_percent': (adjusted_pnl / (position.entry_price * position.amount)) * 100,
                        'commission': commission,
                        'slippage': slippage,
                        'reason': reason
                    })
            
            # Generate signals for symbols without open positions
            for symbol, df in current_data.items():
                if self.position_manager.has_position(symbol):
                    continue
                
                signal = self.strategy.generate_signal(df, symbol)
                
                # MTF Filter Logic (Backtest Simulation)
                if Config.ENABLE_MTF_FILTER and signal in ['buy', 'sell']:
                    # Approximate higher timeframe EMA
                    # If trading 1h and trend 4h -> EMA 200 * 4 = EMA 800
                    # This is a robust approximation for backtesting without multi-df sync
                    trend_factor = 4  # Assuming 1h -> 4h
                    trend_period = Config.TREND_EMA_PERIOD * trend_factor
                    
                    # Calculate trend EMA on the fly (or pre-calc for speed, but this is safer)
                    # Using a long EMA on current timeframe to simulate higher timeframe trend
                    trend_ema = ta.trend.ema_indicator(df['close'], window=trend_period)
                    current_trend_ema = trend_ema.iloc[-1] # Use last value of current slice
                    current_price = df.iloc[-1]['close']
                    
                    is_bullish = current_price > current_trend_ema
                    
                    if signal == 'buy' and not is_bullish:
                        signal = None # Filtered
                    elif signal == 'sell' and is_bullish:
                        signal = None # Filtered
                
                if signal in ['buy', 'sell']:
                    current_price = df.iloc[-1]['close']
                    
                    # Apply slippage to entry price
                    if signal == 'buy':
                        entry_price = current_price * (1 + self.slippage_rate / 100)
                    else:
                        entry_price = current_price * (1 - self.slippage_rate / 100)
                    
                    # Calculate position size
                    stop_loss = self.risk_manager.get_stop_loss_price(entry_price, signal)
                    amount = self.risk_manager.calculate_position_size(
                        symbol,
                        entry_price,
                        stop_loss
                    )
                    
                    # Validate trade
                    is_valid, reason = self.risk_manager.validate_trade(
                        symbol,
                        signal,
                        amount,
                        entry_price,
                        self.position_manager.get_open_positions_count()
                    )
                    
                    if is_valid:
                        # Calculate commission
                        entry_value = amount * entry_price
                        commission = entry_value * (self.commission_rate / 100)
                        
                        # Deduct commission from capital
                        self.risk_manager.current_capital -= commission
                        
                        # Open position
                        take_profit = self.risk_manager.get_take_profit_price(entry_price, signal)
                        self.position_manager.open_position(
                            symbol,
                            signal,
                            entry_price,
                            amount,
                            stop_loss,
                            take_profit
                        )
                    else:
                        self.logger.debug(f"Trade rejected: {reason}")
            
            # Update equity curve
            current_equity = self.risk_manager.current_capital
            open_pnl = self.position_manager.get_total_pnl(current_prices)
            total_equity = current_equity + open_pnl
            
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': total_equity,
                'cash': current_equity,
                'open_pnl': open_pnl,
                'open_positions': self.position_manager.get_open_positions_count()
            })
        
        # Close any remaining open positions
        for symbol in list(self.position_manager.open_positions.keys()):
            exit_price = analyzed_data[symbol].iloc[-1]['close']
            position = self.position_manager.close_position(symbol, exit_price, "backtest_end")
            
            if position:
                exit_value = position.amount * exit_price
                commission = exit_value * (self.commission_rate / 100)
                slippage = exit_value * (self.slippage_rate / 100)
                adjusted_pnl = position.pnl - commission - slippage
                
                self.risk_manager.update_capital(adjusted_pnl)
                
                self.trades.append({
                    'entry_time': position.entry_time,
                    'exit_time': timestamps[-1],
                    'symbol': symbol,
                    'side': position.side,
                    'entry_price': position.entry_price,
                    'exit_price': exit_price,
                    'amount': position.amount,
                    'pnl': adjusted_pnl,
                    'pnl_percent': (adjusted_pnl / (position.entry_price * position.amount)) * 100,
                    'commission': commission,
                    'slippage': slippage,
                    'reason': 'backtest_end'
                })
        
        self.logger.info(f"Backtest completed. Total trades: {len(self.trades)}")
        
        return self.get_results()
    
    def _filter_by_date(
        self,
        data: Dict[str, pd.DataFrame],
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, pd.DataFrame]:
        """Filter data by date range."""
        filtered_data = {}
        
        for symbol, df in data.items():
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
            filtered_data[symbol] = df
        
        return filtered_data
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get backtest results.
        
        Returns:
            Dictionary with results
        """
        trades_df = pd.DataFrame(self.trades)
        equity_df = pd.DataFrame(self.equity_curve)
        
        return {
            'trades': trades_df,
            'equity_curve': equity_df,
            'initial_capital': self.initial_capital,
            'final_capital': self.risk_manager.current_capital,
            'total_return': ((self.risk_manager.current_capital - self.initial_capital) / self.initial_capital) * 100,
            'total_trades': len(self.trades),
            'risk_stats': self.risk_manager.get_statistics(),
            'position_stats': self.position_manager.get_statistics()
        }
    
    def export_trades(self, filename: str = None) -> Path:
        """
        Export trades to CSV.
        
        Args:
            filename: Custom filename. If None, auto-generates.
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"backtest_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = Config.RESULTS_DIR / filename
        
        trades_df = pd.DataFrame(self.trades)
        trades_df.to_csv(filepath, index=False)
        
        self.logger.info(f"Trades exported to {filepath}")
        
        return filepath
    
    def export_equity_curve(self, filename: str = None) -> Path:
        """
        Export equity curve to CSV.
        
        Args:
            filename: Custom filename. If None, auto-generates.
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"backtest_equity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = Config.RESULTS_DIR / filename
        
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.to_csv(filepath, index=False)
        
        self.logger.info(f"Equity curve exported to {filepath}")
        
        return filepath
