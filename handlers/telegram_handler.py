# Importamos las librerías necesarias
import json 

# Funcion para extraer el chat ID y el mensaje del evento
def extract_message(event):
    try:
        # Extraemos el cuerpo POST como String
        body_str = event.get("body", "")
        
        if not body_str:
            raise ValueError("Empty request body")
            
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
        raise ValueError(f"Invalid JSON: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Missing required field: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing message: {str(e)}")