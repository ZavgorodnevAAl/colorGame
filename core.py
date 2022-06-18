from fastapi import FastAPI
from fastapi import WebSocket
from typing import Union
from uuid import uuid4
from dataclasses import dataclass


@dataclass
class MyWS:  # Необходимая информация о подключении
    ws: WebSocket
    ws_id: str
    partner: str = ""


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, MyWS] = {}  # Активные пользователи (web socket)

    async def connect(self, websocket: WebSocket) -> MyWS:
        await websocket.accept()  # Говорим пользователю, что мы приняли запрос на подключение
        ws_id = str(uuid4())
        self.active_connections[ws_id] = MyWS(ws=websocket, ws_id=ws_id)  # Cохраняем новое подключение в наш dict
        return self.active_connections[ws_id]

    def disconnect(self, websocket: Union[WebSocket, str]):
        if type(websocket) is str:  # Если пришла строка, то удаляем по ключу
            del self.active_connections[websocket]
            return

        for key, item in self.active_connections.items():  # Не строка, а значит придётся найти и удалить
            if item == websocket:
                del self.active_connections[key]
                return

    async def send_data(self, websocket: Union[str, WebSocket], response_dict: dict) -> None:
        if type(websocket) is str:  # Достаём само подключение
            websocket: WebSocket = self.active_connections[websocket].ws

        await websocket.send_json(response_dict)  # Отправляем пользователю инфу

    async def get_ws(self, ws_id: str) -> MyWS:
        return self.active_connections[ws_id]

    async def find_partner(self, ws_id: str, exclude: str = None) -> str:
        for partner_id, ws in self.active_connections.items():
            # Ищем партнёра, не подходит: 1. Тот что уже был 2. Мы сами 3. У него уже есть партнёр
            if partner_id == exclude or partner_id == ws_id or ws.partner:
                continue

            return partner_id
        return ""

    async def set_partner(self, f_id: str, s_id: str = ""):
        # Пустая строка - теперь у нас нет партнёра
        self.active_connections[f_id].partner = s_id

        if s_id:
            self.active_connections[s_id].partner = f_id

    async def send_online(self):
        count: int = len(self.active_connections)

        for my_ws in self.active_connections.values():
            await my_ws.ws.send_json({"type": "online", "data": count})


app = FastAPI()
manager = ConnectionManager()
