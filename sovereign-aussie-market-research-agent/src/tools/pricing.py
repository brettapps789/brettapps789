"""Pricing and keyword research tools for Market Research Bruce.

Calculates AUD-denominated pricing recommendations based on Australian reading
habits and genre conventions across ebook, paperback, and hardcover formats.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Pricing knowledge base (2024 AU market data)
# ---------------------------------------------------------------------------

_GENRE_BASE_PRICES: dict[str, float] = {
    "fiction": 4.99,
    "crime": 5.99,
    "thriller": 5.99,
    "romance": 3.99,
    "outback": 6.99,
    "non-fiction": 9.99,
    "non_fiction": 9.99,
    "business": 11.99,
    "self-help": 9.99,
    "self_help": 9.99,
    "memoir": 7.99,
    "box_set": 12.99,
    "box set": 12.99,
}

_DEFAULT_EBOOK_PRICE: float = 6.99

# Format multipliers applied on top of the ebook base price
_FORMAT_MULTIPLIERS: dict[str, float] = {
    "ebook": 1.0,
    "paperback": 3.5,
    "hardcover": 5.5,
}

# KDP keyword suggestions per genre
_GENRE_KEYWORDS: dict[str, list[str]] = {
    "fiction": ["Australian fiction", "Aussie novels", "local fiction AU"],
    "crime": ["Australian crime fiction", "true crime Australia", "Aussie noir"],
    "thriller": ["Australian thriller", "outback thriller", "AU suspense"],
    "romance": ["Australian romance", "Aussie love story", "rural romance AU"],
    "outback": ["outback Australia book", "outback adventure", "Australian outback stories"],
    "non-fiction": ["Australian non-fiction", "true stories AU", "Aussie memoir"],
    "business": ["Australian business book", "AU entrepreneurship", "business Australia"],
    "self-help": ["Australian self-help", "personal development AU", "mindset Australia"],
}


def _resolve_genre_key(genre: str) -> str:
    """Find the best matching key in the pricing table for the given genre string."""
    genre_lower = genre.lower().replace("-", "_")
    if genre_lower in _GENRE_BASE_PRICES:
        return genre_lower

    # Partial match
    for key in _GENRE_BASE_PRICES:
        if key.replace("_", " ") in genre_lower or genre_lower in key.replace("_", " "):
            return key

    return ""


def calculate_price(genre: str, format: str = "ebook") -> dict:
    """Calculate a recommended AUD price for a book.

    Args:
        genre: The book genre (e.g. "fiction", "non-fiction", "box_set").
        format: Book format – "ebook", "paperback", or "hardcover" (default "ebook").

    Returns:
        A dict with the recommended AUD price, format, KDP keywords, and rationale.
    """
    resolved_key = _resolve_genre_key(genre)
    base_ebook_price = _GENRE_BASE_PRICES.get(resolved_key, _DEFAULT_EBOOK_PRICE)

    fmt_lower = format.lower()
    multiplier = _FORMAT_MULTIPLIERS.get(fmt_lower, 1.0)
    recommended_price = round(base_ebook_price * multiplier, 2)

    # Suggest KDP keywords
    keyword_key = resolved_key.replace("_", "-") if resolved_key else genre.lower().split()[0]
    keywords = _GENRE_KEYWORDS.get(keyword_key, [f"Australian {genre}", f"{genre} books AU"])

    return {
        "genre": genre,
        "format": fmt_lower,
        "recommended_price_aud": recommended_price,
        "currency": "AUD",
        "kdp_keywords": keywords,
        "rationale": (
            f"Based on 2024 AU {fmt_lower} reading habits for {genre}. "
            f"Base ebook price AUD {base_ebook_price:.2f} × {multiplier} format multiplier."
        ),
    }
