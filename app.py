import json
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Inicializar cliente de OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(prompt: str) -> str:
    """Obtener respuesta de OpenAI"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al llamar a OpenAI: {str(e)}")
        return "Lo siento, hubo un error al procesar tu solicitud."

def send_telegram_message(chat_id: str, text: str) -> None:
    """Enviar mensaje a través de Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=data)
    return response.json()

def lambda_handler(event, context):
    try:
        # Parsear el evento de entrada
        body = json.loads(event['body'])
        
        # Extraer información del mensaje
        message = body.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        user_message = message.get('text', '')
        
        if not chat_id or not user_message:
            return {'statusCode': 400, 'body': 'Mensaje inválido'}
        
        # Obtener respuesta de IA
        response_text = get_ai_response(user_message)
        
        # Enviar respuesta a Telegram
        send_telegram_message(chat_id, response_text)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Mensaje procesado correctamente'})
        }
        
    except Exception as e:
        print(f"Error en lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno del servidor'})
        }

# Para pruebas locales
if __name__ == "__main__":
    # Ejemplo de evento para pruebas locales
    test_event = {
        'body': json.dumps({
            'message': {
                'chat': {'id': '12345'},
                'text': 'Hola, ¿cómo estás?'
            }
        })
    }
    
    result = lambda_handler(test_event, None)
    print("Resultado:", result)