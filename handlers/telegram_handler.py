# Importamos las librerías necesarias
import json 
import base64
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Funcion para extraer el chat ID y el mensaje del evento
def extract_message(event):
    try:
        # Extraemos el cuerpo POST
        body_str = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)
        
        if not body_str:
            raise ValueError("Empty request body")
            
        # Decodificar si está en base64
        if is_base64:
            try:
                body_str = base64.b64decode(body_str).decode('utf-8')
            except Exception as e:
                logger.error(f"Error decoding base64: {str(e)}")
                raise ValueError("Invalid message encoding")
            
        # Parseamos el cuerpo POST como JSON
        try:
            body_json = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            raise ValueError("Invalid message format")
        
        # Verificamos que el JSON tenga la estructura esperada
        if not isinstance(body_json, dict) or "message" not in body_json:
            logger.error("Missing 'message' in request body")
            raise ValueError("Invalid message format")
            
        message_data = body_json["message"]
        
        # Verificar que el mensaje tenga un chat
        if not isinstance(message_data, dict) or "chat" not in message_data:
            logger.error("Missing chat information in message")
            raise ValueError("Invalid message structure - missing chat information")
            
        chat_id = message_data["chat"]["id"]
        
        # Manejar mensajes de texto
        if "text" in message_data and message_data["text"]:
            return chat_id, message_data["text"]
        # Manejar mensajes de voz
        elif "voice" in message_data:
            logger.info("Voice message received")
            return chat_id, "[VOICE_MESSAGE]"
        else:
            logger.warning(f"Unsupported message type: {message_data.keys()}")
            return chat_id, "[UNSUPPORTED_MESSAGE]"

    except Exception as e:
        logger.error(f"Error in extract_message: {str(e)}")
        # Si no podemos extraer el chat_id, usamos 0 como valor por defecto
        return 0, f"[ERROR] {str(e)}"