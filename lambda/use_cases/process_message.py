from dataclasses import dataclass
from typing import Optional

from ..domain.entities import Message, BotResponse
from ..domain.interfaces import AIServiceInterface, MessagingServiceInterface, LoggerInterface


@dataclass
class ProcessMessageRequest:
    message: Message


@dataclass 
class ProcessMessageResponse:
    success: bool
    error_message: Optional[str] = None


class ProcessMessageUseCase:
    def __init__(
        self,
        ai_service: AIServiceInterface,
        messaging_service: MessagingServiceInterface,
        logger: LoggerInterface
    ):
        self._ai_service = ai_service
        self._messaging_service = messaging_service
        self._logger = logger
    
    def execute(self, request: ProcessMessageRequest) -> ProcessMessageResponse:
        try:
            self._logger.info(f"Processing message from chat {request.message.chat_id.value}")
            
            ai_response_text = self._ai_service.generate_response(request.message.text)
            
            response = BotResponse(
                text=ai_response_text,
                chat_id=request.message.chat_id
            )
            
            success = self._messaging_service.send_message(response)
            
            if success:
                self._logger.info("Message processed successfully")
                return ProcessMessageResponse(success=True)
            else:
                error_msg = "Failed to send response"
                self._logger.error(error_msg)
                return ProcessMessageResponse(success=False, error_message=error_msg)
                
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self._logger.error(error_msg)
            return ProcessMessageResponse(success=False, error_message=error_msg)