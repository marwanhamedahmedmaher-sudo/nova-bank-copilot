# Console modes, risk labels, dev mode, and two Telos fixes (design)

Agreed with Marwan on 6 Nov 2026, the night before Demo Day (7 Nov). The source is the Telos impact review (`demo/telos-review/critique-card.html`) and the chat that followed it.

## Intent

Show the panel the roadmap as one dial in the live console: **Shadow → Copilot → Auto-reply**. Every case carries a **risk label** worked out by code, so the panel can see where automation stops: low-risk cases are already resolved or escalated, and high-risk cases wait for a human's permission. A **dev mode** gives the AI PM and AI engineer the numbers (cost, latency, guardrails, why a label was chosen, blind sends, handle time per mode), keeping them out of the agent's working view. Two fixes from the review ship with it: deadlines worked out in code (rec 16) and logging whether the agent opened a source before sending (rec 14).

## Goals

1. **Risk label on every assessed case**, decided by code, never by the model. The model can only raise risk (through its risk flags), never lower it.
   - **Blocked**: prompt injection, a request about another person, or a draft that failed a guardrail. Never sent automatically, in any mode.
   - **High: needs approval**: any action that moves money, waives a fee or touches a card (`request_fee_waiver`, `block_card`, `order_replacement_card`, `refer_to_credit_team`), or the customer asks for a refund, waiver or approval (`approval_request`), or fraud is suspected.
   - **Low: escalated**: the only actions hand the case to a human team without moving money (`open_dispute`, `escalate_to_supervisor`, `log_complaint`).
   - **Low: resolved**: an information-only answer with no actions.
   - Each label carries a one-line reason ("request_fee_waiver moves money").
2. **Mode switcher** in the header, remembered in the browser:
   - **Shadow**: the copilot drafts silently, and the agent never sees the draft. The agent writes and sends their own reply. The send is logged next to the hidden draft (`mode: shadow`, changed share, handle time). This is how the pilot measures time saved and accuracy with zero risk.
   - **Copilot**: today's console (Phase 1). The risk label is shown on the draft.
   - **Auto-reply** (Phase 2 preview): the console assesses every case in the queue. Low-resolved cases get their reply sent by the copilot. Low-escalated cases get their reply sent and their hand-over actions submitted to the named team. High cases wait with "Needs your approval": the agent opens one, reviews it, and clicks **Approve and send**, which sends the reply and submits the actions to their policy approvers. Blocked cases go to the agent. Every automatic step is written to the audit log as `auto_send` / `auto_action`.
3. **Money never moves without a human.** Auto-reply only removes clicks on information-only answers and on hand-overs to a team. A waiver still goes to the Team Leader or Operations Manager, a dispute decision to the Disputes team.
4. **Dev mode** (header toggle, remembered): shows the "Try to break it" hint, the cost / latency / token row, the full guardrail list (agents see one summary line), the risk rule that fired, and a **dev panel** with session numbers from the audit log: drafts, average latency and cost, blocked drafts, sends by mode, edit share, blind-send share, average handle time by mode, and auto-reply outcomes.
5. **Rec 16: deadlines in code.** Each dispute record line the model sees and cites gains a computed status as of today: "due today", "overdue by N days" or "due in N days (as of YYYY-MM-DD)". The prompt tells the model to suggest escalation only when that line says overdue. The console header shows today's date.
6. **Rec 14: source opens.** Clicking a citation chip logs `source_opened`. Each send logs `sources_opened` (a count) and `handle_s` (seconds from opening the case to sending). The edit report adds "sent unedited without opening a source" and average handle time by mode.

## Non-goals

- No real messaging channel. "Sent" means logged to the audit trail, as it does today.
- No new model prompt per mode. The draft is the same in every mode; only what happens to it changes.
- No changes to the eval golden set or the replay cache format.
- No layout redesign from the review (recs 11, 13, 17, 18 stay roadmap items).

## Anti-goals (a failure even if it works)

- The model deciding or lowering a risk label.
- Anything in auto-reply that moves money, waives a fee or touches a card without a human click.
- The agent's view getting busier: dev information shows only in dev mode.
- Breaking the existing copilot flow, the offline replay, or the evals.

## Constraints

- FastAPI backend and a single static `index.html`, no build step. Windows, `.venv`.
- Masked text only in the audit log (POL-20 §4-5).
- The API key stays in `.env` and is never read by Claude.

## Builder's calls (not discussed; settled here)

- Auto-reply assesses the queue with one request per case, in parallel from the browser, so cards update one by one. If a draft is unavailable (offline), the existing replay fallback applies, and the card says so.
- In auto-reply the copilot's reply is sent as drafted, so an escalated case's reply may still phrase the hand-over as an offer ("I can open a dispute"). This is a known gap: matching the reply to the action taken is rec 15 on the roadmap.
- "Approve and send" submits every suggested action through the existing action endpoint, so approvers still come from the policy table.
- Tests use pytest with the FastAPI TestClient, and the copilot call is stubbed, so the tests spend no API credit.
