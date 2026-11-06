"""Agent console API.  Run:  .venv\\Scripts\\python -m uvicorn app.main:app --port 8000"""
import base64
import os
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["shadow", "copilot", "auto"]

from . import copilot, dev, guards, store

app = FastAPI(title="Nova Bank Copilot")
STATIC = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD")  # set on the hosted copy so strangers can't spend the API credit


@app.middleware("http")
async def password_gate(request: Request, call_next):
    if DEMO_PASSWORD and request.url.path != "/healthz":
        ok = False
        header = request.headers.get("authorization", "")
        if header.startswith("Basic "):
            try:
                password = base64.b64decode(header[6:]).decode().partition(":")[2]
                ok = secrets.compare_digest(password, DEMO_PASSWORD)
            except ValueError:
                ok = False
        if not ok:
            return Response("Password required", status_code=401,
                            headers={"WWW-Authenticate": 'Basic realm="Nova copilot demo"'})
    return await call_next(request)


@app.get("/healthz")
def healthz():
    return {"ok": True}


class SuggestBody(BaseModel):
    message: str | None = None


class ActionBody(BaseModel):
    action: str
    reason: str = ""
    amount_egp: float | None = None


class FlagBody(BaseModel):
    note: str
    drafted_reply: str | None = None
    edited_reply: str | None = None


class SendBody(BaseModel):
    drafted_reply: str
    final_reply: str
    mode: Mode = "copilot"
    sources_opened: int = 0       # citation chips the agent opened before sending (Telos rec 14)
    handle_s: float | None = None  # seconds from opening the case to sending


class ApproveBody(BaseModel):
    final_reply: str
    handle_s: float | None = None
    sources_opened: int = 0


class SourceBody(BaseModel):
    source: str


class ReviewBody(BaseModel):
    vote: Literal["up", "down"]
    note: str = Field("", max_length=500)


AUTO = {}  # case_id -> the assessed draft, so a high-risk case can be approved later
OUTCOME = {"low_resolved": "resolved", "low_escalated": "escalated", "high": "awaiting_approval", "blocked": "needs_agent"}


def _masked(case_id, text):
    """The audit log holds masked text only (POL-20 §4-5): first name back to its placeholder, identifiers masked."""
    first = store.CustomerScope(store.cases()[case_id]["customer_id"]).first_name
    return guards.mask_pii(text.replace(first, "{{FIRST_NAME}}"))


def _edit_fields(case_id, drafted, final):
    """What the agent changed, logged for the edit-rate eval (evals/edit_report.py)."""
    changed = round(guards.changed_share(drafted, final) * 100, 1)
    return {"edited": changed > 0, "changed_pct": changed,
            "drafted_reply": _masked(case_id, drafted), "final_reply": _masked(case_id, final)}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-store"})  # browsers always load the latest console


@app.get("/api/today")
def today():
    return {"today": copilot.today()}


@app.get("/api/cases")
def list_cases():
    out = []
    for c in store.cases().values():
        cust = store.customers()[c["customer_id"]]
        out.append({**c, "customer_name": cust["name"], "plan": cust["plan"]})
    return out


@app.get("/api/cases/{case_id}")
def case_detail(case_id: str):
    case = store.cases().get(case_id)
    if not case:
        raise HTTPException(404, "unknown case")
    scope = store.CustomerScope(case["customer_id"])
    c = scope.customer
    return {
        "case": case,
        # the agent is entitled to see the verified customer; phone and national ID stay masked even here (POL-17 §3)
        "customer": {k: c[k] for k in ("customer_id", "name", "plan", "tenure_months", "city", "card_last4", "card_status",
                                       "card_expiry", "avg_balance_last_month", "salary_transfer", "overdraft_opt_in",
                                       "planned_overdraft_limit")} | {"mobile": "•••••••" + c["mobile"][-3:]},
        "transactions": sorted(scope.transactions, key=lambda t: t["date"], reverse=True),
        "disputes": scope.disputes,
    }


@app.post("/api/cases/{case_id}/suggest")
def suggest(case_id: str, body: SuggestBody):
    if case_id not in store.cases():
        raise HTTPException(404, "unknown case")
    try:
        return copilot.suggest(case_id, body.message)
    except Exception as e:  # surface to the agent instead of a blank panel
        raise HTTPException(502, f"copilot unavailable: {e}")


@app.post("/api/cases/{case_id}/action")
def take_action(case_id: str, body: ActionBody):
    if body.action not in guards.ACTION_RULES:
        raise HTTPException(400, "unknown action")
    _, status, note = guards.ACTION_RULES[body.action]
    approver = guards.approver_for(body.action, body.amount_egp)
    if body.action == "request_fee_waiver":
        note = f"Waiver request sent to the {guards.APPROVER_NAMES[approver]} (POL-11 §2)."
    copilot.audit("agent_action", case_id=case_id, action=body.action, approver=approver, status=status,
                  reason=body.reason, amount_egp=body.amount_egp)
    return {"action": body.action, "approver": approver, "status": status, "note": note}


