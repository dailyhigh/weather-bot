"""
Part 1: Temperature Threshold Alert Bot

Polls the DailyHigh prediction endpoint for a single station
and sends a Discord alert when a temperature threshold is
crossed (or when it becomes unlikely to be reached).

Full tutorial:
https://dailyhigh.app/blog/build-a-temperature-alert-bot-with-the-dailyhigh-api
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DAILYHIGH_API_KEY", "")
BASE = "https://dailyhigh.app"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

STATE_FILE = Path(__file__).parent / "state.json"

# ── Configuration ────────────────────────────────────────────────────
ALERT = {
    "icao": "KLGA",
    "target": 29.4,       # 85 °F in Celsius
    "direction": "over",  # "over" or "under"
}
# ─────────────────────────────────────────────────────────────────────


def get_prediction(icao: str) -> dict | None:
    resp = requests.get(
        f"{BASE}/api/v1/prediction/{icao}",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=10,
    )
    if resp.status_code == 202:
        return None  # prediction not yet cached, retry later
    resp.raise_for_status()
    return resp.json()["data"]


def check_threshold(data: dict, target: float, direction: str) -> str:
    observed = data["observedMax"]
    predicted = data["predictedMax"]
    past_peak = data["isPastPeak"]

    if direction == "over":
        if observed >= target:
            return "crossed"
        if past_peak and predicted < target:
            return "unlikely"
    else:  # "under"
        if past_peak and observed < target:
            return "crossed"
        if observed >= target:
            return "unlikely"

    return "pending"


def format_message(data: dict, status: str, alert: dict) -> str:
    icao = alert["icao"]
    target = alert["target"]
    observed = data["observedMax"]
    predicted = data["predictedMax"]
    confidence = data["confidence"]

    if status == "crossed":
        return (
            f"✅ **{icao}** crossed {target} °C\n"
            f"Observed max: {observed} °C | "
            f"Predicted max: {predicted} °C | "
            f"Confidence: {confidence}/10"
        )
    elif status == "unlikely":
        return (
            f"❌ **{icao}** unlikely to reach {target} °C\n"
            f"Observed max: {observed} °C | "
            f"Predicted max: {predicted} °C | "
            f"Past peak: yes"
        )
    return ""


def send_alert(message: str):
    if not WEBHOOK_URL:
        print("No DISCORD_WEBHOOK_URL set, skipping alert")
        return
    requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)


def already_alerted(icao: str, dt: str) -> bool:
    if not STATE_FILE.exists():
        return False
    state = json.loads(STATE_FILE.read_text())
    return state.get(icao) == dt


def mark_alerted(icao: str, dt: str):
    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    state[icao] = dt
    STATE_FILE.write_text(json.dumps(state))


def main():
    today = date.today().isoformat()

    if already_alerted(ALERT["icao"], today):
        print(f"Already alerted for {ALERT['icao']} on {today}")
        sys.exit(0)

    data = get_prediction(ALERT["icao"])
    if data is None:
        print("Prediction not ready, will retry next run")
        sys.exit(0)

    status = check_threshold(data, ALERT["target"], ALERT["direction"])
    print(
        f'{ALERT["icao"]}: {status} '
        f'(observed={data["observedMax"]}, '
        f'predicted={data["predictedMax"]}, '
        f'confidence={data["confidence"]})'
    )

    if status in ("crossed", "unlikely"):
        msg = format_message(data, status, ALERT)
        send_alert(msg)
        mark_alerted(ALERT["icao"], today)
        print("Alert sent")


if __name__ == "__main__":
    main()
