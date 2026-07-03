import asyncio
import datetime
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ChatAction
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.client.default import DefaultBotProperties

from dify import send_to_d
from config import BOT_TOKEN
from storage import load_data, save_data

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
router = Router()

data = load_data()

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            'conversation_id': '',
            'history': []
        }
    return data[user_id]

chat_ik_mu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Хороший ответ', callback_data='good_score'),
            InlineKeyboardButton(text='Плохой ответ', callback_data='bad_score')
        ]
    ]
)

main_kb_mu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='💬 Новый чат')],
        [KeyboardButton(text='📋 История чата'), KeyboardButton(text='🧹 Очистить историю')]
    ], resize_keyboard=True, is_persistent=True, one_time_keyboard=False
)

@router.message(CommandStart())
async def start(message: Message):
    text = (
        f'👋 <b>Добро пожаловать, {message.from_user.username or "пользователь"}!</b>\n'
        f'<b>Я ваш ИИ ассистент по медицине</b>\n'
        f'<b>Можете задавать любые вопросы</b>'
    )
    user = get_user(message.from_user.id)
    user['conversation_id'] = ''
    user['history'] = []
    save_data(data)
    await message.answer(text, reply_markup=main_kb_mu)


@router.message(Command('help'))
async def cmd_help(message: Message):
    text = (
        f'<b>Список доступных команд </b>\n'
        f'<b>/start - приветствие</b>\n'
        f'<b>/help - сводка доступных команд</b>\n'
        f'<b>/about - информация о боте</b>\n'
        f'<b>/new - начать новый диалог</b>\n'
        f'<b>/history - показать историю диалога</b>\n'
        f'<b>/clear - очистить историю диалога</b>'
    )
    await message.answer(text)


@router.message(Command('about'))
async def about_message(message: Message):
    text = ("🤖 AI Medicine Assistant\n"
            "Разработан на:\n"
            "• Python\n"
            "• Aiogram\n"
            "• Dify\n"
            )
    await message.answer(text)


@router.message(Command('new'))
@router.message(F.text == '💬 Новый чат')
async def cmd_new(message: Message):
    user = get_user(message.from_user.id)
    user['history'] = []
    save_data(data)
    await message.answer('ℹ️ <b>Начался новый чат</b>')


@router.message(Command('history'))
@router.message(F.text == '📋 История чата')
async def cmd_history(message: Message):
    user = get_user(message.from_user.id)
    history = user['history']
    if not history:
        await message.answer('⚠️ <b>История запросов пуста</b>')
        return

    text = '📜 <b>История вашего диалога:</b>\n\n'
    for i in history:
        score_text = f"\nОценка: {i['score']}" if 'score' in i else ""
        text += f'👤 <b>Вы:</b> {i["query"]}\n🤖 <b>ИИ:\n</b> {i["answer"]}\n{score_text}\n\n'

    await message.answer(text)


@router.message(Command('clear'))
@router.message(F.text == '🧹 Очистить историю')
async def cmd_clear(message: Message):
    user = get_user(message.from_user.id)
    user['conversation_id'] = ''
    if not user['history']:
        await message.answer('⚠️ <b>История запросов пуста</b>')
        return

    user['history'] = []
    save_data(data)
    await message.answer('✅ <b>История запросов очищена</b>')


@router.message(F.text)
async def chat(message: Message):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    conversation_id = user['conversation_id']
    text = message.text

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    result = await send_to_d(text, user_id, conversation_id)
    if not result['success']:
        await message.answer(result['text'])
        return

    current_time = datetime.datetime.now().strftime('Date: %d.%m.%Y Time: %H-%M')
    if len(user['history']) < 50:
        user['history'].append({
            'query': text,
            'answer': result['text'],
            'time': current_time
        })
        save_data(data)
    else:
        pass

    user['conversation_id'] = result.get('conversation_id', conversation_id)
    await message.answer(result['text'], reply_markup=chat_ik_mu)


@router.callback_query(F.data == 'good_score')
async def good_score(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    user['history'][-1]['score'] = 'Хороший ответ'
    save_data(data)

    await callback.message.edit_text(f"{callback.message.text}\n\nℹ️ <b>Оценка сохранена</b>")


@router.callback_query(F.data == 'bad_score')
async def bad_score(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    user['history'][-1]['score'] = 'Плохой ответ'
    save_data(data)

    await callback.message.edit_text(f"{callback.message.text}\n\nℹ️ <b>Оценка сохранена</b>")


@router.message(F.file)
async def handle_document(message: Message):
    await message.answer("📄 Пока файлы не поддерживаются.")

@router.message(F.voice)
async def handle_voice(message: Message):
    await message.answer("🎤 Голосовые сообщения пока не поддерживаются.")

@router.message(F.video)
async def handle_video(message: Message):
    await message.answer("🎥 Видео пока не поддерживаются.")

@router.message(F.animation)
async def handle_animation(message: Message):
    await message.answer("🎞 GIF-анимации пока не поддерживаются.")

@router.message(F.sticker)
async def handle_animation(message: Message):
    await message.answer("😃 Спасибо за стикер")

async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_router(router)
    print('Bot is polling')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())