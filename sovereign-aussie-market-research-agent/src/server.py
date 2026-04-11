"""Main MCP Server entry point for Market Research Bruce (mra_001)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from tools import competitors, market_trends, pricing

# ---------------------------------------------------------------------------
# Initialise MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP("Sovereign Aussie Market Research")

# Load business context so Bruce always remembers who he is
_config_path = Path(__file__).parent.parent / "config" / "business_context.json"
with open(_config_path, "r", encoding="utf-8") as _f:
    BUSINESS_CONTEXT: dict = json.load(_f)


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def analyze_niche(genre: str, target_market: str = "AU") -> dict:
    """Identify trends and competition levels for a specific book genre.

    Args:
        genre: The book genre to analyse (e.g. "Outback Non-Fiction").
        target_market: Two-letter country code for the target market (default "AU").

    Returns:
        A trend report dict with interest scores, related topics, and competition level.
    """
    return market_trends.get_trend_report(genre, target_market)


@mcp.tool()
async def get_pricing_strategy(genre: str, format: str = "ebook") -> dict:
    """Provide a recommended AUD pricing strategy based on Australian reading habits.

    Args:
        genre: The book genre (e.g. "fiction", "non_fiction", "box_set").
        format: Book format – "ebook", "paperback", or "hardcover" (default "ebook").

    Returns:
        A pricing recommendation dict with AUD price and rationale.
    """
    return pricing.calculate_price(genre, format)


@mcp.tool()
async def competitor_deep_dive(publisher_name: str) -> dict:
    """Analyse the strengths and weaknesses of a specific publisher.

    Args:
        publisher_name: The name of the publisher to analyse.

    Returns:
        A competitor analysis dict with strengths, weaknesses, and market position.
    """
    return competitors.analyze_publisher(publisher_name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
