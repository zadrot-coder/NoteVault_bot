import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers import router
from database import Database 

db = Database("note_vault.db")

async def main():
    logging.basicConfig(level=logging.INFO)

    await db.boom()    
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp["db"] = db
    
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
