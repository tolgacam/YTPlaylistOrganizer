from yt_dlp import YoutubeDL

def fetch_playlist_items(url: str):
    """
    Returns list of metadata dicts for each video in the playlist.
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
        entries = info.get("entries", [])
        items = []
        for item in entries:
            items.append({
                "title": item.get("title"),
                "categories": item.get("categories"),
                "tags": item.get("tags"),
            })
        return items