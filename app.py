import json
import time
import random
from handlers.telegram_handler import extract_message
from services.telegram_client import send_message_to_telegram
from services.openai_client import get_ai_response, analyze_finances
from services.csv_client import analyze_finances as csv_analyze_finances
from services.operations_client import (
    get_operations,
    analize_operation_prompt,
    operation_functions,
)
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
    
    # Handle health checks or non-POST requests
    http_method = event.get('httpMethod', '').upper()
    if http_method == 'GET':
        logger.info("Health check request received")
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "healthy", "service": "telegram-bot-lambda"})
        }
    elif http_method != 'POST':
        logger.warning(f"Unsupported HTTP method: {http_method}")
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }
    
    try:
        # Load available operations
        operations = get_operations()
        logger.info(f"Loaded operations: {operations}")

        # Extraemos chatid y mensaje del evento
        try:
            chat_id, message_text = extract_message(event)
            logger.info(f"Processing message from chat {chat_id}: {message_text}")
        except ValueError as ve:
            logger.error(f"Message extraction failed: {str(ve)}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid message format: {str(ve)}"})
            }
        
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
        
        # 1. Determine which operation to execute based on the user's message
        prompt = analize_operation_prompt(operations, message_text)
        operation_response_str = get_ai_response(prompt)
        logger.info(f"Operation response from AI: {operation_response_str}")
        print("Operation response from AI: ", operation_response_str)
        try:
            # Extraer el JSON del string, que puede contener markdown
            json_start = operation_response_str.find('{')
            json_end = operation_response_str.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = operation_response_str[json_start:json_end]
                operation_result = json.loads(json_str)
            else:
                operation_result = {}
                logger.warning("No JSON object found in operation_response_str.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e} from string: {operation_response_str}")
            operation_result = {}
        
        
        print(operation_result)

        
        # 2. Execute the identified operation
        operation_name = operation_result.get("operation")
        operation_params= operation_result.get("params")
        print("operation: ", operation_name)
        print("params: ", operation_params)

        if operation_name in operation_functions:
            operation_function = operation_functions[operation_name]
            if operation_params:
                data = operation_function(**operation_params)
            else:
                data = operation_function()
            logger.info(f"Data from operation '{operation_name}': {data}")
        else:
            data = {"error": f"Operation '{operation_name}' not found."}
            logger.error(f"Operation '{operation_name}' not found.")

        print("Data from operation: ", data)
        # 3. Generate the final response for the user based on the operation result
        final_prompt = analyze_finances(message_text, data)
        print("Final prompt: ", final_prompt)
        
        final_response = get_ai_response(final_prompt)
        print("Final response: ", final_response)
                                      
        # Enviamos la respuesta a Telegram
        send_message_to_telegram(chat_id, final_response)
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