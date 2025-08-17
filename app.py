import json
import os
import csv
from datetime import datetime
import pandas as pd
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CSV_FILE = 'movements.csv'

# Inicializar cliente de OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def load_transactions():
    """Cargar transacciones desde el archivo CSV"""
    transactions = []
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Limpiar los valores de espacios en blanco
                row = {k.strip(): v.strip() for k, v in row.items()}
                transactions.append(row)
        return transactions
    except Exception as e:
        print(f"Error al cargar transacciones: {str(e)}")
        return []

def analyze_finances(question):
    """Analizar datos financieros y responder preguntas"""
    transactions = load_transactions()
    
    # Convertir a DataFrame para análisis más fácil
    df = pd.DataFrame(transactions)
    
    # Limpiar y convertir montos a numérico
    # Primero, reemplazar valores vacíos con NaN y luego eliminarlos
    df['Amount'] = df['Amount'].str.strip()
    df = df[df['Amount'] != '']  # Eliminar filas con montos vacíos
    
    # Verificar si hay datos después de la limpieza
    if len(df) == 0:
        return "No se encontraron transacciones válidas para analizar."
    
    # Convertir los montos a numérico
    df['Amount'] = (
        df['Amount']
        .str.replace('$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    
    # Convertir fechas
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Eliminar filas con fechas inválidas
    df = df.dropna(subset=['Date'])
    
    # Verificar si hay datos después de la limpieza
    if len(df) == 0:
        return "No se encontraron transacciones con fechas válidas para analizar."
    
    # Análisis básico
    total_income = df[df['Income/expensive'] == 'income']['Amount'].sum()
    total_expenses = df[df['Income/expensive'] == 'expensive']['Amount'].sum()
    balance = total_income - total_expenses
    
    # Categorías de gastos
    expense_by_category = df[df['Income/expensive'] == 'expensive'].groupby('Category')['Amount'].sum().sort_values(ascending=False)
    
    # Preparar contexto para la respuesta
    context = f"""
    Resumen Financiero:
    - Ingresos totales: ${total_income:,.0f}
    - Gastos totales: ${total_expenses:,.0f}
    - Balance: ${balance:,.0f}
    
    Gastos por categoría:
    """
    
    for category, amount in expense_by_category.items():
        context += f"  - {category}: ${amount:,.0f}\n"
    
    # Usar OpenAI para responder la pregunta basada en los datos
    prompt = f"""
    Eres un asistente financiero. Basándote en los siguientes datos:
    {context}
    
    Responde de manera clara y concisa la siguiente pregunta:
    {question}
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente financiero que ayuda a analizar gastos e ingresos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al analizar con IA: {str(e)}")
        return "Lo siento, hubo un error al analizar los datos financieros."

def get_ai_response(prompt: str) -> str:
    """Obtener respuesta de OpenAI"""
    # Verificar si la pregunta es sobre finanzas
    financial_keywords = ['gasto', 'ingreso', 'dinero', 'finanza', 'balance', 'ahorro', 'presupuesto']
    if any(keyword in prompt.lower() for keyword in financial_keywords):
        return analyze_finances(prompt)
    
    # Si no es sobre finanzas, usar el modelo de IA normal
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
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=data)
    return response.json()

def lambda_handler(event: dict, context) -> dict:
    """
    Handle incoming Lambda events from API Gateway (Telegram webhook).
    """
    print("Received event:", json.dumps(event, default=str))
    
    try:
        # Handle API Gateway test event
        if event.get('httpMethod') == 'GET' and event.get('queryStringParameters', {}).get('test') == '1':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'Webhook is working'})
            }
            
        # Check if the message is directly in the event (direct Lambda invocation)
        if 'message' in event:
            message = event['message']
            body = {}
        else:
            # Parse the request body for API Gateway events
            try:
                body = json.loads(event['body']) if isinstance(event.get('body'), str) else (event.get('body') or {})
                print("Parsed body:", json.dumps(body, default=str))
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }
            
            # Extract message from different possible formats
            if 'message' in body:
                message = body['message']
            elif 'body' in body and isinstance(body['body'], dict):
                if 'message' in body['body']:
                    message = body['body']['message']
                else:
                    message = body['body']
            else:
                message = body
        
        # Debug log the message structure
        print("Extracted message:", json.dumps(message, default=str))
        
        # Try to get chat_id from different possible locations
        chat_id = None
        if isinstance(message, dict):
            if 'chat' in message and isinstance(message['chat'], dict) and 'id' in message['chat']:
                chat_id = message['chat']['id']
            elif 'message' in message and isinstance(message['message'], dict) and 'chat' in message['message']:
                chat_id = message['message']['chat'].get('id')
            
            # Get user message text
            user_message = ''
            if 'text' in message:
                user_message = message['text']
            elif 'message' in message and isinstance(message['message'], dict) and 'text' in message['message']:
                user_message = message['message']['text']
            elif 'body' in message and isinstance(message['body'], dict) and 'text' in message['body']:
                user_message = message['body']['text']
        else:
            user_message = str(message)
        
        print(f"Chat ID: {chat_id}, Message: {user_message}")
        
        if not chat_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'No chat_id found in message',
                    'received_event': event,
                    'parsed_body': body if 'body' in locals() else None,
                    'message': message
                })
            }
            
        if not user_message:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'No message content to process'})
            }
            
        # Process the message
        response_text = get_ai_response(user_message)
        
        # Send response to Telegram
        send_telegram_message(chat_id, response_text)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'Message processed'})
        }
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        import traceback
        print("Traceback:", traceback.format_exc())
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e),
                'event': event
            })
        }

def _parse_event_body(event: dict) -> dict:
    """Parse and return the event body, handling different formats."""
    if 'body' not in event:
        return event  # Direct Lambda invocation
        
    body = event['body']
    
    # Handle base64 encoded body
    if event.get('isBase64Encoded', False):
        import base64
        body = base64.b64decode(body).decode('utf-8')
    
    # Parse JSON if body is a string
    if isinstance(body, str):
        body = json.loads(body)
    
    return body

def _extract_message(body: dict) -> dict:
    """Extract message from the parsed body."""
    message = body.get('message', {})
    if not message and 'body' in body:
        message = body.get('body', {})
    return message

def _get_chat_id(message: dict, body: dict) -> str:
    """Extract chat_id from message or body."""
    if 'chat' in message:
        return message.get('chat', {}).get('id')
    return body.get('chat_id')

def _get_user_message(message: dict, body: dict) -> str:
    """Extract user message from message or body."""
    if 'text' in message:
        return message['text']
    return body.get('text', '')

def _create_response(status_code: int, message: str) -> dict:
    """Create a standardized response object."""
    is_error = status_code >= 400
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'error' if is_error else 'success',
            'message': message
        })
    }

# Para pruebas locales
if __name__ == "__main__":
    # Ejemplo de preguntas para probar
    print(analyze_finances("¿Cuáles son mis mayores categorías de gasto?"))
    print(analyze_finances("¿Cuál es mi balance actual?"))
    print(analyze_finances("¿Cuánto he gastado en restaurantes este mes?"))