"""
Performance metrics calculation for backtesting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def calculate_metrics(
    equity_curve: pd.DataFrame,
    trades: pd.DataFrame,
    initial_capital: float,
    risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Calculate comprehensive performance metrics.
    
    Args:
        equity_curve: DataFrame with equity curve data
        trades: DataFrame with trade data
        initial_capital: Initial capital
        risk_free_rate: Annual risk-free rate for Sharpe ratio
    
    Returns:
        Dictionary with performance metrics
    """
    if len(equity_curve) == 0 or len(trades) == 0:
        return {
            'total_return_pct': 0,
            'annualized_return_pct': 0,
            'max_drawdown_pct': 0,
            'avg_drawdown_pct': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'calmar_ratio': 0,
            'recovery_factor': 0,
            'win_rate_pct': 0,
            'profit_factor': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'gross_profit': 0,
            'gross_loss': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'avg_trade_duration_hours': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'initial_capital': initial_capital,
            'final_capital': initial_capital,
            'total_pnl': 0
        }
    
    # Basic returns
    final_equity = equity_curve['equity'].iloc[-1]
    total_return = ((final_equity - initial_capital) / initial_capital) * 100
    
    # Annualized return
    days = (equity_curve['timestamp'].iloc[-1] - equity_curve['timestamp'].iloc[0]).days
    years = days / 365.25
    if years > 0:
        annualized_return = ((final_equity / initial_capital) ** (1 / years) - 1) * 100
    else:
        annualized_return = 0
    
    # Calculate returns
    equity_curve['returns'] = equity_curve['equity'].pct_change()
    
    # Drawdown calculation
    equity_curve['cummax'] = equity_curve['equity'].cummax()
    equity_curve['drawdown'] = (equity_curve['equity'] - equity_curve['cummax']) / equity_curve['cummax']
    max_drawdown = equity_curve['drawdown'].min() * 100
    avg_drawdown = equity_curve[equity_curve['drawdown'] < 0]['drawdown'].mean() * 100 if len(equity_curve[equity_curve['drawdown'] < 0]) > 0 else 0
    
    # Sharpe Ratio
    returns = equity_curve['returns'].dropna()
    if len(returns) > 0 and returns.std() > 0:
        sharpe_ratio = (returns.mean() - risk_free_rate / 252) / returns.std() * np.sqrt(252)
    else:
        sharpe_ratio = 0
    
    # Sortino Ratio (uses only downside deviation)
    downside_returns = returns[returns < 0]
    if len(downside_returns) > 0 and downside_returns.std() > 0:
        sortino_ratio = (returns.mean() - risk_free_rate / 252) / downside_returns.std() * np.sqrt(252)
    else:
        sortino_ratio = 0
    
    # Trade statistics
    total_trades = len(trades)
    winning_trades = len(trades[trades['pnl'] > 0])
    losing_trades = len(trades[trades['pnl'] < 0])
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Profit factor
    gross_profit = trades[trades['pnl'] > 0]['pnl'].sum()
    gross_loss = abs(trades[trades['pnl'] < 0]['pnl'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    # Average win/loss
    avg_win = trades[trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = trades[trades['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
    
    # Largest win/loss
    largest_win = trades['pnl'].max() if total_trades > 0 else 0
    largest_loss = trades['pnl'].min() if total_trades > 0 else 0
    
    # Average trade duration
    if 'entry_time' in trades.columns and 'exit_time' in trades.columns:
        trades['duration'] = (pd.to_datetime(trades['exit_time']) - pd.to_datetime(trades['entry_time'])).dt.total_seconds() / 3600
        avg_trade_duration_hours = trades['duration'].mean()
    else:
        avg_trade_duration_hours = 0
    
    # Calmar Ratio (annualized return / max drawdown)
    calmar_ratio = abs(annualized_return / max_drawdown) if max_drawdown != 0 else 0
    
    # Recovery Factor (total return / max drawdown)
    recovery_factor = abs(total_return / max_drawdown) if max_drawdown != 0 else 0
    
    # Consecutive wins/losses
    trades['win'] = trades['pnl'] > 0
    trades['streak'] = (trades['win'] != trades['win'].shift()).cumsum()
    win_streaks = trades[trades['win']].groupby('streak').size()
    loss_streaks = trades[~trades['win']].groupby('streak').size()
    
    max_consecutive_wins = win_streaks.max() if len(win_streaks) > 0 else 0
    max_consecutive_losses = loss_streaks.max() if len(loss_streaks) > 0 else 0
    
    return {
        # Returns
        'total_return_pct': total_return,
        'annualized_return_pct': annualized_return,
        
        # Risk metrics
        'max_drawdown_pct': max_drawdown,
        'avg_drawdown_pct': avg_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'calmar_ratio': calmar_ratio,
        'recovery_factor': recovery_factor,
        
        # Trade statistics
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate_pct': win_rate,
        
        # Profit metrics
        'profit_factor': profit_factor,
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'largest_win': largest_win,
        'largest_loss': largest_loss,
        
        # Other
        'avg_trade_duration_hours': avg_trade_duration_hours,
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses,
        
        # Capital
        'initial_capital': initial_capital,
        'final_capital': final_equity,
        'total_pnl': final_equity - initial_capital
    }


def print_metrics(metrics: Dict[str, Any]) -> None:
    """
    Print metrics in a formatted way.
    
    Args:
        metrics: Dictionary with metrics
    """
    print("\n" + "=" * 60)
    print("BACKTEST PERFORMANCE METRICS")
    print("=" * 60)
    
    print("\n--- RETURNS ---")
    print(f"Initial Capital:      ${metrics['initial_capital']:,.2f}")
    print(f"Final Capital:        ${metrics['final_capital']:,.2f}")
    print(f"Total P&L:            ${metrics['total_pnl']:+,.2f}")
    print(f"Total Return:         {metrics['total_return_pct']:+.2f}%")
    print(f"Annualized Return:    {metrics['annualized_return_pct']:+.2f}%")
    
    print("\n--- RISK METRICS ---")
    print(f"Max Drawdown:         {metrics['max_drawdown_pct']:.2f}%")
    print(f"Avg Drawdown:         {metrics['avg_drawdown_pct']:.2f}%")
    print(f"Sharpe Ratio:         {metrics['sharpe_ratio']:.2f}")
    print(f"Sortino Ratio:        {metrics['sortino_ratio']:.2f}")
    print(f"Calmar Ratio:         {metrics['calmar_ratio']:.2f}")
    print(f"Recovery Factor:      {metrics['recovery_factor']:.2f}")
    
    print("\n--- TRADE STATISTICS ---")
    print(f"Total Trades:         {metrics['total_trades']}")
    print(f"Winning Trades:       {metrics['winning_trades']}")
    print(f"Losing Trades:        {metrics['losing_trades']}")
    print(f"Win Rate:             {metrics['win_rate_pct']:.2f}%")
    print(f"Max Consecutive Wins: {metrics['max_consecutive_wins']}")
    print(f"Max Consecutive Loss: {metrics['max_consecutive_losses']}")
    
    print("\n--- PROFIT METRICS ---")
    print(f"Gross Profit:         ${metrics['gross_profit']:,.2f}")
    print(f"Gross Loss:           ${metrics['gross_loss']:,.2f}")
    print(f"Profit Factor:        {metrics['profit_factor']:.2f}")
    print(f"Average Win:          ${metrics['avg_win']:,.2f}")
    print(f"Average Loss:         ${metrics['avg_loss']:,.2f}")
    print(f"Largest Win:          ${metrics['largest_win']:,.2f}")
    print(f"Largest Loss:         ${metrics['largest_loss']:,.2f}")
    
    print("\n--- OTHER ---")
    print(f"Avg Trade Duration:   {metrics['avg_trade_duration_hours']:.1f} hours")
    
    print("=" * 60 + "\n")
