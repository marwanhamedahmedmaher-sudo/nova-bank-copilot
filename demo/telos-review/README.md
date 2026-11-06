# Telos impact review (6 Nov 2026, revised the same day)

A review of the agent console made with the Telos plugin. Telos scores the screens against a business goal, not against general design rules.

- **Key result:** cut handle time on dispute, fee and card chats by 2 minutes per assisted chat (the base case in the business case; EricaAssist's ~1 minute is the floor). Guardrails that must not drop: first-contact resolution, citation accuracy and acceptance after checking.
- **Flow:** Mariam's Franco-Arabic chat about her disputed EGP 1,200 (CASE-101), in six screens: queue, case opened, drafting, draft ready, source check, reply sent.
- **Result:** 3 of 5, Partial. 10 findings (1–10) and 10 fixes (11–20) ranked by impact and effort, each with the audit-log number that shows whether it worked.

**Verdict:** as built, the copilot wins back about 85 of the 120 seconds the business case counts on, almost all of it by writing the formal-Arabic reply. Four pilot fixes close the gap (about 2.4 minutes), and a pre-filled wrap-up takes it to about 3.2. The minute budget on the card shows each line, with estimates marked.

The five HIGH findings:

1. Every chat starts with a wait of about 16 seconds, and the agent has to click Ask copilot to start it.
2. The answer is buried: her EGP 1,200 was already credited provisionally on 2 Oct, but the reply only says so in its third sentence.
3. The reply ends by offering to escalate, which adds a turn before the customer says yes.
4. The flow stops at the "sent" message, with no wrap-up and no way to log the complaint.
9. Nothing shows whether the agent checked the draft, so acceptance can rise while live citation accuracy goes unmeasured.

Scope: dispute-status chats only. Fee and card flows are the next review (rec 19).

Open `index.html` in a browser to start. The screens are static snapshots of the live console with the app's saved drafts, captured before CASE-102, 105 and 106 became chats.
