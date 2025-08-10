from abc import ABC, abstractmethod
from typing import Protocol

from .entities import Message, BotResponse


class AIServiceInterface(ABC):
    @abstractmethod
    def generate_response(self, message: str) -> str:
        pass


class MessagingServiceInterface(ABC):
    @abstractmethod 
    def send_message(self, response: BotResponse) -> bool:
        pass


class LoggerInterface(Protocol):
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...