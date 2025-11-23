"""
Telegram notification service for trading bot.
Sends real-time alerts about trades, signals, and bot status.
"""

import requests
from typing import Optional
from datetime import datetime
from config.config import Config
from core.logger import get_logger


class TelegramNotifier:
    """
    Sends notifications via Telegram bot.
    """
    
    def __init__(self):
        """Initialize Telegram notifier."""
        self.logger = get_logger(__name__)
        self.enabled = Config.TELEGRAM_ENABLED
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        if self.enabled and (not self.bot_token or not self.chat_id):
            self.logger.warning("Telegram enabled but credentials missing. Disabling notifications.")
            self.enabled = False
        
        if self.enabled:
            self.logger.info("Telegram notifications enabled")
            # Startup message will be sent manually by TradingBot with actual capital
    
    def _send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message via Telegram.
        
        Args:
            message: Message text
            parse_mode: Parse mode (HTML or Markdown)
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(self.base_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                self.logger.warning(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def _send_startup_message(self, actual_capital: float = None):
        """Send bot startup notification."""
        mode = "🟢 LIVE" if Config.EXECUTE_REAL else "🟡 SIMULATION"
        capital = actual_capital if actual_capital else Config.INITIAL_CAPITAL
        message = (
            f"🤖 <b>Trading Bot Started</b>\n\n"
            f"Mode: {mode}\n"
            f"Exchange: {'Testnet' if Config.USE_TESTNET else 'Production'}\n"
            f"Symbols: {', '.join(Config.SYMBOLS)}\n"
            f"Strategy: {Config.STRATEGY}\n"
            f"Capital: ${capital:,.2f}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._send_message(message)
    
    def send_signal(self, symbol: str, signal: str, strategy: str, price: float, 
                   stop_loss: float, take_profit: float):
        """
        Send trading signal notification.
        
        Args:
            symbol: Trading pair
            signal: 'buy' or 'sell'
            strategy: Strategy name
            price: Current price
            stop_loss: Stop loss price
            take_profit: Take profit price
        """
        emoji = "🟢" if signal.lower() == "buy" else "🔴"
        message = (
            f"{emoji} <b>SEÑAL DE {signal.upper()}</b>\n\n"
            f"Par: <code>{symbol}</code>\n"
            f"Estrategia: {strategy}\n"
            f"Precio: ${price:,.2f}\n"
            f"Stop Loss: ${stop_loss:,.2f}\n"
            f"Take Profit: ${take_profit:,.2f}\n"
            f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        )
        self._send_message(message)
    
    def send_order_executed(self, symbol: str, side: str, amount: float, 
                          price: float, value: float, order_id: str = None):
        """
        Send order execution notification.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Amount traded
            price: Execution price
            value: Total value
            order_id: Order ID (optional)
        """
        emoji = "✅"
        message = (
            f"{emoji} <b>ORDEN EJECUTADA</b>\n\n"
            f"<code>{symbol}</code>: {side.capitalize()} de {amount:.6f}\n"
            f"Precio: ${price:,.2f}\n"
            f"Valor: ${value:,.2f}\n"
        )
        if order_id:
            message += f"Order ID: <code>{order_id}</code>\n"
        message += f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        
        self._send_message(message)
    
    def send_position_closed(self, symbol: str, side: str, pnl: float, 
                           pnl_percent: float, reason: str, duration: str = None):
        """
        Send position closed notification.
        
        Args:
            symbol: Trading pair
            side: Original position side
            pnl: Profit/loss amount
            pnl_percent: Profit/loss percentage
            reason: Reason for closing
            duration: Position duration (optional)
        """
        emoji = "💰" if pnl > 0 else "📉"
        pnl_sign = "+" if pnl >= 0 else ""
        
        message = (
            f"{emoji} <b>POSICIÓN CERRADA</b>\n\n"
            f"<code>{symbol}</code> ({side.upper()})\n"
            f"Razón: {reason}\n"
            f"PnL: {pnl_sign}${pnl:,.2f} ({pnl_sign}{pnl_percent:.2f}%)\n"
        )
        if duration:
            message += f"Duración: {duration}\n"
        message += f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        
        self._send_message(message)
    
    def send_kill_switch_alert(self, reason: str, drawdown: float, 
                             consecutive_losses: int):
        """
        Send kill switch activation alert.
        
        Args:
            reason: Reason for activation
            drawdown: Current drawdown percentage
            consecutive_losses: Number of consecutive losses
        """
        message = (
            f"🚨 <b>KILL SWITCH ACTIVADO</b>\n\n"
            f"⚠️ <b>{reason}</b>\n\n"
            f"Drawdown: {drawdown:.2f}%\n"
            f"Pérdidas consecutivas: {consecutive_losses}\n"
            f"Estado: Trading detenido automáticamente\n"
            f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._send_message(message)
    
    def send_trailing_stop_activated(self, symbol: str, activation_price: float, 
                                     trailing_stop_price: float, profit_percent: float):
        """
        Send trailing stop activation notification.
        
        Args:
            symbol: Trading pair
            activation_price: Price at activation
            trailing_stop_price: Current trailing stop price
            profit_percent: Unrealized profit percentage at activation
        """
        message = (
            f"🎯 <b>TRAILING STOP ACTIVADO</b>\n\n"
            f"<code>{symbol}</code>\n"
            f"Precio: ${activation_price:,.2f}\n"
            f"Profit: +{profit_percent:.2f}%\n"
            f"Trailing Stop: ${trailing_stop_price:,.2f}\n\n"
            f"✅ Ganancias protegidas!\n"
            f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        )
        self._send_message(message)
    
    def send_error(self, error_type: str, error_message: str):
        """
        Send error notification.
        
        Args:
            error_type: Type of error
            error_message: Error description
        """
        message = (
            f"⚠️ <b>ERROR EN BOT</b>\n\n"
            f"Tipo: {error_type}\n"
            f"Mensaje: {error_message}\n"
            f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._send_message(message)
    
    def send_daily_summary(self, capital: float, return_pct: float, 
                         trades: int, wins: int, losses: int, 
                         win_rate: float, best_trade: float = None):
        """
        Send daily summary notification.
        
        Args:
            capital: Current capital
            return_pct: Total return percentage
            trades: Number of trades
            wins: Winning trades
            losses: Losing trades
            win_rate: Win rate percentage
            best_trade: Best trade PnL (optional)
        """
        emoji = "📈" if return_pct > 0 else "📉"
        return_sign = "+" if return_pct >= 0 else ""
        
        message = (
            f"{emoji} <b>RESUMEN DIARIO</b>\n\n"
            f"Capital: ${capital:,.2f} ({return_sign}{return_pct:.2f}%)\n"
            f"Trades: {trades} ({wins}W / {losses}L)\n"
            f"Win Rate: {win_rate:.1f}%\n"
        )
        if best_trade is not None:
            best_sign = "+" if best_trade >= 0 else ""
            message += f"Mejor trade: {best_sign}${best_trade:,.2f}\n"
        message += f"Fecha: {datetime.now().strftime('%Y-%m-%d')}"
        
        self._send_message(message)
    
    def send_custom(self, title: str, message: str):
        """
        Send custom notification.
        
        Args:
            title: Message title
            message: Message body
        """
        formatted = (
            f"ℹ️ <b>{title}</b>\n\n"
            f"{message}\n"
            f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        )
        self._send_message(formatted)
