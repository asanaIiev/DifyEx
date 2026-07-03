import aiohttp
import logging
from config import API_URL, API_KEY

async def send_to_d(query: str, user_id: str, conversation_id: str):

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'inputs': {},
        'query': query,
        'user': user_id,
        'conversation_id': conversation_id
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=data, timeout=30) as response:
                if response.status in (200, 201):
                    result = await response.json()
                    return {
                        'success': True,
                        'text': result.get('answer', ''),
                        'conversation_id': result.get('conversation_id', '')
                    }

    except Exception as e:
        logging.error(f"Error {e}")
        return {
            'success': False,
            'text': result['text'],
            'conversation_id': conversation_id
        }