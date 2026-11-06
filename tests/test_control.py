"""Control room: guardrails, models with a backup, the golden set and analytics. No API calls."""
import json
from types import SimpleNamespace

import anthropic
import httpx
import pytest

from app import control, copilot, dev


def check(name, passed, severity="block", detail="d"):
    return {"name": name, "passed": passed, "severity": severity, "detail": detail}


def test_switched_off_guardrail_never_blocks(api):
    assert api.post("/api/control/guardrails/Numbers match the sources", json={"enabled": False}).status_code == 200
    out = control.apply_checks([check("Numbers match the sources", False)], ["hi"], "")
    assert out[0]["passed"] and out[0]["severity"] == "off" and "would have failed" in out[0]["detail"]
    assert api.events()[-1]["event"] == "config_change"


def test_block_can_become_warn(api):
    api.post("/api/control/guardrails/Every claim has a source", json={"severity": "warn"})
    out = control.apply_checks([check("Every claim has a source", False)], ["hi"], "")
    assert out[0]["severity"] == "warn" and not out[0]["passed"]


def test_locked_guardrails_stay_on(api):
    assert api.post("/api/control/guardrails/Only this customer's records", json={"enabled": False}).status_code == 403
    assert api.post("/api/control/guardrails/third_party_request", json={"enabled": False}).status_code == 403
    assert api.post("/api/control/guardrails/made up", json={"enabled": False}).status_code == 404


def test_custom_reply_guardrail_blocks_a_phrase(api):
    r = api.post("/api/control/guardrails/custom", json={"name": "Refund promise", "phrases": ["we will refund"]})
    assert r.status_code == 200
    out = control.apply_checks([], ["Hello, we will refund you today."], "where is my money")
    assert out == [{"name": "Refund promise", "passed": False, "severity": "block", "custom": True,
                    "detail": "reply contains: we will refund"}]
    assert control.apply_checks([], ["Hello"], "")[0]["passed"]
    assert control.apply_checks([check("x", True)]) == [check("x", True)]  # late checks: custom rules not added twice
    assert api.delete("/api/control/guardrails/custom/refund-promise").status_code == 200
    assert control.apply_checks([], ["we will refund"], "") == []


def test_custom_message_guardrail(api):
    api.post("/api/control/guardrails/custom", json={"name": "Threat to go to the press", "phrases": ["newspaper"],
                                                      "target": "message", "severity": "warn"})
    out = control.apply_checks([], ["Hello"], "I will tell the newspaper")
    assert out[0]["severity"] == "warn" and not out[0]["passed"] and "customer message" in out[0]["detail"]


def test_custom_guardrail_needs_phrases(api):
    assert api.post("/api/control/guardrails/custom", json={"name": "x", "phrases": [" "]}).status_code == 400


def test_switched_off_input_flag_is_dropped(api):
    api.post("/api/control/guardrails/approval_request", json={"enabled": False})
    assert control.input_flags(["approval_request", "third_party_request"]) == ["third_party_request"]


class FakeClient:
    """Stands in for the Anthropic client: fails for the models in `down`, records which model was asked."""
    def __init__(self, down=()):
        self.down, self.asked = set(down), []
        self.messages = SimpleNamespace(parse=self.parse)

    def parse(self, model, **k):
        self.asked.append(model)
        if model in self.down:
            raise anthropic.APIConnectionError(message="down", request=httpx.Request("POST", "https://x"))
        return SimpleNamespace(stop_reason="end_turn", model=model)


def test_backup_takes_over_when_primary_fails(api, monkeypatch):
    monkeypatch.setattr(copilot, "_client", FakeClient(down={"claude-opus-5-5"}))
    resp, model, fell_back = copilot._call_model([])
    assert (model, fell_back) == ("claude-haiku-5-5", "claude-opus-5-5")
    assert api.events()[-1]["event"] == "model_fallback"


