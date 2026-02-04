import os
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        if not self.token:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN não configurado!")

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Envia mensagem para um chat do Telegram"""
        if not self.token:
            return False
            
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem Telegram: {e}")
            return False

    async def set_webhook(self, webhook_url: str, secret_token: str = None) -> bool:
        """Configura o webhook do bot"""
        if not self.token:
            return False
            
        url = f"{self.base_url}/setWebhook"
        payload = {"url": webhook_url}
        
        if secret_token:
            payload["secret_token"] = secret_token
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                result = response.json()
                logger.info(f"Webhook setup result: {result}")
                return result.get("ok", False)
        except Exception as e:
            logger.error(f"❌ Erro ao configurar webhook: {e}")
            return False
