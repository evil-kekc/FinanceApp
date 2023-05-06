import logging

from aiogram import Bot
from aiogram import types, Dispatcher
from aiogram.types import BotCommand
from aiogram.utils.exceptions import BadRequest
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse

from bot_app.handlers import add_expenses, common_handlers, get_expenses, registration
from config.bot_config import bot, dp, BASE_DIR, LOGGER, TOKEN
from config.bot_config import config
from config.middlewares import UpdateLastActiveMiddleware, CheckUserMiddleware
from databases.db import Database

logging.basicConfig(level=logging.INFO, filename=fr"{str(BASE_DIR)}/{LOGGER}",
                    format="%(asctime)s | %(levelname)s | %(funcName)s: %(lineno)d | %(message)s",
                    datefmt="%H:%M:%S")

DATABASE = Database(fr"{BASE_DIR}/databases/bot.db", f"{BASE_DIR}/databases/create_db.sql")

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = config.tg_bot.host_url + WEBHOOK_PATH


async def set_commands(bot_: Bot):
    """Creating a bot menu

    :param bot_: an instance of the bot class
    :return:
    """
    commands = [
        BotCommand(command='/start', description='Начало работы'),
        BotCommand(command='/add_expense', description='Добавление расхода'),
        BotCommand(command='/cancel', description='Отмена действий'),
        BotCommand(command='/get_all_expenses', description='Сумма всех расходов'),
        BotCommand(command='/get_month_expenses', description='Расходы за месяц'),
        BotCommand(command='/get_week_expenses', description='Расходы за неделю'),
        BotCommand(command='/get_day_expenses', description='Расходы за день'),
    ]

    await bot_.set_my_commands(commands)


async def bot_main():
    """Bot launch

    :return: None
    """
    logging.info('Starting bot')
    dp.middleware.setup(CheckUserMiddleware())
    dp.middleware.setup(UpdateLastActiveMiddleware())

    common_handlers(dp)
    registration(dp)
    get_expenses(dp)
    add_expenses(dp)

    await set_commands(bot)


@app.on_event("startup")
async def on_startup():
    """Setting up a webhook

    :return:
    """
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True
            )
    except BadRequest as ex:
        if "ip address 127.0.0.1 is reserved" in str(ex):
            logging.error('ip address 127.0.0.1 is reserved')
        else:
            logging.error(repr(ex))


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """Getting Telegram updates

    :param update: Telegram update
    :return:
    """
    try:
        telegram_update = types.Update(**update)
        Dispatcher.set_current(dp)
        Bot.set_current(bot)
        await bot_main()
        await dp.process_update(telegram_update)
    except Exception as ex:
        logging.error(repr(ex))


@app.on_event("shutdown")
async def on_shutdown():
    """Closing session and delete webhook

    :return:
    """
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()
    await bot.delete_webhook()


def check_username_and_password_cookies(**kwargs: dict) -> bool | None:
    if 'username' in kwargs.keys() and 'password' in kwargs.keys():
        return True


@app.get("/login")
async def login(request: Request, response: Response):
    response.delete_cookie('username')
    response.delete_cookie('password')
    request = templates.TemplateResponse("login.html", {"request": request})
    request.delete_cookie('username')
    request.delete_cookie('password')
    return request


@app.get('/home')
async def get_home(request: Request):
    if not check_username_and_password_cookies(**request.cookies):
        return RedirectResponse(url='/login')
    username = request.cookies.get('username')
    response = templates.TemplateResponse("home.html", {
        "request": request,
        "username": username,
        "total_expenses": DATABASE.get_sum_of_expenses(username=username),
        "month_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta="month"),
        "week_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta="week"),
        "day_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta="day"),
    })
    return response


@app.post("/home", response_class=HTMLResponse)
async def post_home(request: Request, username: str = Form(None), password: str = Form(None)):
    if not (username and password):
        username = request.cookies.get('username')
        password = request.cookies.get('password')
    if not DATABASE.check_user_by_username_and_password(username=username, password=password):
        logging.warning(f"Пользователь [{username}] не найден")
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

    response = templates.TemplateResponse("home.html", {
        "request": request,
        "username": username,
        "total_expenses": DATABASE.get_sum_of_expenses(username=username),
        "month_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta="month"),
        "week_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta="week"),
        "day_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta="day"),
    })
    response.set_cookie(key="username", value=username)
    response.set_cookie(key="password", value=password)

    return response


@app.get('/add_expense')
async def add_expense(request: Request):
    if not check_username_and_password_cookies(**request.cookies):
        return RedirectResponse(url='/login')
    response = templates.TemplateResponse("expenses/add_expense.html", {
        'request': request
    })
    return response


@app.post('/add_expense', response_class=HTMLResponse)
async def add_expense(request: Request, amount: int = Form(...), category: str = Form(...)):
    if amount and category:
        username = request.cookies.get('username')
        category = DATABASE.get_full_category_codename_by_substring(category)
        DATABASE.add_expense(amount=amount, category_codename=category, username=username)

    return RedirectResponse(url='/all_expenses', status_code=status.HTTP_303_SEE_OTHER)


@app.get('/{expense}')
async def get_expense(request: Request, expense: str):
    if not check_username_and_password_cookies(**request.cookies):
        return RedirectResponse(url='/login')
    username = request.cookies.get('username')
    if expense == 'all_expenses':
        response = templates.TemplateResponse("expenses/all_expenses.html", {
            "request": request,
            "total_expenses": DATABASE.get_sum_of_expenses(username=username),
        })
        return response
    elif expense == 'month_expenses':
        response = templates.TemplateResponse("expenses/month_expenses.html", {
            "request": request,
            "month_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta='month'),
        })
        return response
    elif expense == 'week_expenses':
        response = templates.TemplateResponse("expenses/week_expenses.html", {
            "request": request,
            "week_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta='week'),
        })
        return response
    elif expense == 'day_expenses':
        response = templates.TemplateResponse("expenses/day_expenses.html", {
            "request": request,
            "day_expenses": DATABASE.get_sum_of_expenses(username=username, timedelta='day'),
        })
        return response
    return RedirectResponse(url='/login')