@app.post("/api/cases/{case_id}/send")
def send(case_id: str, body: SendBody):
    if case_id not in store.cases():
        raise HTTPException(404, "unknown case")
    edit = _edit_fields(case_id, body.drafted_reply, body.final_reply)
    copilot.audit("agent_send", case_id=case_id, mode=body.mode, sources_opened=body.sources_opened,
                  handle_s=body.handle_s, **edit)
    return {"edited": edit["edited"], "changed_pct": edit["changed_pct"]}


@app.post("/api/cases/{case_id}/source_opened")
def source_opened(case_id: str, body: SourceBody):
    if case_id not in store.cases():
        raise HTTPException(404, "unknown case")
    copilot.audit("source_opened", case_id=case_id, source=body.source)
    return {"ok": True}


def _submit(case_id, actions, event):
    """Hand each action to its approver from the policy table; nothing here decides an outcome."""
    out = []
    for a in actions:
        approver = guards.approver_for(a["action"], a.get("amount_egp"))
        status = guards.ACTION_RULES[a["action"]][1]
        copilot.audit(event, case_id=case_id, action=a["action"], approver=approver, status=status,
                      reason=a.get("reason", ""), amount_egp=a.get("amount_egp"))
        out.append({"action": a["action"], "approver": approver, "status": status})
    return out


@app.post("/api/cases/{case_id}/auto")
def auto_reply(case_id: str):
    """Auto-reply mode: low risk is answered or handed over by the copilot; high risk waits for a human; blocked goes to an agent."""
    if case_id not in store.cases():
        raise HTTPException(404, "unknown case")
    try:
        result = copilot.with_risk(copilot.suggest(case_id))
    except Exception as e:
        raise HTTPException(502, f"copilot unavailable: {e}")
    AUTO[case_id] = result
    level = result["risk"]["level"]
    outcome, actions = OUTCOME[level], []
    if level in ("low_resolved", "low_escalated"):
        copilot.audit("auto_send", case_id=case_id, reply=_masked(case_id, result["reply"]), risk=level)
        if level == "low_escalated":
            handover = [a for a in result["draft"]["suggested_actions"] if a["action"] in guards.HANDOVER_ACTIONS]
            if not handover:  # escalated on the complaint flag alone: log it, so the label is true
                handover = [{"action": "log_complaint", "reason": "complaint flagged in the customer's message"}]
            actions = _submit(case_id, handover, "auto_action")
    copilot.audit("auto_outcome", case_id=case_id, outcome=outcome, risk=level, reason=result["risk"]["reason"])
    return {"case_id": case_id, "risk": result["risk"], "outcome": outcome, "actions": actions, "result": result}


@app.post("/api/cases/{case_id}/approve")
def approve(case_id: str, body: ApproveBody):
    """A human approves a high-risk auto-reply case: the reply is sent and each action goes to its policy approver."""
    result = AUTO.get(case_id)
    if result is None or result["risk"]["level"] != "high":
        raise HTTPException(409, "only a high-risk case assessed in auto-reply can be approved")
    AUTO.pop(case_id)  # approve once: a double-click must not submit the actions twice
    edit = _edit_fields(case_id, result["reply"], body.final_reply)
    copilot.audit("agent_send", case_id=case_id, mode="auto", approved=True, sources_opened=body.sources_opened,
                  handle_s=body.handle_s, **edit)
    actions = _submit(case_id, result["draft"]["suggested_actions"], "agent_action")
    return {"sent": True, "actions": actions, "changed_pct": edit["changed_pct"]}


@app.post("/api/cases/{case_id}/flag")
def flag(case_id: str, body: FlagBody):
    if case_id not in store.cases():
        raise HTTPException(404, "unknown case")
    edit = _edit_fields(case_id, body.drafted_reply, body.edited_reply) if body.drafted_reply and body.edited_reply else {}
    copilot.audit("agent_flag", case_id=case_id, note=body.note, **edit)
    return {"ok": True, "changed_pct": edit.get("changed_pct")}


@app.get("/api/closed")
def closed_cases(mode: Mode = "copilot"):
    """Closed tab for one mode, newest first. Replies in the log are masked; the console puts the first name back."""
    rows = dev.closed().get(mode, {})
    out = [{"case_id": cid, **info} for cid, info in rows.items() if cid in store.cases()]
    return sorted(out, key=lambda r: r["at"], reverse=True)


