from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove

from handlers.expense import DATABASE


async def get_all_amounts_of_expenses(message: types.Message):
    """Displays information on all expenses of the user

    :param message: message object
    :return:
    """
    mess = f'<b>Расходы за все время:</b>\n'
    sum_of_amount = float()
    for expense in DATABASE.get_sum_of_expenses(user_id=message.from_user.id):
        mess += f'<b>Расходы на {expense.category} составляют:</b> {expense.amount} руб.\n'
        sum_of_amount += expense.amount

    await message.answer(f'{mess}\n<b>Общая сумма расходов:</b> {sum_of_amount} руб.', parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())


async def get_month_amounts_of_expenses(message: types.Message):
    """Displays information on all month expenses of the user

    :param message: message object
    :return:
    """
    mess = f'<b>Расходы за месяц:</b>\n'
    sum_of_amount = float()
    for expense in DATABASE.get_sum_of_expenses(user_id=message.from_user.id, timedelta='month'):
        mess += f'<b>Расходы на {expense.category} составляют:</b> {expense.amount} руб.\n'
        sum_of_amount += expense.amount

    await message.answer(f'{mess}\n<b>Общая сумма расходов за месяц:</b> {sum_of_amount} руб.', parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())


async def get_week_amounts_of_expenses(message: types.Message):
    """Displays information on all week expenses of the user

    :param message: message object
    :return:
    """
    mess = f'<b>Расходы за последние 7 дней:</b>\n'
    sum_of_amount = float()
    for expense in DATABASE.get_sum_of_expenses(user_id=message.from_user.id, timedelta='week'):
        mess += f'<b>Расходы на {expense.category} составляют:</b> {expense.amount} руб.\n'
        sum_of_amount += expense.amount

    await message.answer(f'{mess}\n<b>Общая сумма расходов за 7 дней:</b> {sum_of_amount} руб.', parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())


async def get_day_amounts_of_expenses(message: types.Message):
    """Displays information on all day expenses of the user

    :param message: message object
    :return:
    """

    mess = f'<b>Расходы за день:</b>\n'
    sum_of_amount = float()
    for expense in DATABASE.get_sum_of_expenses(user_id=message.from_user.id, timedelta='day'):
        mess += f'<b>Расходы на {expense.category} составляют:</b> {expense.amount} руб.\n'
        sum_of_amount += expense.amount

    await message.answer(f'{mess}\n<b>Общая сумма расходов за день:</b> {sum_of_amount} руб.', parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())


def register_handlers_get_expenses(dp: Dispatcher):
    """Handler registration function

    :param dp: Dispatcher object
    :return:
    """
    dp.register_message_handler(get_all_amounts_of_expenses, commands='get_all_expenses', state='*')
    dp.register_message_handler(get_month_amounts_of_expenses, commands='get_month_expenses', state='*')
    dp.register_message_handler(get_week_amounts_of_expenses, commands='get_week_expenses', state='*')
    dp.register_message_handler(get_day_amounts_of_expenses, commands='get_day_expenses', state='*')
