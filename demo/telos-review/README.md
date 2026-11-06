# Telos impact review (6 Nov 2026)

A review of the agent console made with the Telos plugin. Telos scores the screens against a business goal, not against general design rules.

- **Key result:** cut average handle time on dispute, fee and card contacts by at least 1 minute per contact, without lowering first-contact resolution.
- **Flow:** Mariam's Franco-Arabic chat about her disputed EGP 1,200 (CASE-101), in six screens: queue, case opened, drafting, draft ready, source check, reply sent.
- **Result:** 3 of 5, Partial. 16 numbered recommendations: 1–8 are things to reconsider, 9–16 are the matching fixes.

The four HIGH findings:

1. Every contact starts with a wait of about 16 seconds, and the agent has to click Ask copilot to start it.
2. The answer is buried: her EGP 1,200 was already credited provisionally on 2 Oct, but the reply only says so in its third sentence.
3. The reply ends by offering to escalate, which adds a turn before the customer says yes.
4. The flow stops at the "sent" message, with no wrap-up and no way to log the complaint.

Open `index.html` in a browser to start. The screens are static snapshots of the live console with the app's saved drafts, captured before CASE-102, 105 and 106 became chats.
