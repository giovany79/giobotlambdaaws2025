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
        
        # Verificar que el mensaje tenga un chat
        if not isinstance(message_data, dict) or "chat" not in message_data:
            raise ValueError("Invalid message structure - missing chat information")
            
        chat_id = message_data["chat"]["id"]
        
        # Manejar mensajes de texto
        if "text" in message_data:
            message_text = message_data["text"]
        # Manejar mensajes de voz
        elif "voice" in message_data:
            raise ValueError("Voice messages are not supported. Please send a text message instead.")
        else:
            raise ValueError("Unsupported message type. Please send a text message.")

        # Retornamos el chatid y el mensaje
        return chat_id, message_text
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {str(e)}")
        raise ValueError("Invalid JSON format")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise