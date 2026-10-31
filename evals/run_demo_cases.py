"""Runs the 9 live demo cases through the full pipeline and prints a one-line verdict each.

    .venv\\Scripts\\python -m evals.run_demo_cases
"""
import json
from concurrent.futures import ThreadPoolExecutor

from app import copilot, store


def run(case_id):
    try:
        return case_id, copilot.suggest(case_id), None
    except Exception as e:
        return case_id, None, repr(e)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=9) as pool:
        results = list(pool.map(run, store.cases()))
    for case_id, r, err in results:
        if err:
            print(f"{case_id}: ERROR {err}")
            continue
        fails = [f"{c['name']}: {c['detail']}" for c in r["checks"] if not c["passed"]]
        acts = ", ".join(f"{a['action']}->{a['approver']}" for a in r["draft"]["suggested_actions"]) or "none"
        flags = sorted(set(r["input_flags"]) | set(r["draft"]["risk_flags"]))
        print(f"\n=== {case_id} [{r['status']}] {r['latency_s']}s ${r['cost_usd']:.4f} retried={r['retried']} flags={flags} actions={acts}")
        print("EN:", r["reply_in_english"])
        for f in fails:
            print("  FAIL", f)
