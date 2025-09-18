from yt_dlp import YoutubeDL
from typing import List, Dict

def fetch_playlist_items(url: str) -> List[Dict]:
    """
    Returns list of metadata dicts for each video in the playlist, including 'id'.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": False,
        "dump_single_json": True,
        "noplaylist": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        items = []
        for item in (info.get("entries") or []):
            items.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "categories": item.get("categories"),
                "tags": item.get("tags"),
            })
        return items