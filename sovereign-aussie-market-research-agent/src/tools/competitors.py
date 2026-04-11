"""Competitor analysis tool for the Sovereign Aussie Market Research Agent."""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Static knowledge base of known publishers
# ---------------------------------------------------------------------------

_PUBLISHER_DB: dict[str, dict[str, Any]] = {
    "pan macmillan": {
        "type": "Traditional",
        "market_share_au": "~8%",
        "strengths": [
            "Extensive retail distribution across AU/NZ",
            "Strong brand recognition and media relationships",
            "Large marketing budgets for frontlist titles",
            "Deep backlist in crime, fiction, and non-fiction",
        ],
        "weaknesses": [
            "Slow publishing timelines (12–24 months from acquisition)",
            "Low royalty rates for authors (8–15%)",
            "Limited flexibility for niche/regional genres",
            "Risk-averse — prefers established authors",
        ],
        "key_genres": ["Literary Fiction", "Crime", "Non-Fiction", "Children's"],
        "indie_threat_level": "Medium",
    },
    "allen & unwin": {
        "type": "Independent Traditional",
        "market_share_au": "~10%",
        "strengths": [
            "Australia's largest independent publisher",
            "Strong local author focus",
            "Respected imprints across fiction and non-fiction",
        ],
        "weaknesses": [
            "Limited international reach compared to global publishers",
            "Selective acquisitions — high rejection rate",
        ],
        "key_genres": ["Australian Fiction", "History", "Politics", "Self-Help"],
        "indie_threat_level": "Medium",
    },
    "amazon kdp": {
        "type": "Self-Publishing Platform",
        "market_share_au": "~35% (ebook)",
        "strengths": [
            "70% royalty rate on ebooks (AUD 2.99–9.99)",
            "Fast time-to-market (24–72 hours)",
            "Global distribution with AU marketplace",
            "Kindle Unlimited for discoverability",
        ],
        "weaknesses": [
            "Crowded marketplace — discoverability challenge",
            "Limited print retail distribution outside Amazon",
            "Algorithm-dependent visibility",
        ],
        "key_genres": ["Romance", "Thriller", "Non-Fiction", "Self-Help"],
        "indie_threat_level": "Low",  # It's the indie platform itself
    },
}


def _normalise_name(name: str) -> str:
    return name.lower().strip()


def analyze_publisher(publisher_name: str) -> dict[str, Any]:
    """Analyse a publisher's competitive position in the Australian market.

    Args:
        publisher_name: Name of the publisher to analyse.

    Returns:
        dict with publisher profile including strengths, weaknesses, and
        recommendations for Fair Dinkum Publishing.
    """
    norm = _normalise_name(publisher_name)

    # Try exact match first, then partial
    profile = _PUBLISHER_DB.get(norm)
    if profile is None:
        for key, data in _PUBLISHER_DB.items():
            if key in norm or norm in key:
                profile = data
                break

    if profile is None:
        return {
            "publisher": publisher_name,
            "status": "Not in knowledge base",
            "recommendation": (
                "No data available for this publisher. Consider researching their "
                "catalogue on Nielsen BookData or the ABA (Australian Booksellers Association)."
            ),
        }

    return {
        "publisher": publisher_name,
        "type": profile["type"],
        "market_share_au": profile["market_share_au"],
        "strengths": profile["strengths"],
        "weaknesses": profile["weaknesses"],
        "key_genres": profile["key_genres"],
        "indie_threat_level": profile["indie_threat_level"],
        "recommendation": (
            f"As an indie publisher, Fair Dinkum Publishing can exploit "
            f"{publisher_name}'s weaknesses ({profile['weaknesses'][0].lower()}) "
            f"by publishing faster, targeting niche AU genres, and offering better "
            f"author royalty terms."
        ),
    }
