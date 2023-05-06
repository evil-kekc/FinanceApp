from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from config.bot_config import bot, ADMIN_ID
from handlers.expense import DATABASE


class RegistrationStates(StatesGroup):
    get_username = State()
    get_password = State()


async def start_registration(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, 'Придумайте имя пользователя')
    await state.set_state(RegistrationStates.get_username.state)


async def get_username(message: types.Message, state: FSMContext):
    if DATABASE.check_user(username=message.text):
        await message.answer('Такое имя пользователя существует, придумайте и введите другое')
        return
    else:
        await state.update_data(username=message.text)
        await message.answer('Придумайте пароль')
        await state.set_state(RegistrationStates.get_password.state)


async def confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('username')
    password = message.text
    await bot.delete_message(message.from_user.id, message.message_id)
    if message.from_user.id == ADMIN_ID:
        is_admin = True
    else:
        is_admin = False
    DATABASE.add_user(user_id=message.from_user.id, is_admin=is_admin, username=username, password=password)
    await message.answer('Привет, я бот, который поможет тебе вести финансы\n\n'
                         'Для добавления расхода нажмите: /add_expense\n'
                         'Для получения расходов за все время нажмите: /get_all_expenses\n'
                         'Для получения расходов за месяц нажмите /get_month_expenses\n'
                         'Для получения расходов за неделю нажмите /get_week_expenses\n'
                         'Для получения расходов за день нажмите /get_day_expenses\n',
                         reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_registration(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(start_registration, text='registration')
    dp.register_message_handler(get_username, state=RegistrationStates.get_username)
    dp.register_message_handler(confirmation, state=RegistrationStates.get_password)
