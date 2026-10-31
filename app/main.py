"""Agent console API.  Run:  .venv\\Scripts\\python -m uvicorn app.main:app --port 8000"""
import base64
import os
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import copilot, store

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

# Who must approve each action before it happens (POL-04 §5, POL-11 §2, POL-07 §1, POL-20 §3)
ACTION_RULES = {
    "block_card": ("agent", "done", "Card blocked by agent."),
    "order_replacement_card": ("agent", "done", "Replacement ordered by agent; fee per POL-03 §2."),
    "open_dispute": ("disputes_team", "submitted", "Dispute submitted; only the Disputes team decides."),
    "request_fee_waiver": ("team_leader", "pending_approval", "Waiver request sent to Team Leader."),
    "log_complaint": ("agent", "logged", "Complaint logged with a C- reference."),
    "escalate_to_supervisor": ("team_leader", "pending_approval", "Escalated to supervisor."),
}


class SuggestBody(BaseModel):
    message: str | None = None


class ActionBody(BaseModel):
    action: str
    reason: str = ""


class FlagBody(BaseModel):
    note: str


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


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
    if body.action not in ACTION_RULES:
        raise HTTPException(400, "unknown action")
    approver, status, note = ACTION_RULES[body.action]
    copilot.audit("agent_action", case_id=case_id, action=body.action, approver=approver, status=status, reason=body.reason)
    return {"action": body.action, "approver": approver, "status": status, "note": note}


@app.post("/api/cases/{case_id}/flag")
def flag(case_id: str, body: FlagBody):
    copilot.audit("agent_flag", case_id=case_id, note=body.note)
    return {"ok": True}


@app.get("/api/policies/{policy_id}")
def policy(policy_id: str):
    p = store.policies().get(policy_id)
    if not p:
        raise HTTPException(404, "unknown policy")
    return p
