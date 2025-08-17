# 🤖 Telegram Bot con AWS Lambda y OpenAI

Bot de Telegram inteligente que usa **OpenAI GPT** para responder mensajes, desplegado en **AWS Lambda**.

## 🏗️ Estructura del Proyecto

```
📦 giobotlambdaaws2025
├── � app.py            # Código principal de la función Lambda
├── � requirements.txt  # Dependencias de Python
├── 📄 .env             # Variables de entorno (crear a partir de .env.example)
└── � README.md        # Este archivo
```

## ✨ Características

- 🧠 **Integración con OpenAI GPT** - Respuestas inteligentes
- ⚡ **AWS Lambda** - Serverless, escalable y económico
- 🚀 **Fácil de desplegar** - Código mínimo, configuración sencilla
- 🔐 **Gestión de Secrets** - Variables de entorno seguras
- 🤖 **Webhook de Telegram** - Comunicación en tiempo real

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
```

## 🏃‍♂️ Ejecución Local

Para probar localmente:

```bash
python app.py
```

Esto ejecutará una prueba con un mensaje de ejemplo.

## ☁️ Despliegue en AWS Lambda

1. **Crear un archivo ZIP** con las dependencias:

```bash
# Instalar dependencias en carpeta package
pip install -r requirements.txt -t ./package

# Crear ZIP
cd package
zip -r ../function.zip .
cd ..
zip -g function.zip app.py
```

2. **Subir a AWS Lambda**:
   - Ve a la consola de AWS Lambda
   - Crea una nueva función
   - Sube el archivo `function.zip`
   - Configura el handler como `app.lambda_handler`
   - Establece las variables de entorno del archivo `.env`

3. **Configurar API Gateway**:
   - Crea una nueva API REST
   - Crea un recurso y un método POST
   - Configúralo para que apunte a tu función Lambda
   - Configura el webhook de Telegram con la URL de tu API Gateway

## 🤖 Uso

Simplemente envía un mensaje a tu bot de Telegram y recibirás una respuesta generada por IA.

## 📝 Comandos de Seguimiento de Movimientos

### Agregar un Nuevo Movimiento
```
agregar <descripción>;<tipo>;<monto>;<categoría>[;fecha]
```

**Ejemplos:**
```
agregar Salario;ingreso;3000000;salario
agregar Supermercado;gasto;350000;comida;2025-01-15
agregar Transporte;gasto;25000;transporte
```

### Ver Movimientos
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

---

**¿Necesitas ayuda?** 
- 🐛 [Reportar un problema](https://github.com/giovany79/giobotlambdaaws2025/issues)
- 💬 [Discusiones](https://github.com/giovany79/giobotlambdaaws2025/discussions)
- 📧 Contacto: [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com)