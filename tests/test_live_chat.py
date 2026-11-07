"""Live chat: customer screen <-> agent console. The model call is stubbed (conftest), so no API credit is spent."""
import time

import pytest

from app import main
from tests.conftest import fake_result

CASE = main.LIVE_CASE


@pytest.fixture
def chat(api):
    main.CHATS.clear()
    main.CHAT_MODE["mode"] = "copilot"
    yield api
    main.CHATS.clear()
    main.CHAT_MODE["mode"] = "copilot"


def wait_for_draft(api, timeout=5):
    end = time.time() + timeout
    while time.time() < end:
        d = api.get(f"/api/chats/{CASE}").json()["draft"]
        if d and not d.get("pending"):
            return d
        time.sleep(0.02)
    raise AssertionError("draft never finished")


def test_customer_message_reaches_agent_with_a_fresh_draft(chat):
    chat.canned[CASE] = fake_result(CASE)
    chat.post("/api/customer/chat", json={"text": "Where is my Noon refund?"})
    draft = wait_for_draft(chat)
    assert draft["result"]["reply"] == "Hello Mariam" and not draft["sent"]
    detail = chat.get(f"/api/chats/{CASE}").json()
    assert [m["role"] for m in detail["messages"]] == ["customer"]  # copilot mode: nothing goes out by itself


def test_agent_reply_shows_on_customer_screen_without_internals(chat):
    chat.canned[CASE] = fake_result(CASE)
    chat.post("/api/customer/chat", json={"text": "hi"})
    wait_for_draft(chat)
    chat.post(f"/api/chats/{CASE}/reply", json={"text": "Hello Nourhan, edited", "drafted_reply": "Hello Mariam"})
    seen = chat.get("/api/customer/chat").json()
    assert [m["role"] for m in seen["messages"]] == ["customer", "agent"]
    assert set(seen["messages"][1]) == {"id", "role", "text", "ts"}  # no draft, risk or citations leak to the customer
    assert chat.get(f"/api/chats/{CASE}").json()["draft"] is None
    assert any(e["event"] == "chat_reply" and e["edited"] for e in chat.events())


def test_auto_mode_sends_low_risk_reply_by_itself(chat):
    main.CHAT_MODE["mode"] = "auto"
    chat.canned[CASE] = fake_result(CASE)
    chat.post("/api/customer/chat", json={"text": "What is my fee?"})
    assert wait_for_draft(chat)["sent"]
    assert [m["role"] for m in chat.get("/api/customer/chat").json()["messages"]] == ["customer", "copilot"]


def test_auto_mode_waits_for_approval_on_high_risk(chat):
    main.CHAT_MODE["mode"] = "auto"
    chat.canned[CASE] = fake_result(CASE, actions=["request_fee_waiver"])
    chat.post("/api/customer/chat", json={"text": "Waive my fee"})
    draft = wait_for_draft(chat)
    assert draft["result"]["risk"]["level"] == "high" and not draft["sent"]
    r = chat.post(f"/api/chats/{CASE}/approve", json={"text": "Hello Mariam"})
    assert r.status_code == 200 and r.json()["actions"][0]["approver"] == "team_leader"
    assert chat.post(f"/api/chats/{CASE}/approve", json={"text": "again"}).status_code == 409  # approve once


def test_takeover_stops_auto_replies(chat):
    main.CHAT_MODE["mode"] = "auto"
    chat.post(f"/api/chats/{CASE}/takeover", json={"on": True})
    chat.canned[CASE] = fake_result(CASE)
    chat.post("/api/customer/chat", json={"text": "hello"})
    assert not wait_for_draft(chat)["sent"]
    assert [m["role"] for m in chat.get("/api/customer/chat").json()["messages"]] == ["customer"]


def test_only_live_cases_are_chats(chat):
    assert chat.get("/api/chats/CASE-101").status_code == 404
    assert [c["case_id"] for c in chat.get("/api/chats").json()] == [CASE]


def test_context_includes_earlier_turns(chat):
    c = main._chat(CASE)
    main._add_message(c, "customer", "first question")
    main._add_message(c, "agent", "first answer")
    m = main._add_message(c, "customer", "follow up")
    text = main._context_message(c, m["id"])
    assert "Customer: first question" in text and "Nova Bank: first answer" in text and text.endswith("follow up")


# ---- ending a chat: Closed tab, customer rating, fresh chat ---------------------------------------
def closed_chats(api, mode):
    return [r for r in api.get(f"/api/closed?mode={mode}").json() if r.get("chat_no")]


def test_end_chat_moves_it_to_closed_and_starts_fresh(chat):
    chat.canned[CASE] = fake_result(CASE)
    chat.post("/api/customer/chat", json={"text": "Where is my Noon refund?"})
    wait_for_draft(chat)
    chat.post(f"/api/chats/{CASE}/reply", json={"text": "Hello Nourhan, it is with the merchant."})
    no = chat.get("/api/customer/chat").json()["chat_no"]
    assert chat.post(f"/api/chats/{CASE}/end").json() == {"ended": no}
    rows = closed_chats(chat, "copilot")
    assert len(rows) == 1 and rows[0]["chat_no"] == no and rows[0]["by"] == "agent" and rows[0]["ended_by"] == "agent"
    assert [m["role"] for m in rows[0]["transcript"]] == ["customer", "agent"]
    assert "Nourhan" not in rows[0]["transcript"][1]["text"]  # masked in the log
    seen = chat.get("/api/customer/chat").json()
    assert seen["messages"] == [] and seen["chat_no"] != no and seen["rate_for"] == no
    assert closed_chats(chat, "auto") == []  # closed in the mode it ended in


def test_customer_ends_and_rates_once(chat):
    chat.post("/api/customer/chat", json={"text": "hi"})
    chat.canned[CASE] = fake_result(CASE)
    no = chat.post("/api/customer/end").json()["ended"]
    assert closed_chats(chat, "copilot")[0]["ended_by"] == "customer"
    assert chat.post("/api/customer/rate", json={"chat_no": no, "stars": 6}).status_code == 422
    assert chat.post("/api/customer/rate", json={"chat_no": no, "stars": 4}).status_code == 200
    assert closed_chats(chat, "copilot")[0]["rating"] == 4
    assert chat.post("/api/customer/rate", json={"chat_no": no, "stars": 1}).status_code == 409
    assert chat.get("/api/customer/chat").json()["rate_for"] is None


def test_empty_chat_cannot_end(chat):
    assert chat.post(f"/api/chats/{CASE}/end").status_code == 409


def test_auto_chat_answered_by_copilot_is_closed_by_copilot(chat):
    main.CHAT_MODE["mode"] = "auto"
    chat.canned[CASE] = fake_result(CASE)
    chat.post("/api/customer/chat", json={"text": "Where is my Noon refund?"})
    wait_for_draft(chat)
    chat.post("/api/customer/end")
    assert closed_chats(chat, "auto")[0]["by"] == "copilot"
