from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.modules.auth.repository import UserRepository
from app.realtime.websocket_manager import websocket_manager

router = APIRouter(tags=["websockets"])


def _get_user_id_from_token(token: str) -> str | None:
    try:
        payload = decode_access_token(token)
        user_id = UUID(payload["sub"])
    except Exception:
        return None

    db: Session = SessionLocal()
    try:
        user = UserRepository(db).get_by_id(user_id)
        return str(user.id) if user else None
    finally:
        db.close()


@router.websocket("/ws/dashboard")
async def dashboard_socket(websocket: WebSocket):
    token = websocket.query_params.get("token", "")
    user_id = _get_user_id_from_token(token)
    if user_id is None:
        await websocket.close(code=1008)
        return

    await websocket_manager.connect(user_id, websocket)
    await websocket.send_json({"type": "connection.ready", "payload": {"message": "Dashboard realtime connected"}})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id, websocket)

