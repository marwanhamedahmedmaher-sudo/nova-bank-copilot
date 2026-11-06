"""Deterministic guardrails around the model. Input checks run before the call;
output checks run on the draft before an agent ever sees it."""
import re
from difflib import SequenceMatcher

from . import store

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
# Franco-Arabic uses digits as letters (3ala, 7aga), so a number touching a Latin letter is not a number.
NUM_RE = re.compile(r"(?<![A-Za-z0-9.])\d+(?:\.\d+)?(?![A-Za-z0-9])")

INJECTION = re.compile(
    r"ignore (all |your |previous |the )*(instructions|rules)|system override|admin mode|developer mode|"
    r"you are now|act as|jailbreak|forget (your|all|the) (rules|instructions)|"
    r"تجاهل|انسى (التعليمات|القواعد)|وضع المسؤول|ignore el rules|sibak men el rules", re.I)
THIRD_PARTY = re.compile(
    r"\b(my )?(wife|husband|brother|sister|mother|father|son|daughter|friend|colleague)('s)?\b|"
    r"مراتي|زوجتي|جوزي|زوجي|أخويا|اخويا|أختي|اختي|ماما|بابا|ابني|بنتي|"
    r"\b(mrati|merati|mra2ti|mratee|gozi|gooz|goozha|gozha|akhoya|okhti|mama|baba|ebni|benti)\b", re.I)
APPROVAL_ASK = re.compile(
    r"approve|\brefund|money back|waive|remove the fee|reverse the|"
    r"وافق|اعتمد|رجعلي فلوسي|رجّعلي|ارجعلي|الغي الرسوم|استرداد|استرجاع|"
    r"e3tamed|wafe2|rag3ly|ragga3ly|raga3ly|shil el fees|elghi", re.I)
# Lost or stolen cards and fraud: code forces these to high risk even if the model suggests no action
CARD_OR_FRAUD = re.compile(
    r"\b(lost|stolen|stole|missing|fraud|scam|hacked|unauthori[sz]ed)\b|"
    r"فقدت|ضاعت|ضايعة|اتسرقت|سرقت|مسروقة|احتيال|نصب|"
    r"\b(da3et|da3it|etsara2et|etsara2it|sara2oha|ensara2|na9ab|nasab)\b", re.I)
# Latin, Arabic, digits, punctuation and currency/arrow symbols; anything else in a reply is a generation glitch
UNEXPECTED_SCRIPT = re.compile(r"[^\x00-\x7F -ɏ؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿ -⁯₠-⃏←-⇿]")
PII_PATTERNS = [
    (re.compile(r"\b(?:\d[ -]?){15}\d\b"), "[CARD_NUMBER]"),
    (re.compile(r"\b[23]\d{13}\b"), "[NATIONAL_ID]"),
    (re.compile(r"\b01[0125]\d{8}\b"), "[PHONE]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[EMAIL]"),
]


# Who must approve each action before it happens (POL-04 §5 disputes, POL-10 §1 and POL-19 §4 credit,
# POL-11 §2 waivers, POL-16 §3 complaints, POL-20 §3)
ACTION_RULES = {
    "block_card": ("agent", "done", "Card blocked by agent."),
    "order_replacement_card": ("agent", "done", "Replacement ordered by agent; fee per POL-03 §2."),
    "open_dispute": ("disputes_team", "submitted", "Dispute submitted; only the Disputes team decides."),
    "request_fee_waiver": ("team_leader", "pending_approval", "Waiver request sent for approval (POL-11 §2)."),
    "log_complaint": ("agent", "logged", "Complaint logged with a C- reference; a disputed decision goes back to the Disputes team (POL-16 §3)."),
    "escalate_to_supervisor": ("team_leader", "pending_approval", "Escalated to the Team Leader."),
    "refer_to_credit_team": ("credit_team", "pending_approval", "Referred to the Credit team, which alone decides (POL-10 §1, POL-19 §4)."),
}
WAIVER_TEAM_LEADER_MAX = 250  # EGP; a bigger waiver needs the Operations Manager (POL-11 §2)
APPROVER_NAMES = {"agent": "agent", "team_leader": "Team Leader", "operations_manager": "Operations Manager",
                  "disputes_team": "Disputes team", "credit_team": "Credit team"}


