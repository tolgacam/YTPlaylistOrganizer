# backend/categorizer.py
from __future__ import annotations
import re
from typing import Dict, List, Optional

LABELS = ["Music", "Tutorial", "Vlog", "Gaming", "Podcast", "News", "Education", "Other"]

KEYWORDS: Dict[str, List[str]] = {
    "Music":     ["official video", "lyrics", "audio", "remix", "live session", "music video", "mv", "instrumental", "cover", "Music"],
    "Tutorial":  ["how to", "tutorial", "guide", "step by step", "walkthrough", "fix", "learn", "course", "setup", "Tutorial"],
    "Vlog":      ["vlog", "day in the life", "travel vlog", "morning routine", "daily"],
    "Gaming":    ["gameplay", "let's play", "lets play", "walkthrough", "speedrun", "patch notes", "ranked", "gaming"],
    "Podcast":   ["podcast", "episode", "ep.", "interview", "clip", "highlights"],
    "News":      ["breaking", "news", "update", "press conference"],
    "Education": ["lecture", "khan academy", "university", "lesson", "explained"],
}

WORD_RE = re.compile(r"[a-z0-9']+")

def _norm(s: Optional[str]) -> str:
    return (s or "").lower()

def _text_blob(title: str, tags: Optional[List[str]], categories: Optional[List[str]]) -> str:
    parts = [title or ""]
    if tags: parts.append(" ".join(tags))
    if categories: parts.append(" ".join(categories))
    return _norm(" ".join(parts))

def _score_keywords(text: str, keywords: List[str]) -> int:
    score = 0
    for kw in keywords:
        kw = kw.lower()
        if " " in kw:
            if kw in text:
                score += 2
        else:
            if re.search(rf"(^|[^a-z0-9]){re.escape(kw)}([^a-z0-9]|$)", text):
                score += 1
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