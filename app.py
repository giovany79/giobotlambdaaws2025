import json
import time
import random
from handlers.telegram_handler import extract_message
from services.telegram_client import send_message_to_telegram
from services.openai_client import get_ai_response
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
        
        response = get_ai_response(message_text)
                                      
        # Enviamos la respuesta a Telegram
        send_message_to_telegram(chat_id, response)
        logger.info("Response sent successfully")

        # Retornamos la respuesta
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "success", "message": "Mensaje procesado correctamente"})
        }

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logger.error(error_msg)
        
        # En caso de error, intentamos notificar al usuario a través de Telegram
        try:
            if 'chat_id' in locals():
                send_message_to_telegram(chat_id, "❌ Lo siento, ha ocurrido un error al procesar tu mensaje.")
        except Exception as inner_e:
            logger.error(f"Could not send error notification: {str(inner_e)}")
            
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": "Error procesando el mensaje",
                "error": str(e)
            })
        }