# Risk labels for every draft, decided here and never by the model; the model can only raise risk through its flags.
MONEY_ACTIONS = {"request_fee_waiver", "block_card", "order_replacement_card", "refer_to_credit_team"}
HANDOVER_ACTIONS = {"open_dispute", "escalate_to_supervisor", "log_complaint"}
BLOCKING_FLAGS = {"prompt_injection", "third_party_request"}
HIGH_FLAGS = {"approval_request", "fraud_suspected", "card_or_fraud"}


def risk_label(status, input_flags, risk_flags, actions):
    """{'level': 'blocked'|'high'|'low_escalated'|'low_resolved', 'reason': one line}. Auto-reply acts only on the two low levels."""
    flags = set(input_flags) | set(risk_flags)
    if status != "ready":
        return {"level": "blocked", "reason": "a guardrail check failed, so no reply goes out"}
    if flags & BLOCKING_FLAGS:
        return {"level": "blocked", "reason": f"{', '.join(sorted(flags & BLOCKING_FLAGS))}: an agent must handle this"}
    money = [a for a in actions if a in MONEY_ACTIONS]
    if money:
        return {"level": "high", "reason": f"{', '.join(money)} moves money or touches a card"}
    if flags & HIGH_FLAGS:
        return {"level": "high", "reason": f"{', '.join(sorted(flags & HIGH_FLAGS))}: a human must decide"}
    handover = [a for a in actions if a in HANDOVER_ACTIONS]
    if handover:
        return {"level": "low_escalated", "reason": f"{', '.join(handover)} hands the case to a human team; no money moves"}
    if "complaint" in flags:
        return {"level": "low_escalated", "reason": "complaint: logged for the complaints team"}
    return {"level": "low_resolved", "reason": "information only, no action needed"}


def approver_for(action, amount_egp=None):
    """Who approves this action, from the table above; a waiver above EGP 250 goes to the Operations Manager."""
    if action == "request_fee_waiver" and (amount_egp or 0) > WAIVER_TEAM_LEADER_MAX:
        return "operations_manager"
    return ACTION_RULES[action][0]


def set_approvers(draft):
    """The approver comes from the policy table, never from the model. Returns the labels the model got wrong."""
    corrected = []
    for a in draft.suggested_actions:
        approver = approver_for(a.action, a.amount_egp)
        if a.approver != approver:
            corrected.append(f"{a.action}: model said {a.approver}, policy says {approver}")
            a.approver = approver
    return corrected


def changed_share(drafted, final):
    """Share of the drafted reply the agent changed, by words: 0 = sent as drafted, 1 = fully rewritten."""
    a, b = drafted.split(), final.split()
    return 0.0 if a == b else 1 - SequenceMatcher(None, a, b, autojunk=False).ratio()


def mask_pii(text):
    for pattern, token in PII_PATTERNS:
        text = pattern.sub(token, text)
    return text


def input_flags(message, scope):
    """Flags for the agent and the model. Nothing here blocks: the scope already makes leaks impossible."""
    flags = []
    if INJECTION.search(message):
        flags.append("prompt_injection")
    other_ids = [m for m in re.findall(r"\bC\d{3}\b|\bD-\d{4}\b|\bT\d{5}\b", message)
                 if m != scope.customer_id and not scope.owns(m)]
    if other_ids or THIRD_PARTY.search(message):
        flags.append("third_party_request")
    if APPROVAL_ASK.search(message):
        flags.append("approval_request")
    if CARD_OR_FRAUD.search(message):
        flags.append("card_or_fraud")
    return flags


def _norm(text):
    return re.sub(r"\s+", " ", text.translate(ARABIC_DIGITS).replace("’", "'").replace("“", '"').replace("”", '"')).strip().lower()


def _numbers(text):
    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text.translate(ARABIC_DIGITS))
    out = set()
    for n in NUM_RE.findall(text):
        v = float(n)
        out.add(str(int(v)) if v.is_integer() else str(v))
    return out


