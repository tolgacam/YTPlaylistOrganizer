# backend/categorizer.py
from __future__ import annotations
import re
from typing import Dict, List, Optional

LABELS = ["Music", "Tutorial", "Vlog", "Gaming", "Podcast", "News", "Education", "Other"]

KEYWORDS: Dict[str, Dict[str, int]] = {
    "Music": {
        "official video": 3,
        "lyrics": 3,
        "audio": 1,
        "remix": 1,
        "live": 1,
        "live session": 1,
        "music video": 1,
        "mv": 1,
        "instrumental": 1,
        "cover": 3,
        "music": 3,
    },
    "Tutorial": {
        "how to": 1,
        "tutorial": 3,
        "guide": 1,
        "step by step": 1,
        "walkthrough": 1,
        "fix": 1,
        "learn": 1,
        "course": 1,
        "setup": 1,
    },
    "Vlog": {
        "vlog": 10,
        "day in the life": 3,
        "travel vlog": 5,
        "morning routine": 3,
        "daily": 1,
    },
    "Gaming": {
        "gameplay": 3,
        "let's play": 3,
        "lets play": 3,
        "walkthrough": 1,
        "speedrun": 3,
        "ranked": 2,
        "gaming": 5,
    },
    "Podcast": {
        "podcast": 12,
        "episode": 2,
        "ep.": 2,
        "interview": 1,
    },
    "News": {
        "breaking": 1,
        "news": 1,
        "update": 1,
        "press conference": 1,
    },
    "Education": {
        "education": 2,
        "lecture": 2,
        "university": 2,
        "lesson": 1,
        "explained": 1,
    },
}

WORD_RE = re.compile(r"[a-z0-9']+")

def _norm(s: Optional[str]) -> str:
    return (s or "").lower()

def _text_blob(title: str, tags: Optional[List[str]], categories: Optional[List[str]]) -> str:
    parts = [title or ""]
    if tags: parts.append(" ".join(tags))
    if categories: parts.append(" ".join(categories))
    return _norm(" ".join(parts))

def _score_keywords(text: str, keywords: Dict[str, int]) -> int:
    score = 0
    for kw, weight in keywords.items():
        kw = kw.lower()
        if " " in kw:
            if kw in text:
                score += weight
        else:
            if re.search(rf"(^|[^a-z0-9]){re.escape(kw)}([^a-z0-9]|$)", text):
                score += weight
    return score

def _label_from_youtube_categories(categories: Optional[List[str]]) -> Optional[str]:
    if not categories:
        return None
    cats_lower = {c.lower() for c in categories}
    if "music" in cats_lower:
        return "Music"
    if {"education", "science & technology", "howto & style"} & cats_lower:
        return "Education"
    if {"news & politics"} & cats_lower:
        return "News"
    return None

def categorize_item(item: Dict) -> str:
    """
    item keys we use: title, tags, categories
    """
    title = item.get("title") or ""
    tags = item.get("tags") or []
    categories = item.get("categories") or []

    cat_hint = _label_from_youtube_categories(categories)
    if cat_hint:
        return cat_hint

    text = _text_blob(title, tags, categories)

    best_label, best_score = "Other", -1
    for label, kws in KEYWORDS.items():
        score = _score_keywords(text, kws)
        if score > best_score:
            best_label, best_score = label, score

    return best_label if best_score > 0 else "Other"

def categorize_items(items: List[Dict]) -> List[str]:
    return [categorize_item(it) for it in items]