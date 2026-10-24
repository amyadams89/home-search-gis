"""Regenerate mortgage_ranges.json for the monthly-cost panel.

Runs the Foresight baseline forecaster for the 30-year fixed rate and keeps
only what the panel needs. Refuses to write a range that fails its checks.
See REFRESH.md.

Usage: python scripts/refresh_mortgage_ranges.py <path to foresight_baseline.py>
   or: FORESIGHT_BASELINE=<path> python scripts/refresh_mortgage_ranges.py
"""
import datetime
import json
import math
import os
import subprocess
import sys

ARGS = ["forecast", "--series", "MORTGAGE30US", "--horizon-days", "90", "--tuned", "--floor", "0"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mortgage_ranges.json")
KEYS = ["p05", "p10", "p25", "p50", "p75", "p90", "p95"]
MAX_AGE_DAYS = 14          # PMMS is weekly; an older as_of means the source did not update
COVERAGE_80_OK = (0.65, 0.95)  # same band as the Home Search "proven" gate


def problems(out):
    found = []
    q = [out["quantiles"][k] for k in KEYS]
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in q + [out["current"]]):
        return ["a quantile or the current rate is not a finite number"]
    if not 0 < out["current"] < 25:
        found.append("current rate %s is outside 0 to 25 percent" % out["current"])
    if q != sorted(q):
        found.append("quantiles are not in order: %s" % q)
    if not all(0 < v < 25 for v in q):
        found.append("a quantile is outside 0 to 25 percent: %s" % q)
    if out["warnings"]:
        found.append("forecaster warnings: %s" % out["warnings"])
    c80 = out["held_out"]["coverage_80"]
    if not COVERAGE_80_OK[0] <= c80 <= COVERAGE_80_OK[1]:
        found.append("held-out 80%% coverage %.3f is outside %s" % (c80, COVERAGE_80_OK))
    age = (datetime.date.today() - datetime.date.fromisoformat(out["as_of"][:10])).days
    if age < 0:
        found.append("as_of %s is in the future" % out["as_of"])
    if age > MAX_AGE_DAYS:
        found.append("as_of %s is %d days old" % (out["as_of"], age))
    return found


def main():
    baseline = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FORESIGHT_BASELINE")
    if not baseline:
        sys.exit("give the path to foresight_baseline.py (argument or FORESIGHT_BASELINE)")
    proc = subprocess.run([sys.executable, baseline] + ARGS, capture_output=True,
                          text=True, encoding="utf-8")
    if proc.returncode != 0:
        sys.exit("forecaster failed (exit %d), NOT written:\n%s" % (proc.returncode, proc.stderr))
    d = json.loads(proc.stdout)
    q = d["quantiles"]
    ho = d["tuning"]["held_out"]
    out = {
        "series": "MORTGAGE30US",
        "description": "Freddie Mac PMMS 30-year fixed mortgage rate (percent), empirical distribution of the rate 90 days after as_of.",
        "as_of": d["as_of"],
        "current": d["current"],
        "horizon_days": d["horizon_days"],
        "quantiles": {"p05": q["0.05"], "p10": q["0.1"], "p25": q["0.25"], "p50": q["0.5"],
                      "p75": q["0.75"], "p90": q["0.9"], "p95": q["0.95"]},
        "held_out": {k: ho[k] for k in ("window", "origins_scored", "n_effective", "coverage_80",
                                        "coverage_80_se", "coverage_50", "coverage_50_se")},
        "warnings": d.get("warnings", []),
        "generated_on": datetime.date.today().isoformat(),
        "generator": "foresight_baseline.py " + " ".join(ARGS),
    }
    found = problems(out)
    if found:
        sys.exit("NOT written:\n  " + "\n  ".join(found))
    tmp = OUT + ".tmp"
    with open(tmp, "w", newline="\n", encoding="utf-8") as f:
        json.dump(out, f, indent=2, allow_nan=False)
        f.write("\n")
    os.replace(tmp, OUT)
    print("wrote", os.path.normpath(OUT), "as_of", out["as_of"], "p10/p50/p90",
          q["0.1"], q["0.5"], q["0.9"])


if __name__ == "__main__":
    main()
