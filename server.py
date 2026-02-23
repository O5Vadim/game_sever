import asyncio
import websockets
import json
from http.server import BaseHTTPRequestHandler
import threading
from http.server import HTTPServer

игроки = {}

# HTTP сервер для проверок Render
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        pass

def запустить_http():
    сервер = HTTPServer(("0.0.0.0", 8080), HealthCheck)
    сервер.serve_forever()

async def обработчик(websocket):
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
    # Запускаем HTTP в отдельном потоке
    http_поток = threading.Thread(target=запустить_http, daemon=True)
    http_поток.start()
    print("HTTP сервер запущен на порту 8080")
    
    async with websockets.serve(обработчик, "0.0.0.0", 10000):
        print("WebSocket сервер запущен на порту 10000!")
        await asyncio.Future()

asyncio.run(main())
