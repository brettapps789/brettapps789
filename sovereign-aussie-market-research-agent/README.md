# 🇦🇺 The Sovereign Aussie Market Research Agent

**Codename:** Market Research Bruce (`mra_001`)  
**Affiliation:** Fair Dinkum Publishing

## 📌 Overview

This is a Sovereign MCP Server designed to provide high-fidelity market research for the
Australian and international publishing markets. Bruce specialises in "True Blue" genres,
from Outback Non-Fiction to Crime Fiction.

## 🛠 Capabilities

- **Trend Identification:** Real-time analysis of AU/NZ/UK/US/CA book trends.
- **Competitor Intelligence:** Deep dives into traditional publishers (e.g., Pan Macmillan) vs. Indie authors.
- **Pricing Optimisation:** Dynamic pricing recommendations based on Australian reading habits.
- **Keyword Research:** Targeted keyword extraction for Amazon KDP and Google Trends.

## 🚀 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/brettapps789/brettapps789
   cd brettapps789/sovereign-aussie-market-research-agent
   ```

2. Install dependencies (using [UV](https://github.com/astral-sh/uv)):
   ```bash
   uv sync
   ```
   Or with pip:
   ```bash
   pip install -e .
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and fill in your API keys
   ```

4. Add to your MCP settings:
   ```json
   "mcpServers": {
     "aussie-market-research": {
       "command": "python",
       "args": ["/path/to/sovereign-aussie-market-research-agent/src/server.py"]
     }
   }
   ```

## 🧰 MCP Tools Exposed

| Tool | Description |
|------|-------------|
| `analyze_niche` | Identifies trends and competition levels for a specific book genre |
| `get_pricing_strategy` | Provides recommended AUD pricing based on Australian reading habits |
| `competitor_deep_dive` | Analyses strengths and weaknesses of a specific publisher |

## 🗂 Project Structure

```
sovereign-aussie-market-research-agent/
├── .env.example              # Template for API keys
├── .gitignore
├── pyproject.toml            # Dependency management (UV/Poetry)
├── README.md
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

## 🤝 Contributing

Pull requests welcome. Please ensure new tools follow the existing pattern in `src/tools/`.

## 📄 Licence

MIT © Brett Sjoberg / Fair Dinkum Publishing
