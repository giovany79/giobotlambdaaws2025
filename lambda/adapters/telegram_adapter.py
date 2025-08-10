import requests

from ..domain.entities import BotResponse
from ..domain.interfaces import MessagingServiceInterface


class TelegramAdapter(MessagingServiceInterface):
    def __init__(self, bot_token: str):
        self._bot_token = bot_token
        self._base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, response: BotResponse) -> bool:
        try:
            url = f"{self._base_url}/sendMessage"
            params = {
                "chat_id": response.chat_id.value,
                "text": response.text
            }
            
            http_response = requests.post(url, params=params, timeout=10)
            return http_response.status_code == 200
            
        except Exception:
            return False