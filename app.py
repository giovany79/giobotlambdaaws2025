import json
import time
import random
from handlers.telegram_handler import extract_message
from services.telegram_client import send_message_to_telegram
from services.openai_client import get_ai_response
from services.csv_client import analyze_finances
from dotenv import load_dotenv
import os
import logging

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cargar variables de entorno
load_dotenv()


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event, indent=2)}")
    
    try:
        # Extraemos chatid y mensaje del evento
        chat_id, message_text = extract_message(event)
        logger.info(f"Processing message from chat {chat_id}: {message_text}")
        
        prompt = analyze_finances(message_text)
        
        response = get_ai_response(prompt)
                                      
        # Enviamos la respuesta a Telegram
        send_message_to_telegram(chat_id, response)
        logger.info("Response sent successfully")

        # Retornamos la respuesta
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "success", "message": "Mensaje procesado correctamente"})
        }

    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Validation error: {error_msg}")
        # Enviar mensaje de error al usuario
        if 'chat_id' in locals():
            send_message_to_telegram(chat_id, f"⚠️ {error_msg}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_msg})
        }
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logger.error(error_msg)
        # Enviar mensaje de error genérico al usuario
        if 'chat_id' in locals():
            send_message_to_telegram(chat_id, "❌ Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, inténtalo de nuevo.")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }