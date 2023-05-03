from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.expense import DATABASE


async def cmd_start(message: types.Message, state: FSMContext):
    """Handling the start command

    :param message: message object
    :param state: state object
    :return:
    """
    await state.finish()
    if DATABASE.check_user(user_id=message.from_user.id):
        await message.answer('Привет, я бот, который поможет тебе вести финансы\n\n'
                             'Для добавления расхода нажмите: /add_expense\n'
                             'Для получения расходов за все время нажмите: /get_all_expenses\n'
                             'Для получения расходов за месяц нажмите /get_month_expenses\n'
                             'Для получения расходов за неделю нажмите /get_week_expenses\n'
                             'Для получения расходов за день нажмите /get_day_expenses\n',
                             reply_markup=types.ReplyKeyboardRemove())


async def get_list_of_expenses(message: types.Message):
    """Displaying information about expense categories

    :param message: message object
    :return:
    """
    all_categories = DATABASE.get_categories()
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    for category in all_categories:
        button = InlineKeyboardButton(text=category.name, callback_data=f'{category.codename}')
        keyboard.add(button)

    await message.answer('Доступны следующие категории расходов: ', reply_markup=keyboard)


async def cmd_cancel(message: types.Message, state: FSMContext):
    """Handling the cancel command

    :param message: message object
    :param state: state object
    :return:
    """
    await state.finish()
    await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())


def register_handlers_common(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(get_list_of_expenses, commands='add_expense', state='*')
    dp.register_message_handler(cmd_start, Text(equals='отмена', ignore_case=True), state='*')
