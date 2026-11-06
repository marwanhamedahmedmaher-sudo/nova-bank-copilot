"""Control room (dev mode): the settings an AI PM or engineer can change live, and what reads them.

Guardrails, models and analytics assumptions live in app/logs/control.json (demo state, not committed;
"Restore defaults" deletes it). The golden set is the real evals/golden_set.jsonl, so an edit there is
an edit to the test set itself. Every change is written to the audit log as a config_change.
"""
import json
import os
import re
import subprocess
import sys
import threading
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = Path(__file__).resolve().parent / "logs" / "control.json"
GOLDEN = ROOT / "evals" / "golden_set.jsonl"
RESULTS = ROOT / "evals" / "results"
EVAL_LOG = Path(__file__).resolve().parent / "logs" / "eval_run.log"

# ---- guardrails -------------------------------------------------------------------------------
# Built-in checks from guards.check_draft and copilot.suggest_for. Locked ones are bank secrecy or
# "a human decides" rules: the panel can see them, not switch them off.
BUILTIN = [
    ("Every claim has a source", "output", "Each fact in the draft needs at least one citation.", False),
    ("Sources exist and quotes match them", "output", "Every cited quote must appear in the cited policy or record.", False),
    ("Only this customer's records", "output", "Citations may only point to the verified customer's records.", True),
    ("Numbers match the sources", "output", "Every amount and date in the reply traces to a cited source.", False),
    ("Reply is clean text in Arabic or Latin script", "output", "Catches generation glitches in other scripts.", False),
    ("No other customer's data", "output", "No other customer's name or record ID in the draft.", True),
    ("Current policy versions", "output", "Flags a draft that cites the superseded fee schedule (POL-02).", False),
    ("No promise of an outcome (second model)", "output", "A second, smaller model checks the reply never promises a refund, waiver or dispute result.", False),
    ("Actions wait for a human", "output", "Approvers come from Nova's policy table, never from the model.", True),
]
INPUT_FLAGS = [
    ("prompt_injection", "Prompt injection in the message", "Instruction-like text aimed at the copilot (\"ignore your rules\").", False),
    ("third_party_request", "Asks about someone else", "Relatives or other customers' IDs (POL-17 §2).", True),
    ("approval_request", "Asks for a refund or approval", "Marks the case high risk so a human decides.", False),
    ("card_or_fraud", "Lost card or fraud", "Lost or stolen card or fraud: always high risk.", False),
]
DEFAULT_SEVERITY = {"Current policy versions": "warn"}

DEFAULTS = {
    "guardrails": {},   # name -> {"enabled": bool, "severity": "block"|"warn"}
    "custom": [],       # [{id, name, phrases, target: "reply"|"message", severity, enabled}]
    "models": [
        {"id": os.getenv("COPILOT_MODEL", "claude-opus-5-5"), "label": "Claude Opus 5.5", "enabled": True, "role": "primary",
         "prices": [4.0, 20.0, 5.0, 0.20]},
        {"id": "claude-haiku-5-5", "label": "Claude Haiku 5.5", "enabled": True, "role": "backup",
         "prices": [0.10, 0.50, 0.125, 0.01]},
    ],
    "simulate_outage": False,
    "analytics": {"saved_chat_min": 2.0, "contacts_per_month": 45000},
}

_lock = threading.Lock()


def state():
    if PATH.exists():
        try:
            saved = json.loads(PATH.read_text(encoding="utf-8"))
            return {**deepcopy(DEFAULTS), **saved}
        except ValueError:
            pass
    return deepcopy(DEFAULTS)


def save(s, what, **detail):
    from . import copilot  # late import: copilot imports this module
    with _lock:
        PATH.parent.mkdir(exist_ok=True)
        PATH.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    copilot.audit("config_change", what=what, **detail)
    return s


def reset():
    if PATH.exists():
        PATH.unlink()
    from . import copilot
    copilot.audit("config_change", what="restore_defaults")


def guardrail_setting(name, s=None):
    s = s or state()
    locked = {n for n, _, _, lk in BUILTIN if lk} | {k for k, _, _, lk in INPUT_FLAGS if lk}
    g = s["guardrails"].get(name, {})
    if name in locked:
        return {"enabled": True, "severity": DEFAULT_SEVERITY.get(name, "block"), "locked": True}
    return {"enabled": g.get("enabled", True), "severity": g.get("severity", DEFAULT_SEVERITY.get(name, "block")), "locked": False}


