import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config_reader import load_config

BASE_DIR = Path(os.path.abspath(__file__)).parent.parent
LOGGER = 'bot.log'

config = load_config(fr'{BASE_DIR}/config/bot_config.ini')
ADMIN_ID = config.tg_bot.admin_id

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())
