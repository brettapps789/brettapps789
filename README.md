<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Ebook Building AI Agent Workforce

A Next.js application powered by the **OpenAI Agents SDK**, **Model Context Protocol (MCP)**, and multi-agent handoffs. The app orchestrates a workforce of AI agents that can write and compile EPUB ebooks, build GitHub-hosted landing pages, and help with market research, advertising, and Stripe monetization.

View your app in AI Studio: https://ai.studio/apps/5434dee8-b8cc-4076-ab05-32b4424b333b

## Table of Contents

- [Run Locally](#run-locally)
- [Architecture Overview](#architecture-overview)
- [MCP Servers](#mcp-servers)
  - [Built-in Node.js MCP Servers](#built-in-nodejs-mcp-servers)
  - [Adding a Custom Python MCP Server](#adding-a-custom-python-mcp-server)
- [AI Agents](#ai-agents)
- [Environment Variables](#environment-variables)

---

## Run Locally

**Prerequisites:** Node.js

1. Install dependencies:
   ```bash
   npm install
   ```
2. Copy `.env.example` to `.env.local` and fill in your API keys (see [Environment Variables](#environment-variables)):
   ```bash
   cp .env.example .env.local
   ```
3. Run the app:
   ```bash
   npm run dev
   ```

---

## Architecture Overview

The application uses the [OpenAI Agents SDK](https://github.com/openai/openai-agents-js) to create a primary **Ebook Building AI Agent Workforce** that can delegate to specialized sub-agents via handoffs. MCP (Model Context Protocol) servers give the primary agent access to the local filesystem and the GitHub API.

```
User Prompt
    │
    ▼
Ebook Building AI Agent Workforce
    ├── MCP: server-filesystem  (read/write local files)
    ├── MCP: server-github      (create repos, push files)
    ├── Tool: compile_epub      (generate EPUB files)
    ├── Tool: enable_github_pages
    │
    └── Handoffs ──► Market Research Agent
                 ──► Advertising Agent
                 ──► Stripe Agent
```

---

## MCP Servers

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open standard that lets AI agents securely connect to external data sources and tools. This app launches MCP servers as child processes over **stdio** using `MCPServerStdio` from the OpenAI Agents SDK.

### Built-in Node.js MCP Servers

Two MCP servers are started automatically on each API request in [`app/api/chat/route.ts`](app/api/chat/route.ts):

| Server | Package | Purpose |
|--------|---------|---------|
| **Filesystem MCP Server** | `@modelcontextprotocol/server-filesystem` | Reads and writes files inside the `sample_files/` directory |
| **GitHub MCP Server** | `@modelcontextprotocol/server-github` | Manages repositories, branches, and file contents via the GitHub API |

### Adding a Custom Python MCP Server

You can extend the agent with your own tools by writing a Python MCP server using the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) and connecting it via `MCPServerStdio`.

#### 1. Install the Python SDK

We recommend [uv](https://docs.astral.sh/uv/) for Python project management:

```bash
uv init my-mcp-server
cd my-mcp-server
uv add "mcp[cli]"
```

Or with pip:

```bash
pip install "mcp[cli]"
```

#### 2. Write a FastMCP Server

Create a file (e.g., `my_mcp_server.py`) that exposes tools using the `FastMCP` high-level API:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Custom Server")

@mcp.tool()
def word_count(text: str) -> int:
    """Count the number of words in a string."""
    return len(text.split())

@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Run it in **stdio** mode so it can be launched as a subprocess:

```bash
python my_mcp_server.py
# or with uv:
uv run my_mcp_server.py
```

#### 3. Connect to the OpenAI Agents SDK

In [`app/api/chat/route.ts`](app/api/chat/route.ts), add an `MCPServerStdio` instance pointing to your Python server and pass it to your agent's `mcpServers` array:

```typescript
import { Agent, MCPServerStdio, run } from "@openai/agents";
import path from "path";

// Replace this with the actual path to your Python server file.
// process.cwd() resolves to the project root at runtime in Next.js.
const pythonServerPath = path.join(process.cwd(), "my-mcp-server", "my_mcp_server.py");

const pythonServer = new MCPServerStdio({
  name: "My Custom Python Server",
  fullCommand: `python ${pythonServerPath}`,
  // If using uv:
  // fullCommand: `uv run ${pythonServerPath}`,
});

await pythonServer.connect();

const agent = new Agent({
  name: "My Agent",
  instructions: "...",
  mcpServers: [server, githubServer, pythonServer],
  // ...
});

// Remember to close the server when done:
result.completed.finally(() => {
  pythonServer.close().catch(console.error);
});
```

The agent will automatically discover all tools registered on your Python server and can call them just like built-in tools.

#### FastMCP Features

The Python SDK's `FastMCP` class supports:

| Feature | Description |
|---------|-------------|
| **Tools** | Functions the LLM can call to perform actions or computation |
| **Resources** | Data endpoints (like GET routes) for loading context into the LLM |
| **Prompts** | Reusable prompt templates |
| **Structured Output** | Return Pydantic models, TypedDicts, or dataclasses — automatically validated |
| **Progress Reporting** | Stream progress updates via `ctx.report_progress()` |
| **Lifespan Management** | Initialize/teardown shared resources (DB connections, HTTP clients, etc.) |

For full documentation see the [MCP Python SDK README](https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md).

---

## AI Agents

| Agent | Role |
|-------|------|
| **Ebook Building AI Agent Workforce** | Primary agent — writes chapters, compiles EPUBs, creates GitHub repos and GitHub Pages sites |
| **Market Research Agent** | Analyzes top-selling genres, pricing, and reader preferences |
| **Advertising Agent** | Designs campaigns on Amazon Ads, Facebook/Instagram, and Google Ads |
| **Stripe Agent** | Generates Stripe Buy Button HTML snippets for landing pages |

---

## Environment Variables

Copy `.env.example` to `.env.local` and set the following:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key for the Agents SDK |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | ✅ | GitHub classic PAT with `repo` scope ([create one](https://github.com/settings/tokens)) |
| `GEMINI_API_KEY` | Optional | Gemini API key used to AI-generate EPUB cover images |
| `APP_URL` | Optional | The URL where this app is hosted (injected automatically by AI Studio) |
