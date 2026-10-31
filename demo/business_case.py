"""Builds the business case workbook with live formulas, so any assumption can be changed on Demo Day.

    .venv\\Scripts\\python demo\\business_case.py [measured_cost_usd_per_suggestion]
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "demo" / "Business Case - Nova Copilot.xlsx"
IN_SCOPE = {"dispute_status", "fee_explanation", "card_replacement"}

# Baseline handle times from our ticket data
by_cat = defaultdict(list)
for t in csv.DictReader(open(ROOT / "data" / "tickets.csv", encoding="utf-8")):
    by_cat[t["category"]].append(float(t["resolution_minutes"]))
all_mins = [m for v in by_cat.values() for m in v]
scope_mins = [m for c, v in by_cat.items() if c in IN_SCOPE for m in v]
aht_all = round(sum(all_mins) / len(all_mins), 2)
aht_scope = round(sum(scope_mins) / len(scope_mins), 2)
scope_share_tickets = round(len(scope_mins) / len(all_mins), 2)
cost_per_suggestion = float(sys.argv[1]) if len(sys.argv) > 1 else 0.03

head = Font(bold=True, color="FFFFFF")
fill = PatternFill("solid", fgColor="0B3A6E")
inp = PatternFill("solid", fgColor="FFF6DD")
out = PatternFill("solid", fgColor="E7F6EE")
bold = Font(bold=True)

wb = Workbook()
a = wb.active
a.title = "Assumptions"
a.append(["Input", "Value", "Unit", "Source / note"])
for c in a[1]:
    c.font, c.fill = head, fill
ASSUMPTIONS = [
    ("contacts", "Contacts per month", 45000, "contacts", "Brief"),
    ("scope", "Share in scope (disputes, fees, cards)", 0.60, "%", f"Brief (our ticket sample: {scope_share_tickets:.0%})"),
    ("growth", "Contact growth per year", 0.15, "%", "Brief"),
    ("agents", "Agents", 120, "agents", "Brief"),
    ("agent_cost", "Fully loaded cost per agent per month", 20000, "EGP", "ASSUMPTION - asked the instructor; test 15k-30k"),
    ("aht_all", "Average handle time, all contacts", aht_all, "min", "Our synthetic tickets (200)"),
    ("aht_scope", "Average handle time, in-scope contacts", aht_scope, "min", "Our synthetic tickets"),
    ("saved_min", "Minutes saved per assisted contact (base)", 2.0, "min", "ASSUMPTION; BofA EricaAssist ~1 min/call is the floor (research/competitors.md)"),
    ("adoption", "Share of in-scope contacts where agents use the copilot", 0.80, "%", "ASSUMPTION"),
    ("calls_per_contact", "Copilot drafts per contact", 1.3, "drafts", "ASSUMPTION (some retries and follow-ups)"),
    ("usd_per_draft", "Model cost per draft", cost_per_suggestion, "USD", "MEASURED in our eval run (Claude Opus 5.5 incl. guard model)"),
    ("fx", "EGP per USD", 56.12, "EGP", "CBE rate 29 Oct 2026 (research/regulation.md)"),
    ("hosting", "In-country hosting and ops per month (production)", 250000, "EGP", "ASSUMPTION - range 150k-400k until Huawei Cairo / self-host quotes"),
    ("build", "One-off build (4 people x 3 months)", 960000, "EGP", "ASSUMPTION"),
    ("deflect", "Phase 2: share of in-scope contacts resolved in the app", 0.30, "%", "ASSUMPTION; Klarna/Erica show higher, we stay conservative"),
    ("p2_start", "Phase 2 starts in month", 7, "month", "Roadmap"),
]
ref = {}
for i, (key, label, value, unit, note) in enumerate(ASSUMPTIONS, start=2):
    a.append([label, value, unit, note])
    a.cell(i, 2).fill = inp
    if unit == "%":
        a.cell(i, 2).number_format = "0%"
    ref[key] = f"Assumptions!$B${i}"
for col, w in zip("ABCD", [52, 14, 10, 80]):
    a.column_dimensions[col].width = w

m = wb.create_sheet("Model")
m.append(["Output", "Year 1 (today's volume)", "Year 2 (+15% volume)", "How it's calculated"])
for c in m[1]:
    c.font, c.fill = head, fill
R = ref
rows = [
    ("In-scope contacts per month", f"={R['contacts']}*{R['scope']}", f"={R['contacts']}*(1+{R['growth']})*{R['scope']}", "contacts x scope share"),
    ("Agent minutes per month (no copilot)", f"={R['contacts']}*{R['aht_all']}", f"={R['contacts']}*(1+{R['growth']})*{R['aht_all']}", "contacts x AHT"),
    ("Minutes per agent per month (capacity)", f"={R['contacts']}*{R['aht_all']}/{R['agents']}", "=C4", "today's minutes / 120 agents"),
    ("Agents needed without copilot", "=B3/B4", "=C3/C4", "minutes / capacity"),
    ("PHASE 1 - agent copilot", None, None, None),
    ("Minutes saved per month", f"=B2*{R['adoption']}*{R['saved_min']}", f"=C2*{R['adoption']}*{R['saved_min']}", "in-scope x adoption x minutes saved"),
    ("Agent capacity freed (FTE)", "=B7/B4", "=C7/C4", "minutes saved / capacity"),
    ("Value of freed capacity per month (EGP)", f"=B8*{R['agent_cost']}", f"=C8*{R['agent_cost']}", "FTE x cost per agent"),
    ("Hires avoided next year", None, f"=MIN(C8,C5-{R['agents']})", "growth absorbed: freed FTE, capped at the hires growth needs"),
    ("Model cost per month (EGP)", f"=B2*{R['adoption']}*{R['calls_per_contact']}*{R['usd_per_draft']}*{R['fx']}",
     f"=C2*{R['adoption']}*{R['calls_per_contact']}*{R['usd_per_draft']}*{R['fx']}", "drafts x measured cost"),
    ("Cost per assisted contact (EGP)", f"=B11/(B2*{R['adoption']})", f"=C11/(C2*{R['adoption']})", "model cost / assisted contacts"),
    ("Agent cost per contact today (EGP)", f"={R['agents']}*{R['agent_cost']}/{R['contacts']}", None, "agent payroll / contacts"),
    ("PHASE 2 - customer-facing (from month 7)", None, None, None),
    ("Contacts resolved in the app per month", f"=B2*{R['deflect']}", f"=C2*{R['deflect']}", "in-scope x deflection"),
    ("Agent capacity freed (FTE)", f"=B15*{R['aht_scope']}/B4", f"=C15*{R['aht_scope']}/C4", "deflected x in-scope AHT / capacity"),
    ("Value per month (EGP)", f"=B16*{R['agent_cost']}", f"=C16*{R['agent_cost']}", "FTE x cost per agent"),
    ("YEAR 1 TOTALS", None, None, None),
    ("Value (EGP)", f"=12*B9+(13-{R['p2_start']})*B17", None, "12 months Phase 1 + Phase 2 from start month"),
    ("Cost (EGP)", f"={R['build']}+12*({R['hosting']}+B11)", None, "build + hosting + model"),
    ("Net (EGP)", "=B19-B20", None, "value - cost"),
    ("Payback (months)", f"={R['build']}/((B19-12*({R['hosting']}+B11))/12)", None, "build / average monthly net"),
]
for label, b, c, how in rows:
    m.append([label, b, c, how])
    r = m.max_row
    if b is None and c is None:
        m.cell(r, 1).font = bold
    else:
        for col in (2, 3):
            m.cell(r, col).number_format = "#,##0.0" if "FTE" in label or "Agents" in label or "Hires" in label or "Payback" in label else "#,##0"
            if m.cell(r, col).value:
                m.cell(r, col).fill = out
for col, w in zip("ABCD", [44, 24, 24, 50]):
    m.column_dimensions[col].width = w

s = wb.create_sheet("Sensitivity")
s.append(["Value of freed capacity per month (EGP), Year 1 - minutes saved per contact vs cost per agent"])
s["A1"].font = bold
costs = [15000, 20000, 25000, 30000]
s.append(["Minutes saved \\ EGP per agent"] + costs)
for c in s[2]:
    c.font, c.fill = head, fill
for mins in [1.0, 1.5, 2.0, 2.5, 3.0]:
    row = [mins] + [f"=Model!$B$2*{R['adoption']}*{mins}/Model!$B$4*{cost}" for cost in costs]
    s.append(row)
    for col in range(2, 6):
        s.cell(s.max_row, col).number_format = "#,##0"
s.column_dimensions["A"].width = 30

p = wb.create_sheet("Budget ask")
p.append(["Internal budget request (instructor: frame as an internal team asking for budget)", "EGP", "", "Basis"])
for c in p[1]:
    c.font, c.fill = head, fill
p.append(["Year 1 budget: build + 12 months of running", f"={R['build']}+12*({R['hosting']}+Model!B11)", "", "Assumptions + Model sheets"])
p.append(["  of which one-off build", f"={R['build']}", "", "4 people x 3 months"])
p.append(["  of which running cost per month", f"={R['hosting']}+Model!B11", "", "in-country hosting + measured model cost"])
p.append(["All-in cost per assisted contact", f"=({R['hosting']}+Model!B11)/(Model!B2*{R['adoption']})", "", "running cost / assisted contacts"])
p.append(["Agent cost per contact today", "=Model!B13", "", "for comparison"])
p.append(["Year 1 value", "=Model!B19", "", "freed agent capacity, Phase 1 + Phase 2"])
p.append(["Year 1 net", "=Model!B21", "", "value - budget"])
p.append([])
p.append(["Build vs buy: what the same 120 seats would cost from a vendor", "EGP / month", "", "Why we still build"])
for c in p[10]:
    c.font, c.fill = head, fill
p.append(["Intercom Copilot, $29 / agent / month", f"=29*{R['fx']}*{R['agents']}", "", "No Egyptian Arabic or Franco-Arabic; hosted abroad (bank secrecy blocks customer data)"])
p.append(["Zendesk Copilot, $50 / agent / month", f"=50*{R['fx']}*{R['agents']}", "", "Same; also needs Zendesk as the helpdesk"])
p.append(["Microsoft D365 Contact Center, $110 / user / month", f"=110*{R['fx']}*{R['agents']}", "", "Full platform replacement, not just a copilot"])
p.append(["Phase 2 benchmark: Intercom Fin, $0.99 / resolution", f"=0.99*{R['fx']}*Model!C15", "", "Customer-facing; offshore hosting"])
p.append(["Source: research/competitors.md, list prices checked 30 Oct 2026, USD 1 = EGP 56.12"])
for r in range(2, 15):
    p.cell(r, 2).number_format = "#,##0"
for col, w in zip("ABCD", [62, 18, 2, 90]):
    p.column_dimensions[col].width = w

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
wb.save(OUT)
print(f"wrote {OUT}")
print(f"baseline AHT all={aht_all} min, in-scope={aht_scope} min, in-scope share in tickets={scope_share_tickets}")
