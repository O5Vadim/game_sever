import asyncio
import websockets
import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

игроки = {}
PORT_WS = 9000
PORT_HTTP = int(os.environ.get("PORT", 8080))

# ===== HTTP ПОТОК (отвечает на пинги Render) =====
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Server is running!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Тихий режим

def запустить_http_сервер():
    сервер = HTTPServer(("0.0.0.0", PORT_HTTP), PingHandler)
    print(f"HTTP сервер запущен на порту {PORT_HTTP}")
    сервер.serve_forever()

# ===== WEBSOCKET ПОТОК (игра, чат, игроки) =====
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

            except json.JSONDecodeError:
                pass

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if игрок_id in игроки:
            del игроки[игрок_id]
        print(f"Игрок отключился. Осталось: {len(игроки)}")

async def запустить_websocket():
    print(f"WebSocket сервер запущен на порту {PORT_WS}")
    async with websockets.serve(обработчик, "0.0.0.0", PORT_WS):
        await asyncio.Future()

# ===== ЗАПУСК =====
if __name__ == "__main__":
    # HTTP в отдельном потоке
    http_поток = threading.Thread(target=запустить_http_сервер, daemon=True)
    http_поток.start()

    # WebSocket в главном потоке
    asyncio.run(запустить_websocket())
