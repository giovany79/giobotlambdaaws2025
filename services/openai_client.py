import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(prompt: str) -> str:
    """Obtener respuesta de OpenAI"""
    
    # Si no es sobre finanzas, usar el modelo de IA normal
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al llamar a OpenAI: {str(e)}")
        return "Lo siento, hubo un error al procesar tu solicitud."