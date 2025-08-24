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
    if not chat_id:
        raise ValueError("El chat_id no puede estar vacío")
        
    try:
        # Convertir chat_id a string por si es un número
        chat_id = str(chat_id).strip()
        
        # Verificar que el chat_id tenga un formato válido
        if not chat_id.lstrip('-').isdigit():
            raise ValueError(f"Formato de chat_id no válido: {chat_id}")
            
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if not response_data.get('ok', False):
            error_msg = response_data.get('description', 'Error desconocido')
            raise Exception(f"Error al enviar mensaje a Telegram: {error_msg} (código: {response_data.get('error_code', 'N/A')})")
            
        return response_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error de conexión con la API de Telegram: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("No se pudo decodificar la respuesta de la API de Telegram")
    except Exception as e:
        raise Exception(f"Error inesperado al enviar mensaje: {str(e)}")