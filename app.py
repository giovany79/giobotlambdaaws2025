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
        
        # Handle special message types
        if message_text == "[VOICE_MESSAGE]":
            send_message_to_telegram(chat_id, "⚠️ Los mensajes de voz no están soportados. Por favor, envía un mensaje de texto.")
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "success", "message": "Voice message handled"})
            }
        elif message_text.startswith("[UNSUPPORTED_MESSAGE]") or message_text.startswith("[ERROR]"):
            send_message_to_telegram(chat_id, "⚠️ Este tipo de mensaje no es compatible. Por favor, envía un mensaje de texto.")
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "success", "message": "Unsupported message type handled"})
            }
        
        # Process normal text message
        prompt = analyze_finances(message_text)
        response = get_ai_response(prompt)
                                      
        # Enviamos la respuesta a Telegram
        send_message_to_telegram(chat_id, response)
        logger.info("Response sent successfully")

        return {
            "statusCode": 200,
            "body": json.dumps({"status": "success", "message": "Mensaje procesado correctamente"})
        }

    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Validation error: {error_msg}")
        if chat_id and chat_id != 0:  # Only send error if we have a valid chat_id
            send_message_to_telegram(chat_id, f"⚠️ Error: {error_msg}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_msg})
        }
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logger.error(error_msg)
        if 'chat_id' in locals() and chat_id and chat_id != 0:  # Only send error if we have a valid chat_id
            send_message_to_telegram(chat_id, "❌ Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, inténtalo de nuevo.")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }