"""
agents/manager_agent.py

MCP @Manager Agent – orchestrates billing, data sync, and Google Sheets dashboard updates.

Knowledge Base:
- Understands workflow triggers, Stripe subscription schema, and Google Sheets schema.
- Knows when to refresh dashboards after billing events.
- Handles subscription lifecycle: create, retrieve, cancel.
- Delegates document generation to @Writer and data analysis to @Analyst.
"""

import asyncio
import logging
from typing import Any

from utils.google_workspace import GoogleWorkspaceHelper
from utils.stripe_api import StripeHelper

logger = logging.getLogger(__name__)


class ManagerAgent:
    """
    Async MCP @Manager agent.

    Responsibilities:
      - Trigger Stripe billing operations (subscriptions, invoices).
      - Sync billing results to a Google Sheets dashboard.
      - Coordinate file management in Google Drive.
      - Hand off tasks to @Writer and @Analyst via the orchestrator.
    """

    def __init__(
        self,
        workspace: GoogleWorkspaceHelper,
        stripe: StripeHelper,
        sheet_id: str,
        drive_folder_id: str,
    ) -> None:
        self.workspace = workspace
        self.stripe = stripe
        self.sheet_id = sheet_id
        self.drive_folder_id = drive_folder_id

    # ------------------------------------------------------------------
    # Public async interface
    # ------------------------------------------------------------------

    async def run_billing_sync(self, customer_email: str, plan_id: str) -> dict[str, Any]:
        """
        Create or retrieve a Stripe subscription for *customer_email* and
        write the result to the Google Sheets dashboard.

        Returns a summary dict consumed by the orchestrator.
        """
        logger.info("[Manager] Starting billing sync for %s", customer_email)

        subscription = await asyncio.to_thread(
            self.stripe.create_subscription,
            email=customer_email,
            plan_id=plan_id,
        )

        row = {
            "email": customer_email,
            "plan_id": plan_id,
            "subscription_id": subscription.get("id", "N/A"),
            "status": subscription.get("status", "unknown"),
        }
        await asyncio.to_thread(
            self.workspace.append_sheet_row,
            spreadsheet_id=self.sheet_id,
            values=list(row.values()),
        )

        logger.info("[Manager] Billing sync complete: %s", row)
        return {"agent": "Manager", "action": "billing_sync", "result": row}

    async def sync_dashboard(self, data_rows: list[list[Any]]) -> dict[str, Any]:
        """
        Overwrite the Google Sheets dashboard with *data_rows*.
        """
        logger.info("[Manager] Syncing %d rows to dashboard", len(data_rows))
        await asyncio.to_thread(
            self.workspace.write_sheet_rows,
            spreadsheet_id=self.sheet_id,
            rows=data_rows,
        )
        return {"agent": "Manager", "action": "sync_dashboard", "rows_written": len(data_rows)}

    async def list_drive_files(self) -> dict[str, Any]:
        """
        List files in the configured Drive folder.
        """
        logger.info("[Manager] Listing Drive files in folder %s", self.drive_folder_id)
        files = await asyncio.to_thread(
            self.workspace.list_drive_files,
            folder_id=self.drive_folder_id,
        )
        return {"agent": "Manager", "action": "list_drive_files", "files": files}