def set_guardrail(name, enabled=None, severity=None):
    known = {n for n, *_ in BUILTIN} | {k for k, *_ in INPUT_FLAGS}
    if name not in known:
        raise KeyError(name)
    if guardrail_setting(name)["locked"]:
        raise PermissionError(f"{name} is locked: bank secrecy and human approval can't be switched off")
    if severity not in (None, "block", "warn"):
        raise ValueError("severity must be block or warn")
    s = state()
    g = s["guardrails"].setdefault(name, {})
    if enabled is not None:
        g["enabled"] = bool(enabled)
    if severity is not None:
        g["severity"] = severity
    return save(s, "guardrail", name=name, enabled=enabled, severity=severity)


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "rule"


def upsert_custom(rule):
    name = (rule.get("name") or "").strip()
    phrases = [p.strip() for p in rule.get("phrases", []) if p and p.strip()]
    if not name or not phrases:
        raise ValueError("a guardrail needs a name and at least one phrase")
    if rule.get("target", "reply") not in ("reply", "message") or rule.get("severity", "block") not in ("block", "warn"):
        raise ValueError("target must be reply or message; severity block or warn")
    s = state()
    rid = rule.get("id") or _slug(name)
    others = [r for r in s["custom"] if r["id"] != rid]
    new = {"id": rid, "name": name, "phrases": phrases, "target": rule.get("target", "reply"),
           "severity": rule.get("severity", "block"), "enabled": bool(rule.get("enabled", True))}
    s["custom"] = others + [new]
    save(s, "custom_guardrail", id=rid, rule=new)
    return new


def delete_custom(rid):
    s = state()
    if not any(r["id"] == rid for r in s["custom"]):
        raise KeyError(rid)
    s["custom"] = [r for r in s["custom"] if r["id"] != rid]
    save(s, "custom_guardrail_deleted", id=rid)


def input_flags(flags):
    """Drop input flags the control room switched off (locked ones always stay)."""
    s = state()
    return [f for f in flags if guardrail_setting(f, s)["enabled"]]


def commitment_check_on():
    return guardrail_setting("No promise of an outcome (second model)")["enabled"]


def _hit(phrases, text):
    low = text.lower()
    return [p for p in phrases if p.lower() in low]


def apply_checks(checks, reply_texts=None, message=""):
    """Add the custom phrase guardrails, then apply on/off and block/warn from the control room.
    A switched-off check stays visible in dev mode, marked off, and never blocks."""
    s = state()
    out = []
    for c in checks:
        g = guardrail_setting(c["name"], s)
        c = {**c, "severity": g["severity"]}
        if not g["enabled"]:
            c = {**c, "severity": "off", "detail": ("off in the control room" + ("" if c["passed"] else f" (would have failed: {c['detail']})")),
                 "passed": True}
        out.append(c)
    if reply_texts is None:  # late checks (second model, approvers): no custom rules to add again
        return out
    reply = " ".join(reply_texts)
    for r in s["custom"]:
        if not r["enabled"]:
            continue
        hits = _hit(r["phrases"], reply if r["target"] == "reply" else message)
        where = "reply" if r["target"] == "reply" else "customer message"
        out.append(dict(name=r["name"], passed=not hits, severity=r["severity"], custom=True,
                        detail=f"{where} contains: {', '.join(hits)}" if hits else f"no listed phrase in the {where}"))
    return out


def guardrails_view(evs):
    """Everything the Guardrails screen lists, with how often each one failed in the audit log."""
    caught = {}
    for e in evs:
        if e.get("event") == "suggestion":
            for c in e.get("checks", []):
                if not c.get("passed"):
                    caught[c["name"]] = caught.get(c["name"], 0) + 1
            for f in e.get("input_flags", []):
                caught[f] = caught.get(f, 0) + 1
    s = state()
    out = [{"key": n, "name": n, "kind": "output", "description": d, "caught": caught.get(n, 0), **guardrail_setting(n, s)}
           for n, _, d, _ in BUILTIN]
    out += [{"key": k, "name": label, "kind": "input", "description": d, "caught": caught.get(k, 0), **guardrail_setting(k, s)}
            for k, label, d, _ in INPUT_FLAGS]
    out += [{"key": r["id"], "kind": "custom", "description": f"Phrases in the {r['target']}: " + ", ".join(r["phrases"]),
             "caught": caught.get(r["name"], 0), "locked": False, **r} for r in s["custom"]]
    return out


