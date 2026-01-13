from __future__ import annotations
import base64
import os.path
from email import policy
from email.parser import BytesParser
from typing import List, Dict, Any

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GmailService:
    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        """
        Handles OAuth flow, stores token.json, and refreshes tokens if required.
        """
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

        return build("gmail", "v1", credentials=creds)

    def fetch_unread_emails(self) -> List[Dict[str, Any]]:
        """
        Returns unread email metadata + body content.
        """
        results = self.service.users().messages().list(
            userId="me", labelIds=["INBOX", "UNREAD"]
        ).execute()

        messages = results.get("messages", [])
        emails = []

        for msg in messages:
            msg_id = msg["id"]
            msg_data = self._get_message(msg_id)
            if msg_data:
                emails.append(msg_data)

        return emails

    def _get_message(self, msg_id: str) -> Dict[str, Any]:
        """
        Get and parse a single Gmail message.
        """
        message = self.service.users().messages().get(
            userId="me", id=msg_id, format="raw"
        ).execute()

        raw_data = base64.urlsafe_b64decode(message["raw"])
        email_obj = BytesParser(policy=policy.default).parsebytes(raw_data)

        sender = email_obj["From"]
        subject = email_obj["Subject"]
        date = email_obj["Date"]
        body = self._extract_body(email_obj)

        return {
            "id": msg_id,
            "from": sender,
            "subject": subject,
            "date": date,
            "body": body,
        }

    def _extract_body(self, email_obj) -> str:
        """
        Extract plain text body or fallback to HTML stripped (optional).
        """
        if email_obj.is_multipart():
            for part in email_obj.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_content()
        return email_obj.get_body(preferencelist=('plain', 'html')).get_content()

    def mark_as_read(self, message_ids: List[str]):
        """
        Marks processed emails as read.
        """
        if not message_ids:
            return

        self.service.users().messages().batchModify(
            userId="me",
            body={
                "ids": message_ids,
                "removeLabelIds": ["UNREAD"],
            },
        ).execute()
