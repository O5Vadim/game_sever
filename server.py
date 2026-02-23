import asyncio
import websockets
import json
import os

игроки = {}

PORT = int(os.environ.get("PORT", 10000))

async def обработчик(websocket, path=None):
    игрок_id = str(id(websocket))
    игроки[игрок_id] = {"ws": websocket, "x": 100, "y": 400, "ник": "Игрок"}
    print(f"Игрок подключился. Всего: {len(игроки)}")
    try:
        async for сообщение in websocket:
            try:
                данные = json.loads(сообщение)
                тип = данные.get("тип", "")
                if тип == "позиция":
                    игроки[игрок_id]["x"] = данные.get("x", 100)
                    игроки[игрок_id]["y"] = данные.get("y", 400)
                    игроки[игрок_id]["ник"] = данные.get("ник", "Игрок")
                    все = {pid: {"x": p["x"], "y": p["y"], "ник": p["ник"]} for pid, p in игроки.items()}
                    ответ = json.dumps({"тип": "игроки", "данные": все})
                    for p in list(игроки.values()):
                        try:
                            await p["ws"].send(ответ)
                        except:
                            pass
                elif тип == "чат":
                    ник = данные.get("ник", "Игрок")
                    текст = данные.get("текст", "")
                    print(f"Чат: {ник}: {текст}")
                    чат = json.dumps({"тип": "чат", "ник": ник, "текст": текст})
                    for p in list(игроки.values()):
                        try:
                            await p["ws"].send(чат)
                        except:
                            pass
            except:
                pass
    except:
        pass
    finally:
        if игрок_id in игроки:
            del игроки[игрок_id]
        print(f"Игрок отключился. Осталось: {len(игроки)}")

async def main():
    print(f"Запуск сервера на порту {PORT}...")
    async with websockets.serve(обработчик, "0.0.0.0", PORT):
        print("Сервер запущен!")
        await asyncio.Future()

asyncio.run(main())
