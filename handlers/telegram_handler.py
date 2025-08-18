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
            body_str = base64.b64decode(body_str).decode('utf-8')
            
        # Parseamos el cuerpo POST como JSON
        body_json = json.loads(body_str)
        
        # Verificamos que el JSON tenga la estructura esperada
        if not isinstance(body_json, dict) or "message" not in body_json:
            raise ValueError("Invalid message format")
            
        message_data = body_json["message"]
        if not isinstance(message_data, dict) or "chat" not in message_data or "text" not in message_data:
            raise ValueError("Invalid message structure")

        # Extraemos el chatid y el mensaje
        chat_id = message_data["chat"]["id"]
        message_text = message_data["text"]

        # Retornamos el chatid y el mensaje
        return chat_id, message_text
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {str(e)}")
        raise ValueError("Invalid JSON format")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise