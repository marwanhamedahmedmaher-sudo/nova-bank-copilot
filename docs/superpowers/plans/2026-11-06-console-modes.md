# Console modes, risk labels, dev mode, recs 14 and 16 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Shadow / Copilot / Auto-reply switcher with code-decided risk labels, a dev mode, deadlines computed in code, and source-open logging to the Nova agent console.

**Architecture:** Pure rules live in `app/guards.py` (`risk_label`) and `app/store.py` (`deadline_status`). `app/main.py` gains endpoints for auto-reply assessment, approve-and-send, source opens and a dev summary; all automatic steps write to the existing audit log. The single-page console (`app/static/index.html`) gains the header switcher, dev toggle, risk badges and mode-specific draft views.

**Tech Stack:** Python 3.12, FastAPI, pydantic, vanilla JS. Tests: pytest and FastAPI TestClient (new dev dependency), with the copilot call stubbed.

**Spec:** `docs/superpowers/specs/2026-11-06-console-modes-design.md`

## Global Constraints

- Risk labels are decided by code; the model can only raise risk through its `risk_flags`, never lower it.
- Labels: `blocked`, `high`, `low_escalated`, `low_resolved`, each with a one-line `reason`.
- Money-moving actions: `request_fee_waiver`, `block_card`, `order_replacement_card`, `refer_to_credit_team`. Hand-over actions: `open_dispute`, `escalate_to_supervisor`, `log_complaint`.
- Nothing in auto-reply moves money, waives a fee or touches a card without a human click.
- Audit log holds masked text only (POL-20 §4-5). New events: `auto_send`, `auto_action`, `source_opened`; `agent_send` gains `mode`, `sources_opened`, `handle_s`.
- Dev information (metrics row, "Try to break it", full guardrail list, risk rule, dev panel) is visible only in dev mode.
- Tests must not call the Anthropic API.

## Review Focus

1. Auto-reply on a case whose draft is `blocked` by guardrails, which must land as `blocked`, never auto-sent: test in Task 2.
2. A draft with no actions but an `approval_request` input flag (CASE-106 style), which must be `high`, not `low_resolved`: test in Task 2.
3. Expected date equal to today, which must read "due today", not overdue: test in Task 1.
4. Dev summary on an empty or missing audit log, which must return zeros, not crash: test in Task 4.
5. Approve-and-send called on a case that was never assessed (no stored draft), which returns 409: test in Task 3.

---

### Task 1: Deadlines in code (rec 16)

**Files:**
- Modify: `app/store.py` (`CustomerScope.__init__`, `record_lines`), `app/copilot.py` (`suggest_for` scope construction, `SYSTEM_RULES` deadline bullet), `app/static/index.html` (header date)
- Create: `tests/test_deadline.py`, `requirements-dev.txt` (`pytest`, `httpx`)

**Interfaces:**
- Produces: `store.deadline_status(expected: str, today: str) -> str` returning `"due today"`, `"overdue by N days"` / `"overdue by 1 day"`, or `"due in N days"` / `"due in 1 day"`. `CustomerScope(customer_id, today: str | None = None)`; when `today` is set, each dispute line ends with ` | deadline status: <status> (as of <today>)`.

- [ ] **Step 1: Write failing tests**: `deadline_status("2026-11-06","2026-11-06") == "due today"`; `("2026-11-06","2026-11-07") == "overdue by 1 day"`; `("2026-11-06","2026-11-10") == "overdue by 4 days"`; `("2026-11-06","2026-11-04") == "due in 2 days"`; `"deadline status: overdue by 1 day (as of 2026-11-07)" in CustomerScope("C001", today="2026-11-07").record_lines()["D-1001"]`; and without `today` the line has no "deadline status".
- [ ] **Step 2:** `pip install -r requirements-dev.txt`, then run `.venv\Scripts\python -m pytest tests/test_deadline.py -v`: expected FAIL (no `deadline_status`).
- [ ] **Step 3:** Implement it. In `suggest_for`, build `store.CustomerScope(customer_id, today=today())`. Replace the deadline bullet in `SYSTEM_RULES` with: each dispute line carries a "deadline status" the bank computed; use it as written and cite the dispute; suggest escalate_to_supervisor only when it says overdue; when it says "due today", say so and do not escalate. Header pill: `Today: <date>` from a new `GET /api/today` returning `{"today": copilot.today()}`.
- [ ] **Step 4:** Tests pass.
- [ ] **Step 5:** Commit `feat: compute dispute deadline status in code (Telos rec 16)`.

### Task 2: Risk labels from code rules

**Files:**
- Modify: `app/guards.py`; `app/copilot.py` (`suggest_for` result gains `"risk"`)
- Create: `tests/test_risk.py`

**Interfaces:**
- Produces: `guards.risk_label(status: str, input_flags: list[str], risk_flags: list[str], actions: list[str]) -> dict` returning `{"level": "blocked"|"high"|"low_escalated"|"low_resolved", "reason": str}`; `guards.MONEY_ACTIONS`, `guards.HANDOVER_ACTIONS` (sets). Result dicts from `copilot.suggest_for` gain `"risk"` (the dict above). Order of rules: blocked status or `prompt_injection` / `third_party_request` flags → blocked; any money action, `approval_request` or `fraud_suspected` in either flag list → high; any hand-over action (or `complaint` flag with no action) → low_escalated; else low_resolved.

- [ ] **Step 1: Write failing tests**: `risk_label("ready",[],[],[])["level"] == "low_resolved"`; `("ready",[],[],["open_dispute"])` → `low_escalated`; `("ready",[],[],["request_fee_waiver"])` → `high` and `"request_fee_waiver" in reason`; `("ready",["approval_request"],[],[])` → `high`; `("ready",[],["fraud_suspected"],["escalate_to_supervisor"])` → `high`; `("blocked",[],[],[])` → `blocked`; `("ready",["prompt_injection"],[],[])` → `blocked`; `("ready",[],[],["block_card","log_complaint"])` → `high`.
- [ ] **Step 2:** Run, expect FAIL.
- [ ] **Step 3:** Implement and attach `risk` in `suggest_for` from `status`, `flags`, `draft.risk_flags`, the action names. Replayed drafts already carry `risk` once regenerated. For old cache entries without it, `copilot.suggest` fills it in with the same function.
- [ ] **Step 4:** Tests pass.
- [ ] **Step 5:** Commit `feat: risk labels decided by code`.

### Task 3: Auto-reply, approve-and-send, shadow and source-open endpoints (rec 14 backend)

**Files:**
- Modify: `app/main.py`
- Create: `tests/test_api_modes.py` (stubs `copilot.suggest` with a canned result per case and points `copilot.LOG` to a tmp file)

**Interfaces:**
- Consumes: `copilot.suggest(case_id) -> dict` with `"risk"`, `"reply"`, `"draft"`, `"status"`.
- Produces:
  - `POST /api/cases/{id}/auto` → `{"case_id", "risk", "outcome": "resolved"|"escalated"|"awaiting_approval"|"needs_agent", "actions": [{"action","approver","status"}], "result": <suggest dict>}`. Low-resolved writes `auto_send`; low-escalated writes `auto_send` plus one `auto_action` per hand-over action (approver from `guards.approver_for`); high → `awaiting_approval`; blocked → `needs_agent`. The suggest result is kept in an in-memory `AUTO: dict[str, dict]`.
  - `POST /api/cases/{id}/approve` body `{"final_reply": str, "handle_s": float | None}` → 409 if the case is not in `AUTO`; else writes `agent_send` (`mode: "auto"`, `approved: true`, edit fields) and one `agent_action` per suggested action. Returns `{"sent": true, "actions": [...]}`.
  - `POST /api/cases/{id}/source_opened` body `{"source": str}` → writes `source_opened`, returns `{"ok": true}`.
  - `SendBody` gains `mode: str = "copilot"`, `sources_opened: int = 0`, `handle_s: float | None = None`, all written on `agent_send`.

- [ ] **Step 1: Write failing tests**: auto on a stubbed low-resolved case returns `outcome == "resolved"` and the log has one `auto_send`; low-escalated with `open_dispute` returns `escalated` and an `auto_action` whose approver is `disputes_team`; a high case returns `awaiting_approval` and writes no `auto_send`; a blocked case returns `needs_agent`; approve before auto returns 409; approve after auto writes `agent_send` with `mode == "auto"`; send with `mode="shadow", sources_opened=0, handle_s=42` logs those fields; source_opened logs `{"event":"source_opened","source":"POL-04 §5"}`.
- [ ] **Step 2:** Run, expect FAIL.
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Tests pass.
- [ ] **Step 5:** Commit `feat: auto-reply, approve-and-send and source-open endpoints`.

### Task 4: Dev summary and edit report (rec 14 reporting)

**Files:**
- Modify: `evals/edit_report.py` (`summarise` adds `blind_send_pct`: share of `agent_send` with `edited == false` and `sources_opened == 0` among sends that carry `sources_opened`; `avg_handle_s_by_mode`); `app/main.py` (`GET /api/dev/summary`)
- Create: `tests/test_dev_summary.py`

**Interfaces:**
- Produces: `GET /api/dev/summary` → `{"drafts", "avg_latency_s", "avg_cost_usd", "blocked", "sends_by_mode": {mode: n}, "blind_send_pct", "avg_handle_s_by_mode": {mode: s}, "edit_share_pct", "auto": {"resolved","escalated","awaiting_approval","needs_agent"}, "source_opens"}` computed from the audit log, all zeros on an empty or missing log. Auto outcomes come from `auto_send`/`auto_action` events plus a new `auto_outcome` event written by `/auto`.

- [ ] **Step 1: Write failing tests**: missing log → `drafts == 0` and `blind_send_pct == 0`; a log with two sends (one unedited with `sources_opened: 0`, one with `sources_opened: 2`) → `blind_send_pct == 50.0`; handle times 60 and 120 in shadow → `avg_handle_s_by_mode["shadow"] == 90.0`.
- [ ] **Step 2:** Run, expect FAIL.
- [ ] **Step 3:** Implement; the edit report's xlsx summary gets two new rows.
- [ ] **Step 4:** Tests pass.
- [ ] **Step 5:** Commit `feat: dev summary with blind sends and handle time by mode`.

### Task 5: Console: mode switcher, risk badges, shadow and auto-reply views, dev mode

**Files:**
- Modify: `app/static/index.html`

**Interfaces:**
- Consumes: the endpoints from Tasks 1, 3 and 4 and `risk` on draft results.
- Produces: `localStorage` keys `nova.mode` (`shadow`|`copilot`|`auto`, default `copilot`) and `nova.dev` (`"1"`/`"0"`).

- [ ] **Step 1:** Header: a segmented switcher Shadow | Copilot | Auto-reply, a Dev mode toggle, and a `Today:` pill; the "Copilot on · suggestions only" pill text follows the mode (Shadow: "Copilot shadowing · agent replies"; Auto-reply: "Auto-reply · high risk needs approval").
- [ ] **Step 2:** Risk badge colours and copy: Low · resolved (green), Low · escalated (teal), High · needs approval (amber), Blocked (red); shown on the draft and on queue cards once assessed; the reason shows on hover and, in dev mode, as text.
- [ ] **Step 3:** Copilot mode: as today, plus the risk badge; citation clicks call `source_opened` and count; Send posts `mode`, `sources_opened`, `handle_s` (from case open). Guardrails collapse to "N/N checks passed" unless dev mode is on or a check failed.
- [ ] **Step 4:** Shadow mode: opening a case starts the draft in the background and shows only "Your reply" plus Send; Send posts the hidden draft as `drafted_reply` with `mode: "shadow"`; the toast reports the share that differed from the copilot's hidden draft. In dev mode the hidden draft is visible below, labelled "Shadow draft (agent can't see this)".
- [ ] **Step 5:** Auto-reply mode: switching to it, or reloading in it, assesses every queue case in parallel via `/auto`, updating each card with its badge and outcome ("Resolved by copilot", "Escalated to Disputes team", "Needs your approval", "Needs an agent"), sorted so approvals come first. Opening a high case shows the draft with **Approve and send** (calls `/approve`); a resolved or escalated case shows what was sent and submitted, read-only.
- [ ] **Step 6:** Dev mode: show the metrics row, "Try to break it", full checks, the risk rule, and a dev panel (a collapsible strip at the top of the right column) filled from `/api/dev/summary`, refreshed after each send or auto run.
- [ ] **Step 7:** Verify in the browser: each mode on CASE-101, 103, 105, 107 and 109; dev toggle; reload keeps the mode; no console errors.
- [ ] **Step 8:** Commit `feat: console mode switcher, risk badges and dev mode`.

### Task 6: Docs and final verification

**Files:**
- Modify: `CLAUDE.md` (How to run: `pytest`), `docs/demo-runbook.md` (a short "Modes" beat for the demo)

- [ ] **Step 1:** Run `.venv\Scripts\python -m pytest -q`: all pass.
- [ ] **Step 2:** Run `.venv\Scripts\python -m evals.edit_report`: prints the summary with `blind_send_pct`.
- [ ] **Step 3:** Commit `docs: modes demo beat and test command`.
