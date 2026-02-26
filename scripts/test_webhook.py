#!/usr/bin/env python3
"""
Webhook tester — sends the same payload that generate_report.py uses
and dumps the raw response so you can inspect the structure.

Usage:
    # From env vars:
    MAKE_WEBHOOK_URL=https://hook.eu2.make.com/xxx MAKE_WEBHOOK_API_KEY=secret python scripts/test_webhook.py

    # Or pass URL and key as arguments:
    python scripts/test_webhook.py https://hook.eu2.make.com/xxx secret
"""

import json
import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv
import pytz

load_dotenv()
import requests

TIMEZONE = os.environ.get("REPORT_TIMEZONE", "Asia/Singapore")


def get_report_window():
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    end = now.replace(hour=10, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=1)
    return start, end


def main():
    # Resolve webhook URL and API key
    url = os.environ.get("MAKE_WEBHOOK_URL")
    api_key = os.environ.get("MAKE_WEBHOOK_API_KEY")

    if not url:
        print("ERROR: No webhook URL provided.")
        print("  Pass as argument:  python scripts/test_webhook.py <url> <api_key>")
        print("  Or set env vars:   MAKE_WEBHOOK_URL=<url> MAKE_WEBHOOK_API_KEY=<key>")
        sys.exit(1)

    if not api_key:
        print("ERROR: No API key provided.")
        print("  Pass as argument:  python scripts/test_webhook.py <url> <api_key>")
        print("  Or set env var:    MAKE_WEBHOOK_API_KEY=<key>")
        sys.exit(1)

    start, end = get_report_window()
    payload = {
        "start": start.isoformat(),
        "end": end.isoformat(),
    }

    headers = {
        "Content-Type": "application/json",
        "x-make-apikey": api_key,
    }

    print("=" * 60)
    print(f"Webhook URL : {url}")
    print(f"Timezone    : {TIMEZONE}")
    print(f"Auth        : Bearer {'*' * (len(api_key) - 4)}{api_key[-4:]}")
    print(f"Payload     :")
    print(json.dumps(payload, indent=2))
    print("=" * 60)
    print("Sending request...")

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
    except requests.exceptions.ConnectionError as e:
        print(f"\nERROR: Could not connect — {e}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("\nERROR: Request timed out after 60s.")
        sys.exit(1)

    print(f"\nStatus      : {resp.status_code} {resp.reason}")
    print(f"Content-Type: {resp.headers.get('Content-Type', '—')}")
    print("\nResponse body:")
    try:
        print(json.dumps(resp.json(), indent=2, default=str))
    except Exception:
        print(resp.text)


if __name__ == "__main__":
    main()
