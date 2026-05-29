from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
import buttons as kb
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from database import Database
from aiogram.utils.keyboard import InlineKeyboardBuilder

class DebtStates(StatesGroup):
    waiting_for_name = State()      
    waiting_for_amount = State()       
    waiting_to_increase = State()      
    waiting_to_decrease = State()      
router = Router()
FAQ_TEXT = """
📋 <b>Часто задаваемые вопросы (FAQ)</b>

<b>🔒 Безопасность и данные</b>
▸ Кто видит мои записи? — Никто, данные привязаны строго к твоему Telegram ID.
▸ Бот сохраняет пароли? — Нет, бот хранит только то, что ты сам запишешь.

<b>📝 Заметки и лимиты</b>
▸ Сколько заметок можно создать? — Сколько угодно, ограничений на объем нет.
▸ Текст может быть огромным? — Да, бот спокойно сохранит длинный текст.

<b>💲 Учет долгов</b>
▸ В какой валюте вести учет? — В любой (рубли, доллары, евро), бот запомнит любой твой ввод.
▸ Можно ли менять сумму долга? — Да, через карточку должника можно увеличивать или уменьшать сумму.

<b>🤖 Технические вопросы</b>
▸ Бот завис и не отвечает? — Просто отправь команду /start заново, это перезапустит меню.
▸ Кто создал бота? — Проект разработан автором: zadrot💎
"""

@router.message(F.text == "💲Долги")
async def handle_duty(message: Message, db: Database):
    debts = await db.get_debt(user_id=message.from_user.id)
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text='➕Добавить должника',
        callback_data='add_new_debt'
    ))

    if not debts:
        await message.answer(
            "💲 <b>Раздел: Долги</b>\n\n📭 Список должников пока пуст.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
            )
    else:
        await message.answer(
            "У вас есть сохраненные долги!",
            reply_markup=builder.as_markup()
        )
@router.callback_query(F.data == 'add_new_debt')
async def start_add_debt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("👤Введите имя должника: ")
    await state.set_state(DebtStates.waiting_for_name)
    await callback.answer() 


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n"
        "Добро пожаловать в NoteVault — твое личное цифровое хранилище🌐.\n\n"
        "Что я умею делать:\n"
        "📝 Сохранять быстрые заметки\n"
        "💲 Вести точный учет долгов\n"
        "🥳 Запоминать важные дни рождения",
        reply_markup=kb.get_main_keyboard() 
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply("Я умею повторять твои сообщения! Просто отправь мне текст.")

@router.message(F.text.lower() == "кто автор бота?")
async def aftor_info(message: Message):
    await message.reply("Автором бота является: zadrot (Alan)")

@router.message(F.text.lower() == "📋faq")
async def faq_comand(message: Message):
    await message.answer(FAQ_TEXT, parse_mode="HTML")

@router.message(F.text == "📝Заметки")
async def handle_notes(message: Message):
    await message.answer("Вы открыли раздел 📝Заметки. На данных момент мы создаем вкладку 💲Долги")

@router.message(F.text == "🎂Дни рождения")
async def handle_birthday(message: Message):
    await message.answer("Вы открыли раздел 🎂Дни рождения. На данных момент мы создаем вкладку 💲Долги")

@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f"ID фото: <code>{message.photo[-1].file_id}</code>", parse_mode="HTML")

@router.message(F.sticker)
async def get_sticker_id(message: Message):
    await message.answer(f"ID стикера: <code>{message.sticker.file_id}</code>", parse_mode="HTML")
