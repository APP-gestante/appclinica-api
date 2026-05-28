from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, ws: WebSocket, patient_id: str):
        await ws.accept()
        self.active.setdefault(patient_id, []).append(ws)

    def disconnect(self, ws: WebSocket, patient_id: str):
        conns = self.active.get(patient_id, [])
        if ws in conns:
            conns.remove(ws)
        if not conns:
            self.active.pop(patient_id, None)

    async def broadcast(self, patient_id: str, data: str):
        for ws in list(self.active.get(patient_id, [])):
            try:
                await ws.send_text(data)
            except Exception:
                self.disconnect(ws, patient_id)


manager = ConnectionManager()
