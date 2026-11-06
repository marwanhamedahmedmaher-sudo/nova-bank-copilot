import json

import pytest
from fastapi.testclient import TestClient

from app import copilot, guards, main


def fake_result(case_id, actions=(), input_flags=(), risk_flags=(), status="ready"):
    draft = {"risk_flags": list(risk_flags), "intent": "other", "customer_language": "en", "facts": [],
             "agent_summary": "s", "suggested_reply": "Hello {{FIRST_NAME}}", "reply_in_english": "Hello",
             "suggested_actions": [{"action": a, "reason": "r", "amount_egp": None, "approver": guards.approver_for(a)}
                                   for a in actions]}
    return copilot.with_risk({"case_id": case_id, "status": status, "input_flags": list(input_flags), "draft": draft,
                              "reply": "Hello Mariam", "reply_in_english": "Hello", "checks": []})


@pytest.fixture
def api(tmp_path, monkeypatch):
    """TestClient with the audit log in a temp file and the model call stubbed (no API credit spent)."""
    monkeypatch.setattr(copilot, "LOG", tmp_path / "audit.jsonl")
    canned = {}
    monkeypatch.setattr(copilot, "suggest", lambda case_id, message=None, **k: canned[case_id])
    main.AUTO.clear()
    client = TestClient(main.app)
    client.canned = canned
    client.events = lambda: ([json.loads(l) for l in copilot.LOG.read_text(encoding="utf-8").splitlines()]
                             if copilot.LOG.exists() else [])
    return client
