import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import os

from test_llm_dialog import get_answer


API_TOKEN = os.environ["API_TOKEN"]
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Словарь для хранения токенов пользователей (вместо базы данных) TODO
user_tokens = {}

# Словарь для хранения истории пользователя (вместо базы данных) TODO
users_history = dict()

# Функция проверки токена в базе данных
def is_valid_token(token):
    # Здесь должна быть логика проверки токена в базе данных
    valid_tokens = ["valid_token1", "valid_token2", "pops"]  # Пример списка действительных токенов
    return token in valid_tokens

# Определяем состояния
class Form(StatesGroup):
    awaiting_token = State()
    chatting = State()

# Команда /start
@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    welcome_text = ("Привет! Я бот, работающий с нейронной сетью.\n"
                    "У вас есть токен для общения с моделью?")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Yes", callback_data="has_token_yes"))
    keyboard.add(InlineKeyboardButton("No", callback_data="has_token_no"))
    await message.reply(welcome_text, reply_markup=keyboard)
    await state.finish()

# Обработка нажатия кнопки Yes
@dp.callback_query_handler(lambda c: c.data == 'has_token_yes', state='*')
async def process_callback_token_yes(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите ваш токен:")
    await Form.awaiting_token.set()

# Обработка нажатия кнопки No
@dp.callback_query_handler(lambda c: c.data == 'has_token_no', state='*')
async def process_callback_token_no(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    instruction_text = ("Чтобы получить токен, перейдите на сайт и зарегистрируйтесь.\n"
                        "После этого введите полученный токен здесь.")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Перейти на сайт", url="https://example.com"))
    await bot.send_message(callback_query.from_user.id, instruction_text, reply_markup=keyboard)
    await state.finish()

# Обработка ввода токена пользователем
@dp.message_handler(state=Form.awaiting_token)
async def handle_token_input(message: types.Message, state: FSMContext):
    token = message.text
    if is_valid_token(token):
        # Очищаем историю пользователя так как общение остановлено TODO
        users_history[message.chat.id] = ""
        user_tokens[message.chat.id] = token
        await message.reply("Токен сохранен. Теперь вы можете начать общение с моделью.")
        await Form.chatting.set()
    else:
        instruction_text = ("Недействительный токен. Пожалуйста, посетите сайт, чтобы получить действительный токен.")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Перейти на сайт", url="https://example.com"))
        await message.reply(instruction_text, reply_markup=keyboard)
        await state.finish()

# Команда /token для смены модели
@dp.message_handler(commands=['token'], state='*')
async def change_token(message: types.Message, state: FSMContext):
    await message.reply("Введите новый токен:")
    await Form.awaiting_token.set()

# Команда /stop для остановки общения
@dp.message_handler(commands=['stop'], state='*')
async def stop_communication(message: types.Message, state: FSMContext):
    if message.chat.id in user_tokens:
        del user_tokens[message.chat.id]
        # Очищаем историю пользователя так как общение остановлено TODO
        users_history[message.chat.id] = ""
    await message.reply("Общение остановлено.")
    await state.finish()

# Обработка всех других сообщений (начало общения с моделью)
@dp.message_handler(state=Form.chatting) # Тут историю надо сделать с помощью db TODO
async def chat_with_model(message: types.Message, state: FSMContext):
    token = user_tokens[message.chat.id]
    # Здесь должна быть логика общения с моделью, использующей токен
    # Здесь я делаю историю пользователя пустой если юзер ранее не общался
    if message.chat.id not in users_history:
        users_history[message.chat.id] = ""
    
    # из test_llm_dialog.py используем функцию get_answer для вывода ответа и получения обновленной истории
    answer, history = get_answer(users_history[message.chat.id], message.text)
    # обновляем историю пользователя
    users_history[message.chat.id] = history

    # Отправляем ответ пользователю
    #response = f"Ваше сообщение: {message.text}\n(Ответ модели: {answer})"
    response = answer
    await message.reply(response)
 
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)