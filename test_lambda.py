import json
import lambda_function

def test_lambda_handler():
    # Ejemplo de evento de Telegram
    test_event = {
        "body": json.dumps({
            "message": {
                "chat": {
                    "id": 6299753048
                },
                "text": "Hola, ¿cómo estás?"
            }
        })
    }
    
    # Contexto falso (no utilizado en nuestro handler)
    test_context = {}
    
    # Invocar la función
    response = lambda_function.lambda_handler(test_event, test_context)
    
    print("\nRespuesta de la función:")
    print(json.dumps(response, indent=2))
    
    # Verificar el código de estado
    assert response['statusCode'] == 200
    print("\n✅ Prueba exitosa!")

if __name__ == "__main__":
    test_lambda_handler()
