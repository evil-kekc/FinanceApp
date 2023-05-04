from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

app = FastAPI()

# Конфигурация шаблонизатора Jinja2
templates = Jinja2Templates(directory=f"app/templates")

# Конфигурация passlib для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Создание списка пользователей
users = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$3uEq7VwF4f4B...s4sZ9YK",
        "disabled": False,
    }
}


# Функция для получения пользователя из списка пользователей по имени пользователя
def get_user(username: str):
    if username in users:
        user_dict = users[username]
        return user_dict
    return None


# Маршрут для страницы авторизации
@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Маршрут для проверки учетных данных и аутентификации пользователя
@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = get_user(username)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})
    hashed_password = user["hashed_password"]
    if not pwd_context.verify(password, hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})
    return templates.TemplateResponse("home.html", {"request": request, "user": user})
