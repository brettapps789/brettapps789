<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# 🛠️ AI Agent Workforce (AAW) + AI Studio App

> **New:** The [AI Agent Workforce Manifest](AAW_MANIFEST.md) — 14 specialized agents covering the full pipeline from research to revenue.

---

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/5434dee8-b8cc-4076-ab05-32b4424b333b

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`

---

## Agent Workforce (AAW) – Phase 2

### Overview

The Agent Workforce (AAW) is a Python-based multi-MCP orchestration layer that lives alongside the Next.js application. It exposes three async agents—**@Manager**, **@Writer**, and **@Analyst**—connected to Google Workspace, Stripe, and Vertex AI.

```
agents/
├── manager_agent.py    # @Manager – billing, Sheets, Drive
├── writer_agent.py     # @Writer  – Docs, Gmail
└── analyst_agent.py    # @Analyst – Vertex AI reasoning

utils/
├── google_workspace.py # Sheets / Docs / Gmail / Drive helpers
├── stripe_api.py       # Stripe customer + subscription helpers
└── vertex_ai.py        # Vertex AI Gemini generation helpers

orchestrator.py         # Async orchestration entry point
test_workflow.py        # E2E mock tests (pytest)
build.json              # Environment and project scaffold
dependency_lock.txt     # Python dependency list
wire_scaffold.mmd       # Mermaid system diagram
agent_mindmap.mmd       # Mermaid mind map
```

### Agent Logic Flow

```
Orchestrator
  │
  ├─► @Manager
  │     ├── Stripe: create/retrieve subscription
  │     └── Google Sheets: write billing row to dashboard
  │
  ├─► @Analyst
  │     ├── Google Sheets: read all rows
  │     ├── Vertex AI (Gemini): generate insight from data
  │     └── Google Sheets: write analysis row
  │
  └─► @Writer
        ├── Google Docs: create summary document
        └── Gmail: send notification email
```

### Python Setup

**Prerequisites:** Python 3.10+, a GCP service account with access to Sheets, Docs, Drive, and Gmail APIs.

1. Install dependencies:
   ```bash
   pip install -r dependency_lock.txt
   ```

2. Copy the environment template and fill in your values:
   ```bash
   cp .env.example .env
   # Edit .env with real credentials (see build.json for the full list)
   ```

3. Run the full workflow demo:
   ```bash
   python orchestrator.py
   ```

4. Run the E2E test suite (no real credentials needed):
   ```bash
   pytest test_workflow.py -v
   ```

### Required Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON |
| `GOOGLE_SHEET_ID` | Target Google Sheets spreadsheet ID |
| `GOOGLE_DRIVE_FOLDER_ID` | Target Google Drive folder ID |
| `STRIPE_API_KEY` | Stripe secret key (`sk_...`) |
| `VERTEX_AI_PROJECT` | GCP project ID for Vertex AI |
| `VERTEX_AI_LOCATION` | Vertex AI region (e.g. `us-central1`) |
| `VERTEX_AI_MODEL` | Gemini model name (e.g. `gemini-1.5-pro`) |
| `GMAIL_SENDER` | Gmail address used as the sender |
