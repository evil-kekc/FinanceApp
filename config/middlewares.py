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
