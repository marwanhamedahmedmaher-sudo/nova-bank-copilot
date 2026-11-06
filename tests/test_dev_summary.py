import json

from evals import edit_report


def write(api, events):
    from app import copilot
    copilot.LOG.write_text("\n".join(json.dumps({"ts": "2026-11-06T10:00:00", **e}) for e in events), encoding="utf-8")


def test_empty_log_gives_zeros(api):
    s = api.get("/api/dev/summary").json()
    assert s["drafts"] == 0 and s["blind_send_pct"] == 0 and s["sends_by_mode"] == {}


def test_blind_send_share(api):
    write(api, [{"event": "agent_send", "case_id": "CASE-101", "mode": "copilot", "edited": False, "changed_pct": 0,
                 "sources_opened": 0, "handle_s": 30},
                {"event": "agent_send", "case_id": "CASE-102", "mode": "copilot", "edited": False, "changed_pct": 0,
                 "sources_opened": 2, "handle_s": 50}])
    assert api.get("/api/dev/summary").json()["blind_send_pct"] == 50.0


def test_handle_time_by_mode(api):
    write(api, [{"event": "agent_send", "case_id": "CASE-101", "mode": "shadow", "edited": True, "changed_pct": 40,
                 "sources_opened": 0, "handle_s": 60},
                {"event": "agent_send", "case_id": "CASE-102", "mode": "shadow", "edited": True, "changed_pct": 20,
                 "sources_opened": 0, "handle_s": 120}])
    s = api.get("/api/dev/summary").json()
    assert s["avg_handle_s_by_mode"]["shadow"] == 90.0
    assert s["sends_by_mode"] == {"shadow": 2}


def test_drafts_and_auto_outcomes_counted(api):
    write(api, [{"event": "suggestion", "case_id": "CASE-101", "status": "ready", "latency_s": 10, "cost_usd": 0.02},
                {"event": "suggestion", "case_id": "CASE-109", "status": "blocked", "latency_s": 20, "cost_usd": 0.04},
                {"event": "auto_outcome", "case_id": "CASE-104", "outcome": "resolved", "risk": "low_resolved"},
                {"event": "auto_outcome", "case_id": "CASE-107", "outcome": "awaiting_approval", "risk": "high"}])
    s = api.get("/api/dev/summary").json()
    assert (s["drafts"], s["blocked"], s["avg_latency_s"]) == (2, 1, 15.0)
    assert s["auto"]["resolved"] == 1 and s["auto"]["awaiting_approval"] == 1


def test_edit_report_blind_sends():
    events = [{"event": "agent_send", "edited": False, "changed_pct": 0, "sources_opened": 0, "mode": "copilot"},
              {"event": "agent_send", "edited": True, "changed_pct": 10, "sources_opened": 0, "mode": "copilot"},
              {"event": "agent_send", "edited": False, "changed_pct": 0, "mode": "copilot"}]  # older send, no field
    assert edit_report.summarise(events)["blind_send_pct"] == 50.0


def test_shadow_sends_stay_out_of_edit_and_blind_send_figures(api):
    write(api, [{"event": "agent_send", "case_id": "CASE-101", "mode": "copilot", "edited": False, "changed_pct": 0,
                 "sources_opened": 1, "handle_s": 30},
                {"event": "agent_send", "case_id": "CASE-104", "mode": "shadow", "edited": True, "changed_pct": 97,
                 "sources_opened": 0, "handle_s": 80}])
    s = api.get("/api/dev/summary").json()
    assert s["edit_share_pct"] == 0 and s["blind_send_pct"] == 0.0
    assert s["sends_by_mode"] == {"copilot": 1, "shadow": 1}


def test_edit_report_leaves_out_shadow_sends():
    events = [{"event": "agent_send", "edited": False, "changed_pct": 0, "sources_opened": 1, "mode": "copilot"},
              {"event": "agent_send", "edited": True, "changed_pct": 97, "sources_opened": 0, "mode": "shadow"}]
    s = edit_report.summarise(edit_report.without_shadow(events))
    assert s["avg_changed_pct_sent"] == 0.0 and s["replies_sent"] == 1
