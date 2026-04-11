"""
test_workflow.py

End-to-end mock/test for the Agent Workforce (AAW) pipeline.

All external service calls (Google Workspace, Stripe, Vertex AI) are
patched with unittest.mock so no real credentials are required.

Run:
    pytest test_workflow.py -v
"""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers: build lightweight stub instances so agents can be instantiated
# without real credentials.
# ---------------------------------------------------------------------------


def _make_workspace_mock() -> MagicMock:
    ws = MagicMock()
    ws.read_sheet_rows.return_value = [
        ["email", "plan_id", "subscription_id", "status"],
        ["user@example.com", "price_123", "sub_abc", "active"],
    ]
    ws.append_sheet_row.return_value = None
    ws.write_sheet_rows.return_value = None
    ws.create_doc.return_value = {"documentId": "doc_xyz", "title": "Test Doc"}
    ws.append_doc_content.return_value = None
    ws.send_gmail.return_value = {"id": "msg_001"}
    ws.list_drive_files.return_value = [
        {"id": "file_1", "name": "report.txt", "mimeType": "text/plain"}
    ]
    ws.download_drive_file.return_value = "Drive file content for testing."
    return ws


def _make_stripe_mock() -> MagicMock:
    stripe_helper = MagicMock()
    stripe_helper.create_subscription.return_value = {
        "id": "sub_abc",
        "status": "active",
        "customer": "cus_001",
    }
    stripe_helper.get_or_create_customer.return_value = {
        "id": "cus_001",
        "email": "user@example.com",
    }
    stripe_helper.get_latest_invoice.return_value = {
        "id": "inv_001",
        "amount_due": 999,
        "status": "paid",
    }
    stripe_helper.cancel_subscription.return_value = {
        "id": "sub_abc",
        "status": "canceled",
    }
    return stripe_helper


def _make_vertex_mock() -> MagicMock:
    vertex = MagicMock()
    vertex.generate_text.return_value = (
        "INSIGHT: Billing activity looks healthy with no anomalies.\n"
        "RECOMMENDATIONS:\n- Continue monitoring.\n- Review plan pricing.\n- Expand offerings."
    )
    vertex.summarize.return_value = "Concise summary of the document."
    vertex.analyze.return_value = {
        "insight": "Revenue is growing steadily.",
        "recommendations": ["Expand tier", "Offer discounts", "Monitor churn"],
        "raw": "INSIGHT: ...",
    }
    return vertex


# ---------------------------------------------------------------------------
# Agent imports (delayed to avoid credential errors at module load time)
# ---------------------------------------------------------------------------

from agents.manager_agent import ManagerAgent
from agents.writer_agent import WriterAgent
from agents.analyst_agent import AnalystAgent

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def workspace():
    return _make_workspace_mock()


@pytest.fixture()
def stripe_helper():
    return _make_stripe_mock()


@pytest.fixture()
def vertex():
    return _make_vertex_mock()


@pytest.fixture()
def manager(workspace, stripe_helper):
    return ManagerAgent(
        workspace=workspace,
        stripe=stripe_helper,
        sheet_id="sheet_001",
        drive_folder_id="folder_001",
    )


@pytest.fixture()
def writer(workspace):
    return WriterAgent(workspace=workspace, gmail_sender="sender@example.com")


@pytest.fixture()
def analyst(workspace, vertex):
    return AnalystAgent(workspace=workspace, vertex=vertex, sheet_id="sheet_001")


# ---------------------------------------------------------------------------
# @Manager tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_manager_billing_sync(manager, stripe_helper, workspace):
    result = await manager.run_billing_sync(
        customer_email="user@example.com", plan_id="price_123"
    )

    assert result["agent"] == "Manager"
    assert result["action"] == "billing_sync"
    assert result["result"]["subscription_id"] == "sub_abc"
    assert result["result"]["status"] == "active"
    stripe_helper.create_subscription.assert_called_once_with(
        email="user@example.com", plan_id="price_123"
    )
    workspace.append_sheet_row.assert_called_once()


@pytest.mark.asyncio
async def test_manager_sync_dashboard(manager, workspace):
    rows = [["col1", "col2"], ["val1", "val2"]]
    result = await manager.sync_dashboard(rows)

    assert result["agent"] == "Manager"
    assert result["action"] == "sync_dashboard"
    assert result["rows_written"] == 2
    workspace.write_sheet_rows.assert_called_once()


@pytest.mark.asyncio
async def test_manager_list_drive_files(manager, workspace):
    result = await manager.list_drive_files()

    assert result["agent"] == "Manager"
    assert result["action"] == "list_drive_files"
    assert len(result["files"]) == 1
    assert result["files"][0]["name"] == "report.txt"
    workspace.list_drive_files.assert_called_once_with(folder_id="folder_001")


