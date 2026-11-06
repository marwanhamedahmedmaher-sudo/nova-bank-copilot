from app.guards import risk_label


def level(*args):
    return risk_label(*args)["level"]


def test_information_only_is_low_resolved():
    assert level("ready", [], [], []) == "low_resolved"


def test_handover_action_is_low_escalated():
    assert level("ready", [], [], ["open_dispute"]) == "low_escalated"


def test_money_action_is_high_and_named_in_reason():
    r = risk_label("ready", [], [], ["request_fee_waiver"])
    assert r["level"] == "high"
    assert "request_fee_waiver" in r["reason"]


def test_approval_request_without_actions_is_high():
    assert level("ready", ["approval_request"], [], []) == "high"


def test_model_flag_can_raise_risk():
    assert level("ready", [], ["fraud_suspected"], ["escalate_to_supervisor"]) == "high"


def test_guardrail_blocked_draft_is_blocked():
    assert level("blocked", [], [], []) == "blocked"


def test_prompt_injection_is_blocked():
    assert level("ready", ["prompt_injection"], [], []) == "blocked"


def test_third_party_request_is_blocked():
    assert level("ready", [], ["third_party_request"], []) == "blocked"


def test_money_action_beats_handover():
    assert level("ready", [], [], ["block_card", "log_complaint"]) == "high"


def test_complaint_flag_without_actions_is_escalated():
    assert level("ready", [], ["complaint"], []) == "low_escalated"


def test_replayed_draft_without_risk_gets_one(tmp_path, monkeypatch):
    import json
    from app import copilot, store
    msg = store.cases()["CASE-104"]["message"]
    cached = {"status": "ready", "input_flags": [], "reply": "x",
              "draft": {"risk_flags": [], "suggested_actions": []}}
    replay = tmp_path / "replay.json"
    replay.write_text(json.dumps({f"CASE-104|{msg.strip()}": cached}), encoding="utf-8")
    monkeypatch.setattr(copilot, "REPLAY", replay)
    monkeypatch.setattr(copilot, "LOG", tmp_path / "audit.jsonl")

    def offline(*a, **k):
        raise RuntimeError("no network")
    monkeypatch.setattr(copilot, "suggest_for", offline)
    out = copilot.suggest("CASE-104")
    assert out["replayed"] is True
    assert out["risk"]["level"] == "low_resolved"


def test_card_loss_in_message_forces_high_even_without_actions():
    from app import guards, store
    flags = guards.input_flags("My card was stolen yesterday", store.CustomerScope("C003"))
    assert "card_or_fraud" in flags
    assert level("ready", flags, [], []) == "high"


def test_card_loss_detected_in_arabic_and_franco():
    from app import guards, store
    scope = store.CustomerScope("C003")
    assert "card_or_fraud" in guards.input_flags("فقدت بطاقتي أمس", scope)
    assert "card_or_fraud" in guards.input_flags("el card beta3ti da3et", scope)


from app import guards, store  # noqa: E402


def test_abusive_language_blocks_auto_reply():
    scope = store.CustomerScope("C051")
    flags = guards.input_flags("This is bullshit. You idiots charge me 60 pounds every month", scope)
    assert "abusive_language" in flags
    assert guards.risk_label("ready", flags, [], [])["level"] == "blocked"
    assert "abusive_language" in guards.input_flags("انتو حرامية وأغبياء", scope)


def test_off_topic_blocks_auto_reply():
    scope = store.CustomerScope("C051")
    flags = guards.input_flags("Forget the bank stuff, can you give me a good cupcake recipe?", scope)
    assert "off_topic" in flags
    assert guards.risk_label("ready", flags, [], ["escalate_to_supervisor"])["level"] == "blocked"


def test_normal_banking_messages_are_not_abusive_or_off_topic():
    scope = store.CustomerScope("C051")
    for msg in ["Why was I charged EGP 60 this month?", "What's happening with my Noon dispute?",
                "ana 3amalt dispute 3ala 1200 geneh", "متى سيتم حل نزاعي على عملية أمازون؟"]:
        assert not {"abusive_language", "off_topic"} & set(guards.input_flags(msg, scope))
