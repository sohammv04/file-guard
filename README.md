# File Guard

File Guard is a cross-platform File Integrity Monitoring System for Windows and Kali Linux. It uses hash comparison to detect unauthorized file changes, deletions, and additions, then surfaces them through a desktop GUI, local logs, and generated reports.

## Features

- PIN-based authentication with first-time registration
- Mobile number capture for OTP-based PIN reset
- Real SMS OTP via Firebase (10,000 free/month)
- File and folder monitoring with recursive scans
- Detects modified, deleted, and newly added files/folders
- User-selectable hashing: MD5, SHA-1, or SHA-256
- Real-time alerts in the GUI and system tray
- JSONL and text logging
- Risk classification for detected changes
- Text and PDF report generation

## Technology

- Python 3.10+
- PyQt6
- hashlib
- pathlib / os
- reportlab
- firebase-admin
- python-dotenv
- requests

## Project structure

```text
File Guard/
├── file_guard/
│   ├── auth.py
│   ├── firebase_setup.py
│   ├── firebase_rest_api.py
│   ├── real_otp_service.py
│   ├── monitor_service.py
│   ├── config.py
│   ├── hashing.py
│   ├── logging_utils.py
│   ├── models.py
│   ├── monitor.py
│   ├── reporting.py
│   ├── risk.py
│   ├── storage.py
│   ├── static/
│   │   └── firebase_frontend.js
│   └── ui/
│       ├── main_window.py
│       ├── otp_widget.py
│       └── theme.py
├── .env.example
├── main.py
├── requirements.txt
├── FINAL_REPORT.md
└── generate_final_report.py
```

## Real SMS OTP Setup (Firebase)(Need to Buy Subscription)

### Step 1: Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project**
3. Enter project name (e.g., `File Guard`)
4. Click **Create Project**

### Step 2: Enable Phone Authentication
1. Go to **Authentication** → **Sign-in method**
2. Enable the **Phone** provider
3. For development, add test phone numbers under **Phone numbers for testing**

### Step 3: Get Service Account Credentials
1. Go to **Project Settings** → **Service Accounts**
2. Click **Generate New Private Key**
3. Save the JSON file and copy:
   - `project_id`
   - `private_key_id`
   - `private_key`
   - `client_email`
   - `client_id`

### Step 4: Get API Key
1. Go to **Project Settings** → **General**
2. Under **Your apps**, copy the **Web API Key**

### Step 5: Configure Environment
1. Copy `.env.example` to `.env`
2. Fill in your Firebase values:

```env
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_service_account@your_project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_API_KEY=your_api_key
```

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 7: Test OTP Flow
1. Register with your mobile number
2. Click **Request OTP** on the auth or settings screen
3. Enter the SMS code in the OTP fields
4. Reset your PIN

**Note:** Phone auth via REST API may require a `FIREBASE_RECAPTCHA_TOKEN` in production. For development, use Firebase test phone numbers. Alternatively, embed `file_guard/static/firebase_frontend.js` via PyQtWebEngine for client-side SMS delivery.

## Installation

### Windows

```powershell
cd "<path-to-File-Guard>"
python -m pip install -r requirements.txt
python main.py
```

### Kali Linux

```bash
cd "/path/to/File Guard"
python3 -m pip install -r requirements.txt
python3 main.py
```

## How to use

1. Launch File Guard.
2. On first use, enter your mobile number and create a numeric PIN.
3. Unlock the app using the PIN.
4. Add one or more files or folders to monitor.
5. Select the hashing algorithm.
6. Start monitoring.
7. Modify, delete, or add files to trigger alerts.
8. Review the alerts and log viewer.
9. Generate the text and PDF reports.

## Local data and logs

File Guard stores its working data in a per-user application folder:

- Windows: `C:\Users\<username>\.file_guard\`
- Linux: `/home/<username>/.file_guard/`

Files created there include:

- `auth.json` for the registered mobile and salted PIN hash
- `baseline.json` for the monitoring baseline
- `monitor_log.jsonl` for structured logs
- `monitor_log.txt` for readable logs
- `reports/` for generated monitoring reports

## OTP delivery

OTP is sent via **Firebase SMS** to the registered mobile number. Configure `.env` with your Firebase credentials before using PIN reset. No OTP codes are printed to the console.

## Generate the documentation PDF

```powershell
cd "<path-to-File-Guard>"
python generate_final_report.py
```

This creates:

- `<path-to-File-Guard>\FINAL_REPORT.pdf`

## Recommended validation

- Test registration, login, and PIN reset.
- Test file modification, deletion, and new file detection.
- Test all three hashing algorithms.
- Test report generation.
- Test dark mode and light mode switching.
- Test on both Windows and Kali Linux.

## Notes

- Risk classification is based on extension and sensitive path hints.
- Real-time monitoring uses repeated scanning rather than kernel-specific hooks, which keeps the implementation simple and cross-platform.
- For production hardening, configure `FIREBASE_RECAPTCHA_TOKEN` for REST API phone auth and use Firebase App Check.
