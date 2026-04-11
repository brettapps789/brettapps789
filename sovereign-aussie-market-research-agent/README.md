# 🇦🇺 The Sovereign Aussie Market Research Agent

**Codename:** Market Research Bruce (`mra_001`)  
**Affiliation:** Fair Dinkum Publishing

## 📌 Overview

This is a Sovereign MCP Server designed to provide high-fidelity market research for the Australian and international publishing markets. Bruce specialises in "True Blue" genres, from Outback Non-Fiction to Crime Fiction.

## 🛠 Capabilities

- **Trend Identification:** Real-time analysis of AU/NZ/UK/US/CA book trends via Google Trends and K-lytics.
- **Competitor Intelligence:** Deep dives into traditional publishers (e.g., Pan Macmillan) vs. Indie authors.
- **Pricing Optimisation:** Dynamic pricing recommendations based on Australian reading habits.
- **Keyword Research:** Targeted keyword extraction for Amazon KDP and Google Trends.

## 🗂 Project Structure

```
sovereign-aussie-market-research-agent/
├── .env.example              # Template for API keys (KDP, Google Trends, etc.)
├── .gitignore                # Standard Python ignore file
├── pyproject.toml            # Dependency management (UV / hatchling)
├── README.md                 # This file
├── config/
│   └── business_context.json # Agent identity & business context
└── src/
    ├── __init__.py
    ├── server.py             # Main MCP Server entry point
    ├── agent_logic.py        # "Market Research Bruce" core reasoning
    └── tools/
        ├── __init__.py
        ├── market_trends.py  # Trend identification tools
        ├── competitors.py    # Competitor analysis tools
        └── pricing.py        # Pricing & keyword research tools
```

## 🚀 Installation

### Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) (recommended) or pip

### Steps

1. Clone the repo:
   ```bash
   git clone https://github.com/brettapps789/sovereign-aussie-market-research-agent
   cd sovereign-aussie-market-research-agent
   ```

2. Install dependencies with UV:
   ```bash
   uv sync
   ```
   Or with pip:
   ```bash
   pip install -e .
   ```

3. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env and fill in your API keys
   ```

4. Run the server:
   ```bash
   python src/server.py
   ```

## 🔌 MCP Configuration

Add to your MCP client settings (e.g. Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aussie-market-research": {
      "command": "python",
      "args": ["/path/to/sovereign-aussie-market-research-agent/src/server.py"]
    }
  }
}
```

## 🛠 Available MCP Tools

| Tool | Description |
|------|-------------|
| `analyze_niche` | Identifies trends and competition levels for a specific book genre |
| `get_pricing_strategy` | Provides recommended AUD pricing based on Australian reading habits |
| `competitor_deep_dive` | Analyses strengths and weaknesses of a specific publisher |

## 🌏 Target Markets

- 🇦🇺 Australia (primary)
- 🇳🇿 New Zealand
- 🇬🇧 United Kingdom
- 🇺🇸 United States
- 🇨🇦 Canada

## 📚 Primary Genres

- Aussie Fiction
- Outback Non-Fiction
- Business & Entrepreneurship
- Self-Help
- True Blue Crime

## 🤝 Contributing

This is a sovereign agent project for Fair Dinkum Publishing. Contact Brett Sjoberg for collaboration enquiries.

## 📄 Licence

MIT © Brett Sjoberg / Fair Dinkum Publishing