@app.post("/api/cases/{case_id}/review")
def review(case_id: str, body: ReviewBody):
    """Thumbs up/down on a case the copilot closed by itself in auto-reply; logged for the evals."""
    row = dev.closed()["auto"].get(case_id)
    if not row or row["by"] != "copilot":
        raise HTTPException(409, "only a case the copilot closed in auto-reply can be reviewed")
    if body.vote == "down" and not body.note.strip():
        raise HTTPException(422, "a thumbs down needs a note for the weekly review")
    copilot.audit("auto_review", case_id=case_id, vote=body.vote, note=_masked(case_id, body.note))  # free text: masked like every other field
    return {"ok": True}


@app.post("/api/demo/reset")
def demo_reset():
    """Reopen every case for the next demo run. Logged, not deleted: the audit log stays append-only."""
    AUTO.clear()
    with CHAT_LOCK:
        CHATS.clear()
    copilot.audit("demo_reset")
    return {"ok": True}


# ---- live chat ------------------------------------------------------------------------------------
# The customer screen (/customer, played by a teammate on another laptop) is bound server-side to one
# verified case, so it can never reach another customer (POL-17 §5). Each new customer message gets a
# fresh copilot draft in the background; in auto-reply the copilot sends low-risk replies by itself
# unless the agent has taken over. Chats live in memory: a server restart starts them again.
LIVE_CASE = "CASE-110"
CHAT_LOCK = threading.Lock()
CHATS = {}                    # case_id -> {"messages", "takeover", "draft", "seq"}
CHAT_MODE = {"mode": "copilot"}  # set by the agent console's mode switch
MAX_CONTEXT_TURNS = 8