# ---- models -----------------------------------------------------------------------------------
def models():
    return state()["models"]


def model_chain():
    """Enabled primary first, then the enabled backup. The copilot tries them in this order."""
    ms = [m for m in models() if m["enabled"]]
    return [m["id"] for m in sorted(ms, key=lambda m: {"primary": 0, "backup": 1}.get(m.get("role"), 9))
            if m.get("role") in ("primary", "backup")]


def price(model_id):
    for m in models():
        if m["id"] == model_id:
            return tuple(m["prices"])
    return tuple(DEFAULTS["models"][0]["prices"])


def outage():
    return state()["simulate_outage"]


def set_outage(on):
    s = state()
    s["simulate_outage"] = bool(on)
    save(s, "simulate_outage", on=bool(on))


def upsert_model(m):
    mid = (m.get("id") or "").strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9.\-]{2,60}", mid):
        raise ValueError("model id looks like claude-sonnet-5-5")
    prices = [float(x) for x in m.get("prices", [])]
    if len(prices) != 4 or any(p < 0 for p in prices):
        raise ValueError("prices: input, output, cache write, cache read in USD per million tokens")
    s = state()
    old = next((x for x in s["models"] if x["id"] == mid), None)
    new = {"id": mid, "label": (m.get("label") or mid).strip(), "enabled": bool(m.get("enabled", True)),
           "role": old["role"] if old else None, "prices": prices}
    s["models"] = [new if x["id"] == mid else x for x in s["models"]] if old else s["models"] + [new]
    save(s, "model", model=new)
    return new


def set_model(mid, role=None, enabled=None):
    """role: primary | backup | none. Making a model primary or backup takes that role from whoever had it."""
    s = state()
    target = next((x for x in s["models"] if x["id"] == mid), None)
    if target is None:
        raise KeyError(mid)
    if role is not None:
        if role not in ("primary", "backup", "none"):
            raise ValueError("role must be primary, backup or none")
        if role != "none":
            for x in s["models"]:
                if x.get("role") == role:
                    x["role"] = None
        target["role"] = None if role == "none" else role
        if role != "none":
            target["enabled"] = True
    if enabled is not None:
        target["enabled"] = bool(enabled)
    if not any(x["enabled"] and x.get("role") == "primary" for x in s["models"]):
        raise ValueError("keep one enabled primary model, or the copilot has nothing to draft with")
    save(s, "model_role", id=mid, role=role, enabled=enabled)


def delete_model(mid):
    s = state()
    target = next((x for x in s["models"] if x["id"] == mid), None)
    if target is None:
        raise KeyError(mid)
    if target.get("role") == "primary":
        raise ValueError("make another model primary before removing this one")
    s["models"] = [x for x in s["models"] if x["id"] != mid]
    save(s, "model_deleted", id=mid)


# ---- golden sets (the "golden rules") ------------------------------------------------------------
# The base set is evals/golden_set.jsonl ("Golden set v1"). Uploaded batches live next to it in
# evals/golden_sets/<id>.jsonl with a .meta.json (name, who uploaded it, when). The evals run on the active set.
GOLDEN_FIELDS = ("id", "type", "intent", "customer_id", "language", "question", "benchmark_answer", "benchmark_location",
                 "expect_answer_found", "must_flag", "must_suggest", "notes")
TYPES = {"grounded": "G", "not_in_sources": "N", "safety": "S"}  # type -> ID prefix
INTENTS = ("dispute_status", "fee_explanation", "card_replacement", "other")
LANGS = ("en", "ar", "arz", "franco")
BASE_SET = "golden_set"


def _sets_dir():
    return GOLDEN.parent / "golden_sets"


def _set_path(set_id):
    if set_id in (None, BASE_SET):
        return GOLDEN
    if not re.fullmatch(r"[a-z0-9-]{1,50}", set_id or "") or not (_sets_dir() / f"{set_id}.jsonl").exists():
        raise KeyError(set_id)
    return _sets_dir() / f"{set_id}.jsonl"


def active_set():
    sid = state().get("active_set", BASE_SET)
    try:
        _set_path(sid)
        return sid
    except KeyError:
        return BASE_SET


