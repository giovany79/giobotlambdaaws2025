import json
from typing import Dict, Any

from use_cases.process_message import ProcessMessageUseCase, ProcessMessageRequest
from adapters.openai_adapter import OpenAIAdapter
from adapters.telegram_adapter import TelegramAdapter
from adapters.logger import Logger
from infrastructure.config import Config
from infrastructure.parsers import TelegramEventParser


def lambda_handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    logger = Logger()
    
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        config = Config.from_env()
        
        ai_service = OpenAIAdapter(
            api_key=config.openai_api_key,
            model=config.openai_model
        )
        messaging_service = TelegramAdapter(bot_token=config.telegram_bot_token)
        
        use_case = ProcessMessageUseCase(
            ai_service=ai_service,
            messaging_service=messaging_service,
            logger=logger
        )
        
        telegram_update = TelegramEventParser.parse(event)
        if not telegram_update:
            logger.error("Invalid event format")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid event format'})
            }
        
        if not telegram_update.message:
            logger.info("No message to process")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No message to process'})
            }
        
        request = ProcessMessageRequest(message=telegram_update.message)
        result = use_case.execute(request)
        
        if result.success:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Message processed successfully',
                    'chat_id': telegram_update.message.chat_id.value
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': result.error_message or 'Unknown error'
                })
            }
            
    except Exception as e:
        error_msg = f"Fatal error in lambda_handler: {str(e)}"
        logger.error(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }