"""Market trends tool for the Sovereign Aussie Market Research Agent.

Uses Google Trends (via pytrends) to surface interest data for book genres
across the target markets defined in the business context.
"""

from __future__ import annotations

import os
from typing import Any

try:
    from pytrends.request import TrendReq
    _PYTRENDS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PYTRENDS_AVAILABLE = False


# ---------------------------------------------------------------------------
# Static fallback data (used when pytrends is unavailable or for known genres)
# ---------------------------------------------------------------------------

_GENRE_KEYWORDS: dict[str, list[str]] = {
    "aussie fiction": ["Australian fiction books", "Aussie novels", "Australian authors"],
    "outback non-fiction": ["Outback Australia books", "Australian bush stories", "Outback memoir"],
    "business": ["Australian business books", "entrepreneur Australia", "startup Australia"],
    "self-help": ["Australian self-help books", "personal development AU", "mindset books Australia"],
    "true blue crime": ["Australian true crime", "Aussie crime books", "Australian crime podcast"],
}

_COMPETITION_LEVELS: dict[str, str] = {
    "aussie fiction": "Medium",
    "outback non-fiction": "Low",
    "business": "High",
    "self-help": "High",
    "true blue crime": "Medium",
}


def _normalise_genre(genre: str) -> str:
    return genre.lower().strip()


def _get_keywords_for_genre(genre: str) -> list[str]:
    norm = _normalise_genre(genre)
    for key, keywords in _GENRE_KEYWORDS.items():
        if key in norm or norm in key:
            return keywords
    # Generic fallback
    return [f"{genre} books", f"best {genre}", f"{genre} author"]


def _fetch_google_trends(keywords: list[str], geo: str) -> dict[str, Any]:
    """Attempt to fetch real Google Trends data; returns empty dict on failure."""
    if not _PYTRENDS_AVAILABLE:
        return {}
    try:
        pytrends = TrendReq(hl="en-AU", tz=570)
        pytrends.build_payload(keywords[:5], cat=22, timeframe="today 12-m", geo=geo)
        interest_df = pytrends.interest_over_time()
        if interest_df.empty:
            return {}
        avg_interest = interest_df.drop(columns=["isPartial"], errors="ignore").mean().to_dict()
        return {kw: round(float(score), 1) for kw, score in avg_interest.items()}
    except Exception:  # noqa: BLE001
        return {}


def get_trend_report(genre: str, target_market: str = "AU") -> dict[str, Any]:
    """Return a trend report for the given genre and market.

    Args:
        genre: Book genre to analyse.
        target_market: Two-letter market code (AU, NZ, UK, US, CA).

    Returns:
        dict with keys: genre, target_market, top_keywords, interest_scores,
        competition_level, and summary.
    """
    geo = target_market.upper()
    keywords = _get_keywords_for_genre(genre)
    interest_scores = _fetch_google_trends(keywords, geo)

    if not interest_scores:
        # Use placeholder scores when live data is unavailable
        interest_scores = {kw: None for kw in keywords}

    competition_level = _COMPETITION_LEVELS.get(_normalise_genre(genre), "Unknown")

    return {
        "genre": genre,
        "target_market": geo,
        "top_keywords": keywords,
        "interest_scores": interest_scores,
        "competition_level": competition_level,
        "summary": (
            f"The '{genre}' genre shows {competition_level.lower()} competition in the "
            f"{geo} market. Top search terms: {', '.join(keywords[:3])}."
        ),
    }
