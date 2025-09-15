from fastapi import FastAPI, WebSocket
import asyncio
import json
from typing import List, Dict, Any

from yt_dlp import YoutubeDL

app = FastAPI()

def fetch_playlist_titles(url: str) -> List[str]:
    """
    Returns list of video titles from a YouTube playlist URL using yt-dlp.
    This does NOT download any media; it only extracts metadata.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,       # don't resolve every video fully; faster
        "dump_single_json": True,   # returns a single JSON result
        "noplaylist": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        entries = info.get("entries", [])
        titles = []
        for item in entries:
            
            title = item.get("title")
            if title:
                titles.append(title)
        return titles

@app.websocket("/playlist-stream")
async def playlist_stream(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            data: Dict[str, Any] = json.loads(msg)

            if data.get("type") == "playlist_link":
                url = (data.get("value") or "").strip()
                if not url:
                    await ws.send_text(json.dumps({"type": "error", "message": "Empty URL"}))
                    continue

                try:
                    titles: List[str] = await asyncio.to_thread(fetch_playlist_titles, url)
                except Exception as e:
                    print(f"[ERROR] Failed to extract playlist: {e}")
                    await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
                    continue

                print("\n=== PLAYLIST TITLES ===")
                for i, t in enumerate(titles, 1):
                    print(f"{i:>2}. {t}")
                print("=======================\n")

                preview = titles[:5]
                await ws.send_text(json.dumps({
                    "type": "success",
                    "count": len(titles),
                    "preview": preview
                }))
            else:
                await ws.send_text(json.dumps({"type": "error", "message": "Unknown message type"}))

    except Exception:
        # Client disconnected or socket closed
        pass