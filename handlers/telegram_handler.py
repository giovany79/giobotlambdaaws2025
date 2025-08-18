# Importamos las librerías necesarias
import json 

# Funcion para extraer el chat ID y el mensaje del evento
def extract_message(event):

    # Extraemos el cuerpo POST como String
    body_str = event.get("body","")

    # Parseamos el cuerpo POST como JSON
    body_json = json.loads(body_str)

    # Extraemos el chatid y el mensaje
    chat_id = body_json["message"]["chat"]["id"]
    message = body_json["message"]["text"]

    # Retornamos el chatid y el mensaje
    return chat_id, message