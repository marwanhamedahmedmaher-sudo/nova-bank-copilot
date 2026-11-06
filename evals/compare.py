"""Compares an eval run with the committed baseline and fails (exit 1) if the copilot got worse.
CI runs this after evals.run_evals, so a lower score blocks the merge. No API calls.

    python -m evals.compare                          # newest evals/results/run *.json vs evals/baseline.json
    python -m evals.compare "evals/results/run 2026-10-30 1835.json"
    python -m evals.compare --write-baseline "evals/results/run 2026-10-31 1233.json"

Fails when: fewer cases pass, Honesty or Harmlessness drops, or a safety case (S..) that passed in the baseline now fails.
Updating the baseline is a human decision: write it, read the diff, commit it in the PR.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
BASELINE = ROOT / "baseline.json"
SCORES = ("Helpfulness", "Honesty", "Harmlessness", "Overall 3H")
GUARDED = ("Honesty", "Harmlessness")  # these may never go below the baseline


def latest_run():
    runs = sorted(RESULTS.glob("run *.json"))  # stamp is YYYY-MM-DD HHMM, so name order is time order
    if not runs:
        sys.exit("no evals/results/run *.json found; run python -m evals.run_evals first")
    return runs[-1]


def load_run(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    s = data["summary"]
    return {
        "source": Path(path).name,
        "passed": s["passed"],
        "total": s["total"],
        "errors": s["errors"],
        "scores": {k: s[k] for k in SCORES},
        # a case that errored counts as failed
        "cases": {r["case"]["id"]: bool(not r["error"] and r["passed"]) for r in data["runs"]},
    }


def compare(base, new):
    """Returns (failures, notes). Any failure blocks the merge."""
    failures, notes = [], []
    if new["passed"] < base["passed"]:
        failures.append(f"Passed dropped: {new['passed']} of {new['total']} (baseline {base['passed']} of {base['total']})")
    for k in GUARDED:
        if new["scores"][k] < base["scores"][k]:
            failures.append(f"{k} dropped: {new['scores'][k]} (baseline {base['scores'][k]})")
    regressed = sorted(cid for cid, ok in base["cases"].items() if cid.startswith("S") and ok and not new["cases"].get(cid, False))
    if regressed:
        failures.append(f"Safety cases that passed in the baseline now fail: {', '.join(regressed)}")
    if new["errors"]:
        notes.append(f"{new['errors']} case(s) errored (counted as failed); check the API key and the log")
    if new["total"] != base["total"]:
        notes.append(f"Case count changed: {new['total']} now, {base['total']} in the baseline")
    fixed = sorted(cid for cid, ok in new["cases"].items() if ok and not base["cases"].get(cid, False))
    broke = sorted(cid for cid, ok in base["cases"].items() if ok and not new["cases"].get(cid, False))
    if fixed:
        notes.append(f"Now passing: {', '.join(fixed)}")
    if broke:
        notes.append(f"Now failing: {', '.join(broke)}")
    return failures, notes


def report(base, new, failures, notes):
    lines = [f"## Evals: {'FAIL' if failures else 'PASS'}", "",
             f"Run `{new['source']}` against baseline `{base['source']}`", "",
             "| | Baseline | This run |", "|---|---|---|",
             f"| Passed | {base['passed']} of {base['total']} | {new['passed']} of {new['total']} |"]
    lines += [f"| {k} | {base['scores'][k]} | {new['scores'][k]} |" for k in SCORES]
    lines += [""] + [f"- **{f}**" for f in failures] + [f"- {n}" for n in notes]
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if args[:1] == ["--write-baseline"]:
        run = load_run(args[1] if len(args) > 1 else latest_run())
        BASELINE.write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {BASELINE.relative_to(ROOT.parent)} from {run['source']}; review the diff and commit it")
        return
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    new = load_run(args[0] if args else latest_run())
    failures, notes = compare(base, new)
    text = report(base, new, failures, notes)
    print(text)
    if os.getenv("GITHUB_STEP_SUMMARY"):  # shows the table on the PR's Checks page
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text + "\n")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
