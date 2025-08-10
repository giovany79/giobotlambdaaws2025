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
   curl -X GET https://api.telegram.org/bot8434484264:AAEB3LyDPqyexF5gdFLffRyzzO8NVDRO9jY/getUpdates
   ```