"""Builds the business case workbook with live formulas, so any assumption can be changed on Demo Day.

Year 1 is all chat: the agent copilot on chats from month 1, then the customer-facing in-app chat
(Phase 2). Calls join as the next phase, once speech-to-text runs in Egypt.

    .venv\\Scripts\\python demo\\business_case.py [measured_cost_usd_per_suggestion]
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "demo" / "Business Case - Nova Copilot.xlsx"
IN_SCOPE = {"dispute_status", "fee_explanation", "card_replacement"}

# Baseline handle times from our ticket data, split by channel
mins = defaultdict(list)  # (channel, in scope?) -> minutes
for t in csv.DictReader(open(ROOT / "data" / "tickets.csv", encoding="utf-8")):
    mins[(t["channel"], t["category"] in IN_SCOPE)].append(float(t["resolution_minutes"]))
avg = lambda xs: round(sum(xs) / len(xs), 2)
all_mins = [m for v in mins.values() for m in v]
scope_mins = [m for (_, in_scope), v in mins.items() if in_scope for m in v]
aht_all, aht_scope = avg(all_mins), avg(scope_mins)
aht_chat, aht_call = avg(mins[("chat", True)]), avg(mins[("phone", True)])
scope_share_tickets = round(len(scope_mins) / len(all_mins), 2)
chat_share_tickets = round(len(mins[("chat", True)]) / len(scope_mins), 2)
cost_per_suggestion = float(sys.argv[1]) if len(sys.argv) > 1 else 0.03

head = Font(bold=True, color="FFFFFF")
fill = PatternFill("solid", fgColor="0B3A6E")
inp = PatternFill("solid", fgColor="FFF6DD")
out = PatternFill("solid", fgColor="E7F6EE")
bold = Font(bold=True)
N, D1, D0, PCT = "#,##0", "#,##0.0", "0", "0%"
STUDY = "Brynjolfsson, Li & Raymond, Generative AI at Work, QJE 2025 (nber.org/papers/w31161)"

wb = Workbook()
a = wb.active
a.title = "Assumptions"
a.append(["Input", "Value", "Unit", "Source / note"])
for c in a[1]:
    c.font, c.fill = head, fill
ASSUMPTIONS = [
    ("contacts", "Contacts per month (calls and chats)", 45000, "contacts", "Brief"),
    ("scope", "Share in scope (disputes, fees, cards)", 0.60, "%", f"Brief (our ticket sample: {scope_share_tickets:.0%})"),
    ("chat_share", "Chats as a share of in-scope contacts", chat_share_tickets, "%",
     "ASSUMPTION from our synthetic tickets; the brief gives no split. Test 20%-50%"),
    ("growth", "Contact growth per year", 0.15, "%", "Brief"),
    ("agents", "Agents", 120, "agents", "Brief"),
    ("agent_cost", "Fully loaded cost per agent per month", 20000, "EGP", "ASSUMPTION - asked the instructor; test 15k-30k"),
    ("aht_all", "Average handle time, all contacts", aht_all, "min", "Our synthetic tickets (200)"),
    ("aht_scope", "Average handle time, in-scope contacts", aht_scope, "min", "Our synthetic tickets"),
    ("aht_chat", "Average handle time, in-scope chats", aht_chat, "min",
     f"Our synthetic tickets: the slowest in-scope contacts, because the agent types every answer (in-scope calls: {aht_call} min)"),
    ("saved_chat", "Minutes saved per assisted chat (base)", 2.0, "min",
     f"ASSUMPTION, traced screen by screen in the Telos minute budget (demo/telos-review): about 1.4 min as built today, 2.4 min once the pilot fixes land (draft ready on open, shorter reading, one-turn answers). 2.0 is the middle. Field study: +14% chats resolved per hour on average, +34% for new agents ({STUDY})"),
    ("acw_saved", "After-chat work saved per assisted chat (pre-filled wrap-up)", 0.75, "min",
     "ASSUMPTION from the Telos minute budget: about 60s typing the note and disposition becomes about 15s checking a wrap-up the copilot pre-fills (rec 13). Counted separately from minutes saved in the chat"),
    ("acw_start", "Pre-filled wrap-up starts in month", 4, "month", "Roadmap: built during the pilot, live after it"),
    ("saved_call", "Minutes saved per assisted call (calls phase)", 1.0, "min",
     "ASSUMPTION at the floor: BofA EricaAssist ~1 min a call (research/competitors.md)"),
    ("adoption", "Share of in-scope contacts where agents use the copilot", 0.80, "%", "ASSUMPTION"),
    ("drafts", "Copilot drafts per contact", 1.5, "drafts", "ASSUMPTION: retries and follow-ups (1.3), plus drafts started when a case is assigned and then reassigned or closed unopened (Telos rec 11)"),
    ("usd_per_draft", "Model cost per draft", cost_per_suggestion, "USD", "MEASURED in our eval run (Claude Opus 5.5 incl. guard model)"),
    ("fx", "EGP per USD", 56.12, "EGP", "CBE rate 29 Oct 2026 (research/regulation.md)"),
    ("hosting", "In-country hosting and ops per month (production)", 250000, "EGP", "ASSUMPTION - range 150k-400k until Huawei Cairo / self-host quotes"),
    ("stt", "In-country speech-to-text per month (calls phase)", 100000, "EGP",
     "ASSUMPTION - range 50k-300k until quotes; Google Agent Assist voice lists $0.03/min but is hosted abroad"),
    ("build", "One-off build (4 people x 3 months)", 960000, "EGP", "ASSUMPTION"),
    ("deflect", "Phase 2: share of in-scope contacts resolved in the in-app chat", 0.30, "%", "ASSUMPTION; Klarna/Erica show higher, we stay conservative"),
    ("p2_start", "Phase 2 (in-app chat) starts in month", 7, "month", "Roadmap"),
    ("calls_start", "Calls phase (live transcript) starts in month", 13, "month", "Roadmap: once speech-to-text runs in Egypt"),
]
ref = {}
for i, (key, label, value, unit, note) in enumerate(ASSUMPTIONS, start=2):
    a.append([label, value, unit, note])
    a.cell(i, 2).fill = inp
    if unit == "%":
        a.cell(i, 2).number_format = PCT
    ref[key] = f"Assumptions!$B${i}"
for col, w in zip("ABCD", [52, 14, 10, 80]):
    a.column_dimensions[col].width = w


def add_rows(ws, rows):
    """rows are (key, label, year1, year2, how, number format). A formula names an input as {input},
    another row in the same column as {row}, or a fixed column as {row:B}. Returns row numbers by key."""
    pos, r = {}, ws.max_row
    for row in rows:
        r += 1
        if row[0]:
            pos[row[0]] = r

    def resolve(f, col):
        def sub(mo):
            name, _, fixed = mo.group(1).partition(":")
            return ref[name] if name in ref else f"{fixed or col}{pos[name]}"
        return re.sub(r"\{(\w+(?::[BC])?)\}", sub, f) if f else f

    for key, label, b, c, how, fmt in rows:
        ws.append([label, resolve(b, "B"), resolve(c, "C"), how])
        r = ws.max_row
        if key is None:
            ws.cell(r, 1).font = bold
            continue
        for col in (2, 3):
            ws.cell(r, col).number_format = fmt
            if ws.cell(r, col).value:
                ws.cell(r, col).fill = out
    return pos


def section(title):
    return (None, title, None, None, None, None)


m = wb.create_sheet("Model")
m.append(["Output", "Year 1 (today's volume)", "Year 2 (+15% volume)", "How it's calculated"])
for c in m[1]:
    c.font, c.fill = head, fill
row = add_rows(m, [
    ("inscope", "In-scope contacts per month", "={contacts}*{scope}", "={contacts}*(1+{growth})*{scope}", "contacts x scope share", N),
    ("chats", "  of which chats", "={inscope}*{chat_share}", "={inscope}*{chat_share}", "in-scope x chat share", N),
    ("calls", "  of which calls", "={inscope}-{chats}", "={inscope}-{chats}", "the rest", N),
    ("minutes", "Agent minutes per month (no copilot)", "={contacts}*{aht_all}", "={contacts}*(1+{growth})*{aht_all}", "contacts x AHT", N),
    ("capacity", "Minutes per agent per month (capacity)", "={contacts}*{aht_all}/{agents}", "={capacity:B}", "today's minutes / 120 agents", N),
    ("needed", "Agents needed without copilot", "={minutes}/{capacity}", "={minutes}/{capacity}", "minutes / capacity", D1),
    section("PHASE 1 - AGENT COPILOT ON CHATS (from month 1)"),
    ("chat_assisted", "Assisted chats per month", "={chats}*{adoption}", "={chats}*{adoption}", "chats x adoption", N),
    ("chat_hr", "Chats an agent closes per hour today", "=60/{aht_chat}", "=60/{aht_chat}", "60 / chat handle time", D1),
    ("chat_hr_cp", "Chats an agent closes per hour with the copilot", "=60/({aht_chat}-{saved_chat})", "=60/({aht_chat}-{saved_chat})",
     "60 / (chat handle time - minutes saved)", D1),
    ("chat_lift", "More chats per agent-hour", "={chat_hr_cp}/{chat_hr}-1", "={chat_hr_cp}/{chat_hr}-1",
     "field study: +14% on average, +34% for new agents", PCT),
    ("chat_saved", "Minutes saved per month", "={chat_assisted}*{saved_chat}", "={chat_assisted}*{saved_chat}", "assisted chats x minutes saved", N),
    ("chat_fte", "Agent capacity freed (FTE)", "={chat_saved}/{capacity}", "={chat_saved}/{capacity}", "minutes saved / capacity", D1),
    ("chat_value", "Value of freed capacity per month (EGP)", "={chat_fte}*{agent_cost}", "={chat_fte}*{agent_cost}", "FTE x cost per agent", N),
    ("acw_min", "After-chat minutes saved per month (from the wrap-up start month)", "={chat_assisted}*{acw_saved}", "={chat_assisted}*{acw_saved}",
     "assisted chats x after-chat minutes saved", N),
    ("acw_fte", "Agent capacity freed by the wrap-up (FTE)", "={acw_min}/{capacity}", "={acw_min}/{capacity}", "minutes saved / capacity", D1),
    ("acw_value", "Value of the wrap-up per month (EGP)", "={acw_fte}*{agent_cost}", "={acw_fte}*{agent_cost}", "FTE x cost per agent", N),
    ("chat_model", "Model cost per month (EGP)", "={chat_assisted}*{drafts}*{usd_per_draft}*{fx}",
     "={chat_assisted}*{drafts}*{usd_per_draft}*{fx}", "drafts x measured cost", N),
    ("chat_egp", "Agent time saved per assisted chat (EGP)", "={saved_chat}*{agent_cost}/{capacity}", None, "minutes saved x agent cost per minute", D1),
    ("chat_model_each", "Model cost per assisted chat (EGP)", "={chat_model}/{chat_assisted}", None, "model cost / assisted chats", D1),
    section("PHASE 2 - CUSTOMER-FACING IN-APP CHAT (from month 7)"),
    ("p2_resolved", "Contacts resolved in the app per month", "={inscope}*{deflect}", "={inscope}*{deflect}", "in-scope x in-app resolution", N),
    ("p2_fte", "Agent capacity freed (FTE)", "={p2_resolved}*{aht_scope}/{capacity}", "={p2_resolved}*{aht_scope}/{capacity}",
     "resolved x in-scope AHT / capacity", D1),
    ("p2_value", "Value per month (EGP)", "={p2_fte}*{agent_cost}", "={p2_fte}*{agent_cost}", "FTE x cost per agent", N),
    section("NEXT PHASE - CALLS WITH A LIVE TRANSCRIPT (from the month set in Assumptions)"),
    ("call_assisted", "Assisted calls per month", "={calls}*{adoption}", "={calls}*{adoption}", "calls x adoption", N),
    ("call_saved", "Minutes saved per month", "={call_assisted}*{saved_call}", "={call_assisted}*{saved_call}", "assisted calls x minutes saved", N),
    ("call_fte", "Agent capacity freed (FTE)", "={call_saved}/{capacity}", "={call_saved}/{capacity}", "minutes saved / capacity", D1),
    ("call_value", "Value per month (EGP)", "={call_fte}*{agent_cost}", "={call_fte}*{agent_cost}", "FTE x cost per agent", N),
    ("call_cost", "Model and speech-to-text cost per month (EGP)", "={call_assisted}*{drafts}*{usd_per_draft}*{fx}+{stt}",
     "={call_assisted}*{drafts}*{usd_per_draft}*{fx}+{stt}", "drafts x measured cost + speech-to-text", N),
    section("TODAY"),
    ("agent_contact", "Agent cost per contact today (EGP)", "={agents}*{agent_cost}/{contacts}", None, "agent payroll / contacts", N),
    section("TOTALS - column B is year 1, column C is year 2"),
    ("m_p2", "Months the in-app chat runs", "=MIN(12,MAX(0,13-{p2_start}))", "=MIN(12,MAX(0,25-{p2_start}))", "from its start month", D0),
    ("m_acw", "Months the pre-filled wrap-up runs", "=MIN(12,MAX(0,13-{acw_start}))", "=MIN(12,MAX(0,25-{acw_start}))", "from its start month", D0),
    ("m_calls", "Months the calls phase runs", "=MIN(12,MAX(0,13-{calls_start}))", "=MIN(12,MAX(0,25-{calls_start}))", "from its start month", D0),
    ("value", "Value (EGP)", "=12*{chat_value}+{m_acw}*{acw_value}+{m_p2}*{p2_value}+{m_calls}*{call_value}",
     "=12*{chat_value}+{m_acw}*{acw_value}+{m_p2}*{p2_value}+{m_calls}*{call_value}",
     "agent chats all year + wrap-up, in-app chat and calls for the months they run", N),
    ("running", "Running cost (EGP)", "=12*({hosting}+{chat_model})+{m_calls}*{call_cost}",
     "=12*({hosting}+{chat_model})+{m_calls}*{call_cost}", "hosting + model, plus speech-to-text once calls start", N),
    ("cost", "Total cost (EGP)", "={build}+{running}", "={running}", "year 1 adds the one-off build", N),
    ("net", "Net (EGP)", "={value}-{cost}", "={value}-{cost}", "value - cost", N),
    ("cum", "Cumulative net (EGP)", "={net:B}", "={net:B}+{net:C}", "running total", N),
    ("hires", "Hires avoided next year", None, "=MIN({chat_fte}+{acw_fte}*{m_acw}/12+{p2_fte}*{m_p2}/12+{call_fte}*{m_calls}/12,{needed}-{agents})",
     "growth absorbed: freed FTE, capped at the hires growth needs", D1),
    ("payback", "Programme pays back in month", "='Cash flow'!B27", None, "first month the cumulative net turns positive (Cash flow sheet)", D0),
])
for col, w in zip("ABCD", [48, 24, 24, 56]):
    m.column_dimensions[col].width = w

f = wb.create_sheet("Cash flow")
f.append(["Month", "Agent chats (incl. wrap-up)", "In-app chat", "Calls", "Running cost", "Build", "Net", "Cumulative net"])
for c in f[1]:
    c.font, c.fill = head, fill
for month in range(1, 25):
    r, col = month + 1, "B" if month <= 12 else "C"
    f.append([
        month,
        f"=Model!{col}{row['chat_value']}+IF($A{r}>={ref['acw_start']},Model!{col}{row['acw_value']},0)",
        f"=IF($A{r}>={ref['p2_start']},Model!{col}{row['p2_value']},0)",
        f"=IF($A{r}>={ref['calls_start']},Model!{col}{row['call_value']},0)",
        f"={ref['hosting']}+Model!{col}{row['chat_model']}+IF($A{r}>={ref['calls_start']},Model!{col}{row['call_cost']},0)",
        f"={ref['build']}" if month == 1 else 0,
        f"=B{r}+C{r}+D{r}-E{r}-F{r}",
        f"=G{r}" if month == 1 else f"=H{r - 1}+G{r}",
    ])
    for c in range(2, 9):
        f.cell(r, c).number_format = N
f.append([])
f.append(["Pays back in month", '=IFERROR(INDEX(A2:A25,MATCH(TRUE,INDEX(H2:H25>=0,0),0)),"after month 24")'])
f["A27"].font = bold
f["B27"].fill = out
for col, w in zip("ABCDEFGH", [20, 16, 16, 16, 16, 14, 16, 18]):
    f.column_dimensions[col].width = w

s = wb.create_sheet("Sensitivity")
s.append(["Agent chats: value of freed capacity per month (EGP), year 1 - minutes saved per chat vs chats' share of in-scope contacts"])
s["A1"].font = bold
shares = [0.20, 0.30, 0.40, 0.50]
s.append(["Minutes saved \\ chat share"] + shares)
for c in s[2]:
    c.font, c.fill = head, fill
for c in s[2][1:]:
    c.number_format = PCT
for saved in [1.0, 1.5, 2.0, 2.5, 3.0]:
    s.append([saved] + [f"=Model!$B${row['inscope']}*{share}*{ref['adoption']}*{saved}/Model!$B${row['capacity']}*{ref['agent_cost']}"
                        for share in shares])
    for c in range(2, 6):
        s.cell(s.max_row, c).number_format = N
s.append([])
s.append(["Year 1 net (EGP) - in-country hosting per month vs share resolved in the in-app chat"])
s.cell(s.max_row, 1).font = bold
hostings, deflects = [150000, 250000, 400000], [0.20, 0.30, 0.40]
s.append(["Hosting \\ in-app resolution"] + deflects)
for c in s[s.max_row]:
    c.font, c.fill = head, fill
for c in s[s.max_row][1:]:
    c.number_format = PCT
B = lambda key: f"Model!$B${row[key]}"
for h in hostings:
    p2_at = lambda d: f"{B('inscope')}*{d}*{ref['aht_scope']}/{B('capacity')}*{ref['agent_cost']}"
    s.append([h] + [f"={B('value')}-{B('m_p2')}*{B('p2_value')}+{B('m_p2')}*{p2_at(d)}-({B('cost')}-12*{ref['hosting']}+12*{h})"
                    for d in deflects])
    s.cell(s.max_row, 1).number_format = N
    for c in range(2, 5):
        s.cell(s.max_row, c).number_format = N
s.append([])
s.append(["Year 1 and year 2 net (EGP) by case - minutes saved in the chat and after it (Telos minute budget)"])
s.cell(s.max_row, 1).font = bold
s.append(["Case", "Minutes saved in the chat", "After-chat minutes saved", "Year 1 net", "Year 2 net"])
for c in s[s.max_row]:
    c.font, c.fill = head, fill
CASES = [("Low: the console as built today, no wrap-up", 1.4, 0),
         ("Base: the Assumptions sheet", None, None),
         ("Upside: all pilot fixes and the wrap-up", 2.4, 0.75)]
for name, in_chat, after in CASES:
    in_chat_f = ref["saved_chat"] if in_chat is None else in_chat
    after_f = ref["acw_saved"] if after is None else after
    r = s.max_row + 1
    per_min = lambda col: f"Model!${col}${row['chat_assisted']}/Model!${col}${row['capacity']}*{ref['agent_cost']}"
    net = lambda col: (f"=Model!${col}${row['net']}+12*(B{r}-{ref['saved_chat']})*{per_min(col)}"
                       f"+Model!${col}${row['m_acw']}*(C{r}-{ref['acw_saved']})*{per_min(col)}")
    s.append([name, f"={in_chat_f}" if in_chat is None else in_chat, f"={after_f}" if after is None else after, net("B"), net("C")])
    for c in (4, 5):
        s.cell(s.max_row, c).number_format = N
s.column_dimensions["A"].width = 30

p = wb.create_sheet("Budget ask")
p.append(["Internal budget request (instructor: frame as an internal team asking for budget)", "EGP", "", "Basis"])
for c in p[1]:
    c.font, c.fill = head, fill
p.append(["Year 1 budget: build + 12 months of running", f"=Model!B{row['cost']}", "", "Assumptions + Model sheets"])
p.append(["  of which one-off build", f"={ref['build']}", "", "4 people x 3 months"])
p.append(["  of which running cost per month", f"={ref['hosting']}+Model!B{row['chat_model']}", "", "in-country hosting + measured model cost"])
p.append(["Agent time saved per assisted chat", f"=Model!B{row['chat_egp']}", "", "2 minutes of agent time in the chat; the wrap-up adds 0.75 min after it from month 4"])
p.append(["Model cost per assisted chat", f"=Model!B{row['chat_model_each']}", "", "measured"])
p.append(["Agent cost per contact today", f"=Model!B{row['agent_contact']}", "", "for comparison"])
p.append(["Year 1 value", f"=Model!B{row['value']}", "", "freed agent capacity: agent chats all year, in-app chat from month 7"])
p.append(["Year 1 net", f"=Model!B{row['net']}", "", "value - budget"])
p.append(["Year 2 value, calls added", f"=Model!C{row['value']}", "", "+15% volume; calls with a live transcript join"])
p.append(["Year 2 net", f"=Model!C{row['net']}", "", "value - running cost, speech-to-text included"])
p.append(["Programme pays back in month", f"=Model!B{row['payback']}", "", "Cash flow sheet"])
for r in range(2, p.max_row + 1):
    p.cell(r, 2).number_format = D1 if r in (5, 6) else (D0 if r == p.max_row else N)
p.append([])
p.append(["Build vs buy: what the same 120 seats would cost from a vendor", "EGP / month", "", "Why we still build"])
for c in p[p.max_row]:
    c.font, c.fill = head, fill
p.append(["Intercom Copilot, $29 / agent / month", f"=29*{ref['fx']}*{ref['agents']}", "", "No Egyptian Arabic or Franco-Arabic; hosted abroad (bank secrecy blocks customer data)"])
p.append(["Zendesk Copilot, $50 / agent / month", f"=50*{ref['fx']}*{ref['agents']}", "", "Same; also needs Zendesk as the helpdesk"])
p.append(["Microsoft D365 Contact Center, $110 / user / month", f"=110*{ref['fx']}*{ref['agents']}", "", "Full platform replacement, not just a copilot"])
p.append(["Phase 2 benchmark: Intercom Fin, $0.99 / resolution", f"=0.99*{ref['fx']}*Model!C{row['p2_resolved']}", "", "Customer-facing; offshore hosting"])
for r in range(p.max_row - 3, p.max_row + 1):
    p.cell(r, 2).number_format = N
p.append(["Source: research/competitors.md, list prices checked 30 Oct 2026, USD 1 = EGP 56.12"])
for col, w in zip("ABCD", [62, 18, 2, 90]):
    p.column_dimensions[col].width = w

for ws in wb.worksheets:
    for r in ws.iter_rows():
        for cell in r:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
wb.save(OUT)
print(f"wrote {OUT}")
print(f"baseline AHT all={aht_all} min, in-scope={aht_scope} min (chats {aht_chat}, calls {aht_call}), "
      f"in-scope share in tickets={scope_share_tickets}, chats' share of in-scope={chat_share_tickets}")
