# Part 1: Temperature Threshold Alerts

Watch a single station and get alerted when the daily high crosses (or won't cross) a temperature target.

**Full tutorial:** [Build a Weather Bot, Part 1: Temperature Threshold Alerts](https://dailyhigh.app/blog/build-a-temperature-alert-bot-with-the-dailyhigh-api)

## How it works

1. Fetches the prediction for a station from `/api/v1/prediction/:icao`
2. Compares the observed max and predicted max against your target
3. Sends a Discord alert when the outcome is decided (crossed or unlikely)
4. Uses a state file to avoid duplicate alerts on the same day

## Configuration

Edit the `ALERT` dict in `alert.py`:

```python
ALERT = {
    "icao": "KLGA",       # station ICAO code
    "target": 29.4,        # target temperature in °C
    "direction": "over",   # "over" or "under"
}
```

## Schedule

Run every 30 minutes during daylight hours:

```bash
*/30 6-20 * * * cd /path/to/weather-bot && python part1_alerts/alert.py >> alert.log 2>&1
```
