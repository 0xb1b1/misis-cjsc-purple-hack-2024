from fastapi import APIRouter, HTTPException
from fastapi.websockets import WebSocket
from loguru import logger

router = APIRouter(
    tags=["Websockets"],
    prefix="/ws/messages",
)

connected_clients = []  # TODO: move to Redis


@router.websocket("/fetch")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    logger.debug(f"Client connected: {websocket.client}")

    # Test welcome message
    await websocket.send_text('{"connected": "true"}')

    for message in message_queue[websocket.client]:
        await websocket.send_text(message)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            # Добавляем сообщение в очередь
            message_queue.append(message)
            # Отправляем сообщение всем подключенным клиентам
            for client in connected_clients:
                await client["websocket"].send_text(message)
    except WebSocketDisconnect:
        # Удаляем клиента из списка при отключении
        connected_clients.remove({"websocket": websocket, "username": username})