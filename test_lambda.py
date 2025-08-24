import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lambda'))
import app

def test_lambda_handler():
    # Ejemplo de evento de Telegram
    test_event = {
        "resource": "/webhook",
        "path": "/webhook",
        "httpMethod": "POST",
        "headers": {
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "Host": "ykhl1jughk.execute-api.us-east-1.amazonaws.com",
            "X-Amzn-Trace-Id": "Root=1-68a9c12c-51b8e2194352213c3d2a1905",
            "X-Forwarded-For": "91.108.5.42",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "multiValueHeaders": {
            "Accept-Encoding": [
                "gzip, deflate"
            ],
            "Content-Type": [
                "application/json"
            ],
            "Host": [
                "ykhl1jughk.execute-api.us-east-1.amazonaws.com"
            ],
            "X-Amzn-Trace-Id": [
                "Root=1-68a9c12c-51b8e2194352213c3d2a1905"
            ],
            "X-Forwarded-For": [
                "91.108.5.42"
            ],
            "X-Forwarded-Port": [
                "443"
            ],
            "X-Forwarded-Proto": [
                "https"
            ]
        },
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "9wy0ys",
            "resourcePath": "/webhook",
            "httpMethod": "POST",
            "extendedRequestId": "PwsfAHkRoAMEjYQ=",
            "requestTime": "23/Aug/2025:13:25:00 +0000",
            "path": "/Prod/webhook",
            "accountId": "058585900003",
            "protocol": "HTTP/1.1",
            "stage": "Prod",
            "domainPrefix": "ykhl1jughk",
            "requestTimeEpoch": 1755955500491,
            "requestId": "4bd004f7-82f0-48d9-ab6d-e5fdf738eb69",
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "sourceIp": "91.108.5.42",
                "principalOrgId": None,
                "accessKey": None,
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": None,
                "user": None
            },
            "domainName": "ykhl1jughk.execute-api.us-east-1.amazonaws.com",
            "deploymentId": "a1a8mj",
            "apiId": "ykhl1jughk"
        },
        "body": "eyJ1cGRhdGVfaWQiOjYyMjYzOTIzNSwKIm1lc3NhZ2UiOnsibWVzc2FnZV9pZCI6Mjc5LCJmcm9tIjp7ImlkIjo2Mjk5NzUzMDQ4LCJpc19ib3QiOmZhbHNlLCJmaXJzdF9uYW1lIjoiR2lvdmFueSIsImxhc3RfbmFtZSI6IlZpbGxlZ2FzIiwibGFuZ3VhZ2VfY29kZSI6ImVuIn0sImNoYXQiOnsiaWQiOjYyOTk3NTMwNDgsImZpcnN0X25hbWUiOiJHaW92YW55IiwibGFzdF9uYW1lIjoiVmlsbGVnYXMiLCJ0eXBlIjoicHJpdmF0ZSJ9LCJkYXRlIjoxNzU1OTU1NDI4LCJ0ZXh0IjoiTWUgcHVlZGVzIGRlY2lyIGxvcyBtb3ZtaWVudG9zIGVuIGVudGVydGFpbm1lbnQgZW4gZWwgbWVzIGRlIGFnb3N0byJ9fQ==",
        "isBase64Encoded": True
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

def test_invalid_message():
    """Test with invalid message format"""
    test_event = {
        "resource": "/webhook",
        "path": "/webhook",
        "httpMethod": "POST",
        "body": "invalid_json_content",
        "isBase64Encoded": False
    }
    
    test_context = {}
    
    response = app.lambda_handler(test_event, test_context)
    
    print("\nRespuesta con mensaje inválido:")
    print(json.dumps(response, indent=2))
    
    assert response['statusCode'] == 400
    print("✅ Error handling funcionó correctamente!")

def test_health_check():
    """Test health check endpoint"""
    test_event = {
        "resource": "/webhook",
        "path": "/webhook",
        "httpMethod": "GET"
    }
    
    test_context = {}
    
    response = app.lambda_handler(test_event, test_context)
    
    print("\nRespuesta de health check:")
    print(json.dumps(response, indent=2))
    
    assert response['statusCode'] == 200
    assert "healthy" in response['body']
    print("✅ Health check funcionó correctamente!")

if __name__ == "__main__":
    test_lambda_handler()
    print("\n" + "="*50)
    test_invalid_message()
    print("\n" + "="*50)
    test_health_check()
