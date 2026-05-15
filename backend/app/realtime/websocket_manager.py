from collections import defaultdict

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[user_id].append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        if websocket in self.connections[user_id]:
            self.connections[user_id].remove(websocket)

    async def send_to_user(self, user_id: str, message: dict) -> None:
        stale_connections = []
        for websocket in self.connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.disconnect(user_id, websocket)


websocket_manager = WebSocketManager()

