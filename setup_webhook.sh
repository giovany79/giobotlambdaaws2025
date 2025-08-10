#!/bin/bash

# Script para configurar webhook de Telegram
# Uso: ./setup_webhook.sh

echo "🤖 Configurador de Webhook para Telegram Bot"
echo "=============================================="

# Cargar variables de entorno
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Variables de entorno cargadas desde .env"
else
    echo "❌ No se encontró archivo .env"
    echo "💡 Crea un archivo .env con:"
    echo "   TELEGRAM_BOT_TOKEN=tu_token_aqui"
    exit 1
fi

# Verificar que existe el token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN no está configurado"
    exit 1
fi

echo "🔄 Obteniendo URL del API Gateway..."

# Intentar obtener URL desde CloudFormation
API_GATEWAY_URL=$(aws cloudformation describe-stacks \
    --stack-name telegram-bot-stack \
    --region us-east-1 \
    --query "Stacks[0].Outputs[?OutputKey=='ApiGatewayUrl'].OutputValue" \
    --output text 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$API_GATEWAY_URL" ]; then
    echo "❌ No se pudo obtener la URL automáticamente"
    echo "💡 Opciones:"
    echo "1. Configura AWS CLI: aws configure"
    echo "2. O introduce la URL manualmente:"
    read -p "🔗 Pega la URL de API Gateway: " API_GATEWAY_URL
    
    if [ -z "$API_GATEWAY_URL" ]; then
        echo "❌ URL requerida para continuar"
        exit 1
    fi
fi

echo "✅ URL encontrada: $API_GATEWAY_URL"

# Configurar webhook
echo "🔄 Configurando webhook..."

RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$API_GATEWAY_URL\", \"drop_pending_updates\": true}")

# Verificar respuesta
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Webhook configurado exitosamente!"
    
    # Mostrar información del webhook
    echo ""
    echo "📋 Información del webhook:"
    curl -s -X GET "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo" | \
        python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    info = data['result']
    print(f'   URL: {info.get(\"url\", \"No configurado\")}')
    print(f'   Actualizaciones pendientes: {info.get(\"pending_update_count\", 0)}')
    if info.get('last_error_date'):
        print(f'   ⚠️  Último error: {info.get(\"last_error_message\", \"N/A\")}')
else:
    print('   ❌ Error obteniendo información')
"
    
    echo ""
    echo "🎉 ¡Todo listo!"
    echo "📱 Ahora puedes enviar mensajes a tu bot en Telegram"
    
else
    echo "❌ Error configurando webhook:"
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'   {data.get(\"description\", \"Error desconocido\")}')
except:
    print('   Respuesta inválida del servidor')
"
    exit 1
fi