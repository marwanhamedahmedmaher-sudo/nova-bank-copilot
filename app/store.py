"""Data access. The only way to read customer records is through CustomerScope,
which is bound to one verified customer and cannot see anyone else (POL-17 §5)."""
import csv
import json
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
SECTION_RE = re.compile(r"^## §(\d+) (.+)$", re.M)


def _read_csv(name):
    with open(DATA / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


@lru_cache
def customers():
    return {c["customer_id"]: c for c in _read_csv("customers.csv")}


@lru_cache
def _transactions():
    return _read_csv("transactions.csv")


@lru_cache
def _disputes():
    return _read_csv("disputes.csv")


@lru_cache
def cases():
    return {c["case_id"]: c for c in json.loads((DATA / "cases.json").read_text(encoding="utf-8"))}


@lru_cache
def policies():
    """{"POL-04": {"title", "header", "status", "sections": {"2": {"title", "text"}}, "raw"}}"""
    out = {}
    for path in sorted((DATA / "policies").glob("POL-*.md")):
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        title = lines[0].split("·", 1)[1].strip()
        header = lines[1].strip()
        sections = {}
        parts = SECTION_RE.split(raw)
        # parts = [preamble, num, title, body, num, title, body, ...]
        for i in range(1, len(parts), 3):
            sections[parts[i]] = {"title": parts[i + 1].strip(), "text": parts[i + 2].strip()}
        out[path.stem] = {"title": title, "header": header, "sections": sections, "raw": raw,
                          "superseded": "SUPERSEDED" in header}
    return out


def policy_section(source_id):
    """'POL-04 §2' -> section text, or None."""
    m = re.fullmatch(r"\s*(POL-\d{2})\s*§\s*(\d+)\s*", source_id)
    if not m:
        return None
    sec = policies().get(m.group(1), {}).get("sections", {}).get(m.group(2))
    return sec and f"{sec['title']}. {sec['text']}"


def policies_prompt_text():
    """All policies as one stable block for the cached system prompt."""
    return "\n\n".join(p["raw"].strip() for p in policies().values())


class CustomerScope:
    """Everything the copilot may know about one customer. Built server-side from the case,
    never from anything the model or the customer message asks for."""

    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.customer = customers()[customer_id]
        self.transactions = [t for t in _transactions() if t["customer_id"] == customer_id]
        self.disputes = [d for d in _disputes() if d["customer_id"] == customer_id]

    @property
    def first_name(self):
        return self.customer["name"].split()[0]

    def profile_line(self):
        """Masked profile: no name, phone or national ID reaches the model (POL-20 §4)."""
        c = self.customer
        overdraft = "planned overdraft facility" if int(c["planned_overdraft_limit"]) else (
            "opted in to standard overdraft coverage" if c["overdraft_opt_in"] == "True" else "no overdraft coverage")
        return (f"PROFILE | plan {c['plan']} | tenure {c['tenure_months']} months | city {c['city']} | "
                f"salary transfer {'yes' if c['salary_transfer'] == 'True' else 'no'} | "
                f"average balance last month EGP {c['avg_balance_last_month']} | {overdraft} | "
                f"card ending {c['card_last4']} status {c['card_status']} expiry {c['card_expiry']}")

    def record_lines(self):
        """{source_id: one-line text}. These lines are both what the model sees and what citations are checked against."""
        lines = {"PROFILE": self.profile_line()}
        for t in self.transactions:
            note = f" | note: {t['note']}" if t["note"] else ""
            lines[t["txn_id"]] = (f"{t['txn_id']} | {t['date']} | {t['merchant']} | EGP {float(t['amount']):.2f} | "
                                  f"{t['category']} | {t['status']} | card {t['card_last4']}{note}")
        for d in self.disputes:
            lines[d["dispute_id"]] = (f"{d['dispute_id']} | transaction {d['txn_id']} | {d['merchant']} | EGP {float(d['amount']):.2f} | "
                                      f"reason: {d['reason']} | opened {d['opened']} | stage: {d['stage']} | "
                                      f"last update {d['last_update']} | provisional credit EGP {float(d['provisional_credit']):.2f} | "
                                      f"expected resolution by {d['expected_resolution_by']} | notes: {d['notes'] or 'none'}")
        return lines

    def owns(self, source_id):
        return source_id in self.record_lines()


def all_record_ids():
    """Every transaction and dispute ID in the bank, used only by the leak scan."""
    return {t["txn_id"]: t["customer_id"] for t in _transactions()} | {d["dispute_id"]: d["customer_id"] for d in _disputes()}
