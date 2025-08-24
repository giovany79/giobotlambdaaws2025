# 🤖 Telegram Bot con AWS Lambda y OpenAI

Bot de Telegram inteligente que usa **OpenAI GPT** para responder mensajes y gestionar finanzas personales, desplegado en **AWS Lambda**.

## 🏗️ Estructura del Proyecto

```
📦 giobotlambdaaws2025
├── 📁 .github/workflows/  # GitHub Actions workflows
│   └── deploy.yml        # Configuración de despliegue automático
├── 📁 handlers/           # Manejadores de eventos
│   ├── __init__.py
│   └── telegram_handler.py
├── 📁 infraestructure/    # Infraestructura como código
│   └── cloudformation/
│       └── template.yaml # Plantilla de CloudFormation
├── 📁 services/           # Servicios y lógica de negocio
│   ├── __init__.py
│   ├── csv_client.py     # Manejo de archivos CSV
│   ├── movements.csv     # Base de datos de movimientos
│   ├── openai_client.py  # Cliente de OpenAI
│   ├── operations_client.py  # Lógica de operaciones
│   └── operations.json   # Configuración de operaciones
├── 📄 .env.example       # Ejemplo de variables de entorno
├── 📄 .gitignore
├── 📄 app.py             # Punto de entrada de Lambda
├── 📄 README.md          # Este archivo
└── 📄 requirements.txt   # Dependencias de Python
```

## ✨ Características

- 🧠 **Integración con OpenAI GPT** - Respuestas inteligentes y procesamiento de lenguaje natural
- 💰 **Gestión de Finanzas** - Seguimiento de ingresos y gastos
- ⚡ **AWS Lambda** - Serverless, escalable y económico
- 🚀 **CI/CD** - Despliegue automático con GitHub Actions
- 🔐 **Gestión de Secrets** - Variables de entorno seguras
- 🤖 **Webhook de Telegram** - Comunicación en tiempo real
- 📊 **Reportes** - Visualización de movimientos financieros

## 🚀 Configuración Rápida

### 1. Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/giovany79/giobotlambdaaws2025.git
cd giobotlambdaaws2025

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
```

### 2. Configurar Variables de Entorno

Edita `.env` con tus credenciales:

```bash
# Token de tu bot de Telegram (obtener de @BotFather)
TELEGRAM_BOT_TOKEN=tu_token_aqui

# API Key de OpenAI (obtener de platform.openai.com)
OPENAI_API_KEY=tu_api_key_aqui

# Configuración de la aplicación
LOG_LEVEL=INFO
```

## 🏃‍♂️ Ejecución Local

Para probar localmente:

```bash
python test_lambda.py
```

O para ejecutar directamente la aplicación:

```bash
python app.py
```

## 🧪 Pruebas

El proyecto incluye pruebas unitarias. Para ejecutarlas:

```bash
python -m pytest tests/
```

## ☁️ Despliegue en AWS

### Despliegue Automático con GitHub Actions

1. Configura los siguientes secretos en tu repositorio de GitHub:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`

2. El workflow de GitHub Actions se encargará automáticamente del despliegue cuando hagas push a la rama `main`.

### Despliegue Manual

1. **Empaqueta la aplicación**:
   ```bash
   # Instalar dependencias
   pip install -r requirements.txt -t ./package
   
   # Crear ZIP
   cd package
   zip -r ../function.zip .
   cd ..
   zip -g function.zip app.py handlers/*.py services/*.py
   ```

2. **Despliega en AWS Lambda** usando AWS CLI o la consola web.

3. **Configura el webhook de Telegram** para que apunte a tu función Lambda a través de API Gateway.'

check webhook
curl "https://api.telegram.org/bot8434484264:AAEB3LyDPqyexF5gdFLffRyzzO8NVDRO9jY/getWebhookInfo"

delete webhook
curl -X POST "https://api.telegram.org/bot8434484264:AAEB3LyDPqyexF5gdFLffRyzzO8NVDRO9jY/deleteWebhook"

Configure webhook
curl -X POST "https://api.telegram.org/bot8434484264:AAEB3LyDPqyexF5gdFLffRyzzO8NVDRO9jY/setWebhook" \
-H "Content-Type: application/json" \
-d '{"url": "https://ykhl1jughk.execute-api.us-east-1.amazonaws.com/Prod/webhook", "drop_pending_updates": true}'



## 🤖 Comandos Disponibles

### Gestión de Finanzas

#### Agregar un Nuevo Movimiento
```
agregar <descripción>;<tipo>;<monto>;<categoría>[;fecha]
```

**Ejemplos:**
```
agregar Salario;ingreso;3000000;salario
agregar Supermercado;gasto;350000;comida;2025-01-15
agregar Transporte;gasto;25000;transporte
```

#### Ver Movimientos
```
ver [filtros]
```

**Filtros disponibles:**
- `ultimos N`: Muestra los últimos N días
- `tipo:ingreso/gasto`: Filtra por tipo
- `categoria:nombre`: Filtra por categoría

**Ejemplos:**
```
ver
ver ultimos 7
ver categoria:comida
```

### Asistente de IA

Puedes hacer preguntas generales o pedir análisis de tus finanzas:
```
¿Cuánto he gastado en comida este mes?
¿Cuáles son mis ingresos mensuales promedio?
Dame un resumen de mis finanzas
```

## 🤝 Contribuir

1. Haz un fork del proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Haz commit de tus cambios: `git commit -m 'Añadir nueva funcionalidad'`
4. Sube tus cambios: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para más detalles.

## 🔗 Enlaces Útiles

- [Documentación de la API de Telegram](https://core.telegram.org/bots/api)
- [Documentación de la API de OpenAI](https://platform.openai.com/docs)
- [Documentación de AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Documentación de AWS CloudFormation](https://docs.aws.amazon.com/cloudformation/)

---

**¿Necesitas ayuda?** 
- 🐛 [Reportar un problema](https://github.com/giovany79/giobotlambdaaws2025/issues)
- 💬 [Discusiones](https://github.com/giovany79/giobotlambdaaws2025/discussions)
- 📧 Contacto: [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com)