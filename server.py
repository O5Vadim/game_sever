import asyncio
import websockets
import json
from websockets.server import serve

игроки = {}

async def обработчик(websocket):
    игрок_id = str(id(websocket))
    игроки[игрок_id] = {"ws": websocket, "x": 100, "y": 400, "ник": "Игрок"}
    try:
        async for сообщение in websocket:
            данные = json.loads(сообщение)
            if данные["тип"] == "позиция":
                игроки[игрок_id]["x"] = данные["x"]
                игроки[игрок_id]["y"] = данные["y"]
                игроки[игрок_id]["ник"] = данные["ник"]
                все = {pid: {"x": p["x"], "y": p["y"], "ник": p["ник"]} for pid, p in игроки.items()}
                ответ = json.dumps({"тип": "игроки", "данные": все})
                for p in игроки.values():
                    await p["ws"].send(ответ)
            elif данные["тип"] == "чат":
                чат = json.dumps({"тип": "чат", "ник": данные["ник"], "текст": данные["текст"]})
                for p in игроки.values():
                    await p["ws"].send(чат)
    except:
        pass
    finally:
        if игрок_id in игроки:
            del игроки[игрок_id]

async def main():
    async with serve(обработчик, "0.0.0.0", 10000, process_request=lambda path, headers: None):
        print("Сервер запущен!")
        await asyncio.Future()

asyncio.run(main())
