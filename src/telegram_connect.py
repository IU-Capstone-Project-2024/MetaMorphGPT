import logging
import psycopg2
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import os
from dotenv import load_dotenv
from google_drive_connection_2 import get_drive_service, try_get_model, get_folder_id

from test_llm_dialog import get_answer

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токенов и параметров подключения к базе данных из переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Функция для получения соединения с базой данных
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Определение состояний для Finite State Machine (FSM)
class Form(StatesGroup):
    awaiting_token = State()
    chatting = State()

# Функция для получения текущего токена пользователя
def get_token(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT current_token FROM chat WHERE user_id = %s', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Функция для проверки валидности токена
def is_valid_token(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM user_models WHERE token = %s', (token,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Функция для сохранения истории чата пользователя
def save_history(user_id, history):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE chat SET history = %s WHERE user_id = %s', (history, user_id))
    conn.commit()
    conn.close()

# Функция для получения истории чата пользователя
def get_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT history FROM chat WHERE user_id = %s', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else ""

# Функция для удаления истории чата пользователя
def delete_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE chat SET history = %s WHERE user_id = %s', ("", user_id))
    conn.commit()
    conn.close()

# Обработчик команды /start
@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    welcome_text = ("Hi! I'm a neural network bot.\n"
 "Do you have a token to communicate with the model?")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Yes", callback_data="has_token_yes"))
    keyboard.add(InlineKeyboardButton("No", callback_data="has_token_no"))
    await message.reply(welcome_text, reply_markup=keyboard)
    await state.finish()

# Обработчик нажатия кнопки Yes
@dp.callback_query_handler(lambda c: c.data == 'has_token_yes', state='*')
async def process_callback_token_yes(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Please, enter your token")
    await Form.awaiting_token.set()

# Обработчик нажатия кнопки No
@dp.callback_query_handler(lambda c: c.data == 'has_token_no', state='*')
async def process_callback_token_no(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    instruction_text = ("To get a token, go to the website and register.\n"
 "Then enter the received token here.")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Go to website ->", url="https://example.com"))
    await bot.send_message(callback_query.from_user.id, instruction_text, reply_markup=keyboard)
    await state.finish()

# Обработчик ввода токена
@dp.message_handler(state=Form.awaiting_token)
async def process_token(message: types.Message, state: FSMContext):
    token = message.text.strip()
    if is_valid_token(token):
        user_id = message.from_user.id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO chat (user_id, history, current_token) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (user_id) 
            DO UPDATE SET history = EXCLUDED.history, current_token = EXCLUDED.current_token
            ''',
            (user_id, '', token)
        )

        conn.commit()
        conn.close()
        try_get_model(drive, models_folder_id, token)
        await message.reply("Token accepted. You can now start chat.")
        await Form.chatting.set()
    else:
        await message.reply("Invalid token. Please try again.")

@dp.message_handler(commands=['token'], state='*')
async def change_token(message: types.Message, state: FSMContext):
    user_id = message.chat.id  # Получаем user_id пользователя Telegram
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Выполняем SQL-запрос для очистки колонок history и current_token
        cursor.execute(
            '''
            UPDATE chat 
            SET history = '' 
            WHERE user_id = %s
            ''',
            (user_id,)
        )
        conn.commit()  # Подтверждаем изменения в базе данных
        conn.close()
        
        await message.reply("Сommunication has stopped")  # Отправляем сообщение пользователю
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
        await state.finish()
    await message.reply("Enter a new token:")
    await Form.awaiting_token.set()

# Обработчик команды /stop
@dp.message_handler(commands=['stop'], state='*')
async def stop_communication(message: types.Message, state: FSMContext):
    user_id = message.chat.id  # Получаем user_id пользователя Telegram
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Выполняем SQL-запрос для очистки колонок history и current_token
        cursor.execute(
            '''
            UPDATE chat 
            SET history = '' 
            WHERE user_id = %s
            ''',
            (user_id,)
        )
        conn.commit()  # Подтверждаем изменения в базе данных
        conn.close()
        
        await message.reply("Communication has stopped.")  # Отправляем сообщение пользователю
        await state.finish()  # Завершаем состояние FSM (Finite State Machine)
    except Exception as e:
        await message.reply(f"An error occured: {e}")
        await state.finish()


# Обработчик сообщений в чате
@dp.message_handler(state=Form.chatting)
async def chat(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_message = message.text.strip()
    history = get_history(user_id)
    print(history)
    print("-----------------------")
    current_token = get_token(user_id)
    
    if current_token:
        model_path = f"models/{current_token}"
        try_get_model(drive, models_folder_id, current_token)
        response, new_history = get_answer(history, user_message, model_path)
        print(response)
        print("-----------------------")
        print(new_history)
        print("-----------------------")
        
        # Обновление истории в базе данных
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE chat
            SET history = %s
            WHERE user_id = %s
        ''', (new_history, user_id))
        conn.commit()
        conn.close()
        
        await message.reply(response)
    else:
        await message.reply("Token not found. Please start again with /start.")
        await state.finish()

if __name__ == '__main__':
    drive = get_drive_service()
    models_folder_name = "models"
    models_folder_id = get_folder_id(drive, models_folder_name)
    executor.start_polling(dp, skip_updates=True)