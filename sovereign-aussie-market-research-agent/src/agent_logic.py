"""Market Research Bruce — core reasoning and agent identity."""

import json
import os
from pathlib import Path


_CONTEXT_PATH = Path(__file__).parent.parent / "config" / "business_context.json"


def load_business_context() -> dict:
    """Load the agent's business context from the config file."""
    with open(_CONTEXT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class MarketResearchBruce:
    """Core agent class for Market Research Bruce (mra_001)."""

    def __init__(self):
        self.context = load_business_context()
        self.agent_id = self.context["agent_id"]
        self.agent_name = self.context["agent_name"]
        self.business = self.context["business_context"]

    @property
    def primary_genres(self) -> list[str]:
        return self.business.get("primary_genres", [])

    @property
    def target_markets(self) -> list[str]:
        return self.business.get("target_markets", ["AU"])

    def get_identity_summary(self) -> dict:
        """Return a summary of the agent's identity for context injection."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "company": self.business.get("company_name"),
            "owner": self.business.get("owner"),
            "primary_genres": self.primary_genres,
            "target_markets": self.target_markets,
        }

    def is_relevant_genre(self, genre: str) -> bool:
        """Check whether a genre aligns with Fair Dinkum Publishing's catalogue."""
        genre_lower = genre.lower()
        return any(g.lower() in genre_lower or genre_lower in g.lower() for g in self.primary_genres)


# Singleton instance used by tools and the server
bruce = MarketResearchBruce()
