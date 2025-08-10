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
    print(f"TOKEN: {TOKEN}")
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
            # Direct message format (for testing)
            print("Using direct message format for testing")
            body = event
            # Add a dummy update_id for testing
            body['update_id'] = 123456789
        else:
            print("No valid message format found")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No valid message format'})
            }
        
        # Validate Telegram webhook update
        if 'update_id' not in body:
            print("Invalid Telegram webhook update")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Invalid Telegram webhook update'})
            }
        
        # Extract message details
        message = body.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        user_message = message.get('text', '').strip()
        
        if not chat_id or not user_message:
            print("No valid chat ID or message text found")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No valid message to process'})
            }
        
        print(f"User: {chat_id}")
        print(f"Received Message: {user_message}")
        
        try:
            # Get response from OpenAI
            gpt_response = get_openai_response(user_message)
            print(f"GPT Response: {gpt_response}")
            
            # Send response to Telegram
            response_telegram = send_message(chat_id, gpt_response)
            
            if response_telegram.status_code != 200:
                print(f"Failed to send message to Telegram: {response_telegram.text}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'error': 'Failed to send response to Telegram',
                        'details': response_telegram.text
                    })
                }
                
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Message processed successfully',
                    'chat_id': chat_id
                })
            }
            
        except Exception as processing_error:
            error_message = f"Error processing message: {str(processing_error)}"
            print(error_message)
            
            # Send error message back to user
            send_message(chat_id, "Sorry, I encountered an error processing your request. Please try again later.")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': error_message
                })
            }
            
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to process message',
                'details': str(e)
            })
        }