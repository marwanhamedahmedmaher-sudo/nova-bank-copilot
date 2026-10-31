# Nova Bank — AI PM Builders Capstone Brief

As of September 19, 2026

## Nova Bank

Nova Bank is a fictional digital-first retail and small-business bank: roughly 2 million customers and no legacy core-banking rewrite in sight.

Products: personal checking and savings, debit and credit cards, SMB business accounts, and unsecured personal loans up to EGP 500,000.

Channels: a mobile app, a web app, and a 120-agent contact center fielding about 45,000 calls and chats a month. It's profitable but stuck: contact-center volume is climbing 15% year over year, SMB loan underwriting takes 9 days on average, and the app gets used for balance checks and nothing more.

## The data

Nova Bank doesn't hand students production data. Each student works from a small synthetic dataset shaped like the real thing (build your own version, or use the sample below as a seed):

| Dataset | Contents | Size |
|---|---|---|
| Customers | customer_id, name, plan, tenure, contact channel | ~50 rows |
| Transactions | date, merchant, amount, category, status (posted / pending / disputed) | ~500 rows |
| Policies & FAQs | fee schedule, dispute process, card replacement, overdraft rules | ~20 documents |
| Contact-center tickets | ticket_id, category, resolution time, agent notes | ~200 rows |

Sample transaction rows:

| Date | Merchant | Amount (EGP) | Category | Status |
|---|---|---|---|---|
| 2026-09-02 | Carrefour Mall of Egypt | -412.50 | Groceries | posted |
| 2026-09-04 | Unknown POS #4471 | -1,200.00 | Uncategorized | disputed |
| 2026-09-10 | Nova Bank ATM Withdrawal | -500.00 | Cash | posted |

## The problem to solve

Nova Bank's contact center is drowning: dispute status, fee explanations, and card replacement account for 60% of contact volume, and that volume is growing faster than headcount. Build an AI customer support copilot that answers a customer's account questions grounded in Nova Bank's real policies and that customer's own transaction history, deflecting the top contact-center reasons without ever inventing an answer, leaking another customer's data, or approving a dispute on its own.

Constraints: this is a regulated bank, so PII and account data must be scoped and never leaked; nothing that moves money or makes a credit decision runs unsupervised; every answer must be groundable in a real Nova Bank source, not the model's general knowledge; and whatever ships in Week 4 has to survive a "why should we trust this" question from a compliance officer.

## Demo Day (in groups)

Students present the live product to a panel, not a slide deck. Bring:

- A working MVP of the proposed solution
- The system design used to build it
- The pricing and business case
- The evals and guardrails used
- The roadmap
