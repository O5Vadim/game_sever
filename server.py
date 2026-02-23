import asyncio
import websockets
import json

игроки = {}

async def обработчик(websocket, path):
    игрок_id = str(id(websocket))
    игроки[игрок_id] = {"ws": websocket, "x": 100, "y": 400, "ник": "Игрок"}
    
    try:
        async for сообщение in websocket:
            данные = json.loads(сообщение)
            
            if данные["тип"] == "позиция":
                игроки[игрок_id]["x"] = данные["x"]
                игроки[игрок_id]["y"] = данные["y"]
                игроки[игрок_id]["ник"] = данные["ник"]
            
            все_игроки = {
                pid: {"x": p["x"], "y": p["y"], "ник": p["ник"]}
                for pid, p in игроки.items()
            }
            ответ = json.dumps({"тип": "игроки", "данные": все_игроки})
            for p in игроки.values():
                await p["ws"].send(ответ)
                
            if данные["тип"] == "чат":
                чат = json.dumps({"тип": "чат", "ник": данные["ник"], "текст": данные["текст"]})
                for p in игроки.values():
                    await p["ws"].send(чат)
    except:
        pass
    finally:
        del игроки[игрок_id]

async def main():
    async with websockets.serve(обработчик, "0.0.0.0", 10000):
        print("Сервер запущен!")
        await asyncio.Future()

asyncio.run(main())
