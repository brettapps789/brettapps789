"""Core reasoning module for Market Research Bruce (mra_001).

This module provides the high-level orchestration logic that combines data from
the individual tool modules into cohesive research reports.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools import competitors, market_trends, pricing

# Load business identity
_config_path = Path(__file__).parent.parent / "config" / "business_context.json"
with open(_config_path, "r", encoding="utf-8") as _f:
    AGENT_CONTEXT: dict = json.load(_f)

AGENT_NAME = AGENT_CONTEXT.get("agent_name", "Market Research Bruce")
PRIMARY_GENRES: list[str] = AGENT_CONTEXT["business_context"].get("primary_genres", [])
TARGET_MARKETS: list[str] = AGENT_CONTEXT["business_context"].get("target_markets", ["AU"])


def full_market_report(genre: str) -> dict:
    """Generate a comprehensive market research report for a given genre.

    Combines trend analysis, competitor intelligence, and pricing recommendations
    into a single structured report.

    Args:
        genre: The book genre to research.

    Returns:
        A dict containing trend data, competitor analysis, and pricing strategy
        for the requested genre across all configured target markets.
    """
    report: dict = {
        "agent": AGENT_NAME,
        "genre": genre,
        "markets": {},
        "pricing": {},
        "competitors": {},
    }

    for market in TARGET_MARKETS:
        report["markets"][market] = market_trends.get_trend_report(genre, market)

    for fmt in ("ebook", "paperback"):
        report["pricing"][fmt] = pricing.calculate_price(genre, fmt)

    # Analyse a selection of well-known Australian and international publishers
    key_publishers = ["Pan Macmillan Australia", "Allen & Unwin", "Penguin Random House AU"]
    for pub in key_publishers:
        report["competitors"][pub] = competitors.analyze_publisher(pub)

    return report


def genre_opportunity_score(genre: str, target_market: str = "AU") -> dict:
    """Calculate an opportunity score (0–100) for a genre in a given market.

    The score is a simple weighted combination of trend interest and inverse
    competition level.

    Args:
        genre: The book genre to evaluate.
        target_market: Two-letter country code (default "AU").

    Returns:
        A dict with the numeric score and a plain-English recommendation.
    """
    trend_data = market_trends.get_trend_report(genre, target_market)
    interest = trend_data.get("average_interest", 50)
    competition = trend_data.get("competition_level", "medium")

    competition_penalty = {"low": 0, "medium": 20, "high": 40}.get(competition, 20)
    score = max(0, min(100, int(interest) - competition_penalty))

    if score >= 70:
        recommendation = "Strong opportunity – consider prioritising this genre."
    elif score >= 40:
        recommendation = "Moderate opportunity – proceed with targeted keyword strategy."
    else:
        recommendation = "Low opportunity – consider pivoting or niching down further."

    return {
        "genre": genre,
        "market": target_market,
        "opportunity_score": score,
        "recommendation": recommendation,
    }
