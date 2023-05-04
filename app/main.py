import logging

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from config.bot_config import BASE_DIR, LOGGER
from databases.db import Database

logging.basicConfig(level=logging.INFO, filename=fr'{str(BASE_DIR)}/{LOGGER}',
                    format="%(asctime)s | %(levelname)s | %(funcName)s: %(lineno)d | %(message)s",
                    datefmt='%H:%M:%S')

DATABASE = Database(fr'{BASE_DIR}/databases/bot.db', fr'{BASE_DIR}/databases/create_db.sql')

app = FastAPI()

templates = Jinja2Templates(directory=f"app/templates")


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing required fields")
    user_exists = DATABASE.check_user_by_username_and_password(username=username, password=password)
    if not user_exists:
        logging.warning(f'Пользователь [{username}] не найден')
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

    total_expenses = DATABASE.get_sum_of_expenses(username=username)
    month_expenses = DATABASE.get_sum_of_expenses(username=username, timedelta='month')
    week_expenses = DATABASE.get_sum_of_expenses(username=username, timedelta='week')
    day_expenses = DATABASE.get_sum_of_expenses(username=username, timedelta='day')

    template = templates.TemplateResponse("home.html", {
        'request': request,
        'username': username,
        'total_expenses': total_expenses,
        'month_expenses': month_expenses,
        'week_expenses': week_expenses,
        'day_expenses': day_expenses,
    })

    response = template
    response.set_cookie(key='username', value=username)

    return response


@app.post('/add_expense', response_class=HTMLResponse)
def add_expense(request: Request, amount: int = Form(...), category: str = Form(...)):
    if amount and category:
        username = request.cookies.get('username')
        category = DATABASE.get_full_category_codename_by_substring(category)
        DATABASE.add_expense(amount=amount, category_codename=category, username=username)

    return RedirectResponse(url='/login')
