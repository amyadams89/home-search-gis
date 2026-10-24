"""Regenerate mortgage_ranges.json for the true-cost panel.

Runs the Foresight baseline forecaster for the 30-year fixed rate and keeps
only what the panel needs. See REFRESH.md.
"""
import datetime
import json
import os
import subprocess
import sys

BASELINE = os.environ.get("FORESIGHT_BASELINE", "C:/Users/amyad/Scripts/foresight_baseline.py")
ARGS = ["forecast", "--series", "MORTGAGE30US", "--horizon-days", "90", "--tuned", "--floor", "0"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mortgage_ranges.json")


def main():
    raw = subprocess.run([sys.executable, BASELINE] + ARGS, check=True,
                         capture_output=True, text=True).stdout
    d = json.loads(raw)
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
    with open(OUT, "w", newline="\n") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("wrote", os.path.normpath(OUT), "as_of", out["as_of"], "p10/p50/p90",
          q["0.1"], q["0.5"], q["0.9"])


if __name__ == "__main__":
    main()
