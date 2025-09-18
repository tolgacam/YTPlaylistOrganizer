from fastapi import FastAPI, WebSocket
import asyncio
import json
from typing import List, Dict, Any
from playlist_service import fetch_playlist_items
from categorizer import categorize_items
from youtube_api import get_youtube_service, ensure_playlists, add_videos_to_playlist, playlist_web_link

app = FastAPI()

@app.websocket("/playlist-stream")
async def playlist_stream(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            data: Dict[str, Any] = json.loads(raw)

            if data.get("type") != "playlist_link":
                await ws.send_text(json.dumps({"type": "error", "message": "Unknown message type"}))
                continue

            url = (data.get("value") or "").strip()
            if not url:
                await ws.send_text(json.dumps({"type": "error", "message": "Empty URL"}))
                continue

            # 1) Fetch + categorize
            try:
                items = await asyncio.to_thread(fetch_playlist_items, url)
            except Exception as e:
                print(f"[ERROR] yt-dlp: {e}")
                await ws.send_text(json.dumps({"type": "error", "message": f"Failed to read playlist: {e}"}))
                continue

            if not items:
                await ws.send_text(json.dumps({"type": "error", "message": "No items found in playlist."}))
                continue

            labels = categorize_items(items)

            # 2) Group video IDs by label
            by_label: Dict[str, List[str]] = {}
            for item, label in zip(items, labels):
                by_label.setdefault(label, []).append(item.get("id"))

            # 3) Auth + ensure playlists
            try:
                yt = get_youtube_service()
                label_list = list(by_label.keys())
                playlist_ids = ensure_playlists(yt, label_list, prefix="SPO: ")
            except Exception as e:
                print(f"[ERROR] YouTube API auth/ensure: {e}")
                await ws.send_text(json.dumps({"type": "error", "message": f"YouTube auth/creation failed: {e}"}))
                continue

            # 4) Add videos to each playlist
            results = []
            for label, vids in by_label.items():
                try:
                    count_added = add_videos_to_playlist(yt, playlist_ids[label], vids)
                    link = playlist_web_link(playlist_ids[label])
                    results.append((label, link, count_added))
                    print(f"[INFO] {label}: added {count_added} videos -> {link}")
                except Exception as e:
                    print(f"[ERROR] adding to {label}: {e}")

            # 5) Send links back to frontend (one per line)
            # Format: "Label — URL (N videos)"
            lines = [f"{label} — {url} ({count} videos)" for (label, url, count) in results]
            payload = {
                "type": "playlists_created",
                "count_labels": len(results),
                "summary": "\n".join(lines)
            }
            await ws.send_text(json.dumps(payload))

    except Exception:
        # Client disconnected or socket closed
        pass