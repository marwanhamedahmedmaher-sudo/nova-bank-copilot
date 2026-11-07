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


def closed_chats(evs=None):
    """{mode: [row]}: live chats that ended since the last reset, with the customer's rating when given."""
    evs = _since_reset(events() if evs is None else evs)
    ratings = {e["chat_no"]: e["stars"] for e in evs if e["event"] == "chat_rating"}
    out = {"shadow": [], "copilot": [], "auto": []}
    for e in evs:
        if e["event"] == "chat_end":
            out.setdefault(e.get("mode", "copilot"), []).append({
                "case_id": e["case_id"], "chat_no": e["chat_no"], "at": e["ts"], "by": e["handled_by"],
                "ended_by": e["ended_by"], "transcript": e["transcript"], "rating": ratings.get(e["chat_no"])})
    return out


# ---- Analytics screen (control room) ------------------------------------------------------------
IN_SCOPE = {"dispute_status", "fee_explanation", "card_replacement"}


def ticket_baseline():
    """Chat handle time and scope share from our synthetic tickets, the same numbers the business case uses."""
    import csv
    from . import store
    rows = list(csv.DictReader(open(store.DATA / "tickets.csv", encoding="utf-8")))
    scope = [r for r in rows if r["category"] in IN_SCOPE]
    chats = [float(r["resolution_minutes"]) for r in scope if r["channel"] == "chat"]
    return {"aht_chat_min": round(sum(chats) / len(chats), 1) if chats else 0,
            "scope_share": round(len(scope) / len(rows), 2) if rows else 0,
            "chat_share": round(len(chats) / len(scope), 2) if scope else 0}


def analytics(assumptions, evs=None):
    """Deflection and agent minutes saved, from the audit log.
    Minutes saved = chats the copilot resolved alone x full chat handle time
                  + chats an agent sent or approved with a copilot draft, or the copilot escalated, x minutes saved per assisted chat.
    Shadow sends save nothing: the agent wrote the reply."""
    evs = events() if evs is None else evs
    base = ticket_baseline()
    aht, saved = base["aht_chat_min"], float(assumptions["saved_chat_min"])
    days = defaultdict(lambda: {"resolved": 0, "escalated": 0, "assisted": 0, "shadow": 0, "minutes": 0.0})
    for e in evs:
        d = days[e["ts"][:10]]
        if e["event"] == "auto_outcome" and e["outcome"] in ("resolved", "escalated"):
            d[e["outcome"]] += 1
            d["minutes"] += aht if e["outcome"] == "resolved" else saved
        elif e["event"] == "agent_send":
            if e.get("mode") == "shadow":
                d["shadow"] += 1
            else:
                d["assisted"] += 1
                d["minutes"] += saved
    tot = {k: sum(d[k] for d in days.values()) for k in ("resolved", "escalated", "assisted", "shadow", "minutes")}
    outcomes = Counter(e["outcome"] for e in evs if e["event"] == "auto_outcome")
    assessed = sum(outcomes.values())
    handled = tot["resolved"] + tot["escalated"] + tot["assisted"] + tot["shadow"]
    per_chat = tot["minutes"] / handled if handled else 0
    in_scope_chats = assumptions["contacts_per_month"] * base["scope_share"] * base["chat_share"]
    deflect_rate = tot["resolved"] / assessed if assessed else 0
    return {
        "baseline": base, "assumptions": assumptions,
        "chats_handled": handled, "assessed_by_copilot": assessed,
        "deflected": tot["resolved"], "escalated_by_copilot": tot["escalated"],
        "deflection_pct": round(100 * deflect_rate, 1),
        "assisted_sends": tot["assisted"], "shadow_sends": tot["shadow"],
        "minutes_saved": round(tot["minutes"], 1), "minutes_per_chat": round(per_chat, 2),
        "auto_outcomes": {k: outcomes.get(k, 0) for k in ("resolved", "escalated", "awaiting_approval", "needs_agent")},
        "avg_handle_s_by_mode": handle_by_mode([e for e in evs if e["event"] == "agent_send"]),
        "copilot_edits": copilot_edits(evs),
        "by_day": [{"day": k, **{x: round(v, 1) if x == "minutes" else v for x, v in d.items()}} for k, d in sorted(days.items())
                   if any(d.values())],
        "projection": {"in_scope_chats_per_month": round(in_scope_chats),
                       "deflected_per_month": round(in_scope_chats * deflect_rate),
                       "agent_hours_saved_per_month": round(in_scope_chats * per_chat / 60)},
    }


EDIT_BANDS = (("as_drafted", "Sent as drafted"), ("light", "Light edit (under 10%)"),
              ("moderate", "Moderate edit (10-30%)"), ("heavy", "Heavy rewrite (over 30%)"))


def copilot_edits(evs):
    """How agents changed copilot drafts before sending, in copilot mode only (a shadow send is the agent's own reply,
    an auto-reply approval is counted with auto-reply). changed_pct = share of the draft's words changed, 0-100."""
    sends = [e for e in evs if e["event"] == "agent_send" and e.get("mode", "copilot") == "copilot" and "changed_pct" in e]
    edited = [e for e in sends if e["changed_pct"] > 0]
    counts = Counter(edit_band(e["changed_pct"]) for e in sends)
    avg = lambda xs: round(sum(e["changed_pct"] for e in xs) / len(xs), 1) if xs else 0
    return {
        "sent": len(sends), "edited": len(edited), "as_drafted": len(sends) - len(edited),
        "edited_pct": round(100 * len(edited) / len(sends), 1) if sends else 0,
        "avg_change_pct": avg(sends),            # across every send, unedited ones count as 0
        "avg_change_when_edited_pct": avg(edited),
        "bands": [{"key": k, "label": label, "count": counts.get(k, 0)} for k, label in EDIT_BANDS],
        "flagged": sum(e["event"] == "agent_flag" for e in evs),
        "biggest": [{"case_id": e["case_id"], "changed_pct": e["changed_pct"], "at": e["ts"]}
                    for e in sorted(edited, key=lambda e: e["changed_pct"], reverse=True)[:5]],
    }


def edit_band(p):
    return "as_drafted" if p == 0 else "light" if p < 10 else "moderate" if p <= 30 else "heavy"


def copilot_edit_rows(evs=None, band=None):
    """Each copilot-mode send with the draft and what the agent sent (both masked, as logged), biggest change first."""
    evs = events() if evs is None else evs
    rows = [{"case_id": e["case_id"], "at": e["ts"], "changed_pct": e["changed_pct"], "band": edit_band(e["changed_pct"]),
             "drafted_reply": e.get("drafted_reply", ""), "final_reply": e.get("final_reply", ""),
             "sources_opened": e.get("sources_opened"), "handle_s": e.get("handle_s")}
            for e in evs if e["event"] == "agent_send" and e.get("mode", "copilot") == "copilot" and "changed_pct" in e]
    return sorted([r for r in rows if not band or r["band"] == band], key=lambda r: (-r["changed_pct"], r["at"]))
