import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from handlers.common import DATABASE


class AccessMiddleware(BaseMiddleware):
    """Authentication - skip messages from only one Telegram account"""

    def __init__(self, access_id: int):
        self.access_id = access_id
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if int(message.from_user.id) != int(self.access_id):
            DATABASE.add_user(user_id=message.from_user.id, is_admin=False)
        else:
            DATABASE.add_user(user_id=self.access_id, is_admin=True)


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
