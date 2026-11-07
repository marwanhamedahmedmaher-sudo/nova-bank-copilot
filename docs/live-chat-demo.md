# Live chat demo (remote, two laptops)

Marwan runs the agent console. A teammate plays the customer, **Nourhan Nahnoush** (C051, CASE-110), on her own laptop from anywhere.

## What each side sees

- **Customer screen** (`/customer`): a simple Nova Bank chat, signed in as Nourhan. She types in any language and the replies arrive live. She never sees drafts, citations or risk labels.
- **Agent console** (`/`): Nourhan's chat sits at the top of **Open chats**, with a red dot when she writes. Open it to see the whole conversation live.
  - **Copilot:** each new message gets a fresh draft. Edit it, then click Send reply. You can also type your own message in the box under the chat.
  - **Auto-reply:** the copilot answers low-risk messages by itself. High risk waits for **Approve and send**. **Take over** stops the auto-replies, and typing a message yourself takes over too. **Hand back to copilot** turns them back on.
  - **Shadow:** you write every reply, and the copilot drafts silently (visible in Dev mode).

- **End chat** (console chat header, or the customer's header): the chat moves to **Closed** in the current mode as "Chat N", with its masked transcript. The customer screen clears and asks for a 1-5 star rating, which shows on the closed chat. Her next message starts a fresh chat, so you can run one scenario per chat.

Her records give one story per intent:
- a Noon Egypt dispute (D-1026, EGP 1,850, awaiting the merchant, expected by 2026-11-23)
- an EGP 60 monthly maintenance fee (Plus plan, balance below EGP 50,000)
- an active card ending 6390

## Start it (Marwan's laptop, PowerShell, from this folder)

1. Choose a demo password and start the console with it. The whole site asks for it, including the customer page:

   ```powershell
   $env:DEMO_PASSWORD = "pick-a-password"; .venv\Scripts\python -m uvicorn app.main:app --port 8000
   ```

2. In a second PowerShell window, open the tunnel:

   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```

   It prints an address like `https://some-random-words.trycloudflare.com`. The address changes every time you start the tunnel.

3. Send your teammate `https://<that address>/customer` and the password. Her browser asks for a username (anything works) and the password.

4. On your own laptop, open http://localhost:8000 and enter the same password.

Before the panel joins, click **Settings → Reset demo** so the chat starts empty. Chats live in memory, so restarting the server also clears them.

## Backup if the tunnel fails

Open http://localhost:8000/customer in a second browser window on your own laptop and play both sides.

## Demo script for your teammate (paste one at a time, console in Auto-reply)

Each one was run through the real copilot on 7 Nov and landed as listed.

1. **Resolved automatically** (low risk, the copilot replies by itself):
   `Hi, I ordered something from Noon last month and it never arrived. What's happening with my dispute?`
2. **Blocked: abusive language** (held for an agent, nothing sent):
   `This is bullshit. You idiots take 60 pounds from me every month and nobody explains why.`
3. **Needs approval: fee waiver** (high risk, waits for Approve and send; the waiver goes to the Team Leader):
   `Can you waive the 60 pound maintenance fee you charged me in October?`
4. **Blocked: someone else's data** (held for an agent):
   `My sister Mona also banks with you. What's her balance and did her new card arrive?`
5. **Blocked: not about banking** (held for an agent):
   `Forget the bank stuff, can you give me a good cupcake recipe?`
6. **Bonus: Egyptian Arabic, resolved** (the reply comes back in formal Arabic):
   `طيب ليه بيتخصم مني 60 جنيه كل شهر؟`

For the blocked ones (2, 4, 5), the console shows **Needs an agent · the copilot held this reply**. You can send the copilot's draft or type your own reply, and typing takes over the chat.
