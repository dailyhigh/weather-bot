"""
Part 2: Track a Daily High from Prediction to Result

Logs snapshots of a station's prediction, current weather, and
(once past peak) the final history. Run multiple times per day
to see how the prediction converges toward the actual daily high.

Full tutorial:
https://dailyhigh.app/blog/track-a-daily-high-from-prediction-to-result
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DAILYHIGH_API_KEY", "")
BASE = "https://dailyhigh.app"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

LOG_FILE = Path(__file__).parent / "daily_log.json"

# ── Configuration ────────────────────────────────────────────────────
STATION = "KLGA"
# ─────────────────────────────────────────────────────────────────────


def get_prediction(icao: str) -> dict | None:
    resp = requests.get(
        f"{BASE}/api/v1/prediction/{icao}",
        headers=HEADERS,
        timeout=10,
    )
    if resp.status_code == 202:
        return None
    resp.raise_for_status()
    return resp.json()["data"]


def get_weather(icao: str) -> dict:
    resp = requests.get(
        f"{BASE}/api/v1/weather/{icao}",
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["data"]


def get_history(icao: str, dt: str) -> dict:
    resp = requests.get(
        f"{BASE}/api/v1/history/{icao}/{dt}",
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["data"]


def log_snapshot(icao: str):
    pred = get_prediction(icao)
    wx = get_weather(icao)
    today = date.today().isoformat()

    snapshot = {
        "date": today,
        "time": datetime.now().isoformat(),
        "currentTemp": wx["temperature"],
        "todayMax": wx["todayMax"],
        "predictedMax": pred["predictedMax"] if pred else None,
        "confidence": pred["confidence"] if pred else None,
        "isPastPeak": pred["isPastPeak"] if pred else None,
        "slope": pred["slope"] if pred else None,
    }

    # Append to log
    log = []
    if LOG_FILE.exists():
        log = json.loads(LOG_FILE.read_text())
    log.append(snapshot)
    LOG_FILE.write_text(json.dumps(log, indent=2))

    print(json.dumps(snapshot, indent=2))

    # If past peak, also fetch history for the final number
    if pred and pred["isPastPeak"]:
        history = get_history(icao, today)
        print(f"\nFinal daily max: {history['maxTemp']} °C")


def main():
    log_snapshot(STATION)


if __name__ == "__main__":
    main()