def _quote_found(quote, source_text):
    q, s = _norm(quote), _norm(source_text)
    if not q:
        return False
    if q in s:
        return True
    # tolerate small punctuation drift: best window of the same length must be ~90% similar
    best = max((SequenceMatcher(None, q, s[i:i + len(q)]).ratio() for i in range(0, max(1, len(s) - len(q) + 1), 3)), default=0)
    return best >= 0.9


def source_text(source_id, scope):
    """Resolve a citation to its text. Records resolve only inside this customer's scope."""
    if source_id.startswith("POL-"):
        return store.policy_section(source_id)
    return scope.record_lines().get(source_id)


def check_draft(draft, scope, customer_message):
    """Returns a list of checks: {name, passed, severity ('block'|'warn'), detail}."""
    checks = []
    others = store.all_record_ids()

    unsourced = [f.statement for f in draft.facts if not f.citations]
    checks.append(dict(name="Every claim has a source", passed=not unsourced, severity="block",
                       detail="; ".join(unsourced) or f"{len(draft.facts)} claims, all cited"))

    bad_refs, bad_quotes, foreign = [], [], []
    cited_texts = []
    for f in draft.facts:
        for c in f.citations:
            sid = c.source_id.strip()
            if sid in others and others[sid] != scope.customer_id:
                foreign.append(sid)
                continue
            text = source_text(sid, scope)
            if text is None:
                bad_refs.append(sid)
            elif not _quote_found(c.quote, text):
                bad_quotes.append(f"{sid}: \"{c.quote[:80]}\"")
            else:
                cited_texts.append(text)
    checks.append(dict(name="Sources exist and quotes match them", passed=not (bad_refs or bad_quotes), severity="block",
                       detail="; ".join([f"unknown source {s}" for s in bad_refs] + [f"quote not in source {q}" for q in bad_quotes]) or "all quotes verified"))
    checks.append(dict(name="Only this customer's records", passed=not foreign, severity="block",
                       detail=f"cited another customer's record: {', '.join(foreign)}" if foreign else f"scoped to {scope.customer_id}"))

    allowed = set().union(*(_numbers(t) for t in cited_texts), _numbers(customer_message)) if cited_texts else _numbers(customer_message)
    stray = sorted(_numbers(draft.suggested_reply) - allowed, key=len)
    checks.append(dict(name="Numbers match the sources", passed=not stray, severity="block",
                       detail=f"not found in any cited source: {', '.join(stray)}" if stray else "every number traced to a source"))

    odd = sorted(set(UNEXPECTED_SCRIPT.findall(draft.suggested_reply)))
    checks.append(dict(name="Reply is clean text in Arabic or Latin script", passed=not odd, severity="block",
                       detail=f"unexpected characters: {' '.join(odd)}" if odd else "Latin and Arabic only"))

    draft_text = " ".join([draft.suggested_reply, draft.reply_in_english, draft.agent_summary])
    leaked = [c["name"] for cid, c in store.customers().items() if cid != scope.customer_id and c["name"].lower() in draft_text.lower()]
    leaked += [m for m in re.findall(r"\bC\d{3}\b|\bD-\d{4}\b|\bT\d{5}\b", draft_text)
               if m != scope.customer_id and others.get(m, scope.customer_id) != scope.customer_id]
    checks.append(dict(name="No other customer's data", passed=not leaked, severity="block",
                       detail=f"found: {', '.join(leaked)}" if leaked else "none found"))

    policy_ids = {c.source_id.split("§")[0].strip() for f in draft.facts for c in f.citations if c.source_id.startswith("POL-")}
    superseded = {pid for pid in policy_ids if store.policies().get(pid, {}).get("superseded")}
    with_current = superseded and "POL-01" in policy_ids  # old schedule cited only to contrast with the current one
    checks.append(dict(name="Current policy versions", passed=not superseded or with_current, severity="warn",
                       detail=("cites superseded POL-02 alongside current POL-01 (explaining the change)" if with_current else
                               "cites superseded POL-02 without the current schedule") if superseded else "no superseded policy cited"))
    return checks


def blocked(checks):
    return [c for c in checks if not c["passed"] and c["severity"] == "block"]
