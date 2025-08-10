import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    openai_api_key: str
    telegram_bot_token: str
    openai_model: str = "gpt-3.5-turbo"
    
    @classmethod
    def from_env(cls) -> 'Config':
        load_dotenv()
        
        openai_key = os.getenv("OPENAI_API_KEY")
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        return cls(
            openai_api_key=openai_key,
            telegram_bot_token=telegram_token,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        )