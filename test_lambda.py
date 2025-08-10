import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lambda'))
import app

def test_lambda_handler():
    # Ejemplo de evento de Telegram
    test_event = {
        "body": json.dumps({
            "message": {
                "chat": {
                    "id": 6299753048
                },
                "text": "Hola Gio, ¿cómo estás?"
            }
        })
    }
    
    # Contexto falso (no utilizado en nuestro handler)
    test_context = {}
    
    # Invocar la función
    response = app.lambda_handler(test_event, test_context)
    
    print("\nRespuesta de la función:")
    print(json.dumps(response, indent=2))
    
    # Verificar el código de estado
    assert response['statusCode'] == 200
    print("\n✅ Prueba exitosa!")

if __name__ == "__main__":
    test_lambda_handler()
