# File Guard

File Guard is a cross-platform File Integrity Monitoring System for Windows and Kali Linux. It uses hash comparison to detect unauthorized file changes, deletions, and additions, then surfaces them through a desktop GUI, local logs, and generated reports.

## Features

- PIN-based authentication with first-time registration
- Mobile number capture for OTP-based PIN reset
- Simulated OTP flow for testing
- Auto-tab OTP input fields
- File and folder monitoring with recursive scans
- User-selectable hashing: MD5, SHA-1, or SHA-256
- Real-time alerts in the GUI and system tray
- JSONL and text logging
- Risk classification for detected changes
- Text and PDF report generation
- Dark mode and light mode toggle

## Technology

- Python 3.10+
- PyQt6
- hashlib
- pathlib / os
- reportlab

## Project structure

```text
File Guard/
├── file_guard/
│   ├── auth.py
│   ├── config.py
│   ├── hashing.py
│   ├── logging_utils.py
│   ├── models.py
│   ├── monitor.py
│   ├── reporting.py
│   ├── risk.py
│   ├── storage.py
│   └── ui/
│       ├── main_window.py
│       ├── otp_widget.py
│       └── theme.py
├── main.py
├── requirements.txt
├── FINAL_REPORT.md
└── generate_final_report.py
```

## Installation

### Windows

```powershell
cd "c:\Users\SOHAM PHATAK\Desktop\Projects\File Guard"
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

## OTP simulation

For testing, OTP delivery is simulated. When the user requests an OTP, File Guard prints the OTP to the console and also shows it in the GUI message so the reset flow can be verified without an SMS gateway.

## Generate the documentation PDF

```powershell
cd "c:\Users\SOHAM PHATAK\Desktop\Projects\File Guard"
python generate_final_report.py
```

This creates:

- `c:\Users\SOHAM PHATAK\Desktop\Projects\File Guard\FINAL_REPORT.pdf`

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
- For production hardening, you could replace simulated OTP with an SMS provider and add stronger secure storage for secrets.
