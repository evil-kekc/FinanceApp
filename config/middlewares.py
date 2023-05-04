import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import Throttled

from config.bot_config import dp
from handlers.common import DATABASE
from handlers.registration.registration import RegistrationStates


class CheckUserMiddleware(BaseMiddleware):
    """Check user in database"""

    def __init__(self):
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        state = dp.current_state(chat=message.chat.id)
        current_state = await state.get_state()
        allowed_states = RegistrationStates.all_states_names

        if not DATABASE.check_user(user_id=message.from_user.id) and current_state not in allowed_states:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='Зарегистрироваться', callback_data='registration'))

            await message.answer('Для использования бота необходимо зарегистрироваться', reply_markup=keyboard)
            raise CancelHandler


class UpdateLastActiveMiddleware(BaseMiddleware):
    """Update last user activity"""

    def __init__(self):
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        DATABASE.update_last_active(user_id=message.from_user.id)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        This handler is called when dispatcher receives a message

        :param message:
        """
        handler = current_handler.get()

        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        """
        Notify user only on first exceed and notify about unlocking only on last exceed

        :param message:
        :param throttled:
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message"

        delta = 5

        if throttled.exceeded_count <= 2:
            await message.reply('Слишком много запросов. Придется немного подождать.')

        await asyncio.sleep(delta)

        thr = await dispatcher.check_key(key)

        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply('Общение с ботом возобновлено.')
