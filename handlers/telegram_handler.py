# Importamos las librerías necesarias
import json 
import base64
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Funcion para extraer el chat ID y el mensaje del evento
def extract_message(event):
    try:
        # Log the incoming event for debugging
        logger.info(f"Processing event: {json.dumps(event, default=str, indent=2)}")
        
        # Extraemos el cuerpo POST
        body_str = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)
        
        if not body_str:
            logger.error("Empty request body received")
            raise ValueError("Empty request body")
            
        # Decodificar si está en base64
        if is_base64:
            try:
                body_str = base64.b64decode(body_str).decode('utf-8')
                logger.info("Successfully decoded base64 body")
            except Exception as e:
                logger.error(f"Error decoding base64: {str(e)}")
                raise ValueError("Invalid message encoding")
        
        logger.info(f"Request body: {body_str}")
            
        # Parseamos el cuerpo POST como JSON
        try:
            body_json = json.loads(body_str)
            logger.info(f"Parsed JSON body: {json.dumps(body_json, default=str, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}, Body: {body_str}")
            raise ValueError("Invalid message format")
        
        # Verificamos que el JSON tenga la estructura esperada
        if not isinstance(body_json, dict):
            logger.error(f"Body is not a dict: {type(body_json)}")
            raise ValueError("Invalid message format - body is not a dict")
            
        if "message" not in body_json:
            logger.error(f"Missing 'message' in request body. Keys: {body_json.keys()}")
            raise ValueError("Invalid message format - missing message key")
            
        message_data = body_json["message"]
        
        # Verificar que el mensaje tenga un chat
        if not isinstance(message_data, dict):
            logger.error(f"Message data is not a dict: {type(message_data)}")
            raise ValueError("Invalid message structure - message data is not a dict")
            
        if "chat" not in message_data:
            logger.error(f"Missing chat information in message. Keys: {message_data.keys()}")
            raise ValueError("Invalid message structure - missing chat information")
            
        chat_info = message_data["chat"]
        if not isinstance(chat_info, dict) or "id" not in chat_info:
            logger.error(f"Invalid chat structure: {chat_info}")
            raise ValueError("Invalid chat structure - missing id")
            
        chat_id = chat_info["id"]
        logger.info(f"Extracted chat_id: {chat_id}")
        
        # Validar que el chat_id sea válido
        if not chat_id or chat_id == 0:
            logger.error(f"Invalid chat_id: {chat_id}")
            raise ValueError("Invalid chat_id")
        
        # Manejar mensajes de texto
        if "text" in message_data and message_data["text"]:
            logger.info(f"Text message received: {message_data['text']}")
            return chat_id, message_data["text"]
        # Manejar mensajes de voz
        elif "voice" in message_data:
            logger.info("Voice message received")
            return chat_id, "[VOICE_MESSAGE]"
        else:
            logger.warning(f"Unsupported message type: {list(message_data.keys())}")
            return chat_id, "[UNSUPPORTED_MESSAGE]"

    except ValueError as ve:
        # Re-raise ValueError with more context
        logger.error(f"Validation error in extract_message: {str(ve)}")
        raise ve
    except Exception as e:
        logger.error(f"Unexpected error in extract_message: {str(e)}")
        # Don't return chat_id=0, let the calling function handle it
        raise ValueError(f"Message extraction failed: {str(e)}")