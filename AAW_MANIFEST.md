# 🛠️ The AI Agent Workforce (AAW) Manifest

> A structured pipeline of 14 specialized AI agents that automate the end-to-end workflow from research to revenue — for digital products, eBooks, landing pages, and beyond.

---

## 🗂️ Agent Directory

| # | Agent | Repo Name | Role | Primary Capabilities |
|---|-------|-----------|------|----------------------|
| 1 | [Research Agent](agents/aaw-research-agent.md) | `aaw-research-agent` | Data Intelligence | Keyword research, competitor analysis, audience pain points |
| 2 | [Market Analysis Agent](agents/aaw-market-analysis-agent.md) | `aaw-market-analysis-agent` | Positioning & Strategy | Niche scoring, title generation, audience segmentation & pricing |
| 3 | [Writing Agent](agents/aaw-writing-agent.md) | `aaw-writing-agent` | Content Generation | Chapter drafting, SEO keyword integration, tone adaptation |
| 4 | [Editing Agent](agents/aaw-editing-agent.md) | `aaw-editing-agent` | Quality Refinement | Grammar/flow enhancement, content expansion, structural optimization |
| 5 | [Fact-Checking Agent](agents/aaw-fact-checking-agent.md) | `aaw-fact-checking-agent` | Accuracy & Trust | Claim verification, citations, legal disclaimers, human-review flags |
| 6 | [Design Agent](agents/aaw-design-agent.md) | `aaw-design-agent` | Visual Identity | Cover art prompts, SVG generation, color palette & font selection |
| 7 | [Formatting Agent](agents/aaw-formatting-agent.md) | `aaw-formatting-agent` | Distribution Prep | PDF/EPUB/HTML export, brand headers/footers, device optimization |
| 8 | [Web Dev Agent](agents/aaw-web-dev-agent.md) | `aaw-web-dev-agent` | Landing Page Construction | HTML/CSS/JS generation, responsive layouts, hero & CTA sections |
| 9 | [SEO Agent](agents/aaw-seo-agent.md) | `aaw-seo-agent` | Search Visibility | Meta tags, Schema.org markup, heading structure, alt-text |
| 10 | [Integration Agent](agents/aaw-integration-agent.md) | `aaw-integration-agent` | Payment & Logic | Stripe checkout, payment redirects, HTTPS/security verification |
| 11 | [Deployment Agent](agents/aaw-deployment-agent.md) | `aaw-deployment-agent` | Cloud Launch | GitHub repo creation, GitHub Pages activation, custom domains |
| 12 | [CI/CD Agent](agents/aaw-cicd-agent.md) | `aaw-cicd-agent` | Automation | GitHub Actions YAML, asset minification, build monitoring |
| 13 | [Testing Agent](agents/aaw-testing-agent.md) | `aaw-testing-agent` | Quality Assurance | Broken links, responsiveness audits, Stripe simulation, WCAG checks |
| 14 | [Analytics Agent](agents/aaw-analytics-agent.md) | `aaw-analytics-agent` | Performance Tracking | GA4 embedding, KPI definition, performance reporting |

---

## 🔄 Pipeline Flow

```
Research Agent
    └─► Market Analysis Agent
            ├─► Writing Agent
            │       └─► Editing Agent
            │               └─► Fact-Checking Agent
            │                       └─► Formatting Agent ──────────┐
            ├─► Design Agent                                        │
            │       └─► Formatting Agent (design system)           │
            │       └─► Web Dev Agent                              │
            └─► Integration Agent                                   │
                    └─► Web Dev Agent                              │
                            └─► SEO Agent                          │
                                    └─► Deployment Agent ◄─────────┘
                                            └─► CI/CD Agent
                                            └─► Analytics Agent
                                                    └─► Testing Agent
                                                    └─► (feeds back to Research & Market Analysis)
```

---

## 🏷️ Naming Convention

All agent repositories follow a consistent pattern so the Orchestrator can locate them programmatically:

```
Pattern:  aaw-[agent-name]-agent
Examples: aaw-research-agent
          aaw-market-analysis-agent
          aaw-web-dev-agent
          aaw-cicd-agent
```

---

## 🚀 Quick Start

1. Clone or fork this manifest repo.
2. Browse the `agents/` directory for individual agent specs.
3. Use the pipeline flow above to understand how agents hand off work to each other.
4. Configure your Orchestrator to call agents in pipeline order using the naming convention above.

---

## 📁 Repository Structure

```
brettapps789/
├── AAW_MANIFEST.md          ← You are here
├── agents/
│   ├── aaw-research-agent.md
│   ├── aaw-market-analysis-agent.md
│   ├── aaw-writing-agent.md
│   ├── aaw-editing-agent.md
│   ├── aaw-fact-checking-agent.md
│   ├── aaw-design-agent.md
│   ├── aaw-formatting-agent.md
│   ├── aaw-web-dev-agent.md
│   ├── aaw-seo-agent.md
│   ├── aaw-integration-agent.md
│   ├── aaw-deployment-agent.md
│   ├── aaw-cicd-agent.md
│   ├── aaw-testing-agent.md
│   └── aaw-analytics-agent.md
└── README.md
```

---

*Built for brettapps789 — AI Agent Workforce v1.0*
