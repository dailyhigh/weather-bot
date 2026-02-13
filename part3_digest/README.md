# Part 3: Monitoring Multiple Stations

Poll all tracked stations, rank by confidence, and generate a daily digest sent to Discord.

**Full tutorial:** [Build a Weather Bot, Part 3: Monitoring Multiple Stations](https://dailyhigh.app/blog/monitor-multiple-stations-with-the-dailyhigh-api)

## How it works

1. Fetches all stations from `/api/v1/stations`
2. Pulls predictions for each station
3. Splits into "settled" (past peak / high confidence) and "still in play"
4. Formats a digest and posts it to Discord

## Schedule

Run 2-3 times per day:

```bash
# 10 AM, 6 PM, 11 PM UTC
0 10,18,23 * * * cd /path/to/weather-bot && python part3_digest/digest.py >> digest.log 2>&1
```

Or use the included GitHub Actions workflow at `.github/workflows/digest.yml`.
