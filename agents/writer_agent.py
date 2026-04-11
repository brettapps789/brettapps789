"""
agents/writer_agent.py

MCP @Writer Agent – generates Google Docs and sends Gmail notifications.

Knowledge Base:
- Understands Google Docs content structure and formatting.
- Knows Gmail MIME structure for composing plain-text and HTML emails.
- Receives context (subject, body, recipient) from the orchestrator.
- Delegates data insights to @Analyst when additional context is needed.
"""

import asyncio
import logging
from typing import Any

from utils.google_workspace import GoogleWorkspaceHelper

logger = logging.getLogger(__name__)


class WriterAgent:
    """
    Async MCP @Writer agent.

    Responsibilities:
      - Create and append content to Google Docs.
      - Send Gmail notifications and summary emails.
      - Format content for human readability.
    """

    def __init__(self, workspace: GoogleWorkspaceHelper, gmail_sender: str) -> None:
        self.workspace = workspace
        self.gmail_sender = gmail_sender

    # ------------------------------------------------------------------
    # Public async interface
    # ------------------------------------------------------------------

    async def create_doc(self, title: str, body: str) -> dict[str, Any]:
        """
        Create a new Google Doc with *title* and initial *body* content.

        Returns a summary dict with the new document's ID and URL.
        """
        logger.info("[Writer] Creating doc: %s", title)
        doc = await asyncio.to_thread(
            self.workspace.create_doc,
            title=title,
            body=body,
        )
        result = {
            "agent": "Writer",
            "action": "create_doc",
            "doc_id": doc.get("documentId", ""),
            "title": title,
        }
        logger.info("[Writer] Doc created: %s", result)
        return result

    async def append_to_doc(self, doc_id: str, content: str) -> dict[str, Any]:
        """
        Append *content* to an existing Google Doc identified by *doc_id*.
        """
        logger.info("[Writer] Appending to doc %s", doc_id)
        await asyncio.to_thread(
            self.workspace.append_doc_content,
            doc_id=doc_id,
            content=content,
        )
        return {"agent": "Writer", "action": "append_to_doc", "doc_id": doc_id}

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> dict[str, Any]:
        """
        Send a plain-text Gmail notification from the configured sender address.
        """
        logger.info("[Writer] Sending email to %s | subject: %s", to, subject)
        result = await asyncio.to_thread(
            self.workspace.send_gmail,
            sender=self.gmail_sender,
            to=to,
            subject=subject,
            body=body,
        )
        return {
            "agent": "Writer",
            "action": "send_email",
            "to": to,
            "subject": subject,
            "message_id": result.get("id", ""),
        }

    async def compose_summary_email(
        self,
        to: str,
        subject: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Format *data* into a readable summary and send it as an email.
        """
        lines = [f"  {k}: {v}" for k, v in data.items()]
        body = f"Summary Report\n\n" + "\n".join(lines)
        return await self.send_email(to=to, subject=subject, body=body)
