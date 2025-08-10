import json
from typing import Optional, Dict, Any

from domain.entities import TelegramUpdate, Message, ChatId


class TelegramEventParser:
    @staticmethod
    def parse(event: Dict[str, Any]) -> Optional[TelegramUpdate]:
        try:
            body = TelegramEventParser._extract_body(event)
            if not body:
                return None
            
            update_id = body.get('update_id')
            if not update_id:
                return None
            
            message_data = body.get('message', {})
            if not message_data:
                return TelegramUpdate(update_id=update_id)
            
            chat_data = message_data.get('chat', {})
            chat_id = chat_data.get('id')
            text = message_data.get('text', '').strip()
            
            if not chat_id or not text:
                return TelegramUpdate(update_id=update_id)
            
            message = Message(
                text=text,
                chat_id=ChatId(value=chat_id)
            )
            
            return TelegramUpdate(update_id=update_id, message=message)
            
        except Exception:
            return None
    
    @staticmethod
    def _extract_body(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                return json.loads(body)
            return body
        elif 'message' in event:
            body = event.copy()
            body['update_id'] = body.get('update_id', 123456789)
            return body
        return None