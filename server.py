import asyncio
import websockets
import json

игроки = {}

async def обработчик(websocket):
    игрок_id = str(id(websocket))
    игроки[игрок_id] = {"ws": websocket, "x": 100, "y": 400, "ник": "Игрок"}
    print(f"Игрок {игрок_id} подключился. Всего: {len(игроки)}")
    
    try:
        async for сообщение in websocket:
            try:
                данные = json.loads(сообщение)
                тип = данные.get("тип", "")
                
                if тип == "позиция":
                    игроки[игрок_id]["x"] = данные.get("x", 100)
                    игроки[игрок_id]["y"] = данные.get("y", 400)
                    игроки[игрок_id]["ник"] = данные.get("ник", "Игрок")
                    
                    все = {
                        pid: {"x": p["x"], "y": p["y"], "ник": p["ник"]}
                        for pid, p in игроки.items()
                    }
                    ответ = json.dumps({"тип": "игроки", "данные": все})
                    
                    мертвые = []
                    for pid, p in игроки.items():
                        try:
                            await p["ws"].send(ответ)
                        except:
                            мертвые.append(pid)
                    for pid in мертвые:
                        if pid in игроки:
                            del игроки[pid]
                
                elif тип == "чат":
                    ник = данные.get("ник", "Игрок")
                    текст = данные.get("текст", "")
                    print(f"Чат от {ник}: {текст}")
                    чат = json.dumps({"тип": "чат", "ник": ник, "текст": текст})
                    
                    мертвые = []
                    for pid, p in игроки.items():
                        try:
                            await p["ws"].send(чат)
                        except:
                            мертвые.append(pid)
                    for pid in мертвые:
                        if pid in игроки:
                            del игроки[pid]
                            
            except json.JSONDecodeError:
                print(f"Неверный JSON: {сообщение}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"Игрок {игрок_id} отключился")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if игрок_id in игроки:
            del игроки[игрок_id]
        print(f"Игроков осталось: {len(игроки)}")

async def main():
    print("Запуск сервера на порту 10000...")
    async with websockets.serve(
        обработчик,
        "0.0.0.0",
        10000,
        ping_interval=20,
        ping_timeout=60,
        max_size=1_000_000
    ):
        print("Сервер запущен!")
        await asyncio.Future()

asyncio.run(main())
