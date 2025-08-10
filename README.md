# giobotlambdaaws2025

## Setup

0. Crear ambiente

    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

1. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```


2. Execute
   ```bash
   python3 lambda_function.py
   ```

3. Probar url telegram
   ```bash
   curl -X POST https://api.telegram.org/bot<TOKEN>/sendMessage -d chat_id=6299753048 -d text="Hello, World!"
   ```