from __future__ import annotations
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Dict, Any

from bs4 import BeautifulSoup


class EmailParser:

    @staticmethod
    def extract_sender(sender_raw: str) -> str:
        """
        Extract email address from formats like:
            "Name <email@example.com>"
        """
        if "<" in sender_raw and ">" in sender_raw:
            match = re.search(r"<(.+?)>", sender_raw)
            if match:
                return match.group(1)
        return sender_raw.strip()

    @staticmethod
    def extract_date(date_raw: str) -> str:
        """
        Convert date to ISO 8601 (e.g., 2026-01-13T14:55:10+05:30)
        """
        dt = parsedate_to_datetime(date_raw)
        return dt.isoformat()

    @staticmethod
    def clean_body(body: str) -> str:
        MAX_BODY_LEN = 48000  # leave buffer below Sheets 50k hard limit

        # Convert HTML → plaintext if needed
        if "<html" in body.lower() or "<div" in body.lower() or "<p" in body.lower():
            soup = BeautifulSoup(body, "lxml")
            text = soup.get_text("\n")
        else:
            text = body

        # Normalize whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

        # Truncate to avoid Sheets API 400 error
        if len(text) > MAX_BODY_LEN:
            text = text[:MAX_BODY_LEN] + "\n...[truncated due to size limit]"

        return text


    @staticmethod
    def parse(email_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main parser used by main.py before writing to sheet.
        """
        return {
            "id": email_obj["id"],
            "from": EmailParser.extract_sender(email_obj["from"]),
            "subject": email_obj.get("subject", "").strip() if email_obj.get("subject") else "",
            "date": EmailParser.extract_date(email_obj["date"]),
            "body": EmailParser.clean_body(email_obj["body"]),
        }
