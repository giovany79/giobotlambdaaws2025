# Importamos las librerías necesarias
import os
import requests
import json

# Funcion para enviar un mensaje a Telegram
def send_message_to_telegram(chat_id, text):
    """Envía un mensaje a un chat de Telegram.
    
    Args:
        chat_id: ID del chat de Telegram (puede ser un número o un string)
        text: Texto del mensaje a enviar
        
    Returns:
        dict: Respuesta de la API de Telegram
        
    Raises:
        ValueError: Si el chat_id no es válido o está vacío
        Exception: Si hay un error al enviar el mensaje
    """
    import logging
    logger = logging.getLogger()
    
    if not chat_id:
        raise ValueError("El chat_id no puede estar vacío")
    
    # Skip sending if chat_id is 0 (invalid)
    if chat_id == 0 or chat_id == '0':
        logger.warning("Skipping message send for invalid chat_id: 0")
        raise ValueError("Chat ID inválido: 0")
        
    try:
        # Convertir chat_id a string por si es un número
        chat_id_str = str(chat_id).strip()
        
        # Verificar que el chat_id tenga un formato válido
        if not chat_id_str.lstrip('-').isdigit():
            raise ValueError(f"Formato de chat_id no válido: {chat_id_str}")
        
        logger.info(f"Sending message to chat_id: {chat_id_str}")
        logger.info(f"Message text: {text[:100]}..." if len(text) > 100 else f"Message text: {text}")
            
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
        payload = {
            "chat_id": chat_id_str,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response_data = response.json()
        
        logger.info(f"Telegram API response: {json.dumps(response_data, indent=2)}")
        
        if not response_data.get('ok', False):
            error_code = response_data.get('error_code', 'N/A')
            error_description = response_data.get('description', 'Error desconocido')
            
            # Log specific error details
            logger.error(f"Telegram API error - Code: {error_code}, Description: {error_description}")
            
            # Handle specific error cases
            if error_code == 400 and "chat not found" in error_description.lower():
                raise Exception(f"Chat {chat_id_str} no encontrado. El usuario puede haber bloqueado el bot o el chat no existe.")
            else:
                raise Exception(f"Error al enviar mensaje a Telegram: {error_description}")
            
        logger.info("Message sent successfully to Telegram")
        return response_data
        
    except requests.exceptions.Timeout:
        logger.error("Timeout sending message to Telegram")
        raise Exception("Timeout al enviar mensaje a Telegram")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise Exception(f"Error de conexión con la API de Telegram: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise Exception("No se pudo decodificar la respuesta de la API de Telegram")
    except Exception as e:
        logger.error(f"Unexpected error sending message: {str(e)}")
        raise Exception(f"Error inesperado al enviar mensaje: {str(e)}")