# ---------------------------------------------------------------------------
# @Writer tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_writer_create_doc(writer, workspace):
    result = await writer.create_doc(title="My Doc", body="Hello world")

    assert result["agent"] == "Writer"
    assert result["action"] == "create_doc"
    assert result["doc_id"] == "doc_xyz"
    workspace.create_doc.assert_called_once_with(title="My Doc", body="Hello world")


@pytest.mark.asyncio
async def test_writer_append_to_doc(writer, workspace):
    result = await writer.append_to_doc(doc_id="doc_xyz", content="More content")

    assert result["agent"] == "Writer"
    assert result["action"] == "append_to_doc"
    assert result["doc_id"] == "doc_xyz"
    workspace.append_doc_content.assert_called_once_with(
        doc_id="doc_xyz", content="More content"
    )


@pytest.mark.asyncio
async def test_writer_send_email(writer, workspace):
    result = await writer.send_email(
        to="to@example.com", subject="Hello", body="Body text"
    )

    assert result["agent"] == "Writer"
    assert result["action"] == "send_email"
    assert result["message_id"] == "msg_001"
    workspace.send_gmail.assert_called_once()


@pytest.mark.asyncio
async def test_writer_compose_summary_email(writer, workspace):
    result = await writer.compose_summary_email(
        to="to@example.com",
        subject="Summary",
        data={"key1": "val1", "key2": "val2"},
    )

    assert result["agent"] == "Writer"
    assert result["action"] == "send_email"
    workspace.send_gmail.assert_called_once()
    call_kwargs = workspace.send_gmail.call_args
    body_arg = call_kwargs.kwargs.get("body") or call_kwargs.args[3]
    assert "key1" in body_arg


# ---------------------------------------------------------------------------
# @Analyst tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analyst_analyze_sheet_data(analyst, workspace, vertex):
    result = await analyst.analyze_sheet_data()

    assert result["agent"] == "Analyst"
    assert result["action"] == "analyze_sheet_data"
    assert result["rows_analyzed"] == 2
    assert "INSIGHT" in result["insight"]
    workspace.read_sheet_rows.assert_called_once()
    vertex.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_analyst_write_analysis_row(analyst, workspace):
    result = await analyst.write_analysis_row("Revenue grew 10% MoM.")

    assert result["agent"] == "Analyst"
    assert result["action"] == "write_analysis_row"
    workspace.append_sheet_row.assert_called_once_with(
        spreadsheet_id="sheet_001",
        values=["Analysis", "Revenue grew 10% MoM."],
    )


@pytest.mark.asyncio
async def test_analyst_summarize_drive_file(analyst, workspace, vertex):
    result = await analyst.summarize_drive_file(file_id="file_1")

    assert result["agent"] == "Analyst"
    assert result["action"] == "summarize_drive_file"
    assert "summary" in result
    workspace.download_drive_file.assert_called_once_with(file_id="file_1")
    vertex.generate_text.assert_called_once()


# ---------------------------------------------------------------------------
# End-to-end chain test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_workflow_chain(manager, writer, analyst, workspace, stripe_helper, vertex):
    """
    Simulate the complete orchestration chain:
      Manager → billing sync
      Analyst → analyze sheet data + write row
      Writer  → create doc + send email
    """
    # Step 1 – Manager billing sync
    billing = await manager.run_billing_sync(
        customer_email="chain@example.com", plan_id="price_chain"
    )
    assert billing["result"]["status"] == "active"

    # Step 2 – Analyst analysis
    analysis = await analyst.analyze_sheet_data(
        prompt_prefix="Analyze billing chain data:"
    )
    assert analysis["rows_analyzed"] > 0
    await analyst.write_analysis_row(analysis["insight"])

    # Step 3 – Writer doc + email
    doc = await writer.create_doc(
        title="Chain Report",
        body=analysis["insight"],
    )
    assert doc["doc_id"] == "doc_xyz"

    email = await writer.compose_summary_email(
        to="notify@example.com",
        subject="Chain Workflow Done",
        data={"insight": analysis["insight"][:100], "doc_id": doc["doc_id"]},
    )
    assert email["action"] == "send_email"

    # Verify all external services were called
    stripe_helper.create_subscription.assert_called_once()
    workspace.read_sheet_rows.assert_called_once()
    vertex.generate_text.assert_called_once()
    workspace.create_doc.assert_called_once()
    workspace.send_gmail.assert_called_once()
