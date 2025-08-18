# Importamos las librerías necesarias
import os
import requests

# Funcion para enviar un mensaje a Telegram
def send_message_to_telegram(chat_id, message):
    
    # Definimos la URL del API de Telegram
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"

    # Definimos los parámetros del mensaje
    params = {
        "chat_id": chat_id,
        "text": message
    }

    # Enviamos el mensaje a Telegram
    response = requests.post(url, json=params)
    
    # Verificamos si la solicitud fue exitosa
    if response.status_code != 200:
        raise Exception(f"Error al enviar mensaje a Telegram: {response.text}")