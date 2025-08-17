from dataclasses import dataclass
from typing import Optional, Dict, Any
import os

from domain.entities import Message, BotResponse
from domain.interfaces import AIServiceInterface, MessagingServiceInterface, LoggerInterface
from domain.interfaces.movement_repository_interface import MovementRepositoryInterface
from use_cases.handle_movement_command import HandleMovementCommandUseCase, HandleMovementCommandRequest


@dataclass
class ProcessMessageRequest:
    message: Message
    movement_repo: Optional[MovementRepositoryInterface] = None


@dataclass 
class ProcessMessageResponse:
    success: bool
    error_message: Optional[str] = None


class ProcessMessageUseCase:
    def __init__(
        self,
        ai_service: AIServiceInterface,
        messaging_service: MessagingServiceInterface,
        logger: LoggerInterface,
        movement_repo: Optional[MovementRepositoryInterface] = None
    ):
        self._ai_service = ai_service
        self._messaging_service = messaging_service
        self._logger = logger
        self._movement_repo = movement_repo or self._create_default_movement_repo()
    
    def _create_default_movement_repo(self):
        """Create a default movement repository if none is provided."""
        try:
            from infrastructure.repositories.csv_movement_repository import CSVMovementRepository
            # Get the absolute path to the movements.csv file in the project root
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'movements.csv')
            return CSVMovementRepository(csv_path)
        except Exception as e:
            self._logger.error(f"Failed to create movement repository: {str(e)}")
            return None
    
    def _is_movement_command(self, text: str) -> bool:
        """Check if the message is a movement-related command."""
        if not text:
            return False
            
        command = text.lower().split()[0]
        return command in ["agregar", "ver", "mostrar", "categorias", "resumen"]
    
    def _handle_movement_command(self, message: Message) -> ProcessMessageResponse:
        """Handle movement-related commands."""
        if not self._movement_repo:
            return ProcessMessageResponse(
                success=False,
                error_message="El sistema de movimientos no está disponible en este momento."
            )
        
        try:
            handler = HandleMovementCommandUseCase(self._movement_repo)
            response = handler.execute(HandleMovementCommandRequest(
                command=message.text,
                chat_id=message.chat_id.value,
                user_id=message.user_id.value if message.user_id else "unknown",
                message_id=message.message_id.value if message.message_id else ""
            ))
            
            # Send the response message
            bot_response = BotResponse(
                text=response.message,
                chat_id=message.chat_id
            )
            
            success = self._messaging_service.send_message(bot_response)
            if not success:
                self._logger.error("Failed to send movement command response")
            
            return ProcessMessageResponse(success=response.success)
            
        except Exception as e:
            self._logger.error(f"Error handling movement command: {str(e)}")
            return ProcessMessageResponse(
                success=False,
                error_message=f"Error al procesar el comando: {str(e)}"
            )
    
    def execute(self, request: ProcessMessageRequest) -> ProcessMessageResponse:
        try:
            self._logger.info(f"Processing message from chat {request.message.chat_id.value}")
            
            # Check if this is a movement command
            if self._is_movement_command(request.message.text):
                return self._handle_movement_command(request.message)
            
            # Otherwise, process with AI
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