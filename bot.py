import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔑 Токены (лучше хранить в .env, но для примера оставим переменные)
TELEGRAM_TOKEN = "ВАШ_TELEGRAM_TOKEN"
COMET_KEY = "ВАШ_COMET_KEY"

# 🔗 CometAPI endpoint (OpenAI-совместимый)
API_URL = "https://api.cometapi.com/v1/chat/completions"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# --- Память: словарь {user_id: [список сообщений]} ---
memory = {}

# --- Хэндлер /start ---
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_firstname = message.from_user.first_name

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            "💈 Записаться на стрижку",
            url="https://dikidi.net/503865"
        )
    )
    await message.answer(
        f"Привет, {user_firstname}! 👋\nХочешь записаться на стрижку?",
        reply_markup=keyboard
    )

# --- Функция запроса к CometAPI ---
def query(user_id, user_text):
    history = memory.get(user_id, [])
    history.append({"role": "user", "content": user_text})
    history = history[-10:]

    headers = {"Authorization": f"Bearer {COMET_KEY}"}
    payload = {"model": "deepseek-chat", "messages": history}

    response = requests.post(API_URL, headers=headers, json=payload, 
timeout=30)
    if response.status_code != 200:
        return f"Ошибка {response.status_code}: {response.text}"

    data = response.json()
    answer = data["choices"][0]["message"]["content"]

    history.append({"role": "assistant", "content": answer})
    memory[user_id] = history

    return answer

# --- Хэндлер любых сообщений ---
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text.strip()

    result = query(user_id, user_text)
    await message.answer(result)

# --- Запуск бота ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

