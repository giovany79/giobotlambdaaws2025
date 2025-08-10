# 🤖 Telegram Bot con AWS Lambda y OpenAI

Bot de Telegram inteligente que usa **OpenAI GPT** para responder mensajes, desplegado en **AWS Lambda** con **arquitectura limpia** y **CI/CD automático** con GitHub Actions.

## 🏗️ Arquitectura

```
📦 Proyecto
├── 🎯 lambda/                 # Código de la Lambda (Clean Architecture)
│   ├── 📁 adapters/          # Adaptadores externos (OpenAI, Telegram, Logger)
│   ├── 📁 domain/            # Entidades y interfaces del dominio
│   ├── 📁 infrastructure/    # Configuración y parsers
│   ├── 📁 use_cases/        # Lógica de negocio
│   └── 📄 app.py            # Handler principal de Lambda
├── 🔧 infraestructure/      # CloudFormation template
├── 🚀 .github/workflows/    # CI/CD con GitHub Actions
└── 🛠️ Scripts automatizados
```

## ✨ Características

- 🧠 **OpenAI GPT Integration** - Respuestas inteligentes
- ⚡ **AWS Lambda** - Serverless, escalable y económico
- 🏛️ **Clean Architecture** - Código mantenible y testeable
- 🚀 **CI/CD Automático** - Deploy con GitHub Actions
- 🔐 **Gestión de Secrets** - Variables de entorno seguras
- 📊 **API Gateway** - Webhook de Telegram
- 🐳 **Docker Build** - Dependencias compatibles con Lambda

## 🚀 Setup Rápido

### 1. Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/giobotlambdaaws2025.git
cd giobotlambdaaws2025

# Crear archivo de configuración
cp .env.example .env
```

### 2. Configurar Variables de Entorno

Edita `.env` con tus credenciales:

```bash
# Telegram Bot Token (obtener de @BotFather)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# OpenAI API Key (obtener de https://platform.openai.com)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Configurar GitHub Secrets

En tu repositorio de GitHub: **Settings** → **Secrets and variables** → **Actions**

Agregar estos secrets:

```
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
TELEGRAM_BOT_TOKEN=tu_bot_token
OPENAI_API_KEY=tu_openai_key
```

### 4. Desplegar Automáticamente

```bash
# Hacer push a main para desplegar
git add .
git commit -m "Deploy bot"
git push origin main
```

GitHub Actions automáticamente:
- ✅ Instala dependencias Python
- ✅ Crea paquete de deployment 
- ✅ Despliega a AWS Lambda
- ✅ Configura API Gateway

## 🔗 Configurar Webhook de Telegram

### Opción 1: Script Automático (Recomendado)

```bash
# Script Python (más robusto)
pip install boto3 requests python-dotenv
python3 setup_webhook.py

# O script Bash (más simple)
./setup_webhook.sh
```

### Opción 2: Manual

1. **Obtener URL del API Gateway:**
   - Ve a AWS Console → CloudFormation → `telegram-bot-stack` → Outputs
   - Copia el valor de `ApiGatewayUrl`

2. **Configurar webhook:**
   ```bash
   curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://tu-api-gateway-url.amazonaws.com/Prod/webhook"}'
   ```

3. **Verificar configuración:**
   ```bash
   curl -X GET "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
   ```

## 🧪 Testing

### Test Local
```bash
# Crear ambiente virtual
python3 -m venv env
source env/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar test
python3 test_lambda.py
```

### Test en AWS Lambda
- Ve a AWS Console → Lambda → `telegram-bot-giobot`
- Usa el event de test configurado
- Revisa CloudWatch Logs para debug

## 📁 Estructura del Proyecto

### Clean Architecture

```
lambda/
├── app.py                 # 🎯 Handler principal
├── domain/               # 🏛️ Capa de dominio
│   ├── entities.py      # Entidades de negocio
│   └── interfaces.py    # Contratos/Interfaces
├── use_cases/           # 📋 Casos de uso
│   └── process_message.py
├── adapters/            # 🔌 Adaptadores externos
│   ├── openai_adapter.py
│   ├── telegram_adapter.py
│   └── logger.py
└── infrastructure/      # ⚙️ Configuración
    ├── config.py
    └── parsers.py
```

### Flujo de Datos

```
Telegram → API Gateway → Lambda → OpenAI → Telegram
    ↓           ↓          ↓         ↓         ↓
 Webhook   HTTP Event  Process   AI Reply  Send Message
```

## 🛠️ Desarrollo

### Agregar Nueva Funcionalidad

1. **Crear caso de uso** en `use_cases/`
2. **Implementar adaptador** si necesitas servicio externo
3. **Actualizar handler** en `app.py`
4. **Push a main** para deploy automático

### Debugging

```bash
# Ver logs de CloudWatch
aws logs tail /aws/lambda/telegram-bot-giobot --follow

# Test local del handler
python3 -c "
from lambda.app import lambda_handler
event = {'body': '{\"message\": {\"text\": \"Hola\", \"chat\": {\"id\": 123}}}'}
print(lambda_handler(event, None))
"
```

## 🔧 Configuración Avanzada

### Personalizar OpenAI
Edita `lambda/adapters/openai_adapter.py`:

```python
# Cambiar modelo
self._model = "gpt-4"  # o "gpt-3.5-turbo"

# Ajustar parámetros
temperature=0.7,  # Creatividad (0-1)
max_tokens=500,   # Longitud de respuesta
```

### Configurar CloudFormation
Edita `infraestructure/cloudformation/template.yaml`:

```yaml
# Cambiar memoria/timeout
MemorySize: 512
Timeout: 30

# Agregar variables de entorno
Environment:
  Variables:
    CUSTOM_VAR: !Ref CustomParameter
```

## 🚨 Troubleshooting

### Errores Comunes

| Error | Solución |
|-------|----------|
| `No module named 'openai'` | Verificar que GitHub Actions instaló dependencias |
| `Webhook not set` | Ejecutar `setup_webhook.py` |
| `OpenAI API error` | Verificar `OPENAI_API_KEY` en secrets |
| `Telegram API error` | Verificar `TELEGRAM_BOT_TOKEN` |

### Logs y Monitoreo

```bash
# CloudWatch Logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/telegram-bot"

# Métricas de Lambda
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=telegram-bot-giobot
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch: `git checkout -b feature/amazing-feature`
3. Commit cambios: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🔗 Links Útiles

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**¿Necesitas ayuda?** 
- 🐛 [Reportar bug](https://github.com/giovany79/giobotlambdaaws2025/issues)
- 💬 [Discusiones](https://github.com/giovany79/giobotlambdaaws2025/discussions)
- 📧 Email: tu-email@ejemplo.com