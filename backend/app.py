# backend.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn, json, time

app = FastAPI()

@app.websocket("/playlist-stream")
async def playlist_stream(ws: WebSocket):
    await ws.accept()
    seq = 0
    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)
            print(f"[BACKEND] {data}")  # <- prints as you type
            seq += 1
            await ws.send_text(json.dumps({"type": "ack", "seq": seq, "ts": int(time.time()*1000)}))
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)