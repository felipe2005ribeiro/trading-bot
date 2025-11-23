"""
Equity curve visualization and export.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional
from config.config import Config


def generate_equity_curve(
    equity_df: pd.DataFrame,
    trades_df: pd.DataFrame = None,
    save_path: Optional[Path] = None,
    show: bool = False
) -> Optional[Path]:
    """
    Generate and optionally save equity curve visualization.
    
    Args:
        equity_df: DataFrame with equity curve data
        trades_df: Optional DataFrame with trade data to mark on chart
        save_path: Path to save the plot. If None, auto-generates filename.
        show: Whether to display the plot
    
    Returns:
        Path to saved plot file, or None if not saved
    """
    if len(equity_df) == 0:
        print("No equity data to plot")
        return None
    
    # Create figure with subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), height_ratios=[3, 1, 1])
    fig.suptitle('Backtest Results - Equity Curve', fontsize=16, fontweight='bold')
    
    # Convert timestamp to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(equity_df['timestamp']):
        equity_df['timestamp'] = pd.to_datetime(equity_df['timestamp'])
    
    # Plot 1: Equity curve
    ax1.plot(equity_df['timestamp'], equity_df['equity'], label='Total Equity', linewidth=2, color='blue')
    ax1.plot(equity_df['timestamp'], equity_df['cash'], label='Cash', linewidth=1, color='orange', alpha=0.7)
    ax1.axhline(y=equity_df['equity'].iloc[0], color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
    ax1.set_ylabel('Equity ($)', fontsize=12)
    ax1.set_title('Portfolio Equity Over Time', fontsize=14)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.ticklabel_format(style='plain', axis='y')
    
    # Plot 2: Drawdown
    equity_df['cummax'] = equity_df['equity'].cummax()
    equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
    
    ax2.fill_between(equity_df['timestamp'], equity_df['drawdown'], 0, color='red', alpha=0.3)
    ax2.plot(equity_df['timestamp'], equity_df['drawdown'], color='red', linewidth=1)
    ax2.set_ylabel('Drawdown (%)', fontsize=12)
    ax2.set_title('Drawdown', fontsize=14)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Open positions
    ax3.plot(equity_df['timestamp'], equity_df['open_positions'], color='green', linewidth=2)
    ax3.fill_between(equity_df['timestamp'], equity_df['open_positions'], 0, alpha=0.3, color='green')
    ax3.set_ylabel('# of Positions', fontsize=12)
    ax3.set_xlabel('Date', fontsize=12)
    ax3.set_title('Number of Open Positions', fontsize=14)
    ax3.grid(True, alpha=0.3)
    
    # Mark trades on equity curve if provided
    if trades_df is not None and len(trades_df) > 0:
        # Convert timestamps
        if not pd.api.types.is_datetime64_any_dtype(trades_df['entry_time']):
            trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])
        if not pd.api.types.is_datetime64_any_dtype(trades_df['exit_time']):
            trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
        
        # Mark entries
        buy_entries = trades_df[trades_df['side'] == 'buy']
        sell_entries = trades_df[trades_df['side'] == 'sell']
        
        for _, trade in buy_entries.iterrows():
            equity_at_entry = equity_df[equity_df['timestamp'] <= trade['entry_time']]['equity'].iloc[-1] if len(equity_df[equity_df['timestamp'] <= trade['entry_time']]) > 0 else equity_df['equity'].iloc[0]
            ax1.scatter(trade['entry_time'], equity_at_entry, color='green', marker='^', s=100, alpha=0.6, zorder=5)
        
        for _, trade in sell_entries.iterrows():
            equity_at_entry = equity_df[equity_df['timestamp'] <= trade['entry_time']]['equity'].iloc[-1] if len(equity_df[equity_df['timestamp'] <= trade['entry_time']]) > 0 else equity_df['equity'].iloc[0]
            ax1.scatter(trade['entry_time'], equity_at_entry, color='red', marker='v', s=100, alpha=0.6, zorder=5)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path or not show:
        if save_path is None:
            from datetime import datetime
            save_path = Config.RESULTS_DIR / f"equity_curve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Equity curve saved to {save_path}")
    
    # Show if requested
    if show:
        plt.show()
    else:
        plt.close()
    
    return save_path if save_path else None


def export_equity_data(equity_df: pd.DataFrame, filename: str = None) -> Path:
    """
    Export equity curve data to CSV.
    
    Args:
        equity_df: DataFrame with equity data
        filename: Custom filename. If None, auto-generates.
    
    Returns:
        Path to exported file
    """
    if filename is None:
        from datetime import datetime
        filename = f"equity_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    filepath = Config.RESULTS_DIR / filename
    equity_df.to_csv(filepath, index=False)
    
    print(f"Equity data exported to {filepath}")
    
    return filepath
