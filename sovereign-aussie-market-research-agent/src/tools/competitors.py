"""Competitor analysis tools for Market Research Bruce.

Provides publisher profiling based on a curated knowledge base of Australian
and international publishing houses, with hooks for live data enrichment.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Curated knowledge base – update as needed
# ---------------------------------------------------------------------------

_PUBLISHER_DB: dict[str, dict] = {
    "pan macmillan australia": {
        "full_name": "Pan Macmillan Australia",
        "type": "Traditional – Big Five affiliate",
        "strengths": [
            "Strong distribution network across AU/NZ",
            "Established brand recognition",
            "Wide genre coverage including literary fiction and crime",
        ],
        "weaknesses": [
            "Slow acquisition process (12–18 months to market)",
            "Lower royalty rates for authors (10–15 %)",
            "Limited focus on niche Aussie genres like Outback Non-Fiction",
        ],
        "market_share_au": "~12 %",
        "notable_authors": ["Garth Nix", "Anna Todd"],
        "kdp_presence": "Low – primarily bricks-and-mortar retail",
    },
    "allen & unwin": {
        "full_name": "Allen & Unwin",
        "type": "Traditional – Independent Australian",
        "strengths": [
            "Australia's largest independent publisher",
            "Strong children's and young adult catalogue",
            "Deep local author relationships",
        ],
        "weaknesses": [
            "Limited global reach compared to Big Five",
            "Selective acquisitions – highly competitive submissions",
        ],
        "market_share_au": "~9 %",
        "notable_authors": ["Tara June Winch", "Richard Flanagan"],
        "kdp_presence": "Low",
    },
    "penguin random house au": {
        "full_name": "Penguin Random House Australia",
        "type": "Traditional – Big Five",
        "strengths": [
            "Largest publisher in Australia by revenue",
            "Global marketing and PR infrastructure",
            "Strong ebook and audiobook distribution",
        ],
        "weaknesses": [
            "Very selective – less than 1 % of submissions accepted",
            "Author autonomy is limited",
            "Slow to adapt to indie and self-publishing trends",
        ],
        "market_share_au": "~22 %",
        "notable_authors": ["Liane Moriarty", "Kate Forsyth"],
        "kdp_presence": "Medium – some titles available on Kindle",
    },
    "indie kdp author": {
        "full_name": "Indie / Self-Published (KDP)",
        "type": "Self-Published",
        "strengths": [
            "Up to 70 % royalty on KDP ebooks",
            "Full creative and pricing control",
            "Fast time-to-market (days vs. years)",
            "Direct reader relationships",
        ],
        "weaknesses": [
            "No advance payment",
            "Self-funded marketing and editing",
            "Discoverability challenges in crowded categories",
        ],
        "market_share_au": "~18 % (growing)",
        "notable_authors": ["Various"],
        "kdp_presence": "High",
    },
}

_DEFAULT_PROFILE: dict = {
    "type": "Unknown",
    "strengths": ["Established market presence"],
    "weaknesses": ["Limited public data available"],
    "market_share_au": "Unknown",
    "notable_authors": [],
    "kdp_presence": "Unknown",
}


def analyze_publisher(publisher_name: str) -> dict:
    """Analyse the competitive profile of a publisher.

    Looks up the publisher in the curated knowledge base and returns a
    structured profile. Falls back to a generic profile for unknown publishers.

    Args:
        publisher_name: The name of the publisher to analyse.

    Returns:
        A dict containing type, strengths, weaknesses, market share, and
        KDP presence for the requested publisher.
    """
    key = publisher_name.strip().lower()
    profile = _PUBLISHER_DB.get(key, None)

    if profile is None:
        # Partial match fallback
        for db_key, db_profile in _PUBLISHER_DB.items():
            if db_key in key or key in db_key:
                profile = db_profile
                break

    if profile is None:
        profile = {**_DEFAULT_PROFILE, "full_name": publisher_name}

    return {
        "publisher": profile.get("full_name", publisher_name),
        "type": profile.get("type"),
        "strengths": profile.get("strengths", []),
        "weaknesses": profile.get("weaknesses", []),
        "market_share_au": profile.get("market_share_au"),
        "notable_authors": profile.get("notable_authors", []),
        "kdp_presence": profile.get("kdp_presence"),
        "source": "Fair Dinkum Publishing knowledge base",
    }
