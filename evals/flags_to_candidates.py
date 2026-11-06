"""Turns drafts that agents flagged in the console into candidate eval cases for a human to review.

    python -m evals.flags_to_candidates                  # reads app/logs/audit.jsonl
    python -m evals.flags_to_candidates path/to/audit.jsonl

Each agent_flag event is paired with the last suggestion for the same case before it, and written to
evals/candidates.jsonl in the golden set's shape. Masked text only. The expected behaviour (type, benchmark
answer and location, expect_answer_found, must_flag, must_suggest) is left blank for a human to fill in;
the "review" field shows what the copilot did and why the agent flagged it.

Nothing goes into golden_set.jsonl automatically. A human fills the blanks and moves the line over, keeping
"review" (the eval runner ignores it, and it stops the same flag being pulled again). To drop a candidate,
leave the line here with "type": "rejected" rather than deleting it.
"""
import json
import re
import sys
from pathlib import Path

from app import guards, store

ROOT = Path(__file__).resolve().parent
LOG = ROOT.parent / "app" / "logs" / "audit.jsonl"
OUT = ROOT / "candidates.jsonl"
GOLDEN = ROOT / "golden_set.jsonl"


def read_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.exists() else []


def flagged(log):
    """Yields (flag event, last suggestion event for that case before the flag, or None)."""
    last = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e["event"] == "suggestion":
            last[e["case_id"]] = e
        elif e["event"] == "agent_flag":
            yield e, last.get(e["case_id"])


def candidate(n, flag, sug):
    if sug:
        d = sug["draft"]
        customer_id, question, intent, language = sug["customer_id"], sug["masked_message"], d["intent"], d["customer_language"]
        cited = sorted({c["source_id"].strip() for f in d["facts"] for c in f["citations"]})
        seen = {"status": sug["status"], "input_flags": sug["input_flags"], "answer_found": d["answer_found"],
                "reply_in_english": d["reply_in_english"], "cited": cited,
                "suggested_actions": [a["action"] for a in d["suggested_actions"]],
                "failed_checks": [c["name"] for c in sug["checks"] if not c["passed"]]}
    else:  # no suggestion in the log (e.g. a replayed draft): fall back to the queued case's own message
        case = store.cases()[flag["case_id"]]
        customer_id, question, intent, language = case["customer_id"], case["message"], "", ""
        seen = {"note": "no suggestion found in the log; question is the case's original message"}
    return {
        "id": f"F{n:02d}", "type": "", "intent": intent, "customer_id": customer_id, "language": language,
        "question": guards.mask_pii(question), "benchmark_answer": "", "benchmark_location": "",
        "expect_answer_found": None, "must_flag": [], "must_suggest": [],
        "review": {"case_id": flag["case_id"], "flagged_at": flag["ts"], "agent_note": guards.mask_pii(flag["note"]),
                   "copilot_did": seen},
    }


def main():
    log = Path(sys.argv[1]) if len(sys.argv) > 1 else LOG
    if not log.exists():
        sys.exit(f"no audit log at {log}; flag a draft in the console first")
    existing = read_jsonl(OUT)
    known = existing + read_jsonl(GOLDEN)  # a flag already reviewed (kept, rejected or promoted) is never pulled again
    done = {(c["review"]["case_id"], c["review"]["flagged_at"]) for c in known if "review" in c}
    n = max((int(c["id"][1:]) for c in known if re.fullmatch(r"F\d+", c["id"])), default=0)
    added, skipped = [], 0
    for flag, sug in flagged(log):
        if (flag["case_id"], flag["ts"]) in done:
            continue
        if not sug and flag["case_id"] not in store.cases():
            skipped += 1
            continue
        n += 1
        added.append(candidate(n, flag, sug))
    with open(OUT, "a", encoding="utf-8") as f:
        for c in added:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"added {len(added)} candidate(s) to {OUT.relative_to(ROOT.parent)} ({len(existing)} already there"
          f"{f', {skipped} skipped with no message to recover' if skipped else ''}). Fill in the blanks before moving any to the golden set.")


if __name__ == "__main__":
    main()