def test_simulated_outage_uses_backup(api, monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr(copilot, "_client", fake)
    api.post("/api/control/outage", json={"on": True})
    _, model, _ = copilot._call_model([])
    assert model == "claude-haiku-5-5" and fake.asked == ["claude-haiku-5-5"]


def test_no_backup_means_the_error_surfaces(api, monkeypatch):
    monkeypatch.setattr(copilot, "_client", FakeClient(down={"claude-opus-5-5"}))
    api.post("/api/control/models/claude-haiku-5-5", json={"enabled": False})
    with pytest.raises(anthropic.APIConnectionError):
        copilot._call_model([])


def test_add_model_and_make_it_backup(api):
    r = api.post("/api/control/models", json={"id": "claude-sonnet-5-5", "label": "Claude Sonnet 5.5", "prices": [1, 5, 1.25, 0.1]})
    assert r.status_code == 200
    r = api.post("/api/control/models/claude-sonnet-5-5", json={"role": "backup"})
    assert r.json()["model_chain"] == ["claude-opus-5-5", "claude-sonnet-5-5"]
    assert control.price("claude-sonnet-5-5") == (1, 5, 1.25, 0.1)
    api.post("/api/control/models/claude-sonnet-5-5", json={"role": "primary"})
    assert control.model_chain() == ["claude-sonnet-5-5"]  # the old primary lost its role; haiku lost backup earlier


def test_primary_cannot_be_removed_or_left_empty(api):
    assert api.delete("/api/control/models/claude-opus-5-5").status_code == 400
    assert api.post("/api/control/models/claude-opus-5-5", json={"enabled": False}).status_code == 400
    assert api.post("/api/control/models", json={"id": "Bad Id!", "prices": [1, 1, 1, 1]}).status_code == 400


GOLD = {"type": "grounded", "intent": "fee_explanation", "customer_id": "C001", "language": "en",
        "question": "Why was I charged 25?", "benchmark_answer": "Card replacement fee (POL-03 §2).",
        "benchmark_location": "POL-03 §2", "must_flag": [], "must_suggest": []}


def test_golden_case_add_edit_delete(api):
    n = len(api.get("/api/control/golden").json()["cases"])
    new = api.post("/api/control/golden", json=GOLD).json()
    assert new["id"] == "G25" and len(control.golden()) == n + 1
    api.post("/api/control/golden", json={**GOLD, "id": "G25", "must_suggest": ["log_complaint"]})
    assert next(c for c in control.golden() if c["id"] == "G25")["must_suggest"] == ["log_complaint"]
    assert api.delete("/api/control/golden/G25").status_code == 200
    assert len(control.golden()) == n
    assert api.post("/api/control/golden", json={**GOLD, "customer_id": "C999"}).status_code == 400
    assert api.delete("/api/control/golden/G99").status_code == 404


def write(events):
    copilot.LOG.write_text("\n".join(json.dumps({"ts": "2026-11-06T10:00:00", **e}) for e in events) + "\n", encoding="utf-8")


def test_analytics_counts_deflection_and_minutes(api):
    write([{"event": "auto_outcome", "case_id": "CASE-104", "outcome": "resolved"},
           {"event": "auto_outcome", "case_id": "CASE-105", "outcome": "escalated"},
           {"event": "auto_outcome", "case_id": "CASE-107", "outcome": "awaiting_approval"},
           {"event": "agent_send", "case_id": "CASE-101", "mode": "copilot", "handle_s": 40},
           {"event": "agent_send", "case_id": "CASE-102", "mode": "shadow", "handle_s": 90}])
    a = api.get("/api/control/analytics").json()
    aht = dev.ticket_baseline()["aht_chat_min"]
    assert a["deflected"] == 1 and a["deflection_pct"] == pytest.approx(33.3)
    assert a["minutes_saved"] == pytest.approx(round(aht + 2.0 + 2.0, 1))  # resolved + escalated + one assisted send
    assert a["chats_handled"] == 4 and a["by_day"][0]["day"] == "2026-11-06"
    a = api.post("/api/control/analytics", json={"saved_chat_min": 3, "contacts_per_month": 45000}).json()
    assert a["minutes_saved"] == pytest.approx(round(aht + 6.0, 1))


def test_control_state_lists_everything(api):
    s = api.get("/api/control").json()
    names = {g["key"] for g in s["guardrails"]}
    assert "Numbers match the sources" in names and "prompt_injection" in names
    assert s["model_chain"] == ["claude-opus-5-5", "claude-haiku-5-5"] and s["golden_count"] >= 41


def test_restore_defaults(api):
    api.post("/api/control/outage", json={"on": True})
    api.post("/api/control/reset")
    assert control.state()["simulate_outage"] is False


def b64(data):
    import base64
    return base64.b64encode(data).decode()


def sheet(header, rows):
    from io import BytesIO
    from openpyxl import Workbook
    wb = Workbook()
    wb.active.append(header)
    for r in rows:
        wb.active.append(r)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_golden_download_round_trips_into_a_named_batch(api):
    r = api.get("/api/control/golden/download")
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/vnd.openxmlformats")
    up = api.post("/api/control/golden/upload", json={"filename": "v2.xlsx", "data_b64": b64(r.content),
                                                      "name": "Fee edge cases", "by": "Marwan"}).json()
    assert up["id"] == "fee-edge-cases" and up["count"] == len(control.golden()) and up["by"] == "Marwan" and up["at"]
    assert [x["id"] for x in api.get("/api/control/golden").json()["sets"]] == ["golden_set", "fee-edge-cases"]
    assert api.events()[-1]["what"] == "golden_set_uploaded" and api.events()[-1]["by"] == "Marwan"


def test_upload_new_cases_then_use_that_set(api):
    data = sheet(control.GOLDEN_SHEET, [["", "grounded", "fee_explanation", "C001", "en", "Why 25?", "Replacement fee.",
                                         "POL-03 §2", "TRUE", "", "log_complaint", "new edge case"]])
    up = api.post("/api/control/golden/upload", json={"filename": "b.xlsx", "data_b64": b64(data), "name": "Batch 3", "by": "M"}).json()
    assert api.get(f"/api/control/golden?set={up['id']}").json()["cases"][0] == {
        "id": "G01", "type": "grounded", "intent": "fee_explanation", "customer_id": "C001", "language": "en",
        "question": "Why 25?", "benchmark_answer": "Replacement fee.", "benchmark_location": "POL-03 §2",
        "expect_answer_found": True, "must_flag": [], "must_suggest": ["log_complaint"], "notes": "new edge case"}
    api.post(f"/api/control/golden-sets/{up['id']}/active")
    assert control.active_set() == "batch-3" and len(control.golden()) == 1
    assert api.delete("/api/control/golden-sets/golden_set").status_code == 400
    api.delete("/api/control/golden-sets/batch-3")
    assert control.active_set() == "golden_set"


def test_bad_rows_reject_the_whole_upload(api):
    data = sheet(control.GOLDEN_SHEET, [["", "grounded", "fee_explanation", "C999", "en", "q", "a", "", "", "", "", ""],
                                        ["", "weird", "fee_explanation", "C001", "en", "q", "a", "", "", "", "", ""]])
    r = api.post("/api/control/golden/upload", json={"filename": "b.xlsx", "data_b64": b64(data), "name": "x", "by": "M"})
    assert r.status_code == 400 and "row 2" in r.json()["detail"] and "row 3" in r.json()["detail"]
    assert len(api.get("/api/control/golden").json()["sets"]) == 1
    assert api.post("/api/control/golden/upload", json={"filename": "b.xlsx", "data_b64": b64(b"nope"), "name": "x",
                                                        "by": "M"}).status_code == 400


def test_eval_notes_upload_logged_with_name_and_time(api):
    r = api.get("/api/control/evals/download")
    assert r.status_code == 200
    from io import BytesIO
    from openpyxl import load_workbook
    wb = load_workbook(BytesIO(r.content))
    ws = wb.active
    assert [c.value for c in ws[1]][-1] == "Notes" and ws["A2"].value == "G01"
    ws["I2"] = "Benchmark should mention the 30-day merchant window"
    buf = BytesIO()
    wb.save(buf)
    up = api.post("/api/control/evals/notes", json={"filename": "evals.xlsx", "data_b64": b64(buf.getvalue()), "by": "Marwan"}).json()
    assert up["count"] == 1 and up["by"] == "Marwan" and up["at"]
    notes = api.get("/api/control/evals").json()["notes"]["G01"]
    assert notes[0]["note"].startswith("Benchmark should") and notes[0]["by"] == "Marwan"
    assert api.events()[-1]["event"] == "eval_notes_uploaded"
    assert api.post("/api/control/evals/notes", json={"filename": "e.xlsx", "data_b64": b64(buf.getvalue()), "by": ""}).status_code == 400
