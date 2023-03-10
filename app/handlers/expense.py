import logging
from typing import NamedTuple

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from config.bot_config import BASE_DIR, LOGGER
from databases.db import Database

DATABASE = Database(fr'{BASE_DIR}/databases/bot.db', fr'{BASE_DIR}/databases/create_db.sql')

ALL_CATEGORIES = [_.codename for _ in DATABASE.get_categories()]

CALLBACK_CONFIRM = CallbackData('confirmation_expense', 'answer', 'quantity', 'codename', 'user_id')

logging.basicConfig(filename=fr'{str(BASE_DIR)}/{LOGGER}',
                    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


class ChoiceExpense(NamedTuple):
    user_id: int
    state: str


def create_confirm_expenses_kb(quantity: float, codename: str, user_id: int):
    """Create confirm expenses_kb

    :param user_id: user id
    :param quantity: expense amount
    :param codename: expense codename
    :return:
    """
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)

    button_yes = types.InlineKeyboardButton(text='Да',
                                            callback_data=CALLBACK_CONFIRM.new(answer='Yes',
                                                                               quantity=quantity,
                                                                               codename=codename,
                                                                               user_id=user_id)
                                            )
    button_no = types.InlineKeyboardButton(text='Нет',
                                           callback_data=CALLBACK_CONFIRM.new(answer='No',
                                                                              quantity=quantity,
                                                                              codename=codename,
                                                                              user_id=user_id)
                                           )
    keyboard.add(button_yes)
    keyboard.add(button_no)
    return keyboard


def quantity_is_valid(quantity: str):
    """Expenditure check for validity

    :param quantity: expense amount
    :return:
    """
    try:
        quantity = float(quantity)
        return quantity
    except Exception as ex:
        logging.info(repr(ex))
        return


def add_expense(user_id: int, amount: float, category_codename: str):
    """Adding an expense to the database

    :param user_id: user id
    :param amount: amount of expense
    :param category_codename: codename of category expense
    :return:
    """
    try:
        DATABASE.add_expense(user_id=user_id, amount=amount, category_codename=category_codename)
        logging.info(f'User {user_id} add {category_codename} on {amount}')
        return True
    except Exception as ex:
        logging.error(repr(ex))
        return
