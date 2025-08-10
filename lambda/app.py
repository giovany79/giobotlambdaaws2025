import json
import os
import time
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_openai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return "Sorry, I encountered an error processing your request. Please try again later."

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.post(url, params=params)
    return response

def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Handle different event formats
        if 'body' in event:
            # API Gateway format
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        elif 'message' in event:
            # Direct invocation format (Telegram webhook data directly)
            body = event
        else:
            print("No valid message format found")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No valid message format'})
            }
        
        # Check if it's a valid Telegram webhook
        if 'message' not in body:
            print("No 'message' key in body")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Webhook received but no message to process'})
            }
        
        # Extract chat ID and message text
        chat_id = body['message']['chat']['id']
        user_message = body['message'].get('text', '')
        
        if not user_message:
            print("No text message found")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No text message to process'})
            }
        
        print(f"User: {chat_id}")
        print(f"Received Message: {user_message}")
        
        # Get response from OpenAI
        gpt_response = get_openai_response(user_message)
        print(f"GPT Response: {gpt_response}")
        
        # Send response to Telegram
        response_telegram =send_message(chat_id, gpt_response)
        print(f"Telegram Response: {response_telegram}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Message processed successfully',
                'chat_id': chat_id
            })
        }
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to process message',
                'details': str(e)
            })
        }