"""
agents/analyst_agent.py

MCP @Analyst Agent – processes data from Google Sheets/Drive and generates
insights via Vertex AI.

Knowledge Base:
- Understands tabular data schemas from Google Sheets.
- Knows how to frame prompts for Vertex AI Gemini models.
- Produces structured analysis reports consumable by @Manager and @Writer.
- Can summarize, classify, or forecast based on raw data rows.
"""

import asyncio
import logging
from typing import Any

from utils.google_workspace import GoogleWorkspaceHelper
from utils.vertex_ai import VertexAIHelper

logger = logging.getLogger(__name__)


class AnalystAgent:
    """
    Async MCP @Analyst agent.

    Responsibilities:
      - Fetch raw data from Google Sheets or Drive.
      - Send structured prompts to Vertex AI for reasoning/analysis.
      - Write analysis results back to Google Sheets.
      - Return structured insights to the orchestrator.
    """

    def __init__(
        self,
        workspace: GoogleWorkspaceHelper,
        vertex: VertexAIHelper,
        sheet_id: str,
    ) -> None:
        self.workspace = workspace
        self.vertex = vertex
        self.sheet_id = sheet_id

    # ------------------------------------------------------------------
    # Public async interface
    # ------------------------------------------------------------------

    async def analyze_sheet_data(
        self,
        range_notation: str = "Sheet1!A1:Z100",
        prompt_prefix: str = "Analyze the following business data and provide key insights:",
    ) -> dict[str, Any]:
        """
        Read *range_notation* from the configured sheet, forward the data to
        Vertex AI with *prompt_prefix*, and return the model's insight.
        """
        logger.info("[Analyst] Fetching sheet data from range %s", range_notation)
        rows = await asyncio.to_thread(
            self.workspace.read_sheet_rows,
            spreadsheet_id=self.sheet_id,
            range_notation=range_notation,
        )

        data_text = "\n".join(["\t".join(str(c) for c in row) for row in rows])
        full_prompt = f"{prompt_prefix}\n\n{data_text}"

        logger.info("[Analyst] Sending %d rows to Vertex AI", len(rows))
        insight = await asyncio.to_thread(
            self.vertex.generate_text,
            prompt=full_prompt,
        )

        return {
            "agent": "Analyst",
            "action": "analyze_sheet_data",
            "rows_analyzed": len(rows),
            "insight": insight,
        }

    async def write_analysis_row(self, analysis: str) -> dict[str, Any]:
        """
        Append a one-row summary of *analysis* to the configured sheet.
        """
        logger.info("[Analyst] Writing analysis row to sheet")
        await asyncio.to_thread(
            self.workspace.append_sheet_row,
            spreadsheet_id=self.sheet_id,
            values=["Analysis", analysis],
        )
        return {"agent": "Analyst", "action": "write_analysis_row"}

    async def summarize_drive_file(self, file_id: str) -> dict[str, Any]:
        """
        Download a text/plain file from Drive and summarize it with Vertex AI.
        """
        logger.info("[Analyst] Fetching Drive file %s for summarization", file_id)
        content = await asyncio.to_thread(
            self.workspace.download_drive_file,
            file_id=file_id,
        )
        prompt = f"Summarize the following document concisely:\n\n{content}"
        summary = await asyncio.to_thread(
            self.vertex.generate_text,
            prompt=prompt,
        )
        return {
            "agent": "Analyst",
            "action": "summarize_drive_file",
            "file_id": file_id,
            "summary": summary,
        }