class ChatText(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class ChatReplyBody(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    drafted_reply: str = ""
    sources_opened: int = 0
    handle_s: float | None = None


class ChatModeBody(BaseModel):
    mode: Mode


class TakeoverBody(BaseModel):
    on: bool


def _chat(case_id):
    case = store.cases().get(case_id)
    if not case or not case.get("live"):
        raise HTTPException(404, "not a live chat")
    return CHATS.setdefault(case_id, {"messages": [], "takeover": False, "draft": None, "seq": 0})


def _add_message(chat, role, text, **extra):
    chat["seq"] += 1
    msg = {"id": chat["seq"], "role": role, "text": text, "ts": datetime.now(timezone.utc).isoformat(), **extra}
    chat["messages"].append(msg)
    return msg


def _context_message(chat, upto_id):
    """The latest customer message, with the turns before it as context. The whole thing is untrusted customer text."""
    msgs = [m for m in chat["messages"] if m["id"] <= upto_id][-MAX_CONTEXT_TURNS:]
    latest, earlier = msgs[-1]["text"], msgs[:-1]
    if not earlier:
        return latest
    who = {"customer": "Customer", "agent": "Nova Bank", "copilot": "Nova Bank"}
    history = "\n".join(f"{who[m['role']]}: {m['text']}" for m in earlier)
    return f"Earlier in this chat, for context only:\n{history}\n\nThe customer's new message, to answer in its own language:\n{latest}"


def _draft_for(case_id, msg_id):
    """Background worker: draft a reply to customer message msg_id; in auto-reply, send it if the risk rule allows."""
    with CHAT_LOCK:
        chat = CHATS.get(case_id)
        if not chat:
            return
        message = _context_message(chat, msg_id)
    try:
        result, error = copilot.with_risk(copilot.suggest(case_id, message)), None
    except Exception as e:
        result, error = None, str(e)
    with CHAT_LOCK:
        chat = CHATS.get(case_id)
        if not chat or not chat["draft"] or chat["draft"]["for"] != msg_id:
            return  # a newer customer message (or a demo reset) superseded this draft
        draft = {"for": msg_id, "pending": False, "result": result, "error": error, "sent": False, "actions": []}
        chat["draft"] = draft
        level = result and result["risk"]["level"]
        if CHAT_MODE["mode"] == "auto" and not chat["takeover"] and level in ("low_resolved", "low_escalated"):
            _add_message(chat, "copilot", result["reply"], risk=level)
            draft["sent"] = True
            copilot.audit("chat_auto_send", case_id=case_id, reply=_masked(case_id, result["reply"]), risk=level)
            if level == "low_escalated":
                handover = [a for a in result["draft"]["suggested_actions"] if a["action"] in guards.HANDOVER_ACTIONS]
                draft["actions"] = _submit(case_id, handover or [{"action": "log_complaint", "reason": "complaint flagged in the chat"}],
                                           "auto_action")


@app.get("/customer")
def customer_page():
    return FileResponse(STATIC / "customer.html", headers={"Cache-Control": "no-store"})


@app.get("/api/customer/chat")
def customer_chat(after: int = 0):
    """What the customer sees: the conversation only. No drafts, citations, risk labels or internal notes."""
    case = store.cases()[LIVE_CASE]
    with CHAT_LOCK:
        chat = _chat(LIVE_CASE)
        typing = bool(chat["draft"] and chat["draft"]["pending"] and CHAT_MODE["mode"] == "auto" and not chat["takeover"])
        msgs = [{k: m[k] for k in ("id", "role", "text", "ts")} for m in chat["messages"] if m["id"] > after]
    return {"customer_name": store.customers()[case["customer_id"]]["name"], "messages": msgs, "typing": typing}


@app.post("/api/customer/chat")
def customer_says(body: ChatText):
    with CHAT_LOCK:
        chat = _chat(LIVE_CASE)
        msg = _add_message(chat, "customer", body.text.strip())
        chat["draft"] = {"for": msg["id"], "pending": True}
    copilot.audit("chat_customer_message", case_id=LIVE_CASE, message=_masked(LIVE_CASE, msg["text"]))
    threading.Thread(target=_draft_for, args=(LIVE_CASE, msg["id"]), daemon=True).start()
    return {"id": msg["id"]}


@app.get("/api/chats")
def chats_summary():
    """One line per live chat for the console's Open chats list (polled)."""
    out = []
    with CHAT_LOCK:
        for cid, case in store.cases().items():
            if case.get("live"):
                chat = _chat(cid)
                last = chat["messages"][-1] if chat["messages"] else None
                out.append({"case_id": cid, "seq": chat["seq"], "last": last, "takeover": chat["takeover"],
                            "drafting": bool(chat["draft"] and chat["draft"]["pending"])})
    return out


@app.get("/api/chats/{case_id}")
def chat_detail(case_id: str):
    with CHAT_LOCK:
        chat = _chat(case_id)
        return {"case_id": case_id, "seq": chat["seq"], "messages": list(chat["messages"]), "takeover": chat["takeover"],
                "draft": chat["draft"], "mode": CHAT_MODE["mode"]}


@app.post("/api/chats/mode")
def chat_mode(body: ChatModeBody):
    CHAT_MODE["mode"] = body.mode
    return {"mode": body.mode}


@app.post("/api/chats/{case_id}/takeover")
def chat_takeover(case_id: str, body: TakeoverBody):
    with CHAT_LOCK:
        chat = _chat(case_id)
        chat["takeover"] = body.on
    copilot.audit("chat_takeover", case_id=case_id, on=body.on)
    return {"takeover": body.on}


@app.post("/api/chats/{case_id}/reply")
def chat_reply(case_id: str, body: ChatReplyBody):
    """The agent sends a message: their own words, or the copilot's draft as edited. Logged with the edit share."""
    with CHAT_LOCK:
        chat = _chat(case_id)
        _add_message(chat, "agent", body.text.strip())
        if chat["draft"] and not chat["draft"].get("pending"):
            chat["draft"] = None  # answered: the next customer message gets a fresh draft
    edit = _edit_fields(case_id, body.drafted_reply, body.text) if body.drafted_reply else {"final_reply": _masked(case_id, body.text)}
    copilot.audit("chat_reply", case_id=case_id, mode=CHAT_MODE["mode"], sources_opened=body.sources_opened,
                  handle_s=body.handle_s, **edit)
    return {"edited": edit.get("edited", True), "changed_pct": edit.get("changed_pct")}


@app.post("/api/chats/{case_id}/approve")
def chat_approve(case_id: str, body: ChatReplyBody):
    """Auto-reply, high risk: the agent approves the copilot's draft; the reply goes out and each action goes to its approver."""
    with CHAT_LOCK:
        chat = _chat(case_id)
        draft = chat["draft"]
        if not draft or draft.get("pending") or not draft.get("result") or draft["result"]["risk"]["level"] != "high":
            raise HTTPException(409, "nothing waiting for approval")
        chat["draft"] = None  # approve once
        _add_message(chat, "agent", body.text.strip(), approved=True)
    result = draft["result"]
    edit = _edit_fields(case_id, result["reply"], body.text)
    copilot.audit("chat_reply", case_id=case_id, mode="auto", approved=True, sources_opened=body.sources_opened,
                  handle_s=body.handle_s, **edit)
    actions = _submit(case_id, result["draft"]["suggested_actions"], "agent_action")
    return {"sent": True, "actions": actions, "changed_pct": edit["changed_pct"]}


@app.get("/api/dev/summary")
def dev_summary():
    return dev.summary()


@app.get("/api/policies/{policy_id}")
def policy(policy_id: str):
    p = store.policies().get(policy_id)
    if not p:
        raise HTTPException(404, "unknown policy")
    return p
