"""Main MCP Server entry point for the Sovereign Aussie Market Research Agent."""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from tools import competitors, market_trends, pricing

# ---------------------------------------------------------------------------
# Initialise MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP("Sovereign Aussie Market Research")

# Load business context so the server knows its identity at startup
_context_path = Path(__file__).parent.parent / "config" / "business_context.json"
with open(_context_path, "r", encoding="utf-8") as _f:
    context = json.load(_f)


# ---------------------------------------------------------------------------
# MCP Tool Definitions
# ---------------------------------------------------------------------------

@mcp.tool()
async def analyze_niche(genre: str, target_market: str = "AU") -> dict:
    """Identify trends and competition levels for a specific book genre.

    Args:
        genre: The book genre to analyse (e.g. "Outback Non-Fiction").
        target_market: Two-letter market code — AU, NZ, UK, US, or CA.

    Returns:
        A trend report dict with interest scores, top keywords, and competition level.
    """
    return market_trends.get_trend_report(genre, target_market)


@mcp.tool()
async def get_pricing_strategy(genre: str, format: str = "ebook") -> dict:
    """Provide recommended AUD pricing based on Australian reading habits.

    Args:
        genre: The book genre (e.g. "True Blue Crime").
        format: One of "ebook", "paperback", or "box_set".

    Returns:
        A pricing recommendation dict including price, currency, and rationale.
    """
    return pricing.calculate_price(genre, format)


@mcp.tool()
async def competitor_deep_dive(publisher_name: str) -> dict:
    """Analyse the strengths and weaknesses of a specific publisher.

    Args:
        publisher_name: Name of the publisher to analyse (e.g. "Pan Macmillan").

    Returns:
        A competitor profile dict with strengths, weaknesses, and market share notes.
    """
    return competitors.analyze_publisher(publisher_name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
