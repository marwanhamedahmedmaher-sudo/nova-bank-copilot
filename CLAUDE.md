# Nova Bank support copilot (AI PM Builders capstone)

Marwan's capstone. Demo Day is **7 Nov 2026** (moved from 31 Oct): a live product shown to a panel. The group is small, so most of the work is built in Claude Code. The full brief is in `docs/brief.md`.

## What we are building

An AI copilot for Nova Bank's contact-center agents. It covers the three reasons behind 60% of contacts: dispute status, fee explanations and card replacement. When an agent opens a chat, the copilot drafts a reply grounded in Nova Bank policy and that customer's own records. Every claim carries a citation. Actions are suggestions only; the agent clicks.

Phase 2 (roadmap): the same engine goes customer-facing in the app for the lowest-risk intents. Anything that moves money hands off to a human.

## Decisions (agreed with Marwan, 30 Oct)

- **First users are agents.** Customer-facing comes later (Phase 2).
- **Channel: chat only in Phase 1** (Marwan, 6 Nov). The copilot does not listen to calls. Calls join as the next phase (year 2 in the business case) with a live transcript, once speech-to-text that understands Egyptian Arabic runs in Egypt.
- **Languages:** English, formal Arabic, Egyptian Arabic and Franco-Arabic (Arabic typed in Latin letters). Policies are written in English, so search has to work across languages and evals cover all four. Replies are always formal (Marwan, 6 Nov): formal Arabic in Arabic script for any Arabic or Franco-Arabic message, formal English for English, with the respectful plural in Arabic because the model never knows the customer's gender.
- **Regulation drives the design.** Customer details are masked before reaching the model, every answer is logged for audit, and the design has a path to an in-country model.
- **Money and credit:** the copilot only suggests (open dispute, order card, waive fee). The agent acts. In Phase 2 those actions escalate to a human.
- **Identity:** the customer ID comes from the case the agent opened, after the contact center verified the caller. Each copilot session is tied to that one customer and cannot look up anyone else.
- **Success metric (Phase 1):** average handle time, after-call work, how often agents accept the suggestion, and whether citations are correct. Deflection is the Phase 2 metric.
- **Data:** we build our own synthetic dataset (the brief allows it), including a disputes table and the 20 policy docs with planted edge cases.
- **Model:** Claude API. Marwan puts the key in `.env` (never committed, never read by Claude).

## Instructor answers (Wafaey, 30 Oct)

1. Pricing: frame it as an **internal team asking for budget** (vendor prices are only the build-vs-buy benchmark).
2. Cost per contact / agent cost: **assume it**, and show the sensitivity range.

## How to run (Windows, from this folder)

- Rebuild data: `.venv\Scripts\python data\generate.py`
- Console: `.venv\Scripts\python -m uvicorn app.main:app --port 8000`, then open http://localhost:8000
- One case from the command line: `.venv\Scripts\python -m app.copilot CASE-101`
- Evals (golden set, writes both course spreadsheets to `evals/results/`): `.venv\Scripts\python -m evals.run_evals`
- Agent edit report (share of each draft agents changed when sending or flagging, blind sends, handle time by mode, from the audit log): `.venv\Scripts\python -m evals.edit_report [YYYY-MM-DD]`
- Tests (no API calls; install once with `.venv\Scripts\python -m pip install -r requirements-dev.txt`): `.venv\Scripts\python -m pytest -q`
- Console modes (header): Shadow (copilot drafts silently, agent replies), Copilot (Phase 1), Auto-reply (Phase 2 preview: risk labels from `guards.risk_label`; low risk resolved or escalated, high risk waits for approval). Dev mode toggle shows cost, guardrails, risk rule and the dev panel.
- Live chat (remote Demo Day): a teammate plays Nourhan Nahnoush (CASE-110) at `/customer` on another laptop through a Cloudflare tunnel with `DEMO_PASSWORD` set. Steps in `docs/live-chat-demo.md`.
- Control room (dev mode on, side menu; `app/control.py`): Guardrails (built-ins on/off and block/warn, a few locked for bank secrecy; custom phrase rules on the reply or the message), Golden rules (the golden set: edit cases, download .xlsx, upload a named batch, pick the set evals use; batches in `evals/golden_sets/`), Evals (run all, failing or one case in a subprocess; download results with a Notes column, upload notes logged by name and time to `evals/results/notes.jsonl`), Models (primary, backup, simulate an outage), Analytics (deflection and minutes saved from the audit log, assumptions editable; copilot-mode drafts edited before sending by size band, click a band to list and download draft vs sent as .xlsx). Settings live in `app/logs/control.json`; every change is a `config_change` in the audit log.
- Hosted copy for teammates (laptop can be off): Vercel, https://nova-bank-capstone.vercel.app (password in Vercel env `DEMO_PASSWORD`, key in `ANTHROPIC_API_KEY`). Redeploy with `npx.cmd vercel deploy --prod --yes` (plain `npx` is blocked by PowerShell's script policy). Entry `index.py`, `vercel.json`, `.vercelignore` keeps `.env` out. On Vercel logs go to `/tmp` and reset; live chat, control-room settings and analytics are unreliable there, golden-set edits and evals fail.
- Business case workbook: `.venv\Scripts\python demo\business_case.py <measured USD per draft>`

## Research findings that shape the design (30 Oct, see `research/`)

- Banks are exempt from the PDPL; bank secrecy (Law 194/2020 Art. 140-143, criminal penalties) and CBE outsourcing rules bind. Foreign providers reportedly can't register, so production keeps customer data and the model in Egypt (Huawei Cloud Cairo or self-hosted). The demo uses Claude on synthetic data only.
- CBE complaints: reference within 2 working days, reply within 15.
- Pricing benchmarks: agent-assist $29-50 per seat a month; customer-facing $0.99-2.00 per resolution.
- BofA EricaAssist: about 1 minute off each call, the floor for our handle-time claim.

## Layout

- `docs/` brief and design notes
- `research/` complaint, competitor and regulation research
- `data/` synthetic dataset and policy docs
- `app/` the copilot (backend + agent console)
- `evals/` eval cases, runner and results
- `demo/` Demo Day materials
