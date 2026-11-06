from tests.conftest import fake_result


def closed(api, mode):
    return {c["case_id"]: c for c in api.get(f"/api/closed?mode={mode}").json()}


def test_send_closes_case_only_in_its_mode(api):
    api.post("/api/cases/CASE-101/send", json={"drafted_reply": "a", "final_reply": "b", "mode": "shadow"})
    assert "CASE-101" in closed(api, "shadow")
    assert closed(api, "shadow")["CASE-101"]["by"] == "agent"
    assert "CASE-101" not in closed(api, "copilot")


def test_auto_resolved_closes_by_copilot_but_high_stays_open(api):
    api.canned["CASE-104"] = fake_result("CASE-104")
    api.canned["CASE-107"] = fake_result("CASE-107", actions=["request_fee_waiver"])
    api.post("/api/cases/CASE-104/auto")
    api.post("/api/cases/CASE-107/auto")
    c = closed(api, "auto")
    assert c["CASE-104"]["by"] == "copilot" and c["CASE-104"]["outcome"] == "resolved"
    assert "CASE-107" not in c


def test_approve_closes_as_approved(api):
    api.canned["CASE-107"] = fake_result("CASE-107", actions=["request_fee_waiver"])
    api.post("/api/cases/CASE-107/auto")
    api.post("/api/cases/CASE-107/approve", json={"final_reply": "Hello Mariam"})
    assert closed(api, "auto")["CASE-107"]["by"] == "approved"


def test_review_logged_and_attached(api):
    api.canned["CASE-104"] = fake_result("CASE-104")
    api.post("/api/cases/CASE-104/auto")
    r = api.post("/api/cases/CASE-104/review", json={"vote": "down", "note": "wrong fee"})
    assert r.status_code == 200
    assert closed(api, "auto")["CASE-104"]["review"] == {"vote": "down", "note": "wrong fee"}
    assert api.get("/api/dev/summary").json()["auto_reviews"] == {"up": 0, "down": 1}


def test_review_rejects_case_copilot_did_not_close(api):
    assert api.post("/api/cases/CASE-104/review", json={"vote": "up"}).status_code == 409
    assert api.post("/api/cases/CASE-104/review", json={"vote": "maybe"}).status_code == 422


def test_reset_reopens_everything(api):
    api.post("/api/cases/CASE-101/send", json={"drafted_reply": "a", "final_reply": "b", "mode": "copilot"})
    api.post("/api/demo/reset")
    assert closed(api, "copilot") == {}
