# POL-20 · AI Copilot Use Standard (internal)
Version 2026.1 · Effective 2026-10-01 · Status: current

## §1 Role of the copilot
The copilot drafts answers for contact-center agents. The agent decides what is said or sent to the customer.

## §2 Grounding
Every factual statement must cite a policy section or a record belonging to the verified customer on the open case. If no source supports an answer, the copilot says so and recommends escalation.

## §3 Actions
The copilot may suggest actions: open a dispute, block a card, order a replacement card, request a fee waiver, log a complaint. It cannot carry out any action that moves money, approve or decline a dispute, approve a waiver or make a credit decision.

## §4 Data masking
Customer identifiers are masked before any data is sent to the language model. Cards are shown by their last 4 digits only.

## §5 Audit
All copilot inputs, sources, outputs and agent actions are logged and kept for 5 years.

## §6 Feedback
Agents report wrong or unsafe suggestions with the Flag button. Flagged cases are reviewed every week.
