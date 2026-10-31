# Nova Bank support copilot

AI PM Builders capstone. An assistant for Nova Bank's contact-center agents: it drafts answers to dispute, fee and card questions from Nova's own policies and the verified customer's own records, in English, formal Arabic, Egyptian Arabic and Franco-Arabic. Every claim is cited and checked by code, and it never approves anything; actions are suggestions an agent or team approves.

Nova Bank is fictional and all data here is synthetic. The brief is in `docs/brief.md`; decisions and research findings are in `CLAUDE.md`.

## What's in the repo

| Folder | What |
|---|---|
| `app/` | The copilot: FastAPI backend (`main.py`), pipeline (`copilot.py`), guardrails (`guards.py`), agent console (`static/index.html`) |
| `data/` | Synthetic customers, transactions, disputes, tickets, 9 demo cases, and 20 policy docs (`data/generate.py` rebuilds them) |
| `evals/` | 41-case golden set, the eval runner, and results in the course's Golden Record and 3H formats |
| `research/` | Regulation, competitor and customer-complaint research (Egypt) |
| `demo/` | Business case workbook and the Demo Day pack page |
| `docs/` | Brief and Demo Day runbook |

## Run it locally (Windows)

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env      # then paste your Claude API key into .env
.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

Open http://localhost:8000. On a Mac or Linux, use `.venv/bin/` instead of `.venv\Scripts\`.

Run the evals: `.venv\Scripts\python -m evals.run_evals` (about 5 minutes, about $3 of API use).

## Deploy (Render, free)

1. On render.com: New > Blueprint, connect this GitHub repo. It reads `render.yaml`.
2. Fill in the two secrets it asks for: `ANTHROPIC_API_KEY` and `DEMO_PASSWORD` (the password people type to open the site; any username works).
3. Wait for the build, then open the `onrender.com` link.

The free plan sleeps after 15 minutes without visits, and the first visit after that takes about a minute. Open the link a few minutes before you present.

Never commit `.env`; it is in `.gitignore`.
