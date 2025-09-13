import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(prompt: str) -> str:
    """Obtener respuesta de OpenAI sin mantener historial de conversación"""
    
    try:
        # Siempre crear una nueva conversación con solo el mensaje actual
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un asistente útil. Responde solo a la pregunta actual sin hacer referencia a mensajes anteriores."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "Lo siento, no pude procesar tu solicitud en este momento."

def analyze_finances(user_message, operation_result):
    """
    Creates a prompt for the AI to analyze financial data based on the user's message and operation result.
    """
    prompt = f"""
    Eres un experto en finanzas. Basado en la siguiente pregunta del usuario:
    '{user_message}'
    
    Y los siguientes datos calculados de sus movimientos financieros:
    '{operation_result}'

    Proporciona una respuesta clara consisa y amigable para el usuario en español. 
    """
    return prompt