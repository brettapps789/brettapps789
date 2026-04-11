"""
orchestrator.py

Async orchestrator for the Agent Workforce (AAW).

Demonstrates a full multi-agent invocation chain:
  1. @Manager – billing sync + dashboard update
  2. @Analyst  – data analysis via Vertex AI
  3. @Writer   – Doc creation + Gmail notification

Run directly:
    python orchestrator.py

Environment variables (see build.json for full list):
    GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_SHEET_ID,
    GOOGLE_DRIVE_FOLDER_ID, STRIPE_API_KEY, VERTEX_AI_PROJECT,
    VERTEX_AI_LOCATION, VERTEX_AI_MODEL, GMAIL_SENDER
"""

import asyncio
import logging
import os
from typing import Any

from dotenv import load_dotenv

from agents.manager_agent import ManagerAgent
from agents.writer_agent import WriterAgent
from agents.analyst_agent import AnalystAgent
from utils.google_workspace import GoogleWorkspaceHelper
from utils.stripe_api import StripeHelper
from utils.vertex_ai import VertexAIHelper

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def _build_agents() -> tuple[ManagerAgent, WriterAgent, AnalystAgent]:
    """Instantiate helpers and agents from environment variables."""
    workspace = GoogleWorkspaceHelper()
    stripe = StripeHelper()
    vertex = VertexAIHelper()

    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    drive_folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
    gmail_sender = os.environ["GMAIL_SENDER"]

    manager = ManagerAgent(
        workspace=workspace,
        stripe=stripe,
        sheet_id=sheet_id,
        drive_folder_id=drive_folder_id,
    )
    writer = WriterAgent(workspace=workspace, gmail_sender=gmail_sender)
    analyst = AnalystAgent(workspace=workspace, vertex=vertex, sheet_id=sheet_id)

    return manager, writer, analyst


async def run_workflow(
    customer_email: str,
    plan_id: str,
    notify_email: str,
) -> dict[str, Any]:
    """
    Execute the full AAW workflow:

    Step 1 – @Manager: create/sync Stripe subscription → write to Sheets.
    Step 2 – @Analyst: read Sheets data → Vertex AI insight → write row.
    Step 3 – @Writer:  create summary Doc → send Gmail notification.

    Returns a dict of results from all three agents.
    """
    manager, writer, analyst = _build_agents()
    results: dict[str, Any] = {}

    # Step 1 – Billing sync
    logger.info("=== Step 1: Manager – Billing Sync ===")
    billing_result = await manager.run_billing_sync(
        customer_email=customer_email,
        plan_id=plan_id,
    )
    results["manager_billing"] = billing_result

    # Step 2 – Data analysis
    logger.info("=== Step 2: Analyst – Data Analysis ===")
    analysis_result = await analyst.analyze_sheet_data(
        prompt_prefix="Summarize the latest billing activity and flag any anomalies:"
    )
    results["analyst_analysis"] = analysis_result

    await analyst.write_analysis_row(analysis_result.get("insight", "No insight available"))

    # Step 3 – Doc + email
    logger.info("=== Step 3: Writer – Doc & Email ===")
    insight_text = analysis_result.get("insight", "No insight available")
    doc_result = await writer.create_doc(
        title=f"AAW Report – {customer_email}",
        body=f"Billing Result:\n{billing_result}\n\nInsight:\n{insight_text}",
    )
    results["writer_doc"] = doc_result

    email_result = await writer.compose_summary_email(
        to=notify_email,
        subject="AAW Workflow Complete",
        data={
            "Subscription ID": billing_result["result"].get("subscription_id", "N/A"),
            "Status": billing_result["result"].get("status", "N/A"),
            "Insight": insight_text[:200],
            "Doc ID": doc_result.get("doc_id", "N/A"),
        },
    )
    results["writer_email"] = email_result

    logger.info("=== Workflow Complete ===")
    for key, value in results.items():
        agent = value.get("agent", key) if isinstance(value, dict) else key
        action = value.get("action", "") if isinstance(value, dict) else ""
        logger.info("%-25s agent=%-10s action=%s", key, agent, action)

    return results


if __name__ == "__main__":
    asyncio.run(
        run_workflow(
            customer_email=os.environ.get("DEMO_CUSTOMER_EMAIL", "demo@example.com"),
            plan_id=os.environ.get("DEMO_PLAN_ID", "price_DEMO"),
            notify_email=os.environ.get("DEMO_NOTIFY_EMAIL", "notify@example.com"),
        )
    )
