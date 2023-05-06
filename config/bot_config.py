import os
from functools import wraps
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from cachetools import TTLCache

from config_reader import load_config

BASE_DIR = Path(os.path.abspath(__file__)).parent.parent
LOGGER = 'bot.log'

config = load_config(fr'{BASE_DIR}/config/bot_config.ini')
ADMIN_ID = config.tg_bot.admin_id
TOKEN = config.tg_bot.token

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())


def antispam(rate: int, interval: int, mess: str = "Слишком много запросов"):
    """A decorator that checks if the user has exceeded the request limit in a given amount of time.
    :param rate: request limit
    :param interval: time interval in seconds
    :param mess: message sent to the user if they have exceeded the request limit
    """

    cache = TTLCache(maxsize=rate, ttl=interval)

    def decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, state: FSMContext, *args, **kwargs):
            user_id = message.from_user.id

            if user_id in cache:
                if cache[user_id] >= rate:
                    await message.reply(mess)
                    return
                cache[user_id] += 1
            else:
                cache[user_id] = 1

            return await func(message, state, *args, **kwargs)

        return wrapped

    return decorator
