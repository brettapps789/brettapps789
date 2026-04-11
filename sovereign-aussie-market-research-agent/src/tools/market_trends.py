"""Market trend identification tools for Market Research Bruce.

Uses the pytrends library to fetch Google Trends data for book genres
across AU, NZ, UK, US, and CA markets.
"""

from __future__ import annotations

import os

# pytrends is an optional dependency; gracefully degrade if not installed
try:
    from pytrends.request import TrendReq
    _PYTRENDS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PYTRENDS_AVAILABLE = False

# Mapping from two-letter market code to Google geo code
_MARKET_GEO: dict[str, str] = {
    "AU": "AU",
    "NZ": "NZ",
    "UK": "GB",
    "US": "US",
    "CA": "CA",
}

# Approximate competition benchmarks by genre keyword
_COMPETITION_BENCHMARKS: dict[str, str] = {
    "fiction": "high",
    "crime": "high",
    "thriller": "high",
    "romance": "high",
    "non-fiction": "medium",
    "outback": "low",
    "business": "medium",
    "self-help": "medium",
    "memoir": "medium",
    "poetry": "low",
}


def _estimate_competition(genre: str) -> str:
    """Return a rough competition level based on known genre benchmarks."""
    genre_lower = genre.lower()
    for keyword, level in _COMPETITION_BENCHMARKS.items():
        if keyword in genre_lower:
            return level
    return "medium"


def get_trend_report(genre: str, target_market: str = "AU") -> dict:
    """Fetch a Google Trends interest report for a book genre in a given market.

    Args:
        genre: The book genre to search for (e.g. "Outback Non-Fiction").
        target_market: Two-letter country code (default "AU").

    Returns:
        A dict containing average interest score (0–100), related topics,
        competition level, and the data source used.
    """
    geo = _MARKET_GEO.get(target_market.upper(), "AU")
    competition = _estimate_competition(genre)

    if _PYTRENDS_AVAILABLE:
        try:
            pytrends = TrendReq(hl="en-AU", tz=570)  # ACST offset
            pytrends.build_payload([genre], cat=0, timeframe="today 12-m", geo=geo)
            interest_df = pytrends.interest_over_time()

            if not interest_df.empty and genre in interest_df.columns:
                average_interest = int(interest_df[genre].mean())
                related_topics_resp = pytrends.related_topics()
                top_topics = []
                if genre in related_topics_resp:
                    top_df = related_topics_resp[genre].get("top")
                    if top_df is not None and not top_df.empty:
                        top_topics = top_df["topic_title"].head(5).tolist()
            else:
                average_interest = 50
                top_topics = []

            return {
                "genre": genre,
                "market": target_market,
                "average_interest": average_interest,
                "top_related_topics": top_topics,
                "competition_level": competition,
                "source": "Google Trends (live)",
            }

        except Exception as exc:  # noqa: BLE001
            # Fall back to mock data on any API error
            return _mock_trend_report(genre, target_market, competition, str(exc))

    return _mock_trend_report(genre, target_market, competition)


def _mock_trend_report(
    genre: str,
    target_market: str,
    competition: str,
    error: str | None = None,
) -> dict:
    """Return a realistic mock trend report when live data is unavailable."""
    mock_interest: dict[str, int] = {
        "AU": 62,
        "NZ": 55,
        "UK": 70,
        "US": 75,
        "CA": 58,
    }
    result = {
        "genre": genre,
        "market": target_market,
        "average_interest": mock_interest.get(target_market.upper(), 60),
        "top_related_topics": [
            f"{genre} books",
            f"best {genre} authors",
            f"{genre} Amazon",
            f"Australian {genre}",
            f"{genre} 2024",
        ],
        "competition_level": competition,
        "source": "Mock data (pytrends unavailable)",
    }
    if error:
        result["warning"] = f"Live fetch failed: {error}"
    return result