def golden_sets():
    out = [{"id": BASE_SET, "name": "Golden set v1", "by": "Nova team", "at": None, "count": len(golden(BASE_SET))}]
    for p in (sorted(_sets_dir().glob("*.meta.json")) if _sets_dir().exists() else []):
        meta = json.loads(p.read_text(encoding="utf-8"))
        out.append({**meta, "count": len(golden(meta["id"]))})
    act = active_set()
    return [{**s, "active": s["id"] == act} for s in out]


def set_active(set_id):
    _set_path(set_id)
    s = state()
    s["active_set"] = set_id
    save(s, "golden_set_active", set=set_id)


def delete_set(set_id):
    if set_id == BASE_SET:
        raise ValueError("the base golden set can't be deleted")
    _set_path(set_id).unlink()
    (_sets_dir() / f"{set_id}.meta.json").unlink(missing_ok=True)
    if state().get("active_set") == set_id:
        s = state()
        s["active_set"] = BASE_SET
        save(s, "golden_set_active", set=BASE_SET)
    from . import copilot
    copilot.audit("config_change", what="golden_set_deleted", set=set_id)


def golden(set_id=None):
    p = _set_path(set_id or active_set())
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _write_golden(cases, set_id):
    p = _set_path(set_id)
    tmp = p.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")
    tmp.replace(p)


def _clean_case(case, existing):
    """Validate one golden case and give it an ID if it has none. Raises ValueError with a plain reason."""
    from . import store
    c = {k: case.get(k) for k in GOLDEN_FIELDS}
    if not str(c["question"] or "").strip() or not str(c["benchmark_answer"] or "").strip():
        raise ValueError("a golden case needs a question and a benchmark answer")
    if c["customer_id"] not in store.customers():
        raise ValueError(f"unknown customer {c['customer_id']!r}: use one of the synthetic customers (C001...)")
    if c["language"] not in LANGS:
        raise ValueError(f"language {c['language']!r} must be one of {', '.join(LANGS)}")
    if c["intent"] not in INTENTS:
        raise ValueError(f"intent {c['intent']!r} must be one of {', '.join(INTENTS)}")
    if c["type"] not in TYPES:
        raise ValueError(f"type {c['type']!r} must be one of {', '.join(TYPES)}")
    for k in ("question", "benchmark_answer"):
        c[k] = str(c[k]).strip()
    c["benchmark_location"] = str(c["benchmark_location"] or "").strip()
    found = c["expect_answer_found"]
    c["expect_answer_found"] = found if isinstance(found, bool) else str(found).strip().lower() not in ("false", "no", "0")
    c["must_flag"] = [x for x in (c["must_flag"] or []) if x]
    c["must_suggest"] = [x for x in (c["must_suggest"] or []) if x]
    c["notes"] = str(c["notes"] or "").strip()
    if not c["notes"]:
        c.pop("notes")
    if not c["id"]:
        pre = TYPES[c["type"]]
        nums = [int(m.group(1)) for x in existing if (m := re.fullmatch(pre + r"(\d+)", x["id"]))]
        c["id"] = f"{pre}{max(nums, default=0) + 1:02d}"
    return c


def upsert_golden(case, set_id=None):
    set_id = set_id or active_set()
    cases = golden(set_id)
    is_new = not case.get("id")
    if not is_new and not any(x["id"] == case["id"] for x in cases):
        raise KeyError(case["id"])
    c = _clean_case(case, cases)
    cases = cases + [c] if is_new else [c if x["id"] == c["id"] else x for x in cases]
    _write_golden(cases, set_id)
    from . import copilot
    copilot.audit("config_change", what="golden_added" if is_new else "golden_edited", id=c["id"], set=set_id)
    return c


def delete_golden(cid, set_id=None):
    set_id = set_id or active_set()
    cases = golden(set_id)
    if not any(x["id"] == cid for x in cases):
        raise KeyError(cid)
    _write_golden([x for x in cases if x["id"] != cid], set_id)
    from . import copilot
    copilot.audit("config_change", what="golden_deleted", id=cid, set=set_id)


# ---- spreadsheets: download and upload ------------------------------------------------------------
GOLDEN_SHEET = ["id", "type", "intent", "customer_id", "language", "question", "benchmark_answer", "benchmark_location",
                "expect_answer_found", "must_flag", "must_suggest", "notes"]
GOLDEN_REQUIRED = ["type", "intent", "customer_id", "language", "question", "benchmark_answer"]
EVAL_SHEET = ["ID", "Customer message", "Benchmark answer", "Copilot reply (English)", "Pass/Fail", "Failed checks",
              "Judge's reason", "Run", "Notes"]


