from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio

# Ваш токен бота
TOKEN = "7794188376:AAGzakyD3zix2lM2_CDytUYROl_Duqph2zE"

# ID администраторов
ADMIN_CHAT_IDS = [7053559428, 1809630966, 6631198858, 7326115641]

# FSM состояния
class Form(StatesGroup):
    CHOOSING = State()
    TROLL = State()
    SNOSER = State()
    VOICER = State()
    DOXER = State()
    SWATTER = State()

# Создаём бот и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Хендлер на старт
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Тролль-Хаудер", callback_data="role_troll")],
        [InlineKeyboardButton(text="Сносер", callback_data="role_snoser")],
        [InlineKeyboardButton(text="Войсер", callback_data="role_voicer")],
        [InlineKeyboardButton(text="Доксер", callback_data="role_doxer")],
        [InlineKeyboardButton(text="Сватер", callback_data="role_swatter")],
    ])
    await message.answer("Привет! Выберите свою роль для заполнения анкеты:", reply_markup=keyboard)
    await state.set_state(Form.CHOOSING)

# Обработчик выбора роли
@dp.callback_query(lambda c: c.data.startswith("role_"))
async def role_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    role = callback_query.data.split("_")[1]
    await state.update_data(role=role)

    # Сообщения для каждой роли
    role_messages = {
        "troll": "1) Сколько находишься в данной сфере?\n"
                 "2) Сколько ВПМ - какой объем?\n"
                 "3) Сколько готов уделять времени для организации?",
        "snoser": "1) Сколько почт - сессий?\n"
                  "2) Сколько вьебов свинорыльников?",
        "voicer": "Требования:\n- Нормальный микрофон.\n- Говорить внятно.\nЕсли подходите, напишите свою анкету.",
        "doxer": "Требования:\n- Хорошие базы данных.\nЕсли подходите, напишите свою анкету.",
        "swatter": "Требования:\n1) Хороший микрофон.\n2) Говорить внятно и ясно.\n3) Соблюдать анонимность.\nЕсли подходите, напишите свою анкету."
    }

    await callback_query.message.edit_text(role_messages.get(role, "Неизвестная роль."))
    await state.set_state(getattr(Form, role.upper()))
    await callback_query.answer()

# Обработчик анкеты
@dp.message()
async def handle_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data.get("role")
    user = message.from_user

    # Формируем сообщение для администраторов
    admin_message = (
        f"Новая анкета!\n"
        f"Роль: {role}\n"
        f"Отправитель: {user.full_name} (@{user.username})\n"
        f"Сообщение: {message.text}"
    )

    # Отправляем администраторам
    for admin_id in ADMIN_CHAT_IDS:
        await bot.send_message(chat_id=admin_id, text=admin_message)

    await message.answer("Спасибо! Ваша анкета отправлена на рассмотрение.")
    await state.clear()

# Добавление администратора
@dp.message(Command("add_admin"))
async def add_admin(message: types.Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply("Используйте команду в формате: /add_admin <chat_id>")
        return

    chat_id = int(args[1])
    if chat_id not in ADMIN_CHAT_IDS:
        ADMIN_CHAT_IDS.append(chat_id)
        await message.reply(f"Чат ID {chat_id} добавлен в список администраторов.")
    else:
        await message.reply("Этот чат ID уже добавлен.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
