from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot
from handlers.expense import CALLBACK_CONFIRM, ChoiceExpense, create_confirm_expenses_kb, quantity_is_valid, \
    ALL_CATEGORIES, add_expense


class Expenses(StatesGroup):
    """Create states"""
    products_add = State()
    coffee_add = State()
    dinner_add = State()
    cafe_add = State()
    transport_add = State()
    taxi_add = State()
    phone_add = State()
    books_add = State()
    internet_add = State()
    subscriptions_add = State()
    other_add = State()


async def expense_start(callback_query: types.CallbackQuery, state: FSMContext):
    """Function to handle state

    :param callback_query: callback_query object
    :param state: state object
    :return:
    """
    expense = ChoiceExpense(
        user_id=callback_query.from_user.id,
        state=f'{callback_query.data}_add'
    )

    async def send_expenses_message(expense_type: str):
        await callback_query.answer(f'Введите сумму расходов на {expense_type}', show_alert=True)
        await bot.send_message(expense.user_id, 'Введите сумму расходов в рублях:\n\nНапример: 1.5')
        await callback_query.message.delete()

    if expense.state == 'products_add':
        await send_expenses_message('еду')
        await state.set_state(Expenses.products_add.state)

    elif expense.state == 'coffee_add':
        await send_expenses_message('кофе')
        await state.set_state(Expenses.coffee_add.state)

    elif expense.state == 'dinner_add':
        await send_expenses_message('обед')
        await state.set_state(Expenses.dinner_add.state)

    elif expense.state == 'cafe_add':
        await send_expenses_message('кафе')
        await state.set_state(Expenses.cafe_add.state)

    elif expense.state == 'transport_add':
        await send_expenses_message('транспорт')
        await state.set_state(Expenses.transport_add.state)

    elif expense.state == 'taxi_add':
        await send_expenses_message('такси')
        await state.set_state(Expenses.taxi_add.state)

    elif expense.state == 'phone_add':
        await send_expenses_message('телефон')
        await state.set_state(Expenses.phone_add.state)

    elif expense.state == 'books_add':
        await send_expenses_message('книги')
        await state.set_state(Expenses.books_add.state)

    elif expense.state == 'internet_add':
        await send_expenses_message('интернет')
        await state.set_state(Expenses.internet_add.state)

    elif expense.state == 'subscriptions_add':
        await send_expenses_message('подписки')
        await state.set_state(Expenses.subscriptions_add.state)

    elif expense.state == 'other_add':
        await send_expenses_message('прочие нужды')
        await state.set_state(Expenses.other_add.state)

    elif callback_query.data == 'NOT_FOUND':
        await callback_query.answer('Эта функция пока не доступна', show_alert=True)
        await state.finish()


async def send_expense(message: types.Message, state: FSMContext):
    """Send confirmation of payment

    :param message: message object
    :param state: state object
    :return:
    """
    quantity = quantity_is_valid(quantity=message.text)
    if not quantity:
        await message.answer('Проверьте введенные данные. Расход должен быть числом')

    current_state = await state.get_state()

    user_id = int(message.from_user.id)

    if current_state == 'Expenses:products_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='products', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию продукты?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:coffee_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='coffee', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию кофе?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:dinner_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='dinner', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию обед?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:cafe_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='cafe', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию кафе?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:transport_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='transport', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию общественный транспорт?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:taxi_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='taxi', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию такси?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:phone_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='phone', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию телефон?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:books_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='books', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию книги?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:internet_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='internet', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию интернет?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:subscriptions_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='subscriptions', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию подписки?', reply_markup=keyboard)
        await state.finish()

    elif current_state == 'Expenses:other_add':
        keyboard = create_confirm_expenses_kb(quantity=quantity, codename='other', user_id=user_id)
        await message.answer(f'Добавляем {message.text}р в категорию остальные расходы?', reply_markup=keyboard)
        await state.finish()


async def confirm_expense(callback_query: types.CallbackQuery, callback_data: dict):
    """confirmation of adding an expense

    :param callback_query:
    :param callback_data:
    :return:
    """
    if callback_data['answer'] == 'Yes':
        user_id = callback_data['user_id']
        category_codename = callback_data['codename']
        amount = callback_data['quantity']

        if add_expense(user_id=user_id, amount=amount, category_codename=category_codename):
            await callback_query.answer(f'Расход {amount}р успешно добавлен в {category_codename}!', show_alert=True)
            await callback_query.message.delete()
        else:
            await callback_query.answer(f'Произошла ошибка! Проверьте введенные данные и повторите попытку',
                                        show_alert=True)
            await callback_query.message.delete()

    else:
        await callback_query.answer(f'Добавление отменено')
        await callback_query.message.delete()


def register_handlers_add_expenses(dp: Dispatcher):
    """Handler Registration

    :param dp: Dispatcher object
    :return:
    """
    dp.register_callback_query_handler(confirm_expense, CALLBACK_CONFIRM.filter())
    dp.register_callback_query_handler(expense_start,
                                       lambda c: c.data == c.data if c.data in ALL_CATEGORIES else 'NOT_FOUND',
                                       state='*')
    dp.register_message_handler(send_expense, state=Expenses.all_states)
