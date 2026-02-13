# weather-bot

Example Python scripts for building weather bots with the [DailyHigh API](https://dailyhigh.app/docs/api).

This repo contains the working code from the three-part tutorial series on the [DailyHigh blog](https://dailyhigh.app/blog):

1. **[Part 1: Temperature Threshold Alerts](https://dailyhigh.app/blog/build-a-temperature-alert-bot-with-the-dailyhigh-api)** — Watch a single station and get alerted when it crosses (or won't cross) a temperature target.
2. **[Part 2: Tracking Predictions Through the Day](https://dailyhigh.app/blog/track-a-daily-high-from-prediction-to-result)** — Follow one station from morning prediction to final daily high using three API endpoints.
3. **[Part 3: Monitoring Multiple Stations](https://dailyhigh.app/blog/monitor-multiple-stations-with-the-dailyhigh-api)** — Poll all tracked stations, rank by confidence, and generate a daily digest.

## Setup

```bash
git clone https://github.com/dailyhigh/weather-bot.git
cd weather-bot
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your API key and (optionally) a Discord webhook URL:

```
DAILYHIGH_API_KEY=dh_live_xxxxx
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

You can get an API key from your [DailyHigh account page](https://dailyhigh.app/account) (requires a Pro subscription).

## Usage

Each part is a standalone script:

```bash
# Part 1: Check a threshold and alert if crossed
python part1_alerts/alert.py

# Part 2: Log a station's prediction lifecycle
python part2_tracking/tracker.py

# Part 3: Generate a multi-station digest
python part3_digest/digest.py
```

## Scheduling

All three scripts are designed to run on a cron or GitHub Actions schedule. See each part's README for recommended intervals, or use the included workflow:

```bash
# .github/workflows/digest.yml runs Part 3 at 10 AM, 6 PM, and 11 PM UTC
```

## API Reference

These scripts use four endpoints from the [DailyHigh API](https://dailyhigh.app/docs/api):

| Endpoint | Used in |
|----------|---------|
| `GET /api/v1/stations` | Part 3 |
| `GET /api/v1/prediction/:icao` | Parts 1, 2, 3 |
| `GET /api/v1/weather/:icao` | Part 2 |
| `GET /api/v1/history/:icao/:date` | Part 2 |

All temperatures are in °C. All timestamps are station-local.

## License

MIT
