from tests.conftest import fake_result


def test_auto_low_resolved_sends_reply(api):
    api.canned["CASE-104"] = fake_result("CASE-104")
    r = api.post("/api/cases/CASE-104/auto").json()
    assert r["outcome"] == "resolved"
    assert [e["event"] for e in api.events()].count("auto_send") == 1


def test_auto_escalated_submits_handover_to_policy_approver(api):
    api.canned["CASE-105"] = fake_result("CASE-105", actions=["open_dispute"])
    r = api.post("/api/cases/CASE-105/auto").json()
    assert r["outcome"] == "escalated"
    acts = [e for e in api.events() if e["event"] == "auto_action"]
    assert acts and acts[0]["approver"] == "disputes_team"


def test_auto_high_waits_and_sends_nothing(api):
    api.canned["CASE-107"] = fake_result("CASE-107", actions=["request_fee_waiver"])
    r = api.post("/api/cases/CASE-107/auto").json()
    assert r["outcome"] == "awaiting_approval"
    assert not [e for e in api.events() if e["event"] in ("auto_send", "auto_action")]


def test_auto_blocked_goes_to_agent(api):
    api.canned["CASE-109"] = fake_result("CASE-109", status="blocked")
    r = api.post("/api/cases/CASE-109/auto").json()
    assert r["outcome"] == "needs_agent"
    assert not [e for e in api.events() if e["event"] == "auto_send"]


def test_auto_writes_outcome_event(api):
    api.canned["CASE-104"] = fake_result("CASE-104")
    api.post("/api/cases/CASE-104/auto")
    outcomes = [e for e in api.events() if e["event"] == "auto_outcome"]
    assert outcomes[0]["outcome"] == "resolved" and outcomes[0]["risk"] == "low_resolved"


def test_approve_before_assessment_is_409(api):
    assert api.post("/api/cases/CASE-107/approve", json={"final_reply": "x"}).status_code == 409


def test_approve_sends_and_submits_actions(api):
    api.canned["CASE-107"] = fake_result("CASE-107", actions=["request_fee_waiver"])
    api.post("/api/cases/CASE-107/auto")
    r = api.post("/api/cases/CASE-107/approve", json={"final_reply": "Hello Mariam", "handle_s": 12}).json()
    assert r["sent"] is True
    send = [e for e in api.events() if e["event"] == "agent_send"][0]
    assert send["mode"] == "auto" and send["approved"] is True
    assert [e["action"] for e in api.events() if e["event"] == "agent_action"] == ["request_fee_waiver"]


def test_send_logs_mode_sources_and_handle_time(api):
    api.post("/api/cases/CASE-101/send", json={"drafted_reply": "a b", "final_reply": "a b", "mode": "shadow",
                                               "sources_opened": 0, "handle_s": 42})
    send = [e for e in api.events() if e["event"] == "agent_send"][0]
    assert (send["mode"], send["sources_opened"], send["handle_s"]) == ("shadow", 0, 42)


def test_source_opened_is_logged(api):
    api.post("/api/cases/CASE-101/source_opened", json={"source": "POL-04 §5"})
    e = [e for e in api.events() if e["event"] == "source_opened"][0]
    assert e["source"] == "POL-04 §5" and e["case_id"] == "CASE-101"


def test_auto_complaint_flag_without_action_really_logs_the_complaint(api):
    api.canned["CASE-101"] = fake_result("CASE-101", risk_flags=["complaint"])
    r = api.post("/api/cases/CASE-101/auto").json()
    assert r["outcome"] == "escalated"
    assert [a["action"] for a in r["actions"]] == ["log_complaint"]
    assert [e["action"] for e in api.events() if e["event"] == "auto_action"] == ["log_complaint"]


def test_approve_refuses_a_blocked_case(api):
    api.canned["CASE-109"] = fake_result("CASE-109", status="blocked")
    api.post("/api/cases/CASE-109/auto")
    assert api.post("/api/cases/CASE-109/approve", json={"final_reply": "x"}).status_code == 409
    assert not [e for e in api.events() if e["event"] == "agent_send"]


def test_approve_twice_submits_actions_once(api):
    api.canned["CASE-103"] = fake_result("CASE-103", actions=["block_card"])
    api.post("/api/cases/CASE-103/auto")
    assert api.post("/api/cases/CASE-103/approve", json={"final_reply": "Hello Mariam"}).status_code == 200
    assert api.post("/api/cases/CASE-103/approve", json={"final_reply": "Hello Mariam"}).status_code == 409
    assert len([e for e in api.events() if e["event"] == "agent_action"]) == 1
