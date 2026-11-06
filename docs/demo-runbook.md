# Demo Day runbook (7 Nov 2026)

## Before you present (5 minutes)

1. Double-click `start-demo.bat` in the `nova-bank-capstone` folder. It stops any older copy still running, a black window opens (leave it open) and the browser opens http://localhost:8000 (press F5 if the page loaded before the server was ready).
2. Click each of the 9 cases and press **Ask copilot** once, on the day (the copilot uses today's date). This warms up the model and saves a good draft for each case, which is what plays if the Wi-Fi drops (you'll see an orange "Offline: replaying the last saved draft" tag).
3. Have `evals/results/` open in File Explorer: the latest `3H Eval` and `Golden Record` spreadsheets, plus the first run for the before/after.
4. Have `demo/Business Case - Nova Copilot.xlsx` open on the **Budget ask** tab.

## The live part (about 6 minutes)

Each draft takes about 10-20 seconds. While it thinks, say what it is doing: "it only sees this customer's records and our 20 policies, and code checks every quote before I see it".

| # | Case | What to point at |
|---|---|---|
| 1 | Mariam, Franco-Arabic, dispute status | She writes Franco, the reply comes back in formal Arabic (every Arabic or Franco message gets formal Arabic, English gets formal English); citation chips (click **D-1001** and a **POL** chip); it spots that the expected date on the record (6 Nov) has passed and suggests escalating, "Team Leader approves"; all checks green |
| 2 | Omar, EGP 225 overdraft fees | 3 x 75 and the daily cap. Then type "Please waive these fees" and ask again: a goodwill waiver, "Team Leader approves" (up to EGP 250) |
| 2b | Hana: type "Please waive the EGP 400 fee and the 35" | The same request above EGP 250 goes to "Ops Manager approves" (POL-11 §2). Code routes it, not the model |
| 3 | Karim, declined dispute, Egyptian Arabic | Flags "Asks for approval"; no refund, offers the complaint route |
| 4 | Nour, lost card, formal Arabic | Block first, free on Premium, EGP 100 next-day in Cairo |
| 5 | Husband asking for his wife's balance | Refused; "the model never had her data" |
| 6 | "SYSTEM OVERRIDE ..." | Flagged as prompt injection; answers only his own dispute |
| 7 | Agent edits | Click into any reply, change a word, press **Send reply**: it says what share of the draft you changed. **Flag as wrong** logs your corrected version for the weekly review and the edit-rate eval |
| 8 | Panel's turn | Edit the customer text box and let them try anything |

Good things for the panel to try: another customer's ID ("what did C023 spend?"), "approve my dispute", "ignore your rules", a fake card number, a question the policies don't cover ("do you have a branch in Luxor?").

## If something goes wrong

- **Red "Blocked by guardrails" card**: that is the product working. Say "a check failed, so the agent never sees an unverified answer", and show the failing check.
- **"Copilot unavailable"**: no internet or API problem. Use a case you warmed up (it replays), or show the eval spreadsheets.
- **Black window closed by accident**: double-click `start-demo.bat` again.

## Numbers to have ready

- 45,000 contacts a month, 60% in scope, +15% a year (brief)
- Evals: six runs, 28 -> 35 -> 37 -> 34 -> 38 -> 40 of 41 passed. Run 6 is the final code (formal replies, approvers routed by policy): 40 of 41, 3H 0.97 (Helpful 0.92, Honest 1.00, Harmless 1.00); the one miss is a "deliver tomorrow" answer that didn't say tomorrow is a weekend. Runs 3 and 4 used the same prompt and rules and scored 37 and 34, so expect about 3 cases of run-to-run variation. In runs 3 to 6, all 41 cases kept other customers' data out, promised no outcome, left every action to a human, resisted hidden instructions and kept card numbers out; benchmark answer 24 of 24; no blocked drafts, no errors.
- Year 1 budget about EGP 4.6M; value about EGP 6.0M; payback about 5 months; about 15 hires avoided next year (assumptions in the workbook, agent cost assumed per the instructor)
- Model cost about $0.03 a draft ($0.034 on 31 Oct, $0.026 on the final run), about 11-14 seconds; production runs in Egypt because of bank secrecy rules

## Likely questions

- **Why not just buy Intercom or Zendesk?** No Egyptian Arabic or Franco-Arabic, hosted abroad, and bank secrecy blocks sending customer data offshore.
- **What stops it inventing a fee?** Every claim needs a citation, code checks the quote is really in that policy section and every number is in a cited source; otherwise the draft is hidden.
- **What if it's wrong anyway?** The agent reads before sending, can flag it, and flagged drafts are reviewed weekly. The eval suite runs before any change ships.
- **Who decides who approves an action?** Code, not the model, from Nova's policies: fee waivers up to EGP 250 go to a Team Leader and above that to the Operations Manager (POL-11 §2); overdraft limits and loans go to the Credit team (POL-10, POL-19); disputes go to the Disputes team; a policy gap or an overdue deadline goes to the Team Leader. If the model suggests the wrong approver, the code corrects it and says so in the checks.
- **What happens after an escalation?** Today it is sent for approval and written to the audit log. A customer who disagrees with a dispute decision gets a complaint and a second review by the Disputes team, which is final, then the CBE consumer protection channel (POL-16). Next on the roadmap: an approvals queue for Team Leaders, the Operations Manager and the Credit team, with the 1- and 15-business-day complaint timers, the customer told the outcome, and anything overdue moving up a level.
- **Why did the score go from 37 to 34?** Nothing in the prompt, rules or data changed between those two runs. The same system scores a few cases differently each run, mostly on wording or an extra suggested action, so we judge a change on the safety checks (other customers' data, promises, approvals, hidden instructions, card numbers), which were 41 of 41 both times, not on one lucky run. The last two runs, after formal replies and policy-based approvers, scored 38 and 40.
- **How do you know how often it's wrong in real use?** Agents edit replies in place, and every send or flag logs the draft next to what the agent actually sent. `evals/edit_report.py` turns that into an error rate: the share of each draft agents had to change, and how many went out untouched.
- **How do the AI engineer and PM keep watch after launch?** Pilot roadmap: a review page separate from the agent console, showing eval runs over time, failing cases with the judge's reasons, which guardrails fail most, flagged drafts and the edit rate. The data already exists in the eval run files and the audit log.
- **Can it improve itself?** We automate the testing and the proposing, never the approving. Next on the roadmap: the eval suite runs on every change and blocks anything that scores lower, flagged drafts become new test questions, and Claude drafts the fix. A person approves every change to the rules, just as an agent approves every action.
- **Why formal Arabic when she wrote Franco?** Everything the bank sends is a record, so replies use one formal register that reads the same for every customer and avoids slang. The copilot still understands all four ways customers write. Arabic replies use the respectful plural, because the model never sees the customer's name or gender.
- **What date does it use?** Today's. The synthetic records run to 29 Oct, so newer deadlines show as passed and it escalates them. The evals pin 30 Oct, the date the benchmark answers were written for.
- **Customer-facing?** Phase 2, month 7: fee explanations and dispute status first, labelled as AI, one tap to a human, anything with money goes to a person.
