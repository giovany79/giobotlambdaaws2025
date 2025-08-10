from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ChatId:
    value: int
    
    def __post_init__(self):
        if not isinstance(self.value, int) or self.value <= 0:
            raise ValueError("Chat ID must be a positive integer")


@dataclass(frozen=True)
class Message:
    text: str
    chat_id: ChatId
    
    def __post_init__(self):
        if not self.text or not self.text.strip():
            raise ValueError("Message text cannot be empty")


@dataclass(frozen=True)
class BotResponse:
    text: str
    chat_id: ChatId
    
    def __post_init__(self):
        if not self.text:
            raise ValueError("Response text cannot be empty")


@dataclass(frozen=True)
class TelegramUpdate:
    update_id: int
    message: Optional[Message] = None
    
    def __post_init__(self):
        if self.update_id <= 0:
            raise ValueError("Update ID must be positive")