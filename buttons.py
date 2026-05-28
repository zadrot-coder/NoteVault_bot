from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📝Заметки"),
        KeyboardButton(text="💲Долги"),
        KeyboardButton(text="🎂Дни рождения"),
        KeyboardButton(text="📋FAQ")
    )
    
    builder.adjust(2) 
    return builder.as_markup(resize_keyboard=True)
