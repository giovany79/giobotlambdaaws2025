#!/usr/bin/env python3
"""
Script para configurar automáticamente el webhook de Telegram
que apunte a tu Lambda a través de API Gateway.
"""

import os
import sys
import json
import requests
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_api_gateway_url():
    """Obtiene la URL del API Gateway desde CloudFormation"""
    try:
        # Configurar cliente de CloudFormation
        cf_client = boto3.client('cloudformation', region_name='us-east-1')
        
        # Obtener información del stack
        response = cf_client.describe_stacks(StackName='telegram-bot-stack')
        
        # Buscar la URL del API Gateway en los outputs
        for output in response['Stacks'][0]['Outputs']:
            if output['OutputKey'] == 'ApiGatewayUrl':
                return output['OutputValue']
        
        print("❌ No se encontró ApiGatewayUrl en los outputs del stack")
        return None
        
    except ClientError as e:
        print(f"❌ Error al obtener información de CloudFormation: {e}")
        print("💡 Asegúrate de tener las credenciales de AWS configuradas:")
        print("   aws configure")
        return None

def set_telegram_webhook(bot_token, webhook_url):
    """Configura el webhook de Telegram"""
    try:
        # URL de la API de Telegram
        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        # Payload para configurar el webhook
        payload = {
            "url": webhook_url,
            "drop_pending_updates": True  # Elimina actualizaciones pendientes
        }
        
        print(f"🔄 Configurando webhook...")
        print(f"   Bot Token: {bot_token[:10]}...")
        print(f"   Webhook URL: {webhook_url}")
        
        # Realizar la petición
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook configurado exitosamente!")
            return True
        else:
            print(f"❌ Error configurando webhook: {result.get('description', 'Error desconocido')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def get_webhook_info(bot_token):
    """Obtiene información del webhook actual"""
    try:
        api_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(api_url)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result['result']
            print("\n📋 Información del webhook:")
            print(f"   URL: {webhook_info.get('url', 'No configurado')}")
            print(f"   Actualizaciones pendientes: {webhook_info.get('pending_update_count', 0)}")
            
            if webhook_info.get('last_error_date'):
                print(f"   ⚠️  Último error: {webhook_info.get('last_error_message', 'N/A')}")
            
            return True
        else:
            print(f"❌ Error obteniendo info del webhook: {result.get('description')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    print("🤖 Configurador de Webhook para Telegram Bot")
    print("=" * 50)
    
    # Verificar que existe el token del bot
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ No se encontró TELEGRAM_BOT_TOKEN en las variables de entorno")
        print("💡 Asegúrate de tener un archivo .env con:")
        print("   TELEGRAM_BOT_TOKEN=tu_token_aqui")
        sys.exit(1)
    
    # Obtener la URL del API Gateway
    print("🔄 Obteniendo URL del API Gateway...")
    api_gateway_url = get_api_gateway_url()
    
    if not api_gateway_url:
        print("\n💡 Si no tienes AWS CLI configurado, puedes:")
        print("1. Ir a AWS Console → CloudFormation → telegram-bot-stack → Outputs")
        print("2. Copiar el valor de 'ApiGatewayUrl'")
        print("3. Ejecutar manualmente:")
        print(f"   curl -X POST 'https://api.telegram.org/bot{bot_token[:10]}...setWebhook' \\")
        print("        -H 'Content-Type: application/json' \\")
        print("        -d '{\"url\": \"TU_API_GATEWAY_URL\"}'")
        sys.exit(1)
    
    print(f"✅ URL encontrada: {api_gateway_url}")
    
    # Configurar el webhook
    success = set_telegram_webhook(bot_token, api_gateway_url)
    
    if success:
        print("\n🎉 ¡Webhook configurado correctamente!")
        print("📱 Ahora puedes enviar mensajes a tu bot en Telegram")
        
        # Mostrar información del webhook
        get_webhook_info(bot_token)
        
        print("\n🚀 Pasos siguientes:")
        print("1. Ve a Telegram")
        print("2. Busca tu bot")
        print("3. Envía cualquier mensaje")
        print("4. ¡El bot debería responder automáticamente!")
        
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()