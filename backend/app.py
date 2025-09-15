from fastapi import FastAPI, WebSocket
import asyncio
import json
from typing import List, Dict, Any
from playlist_service import fetch_playlist_items
from categorizer import categorize_items

app = FastAPI()

@app.websocket("/playlist-stream")
async def playlist_stream(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)

            if data.get("type") == "playlist_link":
                url = (data.get("value") or "").strip()
                if not url:
                    await ws.send_text(json.dumps({"type": "error", "message": "Empty URL"}))
                    continue

                try:
                    items = await asyncio.to_thread(fetch_playlist_items, url)
                    labels = categorize_items(items)
                except Exception as e:
                    print(f"[ERROR] Failed to extract playlist: {e}")
                    await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
                    continue

                print("\n=== PLAYLIST METADATA ===")
                for i, (item, label) in enumerate(zip(items, labels), 1):
                    title = item.get("title")
                    categories = item.get("categories") or []
                    tags = item.get("tags") or []

                    print(f"{i:>2}. {title}")
                    print(f"    Predicted : {label}")
                    print(f"    YT Cats   : {', '.join(categories) if categories else 'N/A'}")
                    print(f"    Tags      : {', '.join(tags[:8]) if tags else 'N/A'}")
                print("==========================\n")

                # send preview back to frontend
                preview_lines = [f"{t} — {lbl}" for t, lbl in zip([i["title"] for i in items[:5]], labels[:5])]
                preview_str = "\n".join(preview_lines)

                await ws.send_text(json.dumps({
                    "type": "success",
                    "count": len(items),
                    "preview": preview_str
                }))

            else:
                await ws.send_text(json.dumps({"type": "error", "message": "Unknown message type"}))

    except Exception:
        # Client disconnected or socket closed
        pass