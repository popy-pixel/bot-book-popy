"""
WebSocket for Real-Time Updates
📁 app/api/websocket.py
"""

import json
import logging
from typing import Set
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        
        text = json.dumps(message, default=str)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(text)
            except Exception:
                disconnected.add(connection)
        
        for conn in disconnected:
            self.active_connections.discard(conn)

manager = ConnectionManager()


@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for live updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("action") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_log(account_id: int, message: str, level: str = "INFO"):
    await manager.broadcast({
        "type": "log",
        "data": {
            "account_id": account_id,
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow().isoformat(),
        }
    })


async def broadcast_screenshot(account_id: int, screenshot_path: str):
    await manager.broadcast({
        "type": "screenshot",
        "data": {
            "account_id": account_id,
            "path": screenshot_path,
            "timestamp": datetime.utcnow().isoformat(),
        }
    })


async def broadcast_task_update(task_id: int, status: str, message: str):
    await manager.broadcast({
        "type": "task_update",
        "data": {
            "task_id": task_id,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
    })