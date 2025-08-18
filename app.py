import json
import time
import random
from handlers.telegram_handler import extract_message
from services.telegram_client import send_message_to_telegram
from dotenv import load_dotenv
import os


# Cargar variables de entorno
load_dotenv()

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def lambda_handler(event, context):
    try:
        # Extraemos chatid y mensaje del evento
        chat_id, message_text = extract_message(event)

        
        response = "hola"
                                      
        # Enviamos la respuesta a Telegram
        send_message_to_telegram(chat_id, response)

        # Retornamos la respuesta
        return {
            "statusCode": 200,
            "body": json.dumps("Mensaje procesado y enviado a Telegram")
        }

    except Exception as e:
        # Imprimimos el error
        print(f"Error en ejecución Lambda: {e}")
        # Retornamos un mensaje de error
        return {
            "statusCode": 500,
            "body": json.dumps("Error procesando el mensaje")
        }