"""Pricing and keyword research tool for the Sovereign Aussie Market Research Agent."""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Pricing knowledge base (AUD, based on 2024 AU reading habits)
# ---------------------------------------------------------------------------

_EBOOK_PRICES: dict[str, float] = {
    "fiction": 4.99,
    "non_fiction": 9.99,
    "box_set": 12.99,
    "business": 9.99,
    "self_help": 7.99,
    "crime": 5.99,
    "true_crime": 6.99,
    "outback": 8.99,
}

_PAPERBACK_PRICES: dict[str, float] = {
    "fiction": 19.99,
    "non_fiction": 29.99,
    "box_set": 49.99,
    "business": 34.99,
    "self_help": 24.99,
    "crime": 22.99,
    "true_crime": 24.99,
    "outback": 27.99,
}

_KDP_KEYWORDS: dict[str, list[str]] = {
    "fiction": ["Australian fiction", "Aussie novel", "down under stories"],
    "non_fiction": ["Australian non-fiction", "true stories Australia", "Aussie memoir"],
    "business": ["Australian business", "entrepreneur Australia", "SME Australia"],
    "self_help": ["Australian self-help", "mindset Australia", "personal growth AU"],
    "crime": ["Australian crime fiction", "Aussie detective", "crime thriller Australia"],
    "true_crime": ["Australian true crime", "crime Australia", "unsolved Australia"],
    "outback": ["Outback Australia", "Australian bush", "red centre stories"],
}


def _classify_genre(genre: str) -> str:
    """Map a free-text genre to one of our pricing category keys."""
    genre_lower = genre.lower()
    if "outback" in genre_lower or "bush" in genre_lower:
        return "outback"
    if "true crime" in genre_lower or "true blue crime" in genre_lower:
        return "true_crime"
    if "crime" in genre_lower or "thriller" in genre_lower:
        return "crime"
    if "business" in genre_lower:
        return "business"
    if "self-help" in genre_lower or "self help" in genre_lower or "personal dev" in genre_lower:
        return "self_help"
    if "non-fiction" in genre_lower or "nonfiction" in genre_lower or "non fiction" in genre_lower:
        return "non_fiction"
    if "fiction" in genre_lower or "novel" in genre_lower:
        return "fiction"
    return "non_fiction"  # safe default


def _classify_format(fmt: str) -> str:
    fmt_lower = fmt.lower()
    if "paper" in fmt_lower or "print" in fmt_lower or "pbk" in fmt_lower:
        return "paperback"
    if "box" in fmt_lower or "bundle" in fmt_lower or "set" in fmt_lower:
        return "box_set"
    return "ebook"


def calculate_price(genre: str, format: str = "ebook") -> dict[str, Any]:
    """Return a recommended AUD price and supporting KDP keywords.

    Args:
        genre: Book genre (e.g. "True Blue Crime", "Outback Non-Fiction").
        format: Publication format — "ebook", "paperback", or "box_set".

    Returns:
        dict with recommended_price_aud, currency, format, kdp_keywords, and rationale.
    """
    genre_key = _classify_genre(genre)
    fmt_key = _classify_format(format)

    if fmt_key == "paperback":
        base_price = _PAPERBACK_PRICES.get(genre_key, _PAPERBACK_PRICES["non_fiction"])
    elif fmt_key == "box_set":
        # Box sets are priced from ebook table with a multiplier
        base_price = _EBOOK_PRICES.get("box_set", 12.99)
    else:
        base_price = _EBOOK_PRICES.get(genre_key, _EBOOK_PRICES["non_fiction"])

    kdp_keywords = _KDP_KEYWORDS.get(genre_key, [f"{genre} book", f"Australian {genre}"])

    return {
        "genre": genre,
        "format": fmt_key,
        "recommended_price_aud": base_price,
        "currency": "AUD",
        "kdp_keywords": kdp_keywords,
        "rationale": (
            f"Recommended AUD {base_price:.2f} for a {fmt_key} in the '{genre}' genre, "
            f"based on 2024 Australian reader price sensitivity and comparable titles. "
            f"Use the provided KDP keywords to maximise discoverability on Amazon AU."
        ),
    }
