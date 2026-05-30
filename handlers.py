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
    if not debts:
        builder.add(InlineKeyboardButton(text='➕ Добавить должника', callback_data='add_new_debt'))
        await message.answer(
            "💲 <b>Раздел: Долги</b>\n\n📭 Список должников пока пуст.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
            )
    else:
        text_answer = "💲 <b>Ваш список долгов:</b>\n\n"
        for row in debts:
            text_answer += f"<b>{row['person_name']}</b>: <code>{row['amount']}</code>₽\n"
            builder.add(InlineKeyboardButton(
                text = f"👤{row['person_name']}",
                callback_data=f"manage_debt_{row['debt_id']}"
            ))  

        builder.add(InlineKeyboardButton(text='➕ Добавить должника', callback_data='add_new_debt'))
        builder.adjust(1) 
        await message.answer(
            text_answer,
            reply_markup=builder.as_markup(),
            parse_mode='HTML'
        )

@router.callback_query(F.data.startswith('manage_debt_'))
async def open_debt_card(callback: CallbackQuery, db: Database):
    debt_id = int(callback.data.split('_')[-1])
    card_builder = InlineKeyboardBuilder()

    card_builder.add(
        InlineKeyboardButton(text='📈Увеличить сумму', callback_data=f"inc_debt_{debt_id}"),
        InlineKeyboardButton(text='📉Уменьшить сумму', callback_data=f"dec_debt_{debt_id}"),
        InlineKeyboardButton(text='❌Удаление пользователя', callback_data=f"del_debt_{debt_id}")
    )
    card_builder.adjust(2, 1) 

    await callback.message.edit_text(
        f"⚙️ <b>Управление должником</b>\n\n"
        f"Вы выбрали запись с ID: <code>{debt_id}</code>\n"
        f"Здесь мы сделаем кнопки увеличения, уменьшения и удаления!",
        reply_markup=card_builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith('del_debt_'))
async def process_delete_debt(callback: CallbackQuery, db: Database):
    debt_id = int(callback.data.split('_')[-1])
    succes = await db.delete_debt(debt_id=debt_id, user_id=callback.from_user.id)
    if succes:
        await callback.message.edit_text(
            "<b>🗑️Пользователь успешно удален</b>\n\n"
            "✅Этого должника больше нету в вашей базе данных",
            parse_mode='HTML'
        )
    else:
        await callback.message.edit_text(
            "❌<b>Ошибка! Не удалось найти или удалить эту запись.</b>",
            parse_mode='HTML'
        )
    await callback.answer()
@router.callback_query(F.data.startswith('inc_debt_'))
async def process_more_debt(callback: CallbackQuery, state: FSMContext):
    debt_id = int(callback.data.split('_')[-1])
    await state.update_data(current_debt_id = debt_id)
    await callback.message.edit_text(
        "📈<b>Увелечение суммы долга</b>\n\n"
        "Введите сумму цифрами, которую хотите <b>ДОБАВИТЬ</b> к текущему долгу 👇",
        parse_mode='HTML'
    )
    await state.set_state(DebtStates.waiting_to_increase)
    await callback.answer()

@router.message(DebtStates.waiting_to_increase, F.text)
async def process_increase_amount(message: Message, state: FSMContext, db: Database):
    try:
        new_amount = float(message.text.replace(',', '.'))
    except ValueError:
        return await message.answer("Ошибка! Введите сумму только цифрами(Например: 500 или 500.25).")
    
    fsm_data = await state.get_data()
    debt_id = fsm_data.get("current_debt_id")
    all_debts = await db.get_debt(user_id=message.from_user.id)
    current_debt = next((d for d in all_debts if d['debt_id'] == debt_id), None)

    if not current_debt:
        await message.answer("❌ Запись не найдена")
        await state.clear()
        return
    total_amount = current_debt['amount'] + new_amount
    await db.delete_debt(debt_id=debt_id, user_id=message.from_user.id)
    await db.add_debt(
        user_id=message.from_user.id,
        name=current_debt['person_name'],
        amount=total_amount,
        debt_type=current_debt['debt_type'],
        comment=current_debt['comment']
    )
    await message.answer(
        f"📈 Сумма обновлена!\n\n"
        f"Должник: <b>{current_debt['person_name']}</b>\n"
        f"Было: <code>{current_debt['amount']}</code> ₽\n"
        f"Добавлено: <code>{new_amount}</code> ₽\n"
        f"💵 Новый долг: <b>{total_amount}</b> ₽",
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data.startswith('dec_debt_'))
async def process_to_decrease(callback: CallbackQuery, state: FSMContext):
    debt_id = int(callback.data.split('_')[-1])
    await state.update_data(current_debt_id = debt_id)
    await callback.message.edit_text(
        "📉<b>Уменьшение суммы долга</b>\n\n"
        "Введите сумму цифрами, которую хотите <b>УБАВИТЬ</b> к текущему долгу 👇",
        parse_mode='HTML'
    )
    await state.set_state(DebtStates.waiting_to_decrease)   
    await callback.answer()
@router.message(DebtStates.waiting_to_decrease, F.text)
async def process_decrease_amount(message: Message, state: FSMContext, db: Database):
    try:
        new_amount = float(message.text.replace(',', '.'))
    except ValueError:
        return await message.answer("Ошибка! Введите сумму только цифрами(Например: 500 или 500.25).")
    
    fsm_data = await state.get_data()
    debt_id = fsm_data.get("current_debt_id")
    all_debts = await db.get_debt(user_id=message.from_user.id)
    current_debt = next((d for d in all_debts if d['debt_id'] == debt_id), None)

    if not current_debt:
        await message.answer("❌ Запись не найдена")
        await state.clear()
        return
    total_amount = current_debt['amount'] - new_amount
    await db.delete_debt(debt_id=debt_id, user_id=message.from_user.id)
    await db.add_debt(
        user_id=message.from_user.id,
        name=current_debt['person_name'],
        amount=total_amount,
        debt_type=current_debt['debt_type'],
        comment=current_debt['comment']
    )
    await message.answer(
        f"📉 Сумма обновлена!\n\n"
        f"Должник: <b>{current_debt['person_name']}</b>\n"
        f"Было: <code>{current_debt['amount']}</code> ₽\n"
        f"Убавлено: <code>{new_amount}</code> ₽\n"
        f"💵 Новый долг: <b>{total_amount}</b> ₽",
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data == 'add_new_debt')
async def start_add_debt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("👤Введите имя должника: ")
    await state.set_state(DebtStates.waiting_for_name)
    await callback.answer() 

@router.message(DebtStates.waiting_for_name, F.text)
async def process_debt_name(message: Message, state: FSMContext):
    await state.update_data(chosen_name=message.text)
    
    await message.answer(f"💰 Введите сумму долга для <b>{message.text}</b> (только цифры):", parse_mode="HTML")
    
    await state.set_state(DebtStates.waiting_for_amount)

@router.message(DebtStates.waiting_for_amount, F.text)
async def process_debt_amount(message: Message, state: FSMContext, db: Database):
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        return await message.answer("Ошибка! Введите сумму только цифрами(Например: 500 или 500.25).")
    data = await state.get_data()
    name = data.get("chosen_name")
    await db.add_debt(user_id=message.from_user.id, name = name, amount = amount, debt_type = 0)
    await message.answer(f"✅ Долг для <b>{name}</b> на сумму <code>{amount}</code> успешно записан в базу!", parse_mode="HTML")
    await state.clear()

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
    await message.reply("Автором бота является: zadrot (Alan)💎")

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
