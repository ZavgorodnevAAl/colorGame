from fastapi.staticfiles import StaticFiles

from os import system

from core import app
from settings import STATIC_DIR, STATIC_URL
from endpoint import router

app.mount(STATIC_URL, StaticFiles(directory=STATIC_DIR), name="static")  # Где найти статику Static
app.include_router(router, tags=["core"])  # Подключаем отслеживание адресов


if __name__ == '__main__':
    system("uvicorn main:app --reload")
