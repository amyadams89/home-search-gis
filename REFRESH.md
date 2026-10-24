# Refreshing the monthly-cost panel data

`mortgage_ranges.json` holds the P05 to P95 range for the 30-year fixed mortgage rate
(Freddie Mac PMMS, FRED series `MORTGAGE30US`) 90 days after its `as_of` date. The panel
reads it at page load and prints `as_of` in its fine print.

Refresh weekly (PMMS publishes Thursdays):

```bash
python scripts/refresh_mortgage_ranges.py <path to foresight_baseline.py>
git diff mortgage_ranges.json   # check as_of moved and the quantiles look sane
```

The script runs `foresight_baseline.py forecast --series MORTGAGE30US --horizon-days 90 --tuned --floor 0`
(path as an argument or in `FORESIGHT_BASELINE`). `held_out` records the forecaster's out-of-sample
coverage (the share of past outcomes that landed inside the 80% and 50% bands). The script refuses to
write when the quantiles are out of order, the forecaster warns, 80% coverage is outside 0.65 to 0.95,
or `as_of` is more than 14 days old. The page shows an out-of-date warning once `as_of` is 21 days old.

Pushing to `master` deploys publicly within seconds. Commit the refreshed JSON on its own.

Property-tax defaults live in `index.html` (`COUNTY_TAX`), each with a dated source URL.
The defaults are median effective rates, which understate a new purchase in a MUD area.
Re-check them once a year after counties adopt rates (October).
