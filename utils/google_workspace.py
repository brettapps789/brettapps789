"""
utils/google_workspace.py

Helper class for Google Workspace APIs:
  - Google Sheets (read/write rows)
  - Google Docs (create document, append content)
  - Gmail (send email)
  - Google Drive (list files, download file)

Authentication uses a service-account JSON pointed to by the
GOOGLE_APPLICATION_CREDENTIALS environment variable.
"""

import base64
import logging
import os
from email.mime.text import MIMEText
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

logger = logging.getLogger(__name__)

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive",
]


class GoogleWorkspaceHelper:
    """
    Thin wrapper around Google Workspace APIs.

    All methods are synchronous and intended to be run via
    ``asyncio.to_thread`` in the async agents.
    """

    def __init__(self, credentials_path: str | None = None) -> None:
        creds_path = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path:
            raise ValueError(
                "Google credentials path must be provided via the "
                "GOOGLE_APPLICATION_CREDENTIALS environment variable or the "
                "credentials_path constructor argument."
            )
        credentials = service_account.Credentials.from_service_account_file(
            creds_path, scopes=_SCOPES
        )
        self._sheets = build("sheets", "v4", credentials=credentials)
        self._docs = build("docs", "v1", credentials=credentials)
        self._gmail = build("gmail", "v1", credentials=credentials)
        self._drive = build("drive", "v3", credentials=credentials)

    # ------------------------------------------------------------------
    # Google Sheets
    # ------------------------------------------------------------------

    def read_sheet_rows(
        self, spreadsheet_id: str, range_notation: str = "Sheet1!A1:Z100"
    ) -> list[list[Any]]:
        """Return all rows in *range_notation* as a list of lists."""
        response = (
            self._sheets.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_notation)
            .execute()
        )
        return response.get("values", [])

    def append_sheet_row(self, spreadsheet_id: str, values: list[Any]) -> None:
        """Append a single row to the first available empty row in the sheet."""
        body = {"values": [values]}
        self._sheets.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body=body,
        ).execute()

    def write_sheet_rows(
        self, spreadsheet_id: str, rows: list[list[Any]], range_notation: str = "Sheet1!A1"
    ) -> None:
        """Overwrite the sheet starting at *range_notation* with *rows*."""
        body = {"values": rows}
        self._sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_notation,
            valueInputOption="RAW",
            body=body,
        ).execute()

    # ------------------------------------------------------------------
    # Google Docs
    # ------------------------------------------------------------------

    def create_doc(self, title: str, body: str) -> dict[str, Any]:
        """Create a new Google Doc with *title* and *body* content."""
        doc = self._docs.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]
        requests = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": body,
                }
            }
        ]
        self._docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()
        return doc

    def append_doc_content(self, doc_id: str, content: str) -> None:
        """Append *content* to the end of an existing Google Doc."""
        doc = self._docs.documents().get(documentId=doc_id).execute()
        end_index = doc["body"]["content"][-1]["endIndex"] - 1
        requests = [
            {
                "insertText": {
                    "location": {"index": end_index},
                    "text": f"\n{content}",
                }
            }
        ]
        self._docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    # ------------------------------------------------------------------
    # Gmail
    # ------------------------------------------------------------------

    def send_gmail(
        self, sender: str, to: str, subject: str, body: str
    ) -> dict[str, Any]:
        """Send a plain-text email via the Gmail API and return the message dict."""
        message = MIMEText(body)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return (
            self._gmail.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )

    # ------------------------------------------------------------------
    # Google Drive
    # ------------------------------------------------------------------

    def list_drive_files(self, folder_id: str) -> list[dict[str, Any]]:
        """List files in a Drive folder, returning id/name/mimeType dicts."""
        query = f"'{folder_id}' in parents and trashed = false"
        response = (
            self._drive.files()
            .list(q=query, fields="files(id, name, mimeType)")
            .execute()
        )
        return response.get("files", [])

    def download_drive_file(self, file_id: str) -> str:
        """
        Download a plain-text Drive file and return its content as a string.
        For binary or non-text files the raw bytes are base64-encoded.
        """
        request = self._drive.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        content_bytes = buffer.getvalue()
        try:
            return content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return base64.b64encode(content_bytes).decode("ascii")
