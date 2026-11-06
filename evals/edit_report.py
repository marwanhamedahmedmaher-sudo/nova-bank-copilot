"""Agent edit report: how much of each drafted reply the agents changed before sending it, or when flagging it as wrong.

    .venv\\Scripts\\python -m evals.edit_report [YYYY-MM-DD]

Reads the audit log (agent_send and agent_flag events from the console) and writes
"Agent Edits - Nova Copilot <stamp>.xlsx" to evals/results/. The optional date keeps only events from that day on.
The changed share is word-level: 0% means sent exactly as drafted, 100% means fully rewritten. Averaged over every
reply an agent sent or corrected, it is the copilot's error rate as the agents see it.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from app import copilot

RESULTS = Path(__file__).resolve().parent / "results"


def load(since=None):
    if not copilot.LOG.exists():
        return []
    events = [json.loads(line) for line in copilot.LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [e for e in events if "changed_pct" in e and e["event"] in ("agent_send", "agent_flag")
            and (not since or e["ts"][:10] >= since)]


def summarise(events):
    sends = [e for e in events if e["event"] == "agent_send"]
    flags = [e for e in events if e["event"] == "agent_flag"]
    avg = lambda xs: round(sum(e["changed_pct"] for e in xs) / len(xs), 1) if xs else 0.0
    return {
        "replies_reviewed": len(events),
        "error_pct": avg(events),  # share of the drafted text agents changed, across everything they sent or corrected
        "replies_sent": len(sends),
        "sent_as_drafted_pct": round(100 * sum(not e["edited"] for e in sends) / len(sends), 1) if sends else 0.0,
        "avg_changed_pct_sent": avg(sends),
        "flags_with_correction": len(flags),
        "avg_changed_pct_flagged": avg(flags),
    }


def write_xlsx(events, summary, stamp):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    head, fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="0B3A6E")
    wrap = Alignment(wrap_text=True, vertical="top")
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Nova Bank Support Copilot - Agent Edits"]); ws["A1"].font = Font(bold=True, size=14)
    ws.append(["How much of each drafted reply agents changed before sending it, or when flagging it as wrong. "
               "Word-level: 0% = sent as drafted, 100% = fully rewritten."])
    ws.append([])
    rows = [("Replies sent or corrected", summary["replies_reviewed"]),
            ("Error rate: average share of the draft changed", f"{summary['error_pct']}%"),
            ("Replies sent", summary["replies_sent"]),
            ("Sent exactly as drafted", f"{summary['sent_as_drafted_pct']}%"),
            ("Average share changed before sending", f"{summary['avg_changed_pct_sent']}%"),
            ("Flags with a corrected reply", summary["flags_with_correction"]),
            ("Average share changed in flagged corrections", f"{summary['avg_changed_pct_flagged']}%")]
    for label, value in rows:
        ws.append([label, value])
        ws.cell(ws.max_row, 1).font = Font(bold=True)
    ws.column_dimensions["A"].width = 48
    ws.column_dimensions["B"].width = 16

    ws = wb.create_sheet("Edits")
    cols = ["Time (UTC)", "Case", "Event", "Changed %", "Agent note", "Drafted reply", "Agent's version"]
    ws.append(cols)
    for cell in ws[1]:
        cell.font, cell.fill = head, fill
    for e in events:
        ws.append([e["ts"][:19].replace("T", " "), e["case_id"], "sent" if e["event"] == "agent_send" else "flagged",
                   e["changed_pct"], e.get("note", ""), e["drafted_reply"], e["final_reply"]])
        for cell in ws[ws.max_row]:
            cell.alignment = wrap
    for col, w in zip("ABCDEFG", (19, 10, 9, 11, 30, 60, 60)):
        ws.column_dimensions[col].width = w
    path = RESULTS / f"Agent Edits - Nova Copilot {stamp}.xlsx"
    RESULTS.mkdir(exist_ok=True)
    wb.save(path)
    return path


if __name__ == "__main__":
    events = load(sys.argv[1] if len(sys.argv) > 1 else None)
    summary = summarise(events)
    print(json.dumps(summary, indent=2))
    if events:
        print("wrote", write_xlsx(events, summary, datetime.now().strftime("%Y-%m-%d %H%M")))
    else:
        print("No agent sends or flags with edits in the audit log yet.")