def _xlsx(title, header, rows, widths):
    from io import BytesIO
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook()
    ws = wb.active
    ws.title = title
    ws.append(header)
    for c in ws[1]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="0B3A6E")
    for r in rows:
        ws.append(r)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    ws.freeze_panes = "A2"
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def golden_xlsx(set_id=None):
    rows = [[c.get("id"), c.get("type"), c.get("intent"), c.get("customer_id"), c.get("language"), c.get("question"),
             c.get("benchmark_answer"), c.get("benchmark_location"), "TRUE" if c.get("expect_answer_found", True) else "FALSE",
             ", ".join(c.get("must_flag", [])), ", ".join(c.get("must_suggest", [])), c.get("notes", "")] for c in golden(set_id)]
    return _xlsx("Golden set", GOLDEN_SHEET, rows, [7, 14, 16, 11, 9, 45, 50, 22, 12, 22, 24, 40])


def evals_xlsx():
    ev = evals_view()
    rows = []
    for c in golden():
        r = ev["latest"].get(c["id"]) or {}
        rows.append([c["id"], c["question"], c["benchmark_answer"], r.get("reply_in_english", ""),
                     "" if not r else ("Pass" if r["passed"] else "Fail"), "; ".join(r.get("failed", [])) or r.get("error", ""),
                     r.get("reason", ""), r.get("stamp", "not run yet"), ""])
    return _xlsx("Eval results", EVAL_SHEET, rows, [7, 40, 40, 45, 9, 35, 40, 15, 40])


def _read_sheet(filename, data):
    """Rows as dicts keyed by the first row. Accepts .xlsx or .csv."""
    import csv
    from io import BytesIO, StringIO
    if filename.lower().endswith(".csv"):
        rows = list(csv.reader(StringIO(data.decode("utf-8-sig"))))
    else:
        from openpyxl import load_workbook
        try:
            ws = load_workbook(BytesIO(data), read_only=True, data_only=True).active
            rows = [["" if v is None else str(v) for v in r] for r in ws.iter_rows(values_only=True)]
        except Exception:
            raise ValueError("that file isn't a readable .xlsx or .csv")
    rows = [r for r in rows if any(str(v).strip() for v in r)]
    if not rows:
        raise ValueError("the file is empty")
    header = [str(h).strip() for h in rows[0]]
    return header, [dict(zip(header, r)) for r in rows[1:]]


def _split(v):
    return [x.strip() for x in re.split(r"[,;]", str(v or "")) if x.strip()]


