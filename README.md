# 📌 Gmail → Google Sheets Automation

**Author:** Rajat Kumar Dubey  
**Language:** Python 3  
**APIs Used:** Gmail API + Google Sheets API  
**Auth:** OAuth 2.0 (Installed App)

This project automates the extraction of unread emails from Gmail and logs them into a Google Sheet with no duplicates, persistent state, and idempotent re-runs.

---

## 🎯 Objective

Whenever the script runs:

✔ Read unread emails from Gmail (Inbox scope)  
✔ Parse sender, subject, timestamp, and body  
✔ Append each email as a new row in a Google Sheet  
✔ Prevent duplicates across runs  
✔ Mark processed emails as **READ**  
✔ Persist state locally so re-running does not reprocess old emails  

---

## 🧱 High-Level Architecture

```
              +------------------+
              |   Gmail Inbox    |
              +--------+---------+
                       |
                (Unread Emails)
                       |
               Gmail API (OAuth)
                       |
                       v
+--------------- Email Parser ----------------+
| Extract: from, subject, date, body, id      |
+---------------------+-----------------------+
                      |
                      v
              Sheets API (OAuth)
                      |
                      v
          +-----------------------------+
          |   Google Spreadsheet Rows   |
          +-----------------------------+

State: `state.json` stores last processed message ID
```

---

## 📂 Project Structure

```
gmail-to-sheets/
 ├── src/
 │   ├── main.py
 │   ├── gmail_service.py
 │   ├── sheets_service.py
 │   ├── email_parser.py
 ├── config.py
 ├── credentials/
 │   └── credentials.json        (NOT committed)
 ├── state.json                  (Generated)
 ├── requirements.txt
 ├── README.md
 ├── .gitignore
 └── proof/
```

---

## ⚙️ Technical Requirements Satisfaction Checklist

| Requirement | Status |
|---|---|
| Python 3 | ✔ |
| Gmail API | ✔ |
| Sheets API | ✔ |
| OAuth 2.0 (no service accounts) | ✔ |
| Read only unread emails | ✔ |
| Append only new rows | ✔ |
| Mark emails as read | ✔ |
| No duplicates | ✔ |
| Persist state | ✔ |
| Proof of execution | ✔ |
| README design explanation | ✔ |

---

## 🔐 OAuth Flow Explanation

This project uses the **Installed Application OAuth Flow**:

1. On first run, user is redirected to Google OAuth consent screen.
2. Gmail + Sheets permissions requested:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/spreadsheets`
3. User approves authentication.
4. Refresh tokens stored locally as:
   ```
   gmail_token.json
   sheets_token.json
   ```
5. Future runs skip login until token expires.

No service accounts are used, meeting assignment rules.

---

## 📥 Email Processing Logic

✔ Scope: **UNREAD** + **INBOX**  
✔ Emails converted to plaintext (HTML stripped)  
✔ Content normalized for Sheets  
✔ Large bodies truncated (Sheets cell limit = 50,000 chars)

---

## 🧾 Google Sheets Data Model

Each new email creates a new row with columns:

| Column | Description |
|---|---|
| From | Sender email |
| Subject | Email subject |
| Date | ISO timestamp |
| Body | Plaintext email body |
| ID | Gmail message ID |

---

## 🧱 Duplicate Prevention Logic

Duplicate prevention uses two layers:

### **Layer 1 — Sheets-based dedupe**
Existing message IDs fetched from Column `E`:
```
existing_ids = sheets.fetch_existing_ids()
```
Only emails not present are appended.

### **Layer 2 — Mark-as-Read Behavior**
After processing, all unread emails are marked `READ`.

This ensures re-running script does **not** reprocess old data.

---

## 💾 State Persistence

State stored in `state.json`:

```json
{
  "last_processed_id": "1893adf..."
}
```

This ensures pipeline is **idempotent** and avoids reprocessing between runs.

**Why JSON state?**

✔ Lightweight  
✔ Local & durable  
✔ No DB required  
✔ Assignment-friendly  

---

## 🧪 Setup Instructions

### **1. Install dependencies**
```sh
pip install -r requirements.txt
```

### **2. Enable Google APIs**
Enable:
- Gmail API
- Sheets API

### **3. Create OAuth Credentials**
Type: **Desktop App**  
Download: `credentials.json`

Place into:
```
credentials/credentials.json
```

### **4. Configure Sheet**
1. Create new Google Sheet
2. Add header row:

| From | Subject | Date | Body | ID |

3. Get `Sheet ID` from URL:
```
/d/<THIS_PART>/edit
```
4. Update `config.py`:
```python
SHEET_ID = "<your-sheet-id>"
SHEET_NAME = "Sheet1"
```

### **5. Run**
```sh
python -m src.main
```

First run requires OAuth browser approval.

---

## 📸 Proof of Execution (Required)

Inside `/proof/` folder:

✔ Gmail inbox showing unread emails  
✔ OAuth consent screen  
✔ Google Sheet with 5+ rows  
✔ Script re-run showing no duplicates  
✔ 2–3 min demo video 

---

## 🎥 Demo Video Requirements

Video explains:

✔ OAuth workflow  
✔ Gmail → Sheets data flow  
✔ Duplicate prevention  
✔ State handling  
✔ Re-run behavior

---

## 🧩 Challenge Faced & Solution

**Challenge:** Marketing emails exceed Google Sheets 50k cell limit → API returns 400 error.

**Solution:** Truncate body to 48,000 characters with note:
```
...[truncated due to size limit]
```

---

## 🚧 Limitations

- Works only for unread inbox emails
- State is local to machine (not multi-user safe)
- No label-based filtering (possible extension)
- Not intended for large-scale sync jobs

---

## ⭐ Bonus Features Implemented

✔ HTML → plaintext conversion  
✔ ISO timestamp normalization  
✔ Two-level dedupe  
✔ Idempotent re-runs  
✔ State persistence  
✔ Error prevention for Sheets cell size  

---

## 🔄 Post-Submission Modification Support

Architecture supports quick changes such as:

- Filter by subject (e.g., "Invoice")
- Filter by date range (e.g., last 24 hours)
- Add new Sheet columns
- Exclude senders (e.g., no-reply)
- Include labels (e.g., Promotions)

---

## 📦 Submission Includes

✔ Public Git repository link  
✔ Proof folder with screenshots + video  
✔ README design explanation  
✔ No OAuth secrets or tokens committed  

---

## 🙋 Full Name

**Rajat Kumar Dubey**

