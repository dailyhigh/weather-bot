"""
Part 3: Multi-Station Digest

Fetches predictions for all tracked DailyHigh stations,
ranks them by confidence, and sends a formatted digest
to a Discord webhook.

Full tutorial:
https://dailyhigh.app/blog/monitor-multiple-stations-with-the-dailyhigh-api
"""

import os
import time

import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DAILYHIGH_API_KEY", "")
BASE = "https://dailyhigh.app"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")


def get_stations() -> list[dict]:
    resp = requests.get(
        f"{BASE}/api/v1/stations",
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["data"]


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


def fetch_all_predictions(stations: list[dict]) -> list[dict]:
    results = []
    for station in stations:
        pred = get_prediction(station["icao"])
        if pred is None:
            continue
        results.append({
            "icao": station["icao"],
            "name": station["name"],
            "timezone": station["timezone"],
            "peakHour": station["peakHour"],
            **pred,
        })
        time.sleep(0.5)  # stay well within rate limits
    return results


def split_by_status(predictions: list[dict]):
    settled = [p for p in predictions if p["isPastPeak"] or p["confidence"] >= 8]
    active = [p for p in predictions if not p["isPastPeak"] and p["confidence"] < 8]
    return settled, active


def format_digest(predictions: list[dict]) -> str:
    settled, active = split_by_status(predictions)

    lines = []
    lines.append(
        f"📊 DailyHigh Digest - "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )
    lines.append("")

    if settled:
        lines.append("**Settled (past peak or high confidence):**")
        lines.append("```")
        lines.append(f"{'Station':<12} {'Observed':>9} {'Predicted':>10} {'Conf':>5}")
        lines.append("-" * 40)
        for p in settled:
            lines.append(
                f"{p['icao']:<12} "
                f"{p['observedMax']:>8.1f}° "
                f"{p['predictedMax']:>9.1f}° "
                f"{p['confidence']:>4}/10"
            )
        lines.append("```")
        lines.append("")

    if active:
        lines.append("**Still in play:**")
        lines.append("```")
        lines.append(f"{'Station':<12} {'Observed':>9} {'Predicted':>10} {'Peak in':>8}")
        lines.append("-" * 43)
        for p in active:
            hrs = p["hoursUntilPeak"]
            lines.append(
                f"{p['icao']:<12} "
                f"{p['observedMax']:>8.1f}° "
                f"{p['predictedMax']:>9.1f}° "
                f"{hrs:>6.1f}h"
            )
        lines.append("```")

    return "\n".join(lines)


def near_threshold(predictions: list[dict], target: float, margin: float = 1.0):
    """Return stations where predictedMax is within `margin` °C of target."""
    return [
        p for p in predictions
        if abs(p["predictedMax"] - target) <= margin
    ]


def send_digest(message: str):
    if not WEBHOOK_URL:
        print("No DISCORD_WEBHOOK_URL set, skipping send")
        return
    requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)


def main():
    stations = get_stations()
    predictions = fetch_all_predictions(stations)
    predictions.sort(key=lambda p: p["confidence"], reverse=True)

    digest = format_digest(predictions)
    print(digest)
    send_digest(digest)


if __name__ == "__main__":
    main()
