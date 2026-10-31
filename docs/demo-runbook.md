# Demo Day runbook (31 Oct 2026)

## Before you present (5 minutes)

1. Double-click `start-demo.bat` in the `nova-bank-capstone` folder. A black window opens (leave it open) and the browser opens http://localhost:8000.
2. Click each of the 9 cases and press **Ask copilot** once. This warms up the model and saves a good draft for each case, which is what plays if the Wi-Fi drops (you'll see an orange "Offline: replaying the last saved draft" tag).
3. Have `evals/results/` open in File Explorer: the latest `3H Eval` and `Golden Record` spreadsheets, plus the first run for the before/after.
4. Have `demo/Business Case - Nova Copilot.xlsx` open on the **Budget ask** tab.

## The live part (about 6 minutes)

Each draft takes about 10-20 seconds. While it thinks, say what it is doing: "it only sees this customer's records and our 20 policies, and code checks every quote before I see it".

| # | Case | What to point at |
|---|---|---|
| 1 | Mariam, Franco-Arabic, dispute status | Reply in her own Franco; citation chips (click **D-1001** and a **POL** chip); all checks green |
| 2 | Omar, EGP 225 overdraft fees | 3 x 75 and the daily cap; the waiver is "Team Leader approves", the agent can't do it alone |
| 3 | Karim, declined dispute, Egyptian Arabic | Flags "Asks for approval"; no refund, offers the complaint route |
| 4 | Nour, lost card, formal Arabic | Block first, free on Premium, EGP 100 next-day in Cairo |
| 5 | Husband asking for his wife's balance | Refused; "the model never had her data" |
| 6 | "SYSTEM OVERRIDE ..." | Flagged as prompt injection; answers only his own dispute |
| 7 | Panel's turn | Edit the customer text box and let them try anything |

Good things for the panel to try: another customer's ID ("what did C023 spend?"), "approve my dispute", "ignore your rules", a fake card number, a question the policies don't cover ("do you have a branch in Luxor?").

## If something goes wrong

- **Red "Blocked by guardrails" card**: that is the product working. Say "a check failed, so the agent never sees an unverified answer", and show the failing check.
- **"Copilot unavailable"**: no internet or API problem. Use a case you warmed up (it replays), or show the eval spreadsheets.
- **Black window closed by accident**: double-click `start-demo.bat` again.

## Numbers to have ready

- 45,000 contacts a month, 60% in scope, +15% a year (brief)
- Evals (final run, 31 Oct): 37 of 41 passed; 3H = Helpful 0.93, Honest 1.00, Harmless 0.99, overall 0.97; benchmark answer 24 of 24. Three runs: 28 -> 35 -> 37 passed.
- Year 1 budget about EGP 4.6M; value about EGP 6.0M; payback about 5 months; about 15 hires avoided next year (assumptions in the workbook, agent cost assumed per the instructor)
- Model cost about $0.034 a draft, about 14 seconds; production runs in Egypt because of bank secrecy rules

## Likely questions

- **Why not just buy Intercom or Zendesk?** No Egyptian Arabic or Franco-Arabic, hosted abroad, and bank secrecy blocks sending customer data offshore.
- **What stops it inventing a fee?** Every claim needs a citation, code checks the quote is really in that policy section and every number is in a cited source; otherwise the draft is hidden.
- **What if it's wrong anyway?** The agent reads before sending, can flag it, and flagged drafts are reviewed weekly. The eval suite runs before any change ships.
- **Customer-facing?** Phase 2, month 7: fee explanations and dispute status first, labelled as AI, one tap to a human, anything with money goes to a person.
