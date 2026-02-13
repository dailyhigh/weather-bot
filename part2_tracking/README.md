# Part 2: Tracking Predictions Through the Day

Follow one station through the full day: morning prediction, midday observations, and the final daily high from the history endpoint.

**Full tutorial:** [Build a Weather Bot, Part 2: Tracking Predictions Through the Day](https://dailyhigh.app/blog/track-a-daily-high-from-prediction-to-result)

## How it works

1. Fetches the prediction, current weather, and (if past peak) history for a station
2. Logs a snapshot to `daily_log.json` each time it runs
3. Shows how the prediction converges toward the final result through the day

## Configuration

Edit the `STATION` variable in `tracker.py`:

```python
STATION = "KLGA"  # any ICAO code tracked by DailyHigh
```

## Schedule

Run 3 times per day (morning, midday, evening):

```bash
0 8,13,17 * * * cd /path/to/weather-bot && python part2_tracking/tracker.py >> tracker.log 2>&1
```
