"""Numbers for the AI PM and AI engineer (dev mode), read from the audit log."""
import json
from collections import Counter, defaultdict

from . import copilot


def events():
    if not copilot.LOG.exists():
        return []
    return [json.loads(line) for line in copilot.LOG.read_text(encoding="utf-8").splitlines() if line.strip()]


def blind_send_pct(sends):
    """Share of sends that went out unedited without the agent opening a single source (Telos rec 14).
    Only sends that record sources_opened count, so older log lines don't skew it."""
    tracked = [e for e in sends if "sources_opened" in e]
    blind = [e for e in tracked if not e.get("edited") and not e["sources_opened"]]
    return round(100 * len(blind) / len(tracked), 1) if tracked else 0.0


def handle_by_mode(sends):
    times = defaultdict(list)
    for e in sends:
        if e.get("handle_s") is not None:
            times[e.get("mode", "copilot")].append(e["handle_s"])
    return {m: round(sum(v) / len(v), 1) for m, v in times.items()}


def summary(evs=None):
    evs = events() if evs is None else evs
    drafts = [e for e in evs if e["event"] == "suggestion"]
    sends = [e for e in evs if e["event"] == "agent_send"]
    assisted = [e for e in sends if e.get("mode") != "shadow"]  # a shadow send is the agent's own reply, not an edit
    avg = lambda xs, k: round(sum(e[k] for e in xs) / len(xs), 4 if k == "cost_usd" else 1) if xs else 0
    outcomes = Counter(e["outcome"] for e in evs if e["event"] == "auto_outcome")
    return {
        "drafts": len(drafts),
        "avg_latency_s": avg(drafts, "latency_s"),
        "avg_cost_usd": avg(drafts, "cost_usd"),
        "blocked": sum(e["status"] == "blocked" for e in drafts),
        "sends_by_mode": dict(Counter(e.get("mode", "copilot") for e in sends)),
        "blind_send_pct": blind_send_pct(assisted),
        "avg_handle_s_by_mode": handle_by_mode(sends),
        "edit_share_pct": avg([e for e in assisted if "changed_pct" in e], "changed_pct"),
        "auto": {k: outcomes.get(k, 0) for k in ("resolved", "escalated", "awaiting_approval", "needs_agent")},
        "source_opens": sum(e["event"] == "source_opened" for e in evs),
        "auto_reviews": {v: sum(1 for r in reviews(evs).values() if r["vote"] == v) for v in ("up", "down")},
    }


def _since_reset(evs):
    """The demo can be reset; only events after the last reset decide what is closed. The log itself stays append-only."""
    last = max((i for i, e in enumerate(evs) if e["event"] == "demo_reset"), default=-1)
    return evs[last + 1:]


def reviews(evs=None):
    """Latest thumbs up/down per auto-closed case (the agent can change their mind)."""
    evs = events() if evs is None else evs
    return {e["case_id"]: {"vote": e["vote"], "note": e.get("note", "")} for e in _since_reset(evs) if e["event"] == "auto_review"}


def closed(evs=None):
    """{mode: {case_id: {by, at, reply, outcome?, review?}}}: what each mode's Closed tab shows."""
    evs = _since_reset(events() if evs is None else evs)
    out = {"shadow": {}, "copilot": {}, "auto": {}}
    replies = {}
    for e in evs:
        cid = e.get("case_id")
        if e["event"] == "agent_send":
            m = e.get("mode", "copilot")
            out.setdefault(m, {})[cid] = {"by": "approved" if e.get("approved") else "agent", "at": e["ts"],
                                          "reply": e.get("final_reply", "")}
        elif e["event"] == "auto_send":
            replies[cid] = e.get("reply", "")
        elif e["event"] == "auto_outcome" and e["outcome"] in ("resolved", "escalated"):
            out["auto"][cid] = {"by": "copilot", "at": e["ts"], "reply": replies.get(cid, ""), "outcome": e["outcome"]}
    for cid, r in reviews(evs).items():
        if cid in out["auto"]:
            out["auto"][cid]["review"] = r
    return out
