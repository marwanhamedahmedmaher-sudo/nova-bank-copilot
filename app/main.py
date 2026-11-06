"""Agent console API.  Run:  .venv\\Scripts\\python -m uvicorn app.main:app --port 8000"""
import base64
import os
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import copilot, guards, store

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
    copilot.audit("agent_send", case_id=case_id, **edit)
    return {"edited": edit["edited"], "changed_pct": edit["changed_pct"]}


@app.post("/api/cases/{case_id}/flag")
def flag(case_id: str, body: FlagBody):
    if case_id not in store.cases():
        raise HTTPException(404, "unknown case")
    edit = _edit_fields(case_id, body.drafted_reply, body.edited_reply) if body.drafted_reply and body.edited_reply else {}
    copilot.audit("agent_flag", case_id=case_id, note=body.note, **edit)
    return {"ok": True, "changed_pct": edit.get("changed_pct")}


@app.get("/api/policies/{policy_id}")
def policy(policy_id: str):
    p = store.policies().get(policy_id)
    if not p:
        raise HTTPException(404, "unknown policy")
    return p
