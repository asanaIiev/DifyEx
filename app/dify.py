import aiohttp
import logging
from config import API_URL, API_KEY

async def send_to_d(query: str, user_id: str, conversation_id: str) -> dict:

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
                        'text': result.get('answer', '⚠️ Пустой ответ от сервера.'),
                        'conversation_id': result.get('conversation_id', '')
                    }
                elif response.status == 401:
                    logging.error("Dify API Error: Неверный API KEY (Unauthorized).")
                    return {'success': False, 'text': '⚠️ Ошибка авторизации: Неверный API-ключ сервиса.'}
                elif response.status == 404:
                    logging.error("Dify API Error: Неверный URL (Not Found).")
                    return {'success': False, 'text': '⚠️ Ошибка подключения: Неверный адрес API.'}
                else:
                    error_body = await response.text()
                    logging.error(f"Dify API Error {response.status}: {error_body}")
                    return {'success': False, 'text': f'⚠️ Ошибка сервера Dify (Код {response.status}).'}

    except aiohttp.ClientConnectorError:
        logging.error("Dify API Error: Отсутствует интернет или сервер недоступен.")
        return {'success': False, 'text': '🌐 Нет подключения к интернету или сервер Dify недоступен.'}
    except Exception as e:
        logging.error(f"Dify API Unknown Error: {e}")
        return {'success': False, 'text': '❌ Произошла неизвестная ошибка при считывании ответа.'}