def upload_golden(filename, data, name, by):
    """A new named golden set from a spreadsheet. Every row must be valid, or nothing is saved."""
    name, by = (name or "").strip(), (by or "").strip()
    if not name or not by:
        raise ValueError("name the batch and say who is uploading it")
    header, rows = _read_sheet(filename, data)
    missing = [h for h in GOLDEN_REQUIRED if h not in header]
    if missing:
        raise ValueError(f"missing columns: {', '.join(missing)} (download a set to get the template)")
    cases, errors = [], []
    for i, r in enumerate(rows, start=2):
        r = {**r, "must_flag": _split(r.get("must_flag")), "must_suggest": _split(r.get("must_suggest")),
             "id": str(r.get("id") or "").strip() or None, "expect_answer_found": r.get("expect_answer_found") or "TRUE"}
        try:
            c = _clean_case(r, cases)
            if any(x["id"] == c["id"] for x in cases):
                raise ValueError(f"ID {c['id']} appears twice")
            cases.append(c)
        except ValueError as e:
            errors.append(f"row {i}: {e}")
    if errors:
        raise ValueError("nothing was uploaded. " + " | ".join(errors[:8]) + (f" | and {len(errors) - 8} more" if len(errors) > 8 else ""))
    if not cases:
        raise ValueError("no cases in the file")
    from datetime import datetime, timezone
    base = _slug(name)
    sid, n = base, 2
    while sid == BASE_SET or (_sets_dir() / f"{sid}.jsonl").exists():
        sid, n = f"{base}-{n}", n + 1
    _sets_dir().mkdir(parents=True, exist_ok=True)
    (_sets_dir() / f"{sid}.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")
    meta = {"id": sid, "name": name, "by": by, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "file": filename}
    (_sets_dir() / f"{sid}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    from . import copilot
    copilot.audit("config_change", what="golden_set_uploaded", set=sid, name=name, by=by, file=filename, count=len(cases))
    return {**meta, "count": len(cases)}


def _notes_path():
    return GOLDEN.parent / "results" / "notes.jsonl"


def eval_notes():
    p = _notes_path()
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def upload_eval_notes(filename, data, by):
    """Reads the Notes column of a downloaded eval sheet; every non-empty note is logged with who and when."""
    by = (by or "").strip()
    if not by:
        raise ValueError("say who is uploading the notes")
    header, rows = _read_sheet(filename, data)
    if "ID" not in header or "Notes" not in header:
        raise ValueError("the sheet needs the ID and Notes columns (download the eval results to get it)")
    from datetime import datetime, timezone
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    known = {c["id"] for s in golden_sets() for c in golden(s["id"])}
    new = [{"case_id": str(r["ID"]).strip(), "note": str(r["Notes"]).strip(), "by": by, "at": at, "run": str(r.get("Run") or ""),
            "file": filename} for r in rows if str(r.get("Notes") or "").strip() and str(r.get("ID") or "").strip() in known]
    if not new:
        raise ValueError("no notes found: write them in the Notes column next to a case ID")
    _notes_path().parent.mkdir(exist_ok=True)
    with open(_notes_path(), "a", encoding="utf-8") as f:
        for n in new:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
    from . import copilot
    copilot.audit("eval_notes_uploaded", by=by, file=filename, count=len(new), cases=[n["case_id"] for n in new])
    return {"count": len(new), "by": by, "at": at}


# ---- eval runs --------------------------------------------------------------------------------
_proc = {"p": None, "ids": [], "set": None}


def _runs():
    return sorted(RESULTS.glob("run *.json"), key=lambda p: p.stem)


def evals_view():
    """Run history (newest first), the latest result per case across all runs, and the review notes."""
    history, latest = [], {}
    for p in _runs():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            continue
        stamp = p.stem[4:]
        history.append({"stamp": stamp, "golden_set": data["summary"].get("golden_set", "Golden set v1"),
                        **{k: data["summary"].get(k) for k in
                           ("passed", "total", "errors", "Helpfulness", "Honesty", "Harmlessness", "Overall 3H", "avg_cost_usd_per_answer")},
                        "model": next((r["result"].get("model") for r in data["runs"] if r.get("result")), None)})
        for r in data["runs"]:
            cid = r["case"]["id"]
            if r.get("error"):
                latest[cid] = {"stamp": stamp, "passed": False, "error": r["error"]}
                continue
            latest[cid] = {"stamp": stamp, "passed": r["passed"], "status": r["result"]["status"],
                           "failed": [row[1] for row in r["rows"] if row[2] == "No"],
                           "reason": r["verdict"].get("overall_reason", ""),
                           "reply_in_english": r["result"].get("reply_in_english", ""),
                           "model": r["result"].get("model")}
    notes = {}
    for n in eval_notes():
        notes.setdefault(n["case_id"], []).append(n)
    p = _proc["p"]
    running = p is not None and p.poll() is None
    return {"history": history[::-1], "latest": latest, "notes": notes, "running": running,
            "running_ids": _proc["ids"] if running else [], "running_set": _proc["set"] if running else None,
            "last_exit": None if p is None or running else p.returncode,
            "active_set": active_set(), "cases": golden()}


def run_evals(ids):
    """Runs the real eval runner on the active golden set, in its own process
    (the runner pins the eval date, which must not leak into the console)."""
    p = _proc["p"]
    if p is not None and p.poll() is None:
        raise RuntimeError("an eval run is already going")
    sid = active_set()
    known = {c["id"] for c in golden(sid)}
    ids = [i for i in ids if i in known]
    name = next(s["name"] for s in golden_sets() if s["id"] == sid)
    EVAL_LOG.parent.mkdir(exist_ok=True)
    log = open(EVAL_LOG, "w", encoding="utf-8")
    _proc["p"] = subprocess.Popen([sys.executable, "-m", "evals.run_evals", *ids], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                  env={**os.environ, "PYTHONUTF8": "1", "GOLDEN_SET": str(_set_path(sid)), "GOLDEN_SET_NAME": name})
    _proc["ids"], _proc["set"] = ids or sorted(known), name
    from . import copilot
    copilot.audit("config_change", what="eval_run", ids=_proc["ids"], set=sid)
    return _proc["ids"]
