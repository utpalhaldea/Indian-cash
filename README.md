# Visual India-style Flask starter

## Features
- Responsive login/register pages inspired by the supplied screenshot
- Flask + SQLite registration/login
- Passwords stored as secure hashes
- Optional referral code field
- Basic dashboard/logout
- Forgot-password placeholder (does not send OTP/reset codes)

## Run locally
1. Install Python 3.10+.
2. In a terminal, enter this folder.
3. Create a virtual environment (recommended):
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set a strong secret key before deployment:
   - macOS/Linux: `export SECRET_KEY="replace-with-a-long-random-value"`
   - Windows PowerShell: `$env:SECRET_KEY="replace-with-a-long-random-value"`
6. Run: `python main.py`
7. Open `http://127.0.0.1:5000`

## Before public deployment
- Replace the development secret key with a long random secret.
- Set `COOKIE_SECURE=1` when served over HTTPS.
- Add CSRF protection, login rate limiting, email/SMS verification, secure password-reset tokens, backups, and monitoring.
- Use HTTPS and a production WSGI server; do not expose Flask debug mode.
- Do not collect payment details or promise earnings unless those functions are real and legally compliant.
