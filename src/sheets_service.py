from __future__ import annotations
import os
from typing import List, Dict, Any

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class SheetsService:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, spreadsheet_id: str, credentials_path: str, token_path: str, sheet_name: str = "Sheet1"):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        return build("sheets", "v4", credentials=creds)

    def append_rows(self, rows: List[Dict[str, Any]]):
        """
        Append rows to the sheet.
        Expected format:
        [
            {"from": "...", "subject": "...", "date": "...", "body": "...", "id": "..."}
        ]
        """
        if not rows:
            return

        values = [
            [r["from"], r["subject"], r["date"], r["body"], r["id"]]
            for r in rows
        ]

        body = {"values": values}

        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.sheet_name}!A:E",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

    def fetch_existing_ids(self) -> set:
        """
        Fetch existing message IDs to prevent duplicates.
        Assumes ID is stored in column E.
        """
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.sheet_name}!E:E"
        ).execute()

        values = result.get("values", [])
        return set(v[0] for v in values if v)

