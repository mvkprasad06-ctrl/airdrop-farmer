"""Telegram notifier for farmer alerts."""
import os
import requests
import logging
from typing import Optional

class TelegramNotifier:
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)
        self.logger = logging.getLogger(__name__)
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
    
    def send(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.enabled:
            return False
        try:
            r = requests.post(
                f"{self.base_url}/sendMessage",
                json={"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode},
                timeout=10
            )
            return r.status_code == 200
        except Exception as e:
            self.logger.error(f"Telegram send failed: {e}")
            return False
    
    def alert(self, level: str, message: str, details: str = "") -> bool:
        emoji = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}.get(level, "📢")
        text = f"{emoji} <b>{level}</b>\n{message}"
        if details:
            text += f"\n<code>{details}</code>"
        return self.send(text)
    
    def daily_summary(self, stats: dict) -> bool:
        text = (
            f"📊 <b>Daily Summary</b>\n"
            f"Wallets: {stats.get('wallets', 0)}\n"
            f"Chains Active: {stats.get('chains', 0)}\n"
            f"Txns Today: {stats.get('txns', 0)}\n"
            f"Faucet Success: {stats.get('faucet_rate', 0):.0%}\n"
            f"Errors: {stats.get('errors', 0)}\n"
            f"CPU Avg: {stats.get('cpu_avg', 0):.0f}%\n"
            f"RAM Avg: {stats.get('ram_avg', 0):.0f}%"
        )
        return self.send(text)