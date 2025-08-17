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
    df['Amount'] = df['Amount'].str.replace('$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    
    # Convertir fechas
    df['Date'] = pd.to_datetime(df['Date'])
    
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
    # Ejemplo de preguntas para probar
    print(analyze_finances("¿Cuáles son mis mayores categorías de gasto?"))
    print(analyze_finances("¿Cuál es mi balance actual?"))
    print(analyze_finances("¿Cuánto he gastado en restaurantes este mes?"))