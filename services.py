from random import randint

from core import manager, MyWS
from pd_model import StandardModel


async def disconnect_message(ws: MyWS) -> None:
    if ws.partner:  # Если есть партнёр, то пишем ему, что он теперь один
        response: StandardModel = StandardModel(type="disconnectPartner",
                                                data="We are looking for a new partner")
        await manager.set_partner(ws.partner)
        await manager.send_data(ws.partner, response.dict())
    await manager.send_online()  # Всем сообщаем новое число игроков


async def proc_request(ws_id: str, data: str) -> None:
    # В зависимости от типа запроса запускаем свой обработчик
    if data == "changePartner":
        await change_partner(ws_id)

    elif data == "changeColor":
        await _change_color(ws_id)


def r_color() -> str:
    return '#%02X%02X%02X' % (randint(0, 255), randint(0, 255), randint(0, 255))


async def change_partner(ws_id: str) -> None:
    ws: MyWS = await manager.get_ws(ws_id)
    partner_id: str = await manager.find_partner(ws_id, ws.partner)
    if ws.partner:
        await manager.set_partner(ws.partner)  # Говорим партнёру, что мы больше с ним не связаны
        response: StandardModel = StandardModel(type="disconnectPartner",
                                                data="We are looking for a new partner")
        await manager.send_data(ws.partner, response.dict())

    await manager.set_partner(ws_id, partner_id)  # Устанавливаем себе нового партнура

    if partner_id:  # Всякие сообщения себе и партнёру о том что у нас теперь связь
        response: StandardModel = StandardModel(type="changePartner", data=ws_id)
        await manager.set_partner(partner_id, ws_id)
        await manager.send_data(partner_id, response.dict())
        response.data = partner_id

    else:  # Себе, что у нас нет больше партнёра
        response: StandardModel = StandardModel(type="disconnectPartner",
                                                data="We are looking for a new partner")
    await manager.send_data(ws.ws, response.dict())


async def _change_color(ws_id: str) -> None:
    ws: MyWS = await manager.get_ws(ws_id)

    if ws.partner:  # Если есть партнёр, то меняем цвет
        response: StandardModel = StandardModel(type="changeColor", data=r_color())
        await manager.send_data(ws.partner, response.dict())

    else:
        response: StandardModel = StandardModel(type="message",
                                                data="You haven't a partner, "
                                                     "you can't change a color")
        await manager.send_data(ws_id, response.dict())
