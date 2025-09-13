import os
from openai import OpenAI
from dotenv import load_dotenv
import json

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
    
    Args:
        user_message (str): The user's original message.
        operation_result (dict): The result from the operation function.
        
    Returns:
        str: A prompt for the AI to generate a response.
    """
    # Handle error cases
    if isinstance(operation_result, dict) and 'error' in operation_result:
        return f"""
        El usuario preguntó: '{user_message}'
        
        Ocurrió un error al procesar la solicitud: {operation_result['error']}
        
        Por favor, pide disculpas y sugiere al usuario que intente nuevamente o con diferentes parámetros.
        """
    
    # Handle case when no data was found
    if isinstance(operation_result, dict) and operation_result.get('status') == 'no_data':
        return f"""
        El usuario preguntó: '{user_message}'
        
        {operation_result.get('message', 'No se encontraron datos para la consulta.')}
        
        Por favor, responde de manera amable y sugiere al usuario que verifique los parámetros o intente con otro rango de fechas.
        """
    
    # Handle empty results
    if not operation_result or (isinstance(operation_result, dict) and not operation_result):
        return f"""
        El usuario preguntó: '{user_message}'
        
        No se encontraron resultados para la consulta.
        
        Por favor, informa al usuario que no se encontraron datos y sugiere que verifique los parámetros de búsqueda.
        """
    
    # Default case with data
    return f"""
    Eres un experto en finanzas. Basado en la siguiente pregunta del usuario:
    '{user_message}'
    
    Y los siguientes datos calculados de sus movimientos financieros:
    {json.dumps(operation_result, indent=2, ensure_ascii=False)}
    
    Proporciona una respuesta clara, concisa y amigable para el usuario en español. 
    Incluye los montos formateados con separadores de miles y dos decimales.
    Si hay múltiples categorías o períodos, organízalos de manera clara y fácil de entender.
    """