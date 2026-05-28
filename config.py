import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bot_token: str = os.getenv("BOT_TOKEN", "ТУТ ВВОДИТЬ СВОЙ ТОКЕН")

config = Settings()
