from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

import buttons as kb 

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

@router.message(F.text.lower() == "Кто автор бота?")
async def aftor_info(message: Message):
    await message.reply("Автором бота является: zadrot (Alan)")

@router.message(F.text.lower() == "📋faq")
async def faq_comand(message: Message):
    await message.answer(FAQ_TEXT, parse_mode="HTML")

@router.message(F.text == "📝Заметки")
async def handle_notes(message: Message):
    await message.answer("Вы открыли раздел 📝Заметки. Здесь пока пусто. Мы создаем бота")

@router.message(F.text == "💲Долги")
async def handle_duty(message: Message):
    await message.answer("Вы открыли раздел 💲Долги. Здесь пока пусто. Мы создаем бота")

@router.message(F.text == "🎂Дни рождения")
async def handle_birthday(message: Message):
    await message.answer("Вы открыли раздел 🎂Дни рождения. Здесь пока пусто. Мы создаем бота")

@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f"ID фото: <code>{message.photo[-1].file_id}</code>", parse_mode="HTML")

@router.message(F.sticker)
async def get_sticker_id(message: Message):
    await message.answer(f"ID стикера: <code>{message.sticker.file_id}</code>", parse_mode="HTML")
