from __future__ import annotations
import json
import os
from src.gmail_service import GmailService
from src.sheets_service import SheetsService
from src.email_parser import EmailParser
import config



STATE_FILE = "state.json"


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {"last_processed_id": None}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    print("🔄 Starting Gmail → Sheets sync...")

    state = load_state()
    last_id = state.get("last_processed_id")

    gmail = GmailService(
        credentials_path=config.GMAIL_CREDENTIALS,
        token_path=config.GMAIL_TOKEN,
    )

    sheets = SheetsService(
        spreadsheet_id=config.SHEET_ID,
        credentials_path=config.SHEETS_CREDENTIALS,
        token_path=config.SHEETS_TOKEN,
        sheet_name=config.SHEET_NAME,
    )

    # 1. Fetch unread emails
    emails = gmail.fetch_unread_emails()
    if not emails:
        print("✔ No new unread emails found. Exiting.")
        return

    # 2. Parse them
    parsed = [EmailParser.parse(e) for e in emails]

    # 3. Dedupe based on existing sheet data
    existing_ids = sheets.fetch_existing_ids()
    filtered = [e for e in parsed if e["id"] not in existing_ids]

    if not filtered:
        print("✔ No new unique emails to append. Exiting.")
        # still mark as read to prevent future reprocessing
        gmail.mark_as_read([e["id"] for e in emails])
        return

    # 4. Append to Sheets
    sheets.append_rows(filtered)

    # 5. Mark as read on Gmail
    gmail.mark_as_read([e["id"] for e in filtered])

    # 6. Update state persistence
    newest_id = filtered[-1]["id"]
    state["last_processed_id"] = newest_id
    save_state(state)

    print(f"✔ Successfully processed {len(filtered)} new email(s).")


if __name__ == "__main__":
    main()
