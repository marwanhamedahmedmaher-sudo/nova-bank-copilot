# Regulation: Nova Bank agent copilot (Egypt)

Research date: 30 Oct 2026. Scope: Steps 1-3 of the regulatory-research method (identify, research, assess). Nova Bank is fictional; the rules below are real.
FX used for USD figures: EGP 56.12 = USD 1 (CBE official sell rate dated 29 Oct 2026, as shown on the nabdmal.com aggregator, which cites the CBE) [S30].
Labels: **[Assumption]** = our assumption, not a finding. **[Unverified]** = we could not confirm it on an official page. **[Unclear]** = the rule exists but its application to us is a grey area.

> This is research to brief Nova Bank's legal and compliance team. It is not legal advice.

---

## Bottom line

1. **Banks are carved out of Egypt's data protection law.** PDPL 151/2020 does not apply to personal data held by the CBE and entities it supervises (except money-transfer and exchange companies) [S1]. Nova's binding data rules are **bank secrecy** (Banking Law 194/2020, Art. 140-143, criminal penalties) and **CBE instructions**, not the PDPL.
2. **The hard constraint is offshore processing.** Customer data may be shared only with written customer consent or with a **CBE-registered** outsourcing provider for what the service needs; the CBE is reported not to register companies located outside Egypt [S3, S5]. So raw customer data cannot go to a foreign LLM API.
3. **Complaint timelines are explicit and the copilot can carry them:** reference number within 2 working days, reply within 15 working days, quarterly reporting to the CBE (CBE circular, 7 May 2024) [S44, S45].
4. **AI rules are soft law, but they speak directly to us:** the 2023 Charter names "automated call centers" as a case where users have a right to know they are talking to an AI; the March 2026 national framework puts chatbots in Tier 3 (transparency and labelling) [S14, S15].
5. **There is no hyperscaler region in Egypt.** Huawei Cloud Cairo is the only public cloud region (since May 2024) and has offered LLMs as a service since 25 Jun 2026; Egypt's national LLM Karnak was launched 11 Feb 2026 [S20, S21, S23]. Recommendation: Claude API on synthetic data for the demo; in-country by default for production, with an offshore model only for non-customer data and only after CBE sign-off.

---

## 1. Governing bodies

| Body | What it governs for this copilot | Binding on Nova? | Official site |
|---|---|---|---|
| **Central Bank of Egypt (CBE)** | Banking licence, bank secrecy, outsourcing registration, consumer protection and complaints, cybersecurity, payments and cards | Yes, primary regulator | cbe.org.eg |
| **Personal Data Protection Center (PDPC)**, under MCIT | PDPL 151/2020 and Executive Regulations (Decree 816/2025): licences, consent, cross-border transfer, breach notification | Not for Nova's own customer data (Art. 3 exemption). Possibly yes for any vendor that is not CBE-supervised **[Unclear]** | pdpc.gov.eg |
| **MCIT / National Council for AI (NCAI) / Egyptian Center for Responsible AI (ECRAI)** | National AI Strategy 2025-2030, Charter for Responsible AI, AI governance framework and guidelines | Soft law (guidance), no penalties | ai.gov.eg, mcit.gov.eg |
| **ITIDA** | AI ecosystem; announced the Karnak national LLM | Not a regulator for us | itida.gov.eg |
| **NTRA** | Licenses data centres and cloud providers operating in Egypt | Binds our hosting provider, not Nova directly | tra.gov.eg |
| **Financial Regulatory Authority (FRA)** | Non-bank financial services (insurance, investment, consumer finance); FRA Decree 57/2024 on robo-advisors | Out of scope unless Nova sells non-bank products through the copilot **[Assumption: it does not]** | fra.gov.eg |
| **Consumer Protection Agency** (Law 181/2018) | General consumer protection | Reported not to apply to CBE-regulated entities (Law 194/2020, Art. 216) [S4] | cpa.gov.eg |
| **Visa, Mastercard** (and Meeza, Egypt's domestic scheme) | Card dispute and chargeback rules, by contract with the issuer | Yes, contractually | visa.com, mastercard.com |

---

## 2. Rules that apply (source and date for each)

**R1. Bank secrecy: Banking Law 194/2020, Art. 140-143 and Art. 231.**
All customer data, accounts, deposits, safe-kept valuables and related transactions are confidential and may not be disclosed, directly or indirectly, without the customer's written consent or a court or arbitral order; the duty survives the end of the relationship (Art. 140). Staff may not disclose what they learn through their job (Art. 142). Exceptions include "informing outsourcing service providers of customer data necessary to carry out the services entrusted to them" (Art. 143(9)). Breach: imprisonment of at least one year and a fine of EGP 200,000-500,000 (USD 3,560-8,910), multiplied by the number of affected parties, for staff and for outsourcing providers (Art. 231, as summarised by Baker McKenzie).
Sources: Law 194/2020 (CBE lists it at [S2]); English translation, Andersen Egypt, Jul 2025 [S3]; Art. 143 exceptions, Mohamed Nasser Law, 23 May 2024 [S6]; penalties, Baker McKenzie Cloud Compliance Center (undated, accessed 30 Oct 2026) [S5].

**R2. Outsourcing: Banking Law 194/2020 ("delegated services") and CBE outsourcing rules.**
The CBE Board defines the important outsourced and technology services and their registration conditions (governance, risk management, performance, confidentiality). Banks may not use unregistered providers and remain fully responsible for outsourced functions (Art. 96 according to Matouk Bassiouny, 5 Oct 2020; **article number [Unverified]** against the Official Gazette) [S3, S7]. Contracts must cover confidentiality, service standards, unilateral termination without cost, no change of service without bank approval, reporting to the bank's board [S5]. CBE internet-banking rules require prior CBE approval before outsourcing internet-banking services, with audit rights, business continuity and exit terms (Chambers Fintech 2026, 31 Mar 2026) [S4]. Baker McKenzie reports that, "to the best of our knowledge, the CBE does not accept the registration of outsourcing companies located outside of Egypt" [S5]. This is a law firm's hedged view on an undated page, not a published CBE rule: **[Unverified]**, but it is the most authoritative statement we found and we design around it.

**R3. Personal Data Protection Law 151/2020 and Executive Regulations (Minister of CIT Decree 816/2025).**
- *Status:* Law published 13-17 Jul 2020. Executive Regulations dated 1 Nov 2025 (Official Gazette), in force the next day, made public on 25 Dec 2025. One-year grace period ends **31 Oct 2026** (Baker McKenzie, 7 Oct 2026) or **1 Nov 2026** (Legal 500 / Soliman Hashish, 6 Apr 2026): sources differ by one day, either way **tomorrow** [S10, S11, S12]. No extension reported as of 7 Oct 2026 [S10].
- *Bank exemption:* Art. 3 of the issuing law excludes "personal data held by the Central Bank of Egypt and entities subject to its control and supervision, with the exception of money transfer companies and currency exchange companies", which must follow CBE rules on personal data [S1].
- *Rules for those in scope:* a licence or permit from the PDPC for any controller or processor; **financial data is "sensitive personal data"** (Art. 1) and needs a licence (Art. 12) and explicit written consent [S16, S49]; cross-border transfer needs a PDPC licence, an adequate destination and the data subject's consent (Art. 14-16), and the PDPC says this "includes engaging with cloud service providers where personal data is processed or stored on servers located outside Egypt"; breach notice to the PDPC within 72 hours and to data subjects within 3 working days; PDPC decides cross-border applications within 90 working days; annual licence fee capped at EGP 666,666 (USD 11,880) for more than 5 million records; foreign controllers need a local representative [S10, S12, S13, S16, S17, S49].

**R4. CBE Consumer Protection Instructions (Feb 2019) and Banking Law 194/2020, Art. 216-220.**
Principles: fair treatment, disclosure and transparency, complaint handling, awareness, data protection [S8]. Interest rates and tariffs must be published on the bank's website and in branches; the customer must get clear, not misleading information on terms and cost before agreeing; the bank may not claim fees not agreed or not notified; where the bank uses outsourced entities, it must tell the customer that **the bank is fully responsible** for their services (NBE summary of the instructions; Shalakany) [S18, S19]. Date: circular of **19 Feb 2019**, confirmed by the CBE's own May 2024 complaint instructions [S44] and the CBE Financial Stability Report March 2024 [S9] (an NBE document cites 13 Feb 2019; we follow the CBE text) [S18]. The full 2019 text was not opened; the disclosure points above come from bank and law-firm summaries of it.

**R5. CBE instructions on the complaint-handling mechanism in banks (Governor's circular of 7 May 2024; CBE Board decision of 30 Apr 2024), complementing the 2019 instructions.**
A complaint is any oral or written expression, by any means including sign language, showing dissatisfaction with the bank, its outsourced service providers, payment service providers or agents, including problems with disclosure of rates, **fees** or penalties [S44, S47]. Banks acknowledge immediately with a reference number, or within **2 working days** at most; reply in writing or electronically within **15 working days** (except complaints about transactions with third parties, where the customer is told the time needed); accept a written objection within 15 working days; give a reasoned final reply; and tell the customer they can escalate to the CBE only after the bank's process [S44, S45]. Complaints are reported to the CBE quarterly, within 30 days of quarter end; the service is free at every stage and offered on several channels; banks had 6 months from issue to comply [S44, S47, S24, S25].
Context from the CBE (Financial Stability Report 2022): **cards were 58.5% of complaints**, concentrated in disputed withdrawals and purchases, and the **call centre received 95% of complaints**; complaints handled within 15 working days rose from 86% to 89% [S26].

**R6. CBE cybersecurity: EG Financial Cybersecurity Framework, version 2 in preparation.**
The CBE issued Egypt's first Financial Cybersecurity Framework and assesses licensed entities against it (issue date **[Unverified]**) [S27]. The CBE Financial Stability Report (March 2026 edition, published 14 Oct 2026) says a **second cybersecurity regulatory framework** is being prepared with guidance on **AI security, governance-risk-compliance and cloud computing security** (as reported by Daily News Egypt, 17 Oct 2026; we could not open the CBE report page, which blocked our tools) [S28].

**R7. Cloud and data residency for banks.**
No published CBE cloud-computing rule for banks was found. The CBE said in July 2023 it was finalising cloud-service rules [S29]; on 24 Oct 2026 the Governor said the CBE is building a sector cloud and unified data centre [S31]. Law firms describe banking law as "generally silent" on cloud, with NTRA accreditation allowing cloud hosting of "low-risk banking information other than customer data" [S5]. **Status of a binding CBE cloud rule: [Unverified], treat as pending.**

**R8. Egyptian AI policy (soft law).**
- National AI Strategy, 2nd edition (2025-2030), launched Jan 2025 [S32].
- Egyptian Charter for Responsible AI (2023): users have "the fundamental right to know" when interacting with an AI system, "for example in the case of automated call centers" (general guideline 2); affected people can challenge outcomes (GG 4); accountability always lies with natural or legal persons (GG 10); final decisions stay human (GG 10-11 per Legal 500) [S14, S33].
- Guide to Egypt's National AI Governance Framework (ECRAI/NCAI, March 2026): four tiers; **Tier 3 "Limited risk: chatbots and deepfakes" requires transparency and labelling**; every system's tier is recorded in an AI risk registry [S15].
- National Guidelines for Trustworthy and Responsible AI v2.0 (March 2026): human-in-the-loop mandatory for high-risk decisions; test-evaluate-verify-validate (TEVV) documentation and formal sign-off by risk, security and compliance before deployment; LLM-based systems flagged for special governance [S34]. National Generative AI Guidelines (March 2026): disclose AI-generated text [S35].
- A draft AI law is reported to be before Parliament (Legal 500) **[Unverified status]** [S33]. No CBE-specific AI guidance for banks was found; the CBE runs an AI-in-banking diploma (Feb 2026) and the v2 cyber framework will include AI security [S28, S36].

**R9. Card dispute timelines (scheme rules, apply to Egyptian issuers by contract).**
- Visa: a dispute must be processed within **120 calendar days** of the Transaction Processing Date (or of the last expected delivery date for merchandise/services not received, capped at 540 days from the Transaction Processing Date). The current Visa Core Rules edition is dated **24 Oct 2026** and keeps a dispute time-limit table per condition (e.g., Table 11-93 for condition 13.1) [S46]; the 120/540-day wording is confirmed in Visa's Oct 2026 Interlink rules and Visa's own rule-change notice, and quoted from the Visa Core Rules by the Irish and UK ombudsmen [S48, S37, S38]. The Oct 2026 edition lists changes to some dispute time-limit sections effective through Oct 2027, so the exact limit per reason code must be checked in that edition **[Unverified per reason code]**.
- Mastercard: chargeback within **120 calendar days** of the settlement / central processing date; the acquirer's second presentment within 45 days (Mastercard Chargeback Guide) [S39].
- Meeza (domestic scheme) dispute timelines and any CBE rule on chargebacks: **not found [Unverified]**. Under R5, card-scheme disputes count as "transactions with third parties", so the 15-day reply limit does not apply but the customer must be told the expected time.

**R10. Cybercrime Law 175/2018.** IT and data-processing service providers must keep user data (identification, traffic and content of the service system) for at least 180 days and keep it confidential (Soliman Hashish & Partners, Aug 2025) [S40]. Applies to our hosting/processing provider; whether it applies to an internal copilot is **[Unclear]**.

---

## 3. Rule -> requirement -> design implication -> risk

| # | Rule | What it requires | Design implication for the copilot | Risk |
|---|---|---|---|---|
| R1 | Bank secrecy, Law 194/2020 Art. 140-143, 231 | No disclosure of customer data without written consent; outsourcers get only what they need; criminal penalties | Mask or tokenise names, IDs, card/account numbers, phone, amounts-plus-merchant before any model call; the copilot session is bound to the one verified customer from the agent's case and cannot query another; no customer data in prompts to any provider that is not CBE-registered | **H** |
| R2 | Outsourcing registration and contract terms | Only CBE-registered providers; bank fully responsible; exit and audit rights | Model provider abstraction layer (swap model without rework); vendor register entry for the model host; contract checklist (termination, audit, no silent model changes, version pinning); log model name and version per answer | **H** offshore / **M** in-country |
| R3 | PDPL 151/2020 + Decree 816/2025 | Bank exempt; vendors in scope need licence, consent for sensitive (financial) data, cross-border licence, 72h breach notice | Keep Nova as the only data holder: vendors process inside Nova's environment where possible; if a non-CBE vendor touches personal data, plan a PDPC licence (allow 90 working days for cross-border); breach runbook with 72h clock | **M** |
| R4 | CBE Consumer Protection Instructions 2019 | Clear, not misleading information on fees; no fees beyond agreed/published; bank responsible for third parties | Fee answers only from the current published tariff, with version and effective date in the citation; if no source is found the copilot says so instead of answering; "waive fee" is a suggestion the agent approves | **M** |
| R5 | CBE complaint regulations May 2024 | Reference number in 2 working days, reply in 15, objection cycle, quarterly reporting | Detect dissatisfaction in the conversation and prompt the agent to log a complaint; show the SLA countdown on the case; tag card-scheme disputes as "third party" with the expected time to tell the customer; export complaint data in the quarterly report format | **M** |
| R6 | EG Financial Cybersecurity Framework (v2 adds AI and cloud security) | Security controls assessed by CBE; AI security guidance coming | Prompt-injection defences on retrieved policy text; output filtering for customer data; role-based access; penetration test before go-live; design to ISO 27001 and ISO/IEC 42001 so v2 is a delta, not a rebuild **[Assumption: v2 will follow these standards]** | **M** |
| R7 | Cloud / residency (no CBE cloud rule found) | Customer data hosted by CBE-registered, in practice in-country, providers | In-country default for data store, retrieval index and logs; "residency switch" config so the model endpoint can move in-country without code changes | **H** until CBE rule is published |
| R8 | AI Charter 2023, AI Governance Framework and Guidelines 2026 | Right to know it is AI; human final decision; Tier 3 labelling; TEVV and sign-off; risk registry | Phase 1: agent-facing, every draft marked "AI draft"; agent sends. Phase 2: in-app label "You are chatting with Nova's AI assistant" and one-tap handoff to a human; record the copilot in Nova's AI risk registry as Tier 3; keep our eval suite as the TEVV evidence | **L** Phase 1 / **M** Phase 2 |
| R9 | Visa / Mastercard dispute rules | 120 calendar days from processing/settlement date | Compute the dispute deadline from the transaction processing date and warn the agent when under 15 days remain **[Assumption: 15-day buffer]**; dispute-status answers cite the scheme stage (chargeback, second presentment) | **L** |
| R10 | Cybercrime Law 175/2018 | Providers retain user data 180 days, confidential | Audit log of every prompt, retrieved source and answer, retained at least 180 days in-country, access-controlled **[Assumption: Nova's own retention policy may require longer]** | **L** |

---

## 4. Compliance assessment (Step 3)

**Where the concept already aligns**
- "Suggest only, agent clicks" matches the Charter's human-final-decision principle and the national guidelines' human-in-the-loop requirement [S14, S34].
- Citations on every claim match CBE's "clear, not misleading information" duty for fees [S18].
- One session per verified customer limits secrecy exposure under Art. 140.
- Masking plus an audit log (already decided in CLAUDE.md) answers R1 and R10 in principle.

**Where it conflicts or is exposed**
- Using a foreign hosted model API with real customer data conflicts with R1 and R2 as they are described by Baker McKenzie [S5]. Masking reduces but does not remove this: whether masked transaction data is still "customer data" under Art. 140 is **[Unclear]**, and no CBE guidance on it was found.
- Fee hallucination is a consumer-protection breach even if an agent sends it, because the bank is responsible for the information given [S18].

**Grey areas (need CBE or counsel)**
1. Does a pseudonymised prompt (no name, ID or account number, but real amounts and dates) count as disclosure under Art. 140?
2. Is an LLM API an "important outsourced service" that needs CBE registration, or a software licence?
3. Would a non-CBE-supervised AI vendor that processes Nova data fall under the PDPL despite Nova's exemption?
4. Will the CBE v2 cyber framework impose AI-specific controls (model risk validation, explainability) that we should design for now?

**Risk by category (justified)**

| Category | Risk | Why |
|---|---|---|
| Bank secrecy and data residency | **H** | Criminal penalties (Art. 231); foreign providers reportedly not registrable; masking status unclear |
| Outsourcing and vendor management | **H** offshore / **M** in-country | Registration duty plus full bank responsibility; manageable if the model runs in Nova's or a registered local environment |
| Data protection (PDPL) | **M** | Nova exempt, but vendors may be in scope, financial data is sensitive, and the grace period ends 31 Oct / 1 Nov 2026 |
| Consumer protection and fee disclosure | **M** | Wrong fee information is a breach; mitigated by tariff-only answers, citations and agent review |
| Complaint handling | **M** | Strict SLAs; the copilot can help (SLA timers) or hurt (missed complaint logging) |
| AI governance | **L** Phase 1 / **M** Phase 2 | Soft law today; agent-assist with human approval fits it; customer-facing triggers Tier 3 labelling and a possible future AI law |
| Cybersecurity | **M** | LLM-specific threats (prompt injection, data leakage) and AI security guidance coming in CBE v2 |
| Card scheme rules | **L** | Clear, contractual 120-day limits; risk is a missed deadline, not a regulatory breach |
| Data retention (Cybercrime Law) | **L** | Simple to meet with an in-country audit log |

---

## 5. Hosting options

**What is available (as of Aug-Oct 2026)**
- **No AWS, Azure, Google Cloud or Oracle region in Egypt.** Nearest: Azure UAE North and Qatar Central (Saudi Arabia East due Q4 2026); AWS UAE and Bahrain (Egypt has only a CloudFront edge in Cairo since May 2024); Oracle's nearest new region is Casablanca (Feb 2026) [S20, S22].
- **Huawei Cloud Cairo region** (May 2024, USD 300m over five years): the only public cloud region in Egypt; **Model-as-a-Service launched in Egypt on 25 Jun 2026**, pitched at financial services and customer service [S20, S21].
- **Karnak**, Egypt's national LLM, launched by MCIT/ITIDA on 11 Feb 2026 as a foundation for local enterprises [S23]. A 40B-parameter Arabic-English version built on Alibaba's Qwen3-30B-A3B is reported to be public on Hugging Face (ME Observer, 23 Aug 2026); licence terms, Egyptian-dialect and Franco-Arabic quality are **[Unverified]** [S41].
- **Local data centres:** about 13 colocation facilities, nine in Cairo (GlobeNewswire, 27 Oct 2026); NTRA licensed Hassan Allam Digital Infrastructure for data centres and cloud on 15 Jun 2026 [S22, S42]. Telecom Egypt and local providers also offer cloud.
- **Claude API is available from Egypt** (Anthropic supported regions list) [S43]. Whether specific models are offered in the UAE/Qatar hyperscaler regions should be checked in each provider's console **[Unverified]**.

**Can a bank send masked data to a hosted LLM API outside Egypt?**
- *Policy documents, tariffs, scripts (no customer data):* **Yes, low risk.** Not customer data under Art. 140 and not personal data under the PDPL.
- *Raw customer data:* **No**, in practice. Needs written consent per customer (Art. 140) or a CBE-registered provider (Art. 143(9) plus R2), and foreign providers are reportedly not registered [S5].
- *Masked or tokenised conversation:* **Grey area [Unclear].** Defensible only if what leaves cannot be linked back to a customer outside Nova, and only with a written CBE no-objection. Design so we do not depend on it.

**Options compared**

| Option | Data residency | Model quality (EN, Arabic, Egyptian, Franco) | Regulatory fit | Effort |
|---|---|---|---|---|
| A. Foreign hosted API (e.g., Claude API) | Offshore | High | Demo / policy-only use only | Low |
| B. Hyperscaler in UAE or Qatar | Offshore (regional) | High | Same issue as A; closer, still cross-border | Medium |
| C. Huawei Cloud Cairo MaaS | In Egypt | Depends on models offered **[Unverified]** | Good if the provider is CBE-registered **[Unverified]** | Medium |
| D. Self-hosted open-weight model (e.g., Karnak-40B) in Nova's data centre or local colo | In Egypt, Nova-controlled | Unknown on dialect and Franco; needs our evals | Strongest | High (GPUs, MLOps) |
| E. Hybrid router: D or C for anything with customer data, A only for policy-only tasks | In Egypt for customer data | Best of both | Strong, if CBE agrees to policy-only offshore calls | Medium-high |

**Recommendation**
- **Demo (31 Oct 2026):** Option A, Claude API, on our **synthetic** dataset only. No real customer data, so R1-R3 are not triggered. Keep the masking layer and audit log switched on so the panel sees the production controls working, and show the "residency switch" in config.
- **Production Phase 1 (agent-assist):** Option E. Data store, retrieval index, masking service and audit logs in Egypt from day one. Start with an in-country model (C or D) for any prompt that contains customer data; allow the offshore model only for policy-only work (for example drafting fee-explanation templates or generating evals) and only after a written CBE no-objection. Gate go-live on our four-language eval suite passing on the in-country model.
- **Phase 2 (customer-facing in app):** in-country model only, Tier 3 labelling, human handoff for anything that moves money.

---

## 6. Questions a compliance officer will ask, and our answer

1. **"Does any customer data leave Egypt?"**
   Not in production. Customer data, the search index and logs stay in Egypt; masking runs before any model call; the model that sees customer context runs in Egypt. Only policy text may go to an offshore model, and only with CBE no-objection. Basis: Art. 140-143, Law 194/2020 [S3, S6]. The demo uses synthetic data only.
2. **"The PDPL deadline is tomorrow. Are we compliant?"**
   Nova, as a CBE-supervised bank, is outside the PDPL under Art. 3 of the issuing law and follows CBE rules instead [S1]. We still apply PDPL-grade practice (minimisation, 72-hour breach runbook) and check whether any vendor touching our data needs its own PDPC licence [S10, S12].
3. **"Who is accountable if the copilot gives a customer a wrong fee?"**
   Nova. CBE instructions make the bank responsible for information given and for third parties it uses [S18]. That is why fee answers come only from the current published tariff, cite its version and date, refuse when no source exists, and are sent by the agent, not the model.
4. **"Can the copilot move money or waive fees?"**
   No. It suggests (open dispute, order card, waive fee); the agent approves and executes in the core system. This matches the Charter's "final decision is human" and the national guidelines' human-in-the-loop rule [S14, S34].
5. **"Could an agent see another customer's data through the copilot?"**
   No. Each session is bound to the customer ID from the case the agent opened after verification, and the copilot's data tools reject any other ID. Every lookup is logged. This narrows Art. 140 exposure to what the verified customer's own call needs.
6. **"Is the AI vendor an outsourcing provider that needs CBE registration?"**
   We treat it as one until the CBE says otherwise [S5, S7]. That is why the production model runs in Nova's environment or with a CBE-registered local provider, behind an abstraction layer so we can change provider. Open question for the CBE (grey area 2).
7. **"How does this help us meet the complaint rules?"**
   It flags dissatisfaction as a likely complaint, prompts the agent to log it so the 2-working-day reference number is issued, shows the 15-working-day countdown, marks card-scheme disputes as third-party cases with the expected time to tell the customer, and exports data for the quarterly CBE report [S44, S45].
8. **"How do you handle card dispute deadlines?"**
   The copilot computes the 120-calendar-day scheme limit from the transaction processing date and warns the agent when it is close; dispute status shows which scheme stage the case is in [S46, S39]. Meeza timelines still need confirmation from Nova's card operations.
9. **"When it goes customer-facing, will customers know it is AI?"**
   Yes. The Charter names automated call centres as a case where users must be told, and the March 2026 framework requires labelling for Tier 3 chatbots [S14, S15]. Phase 2 shows a clear AI label and a one-tap route to a human.
10. **"Can you prove what the copilot said and why?"**
    Yes. Every answer is logged with the masked prompt, retrieved sources, model and version, the agent's edit and final send, kept in Egypt for at least 180 days [S40] and available for CBE inspection. Our eval suite and sign-off record serve as the TEVV evidence the national guidelines ask for [S34].

---

## 7. Regulatory Risk Outlook

**Score: 6/10 (medium-high).** Egypt is a high-sensitivity environment for this product because bank secrecy carries criminal penalties and offshore outsourcing is effectively closed for customer data. Our design choices (agent-assist, suggestions only, masking, one-customer sessions, audit log, in-country path) bring the realistic risk down to medium. With a foreign LLM receiving real customer data the score would be about 8/10; fully in-country with CBE sign-off, about 4/10.

Before launch, the PM should prioritise (1) a written CBE position on whether masked prompts and an LLM provider count as disclosure and outsourcing, and (2) an in-country model passing our four-language evals, because both decide the production architecture.

---

## 8. Sources

| ID | Source | Date | URL |
|---|---|---|---|
| S1 | Law 151/2020 issuing articles, Art. 3 (Arabic/English text, PrivacyLaws.com); confirmed by Chambers Fintech 2026 | 2020; 31 Mar 2026 | https://www.privacylaws.com/media/3263/egypt-data-protection-law-151-of-2020.pdf |
| S2 | CBE, Banking Laws page (Law 194/2020) | last updated 23 Mar 2023 | https://www.cbe.org.eg/en/laws-regulations/laws/banking-laws |
| S3 | Andersen Egypt, translation of Law 194/2020 | Jul 2025 | https://eg.andersen.com/wp-content/uploads/2025/07/banking-law-no-194-of-2020.pdf |
| S4 | Chambers Global Practice Guides, Fintech 2026: Egypt | 31 Mar 2026 | https://practiceguides.chambers.com/practice-guides/fintech-2026/egypt |
| S5 | Baker McKenzie, Cloud Compliance Center: Egypt | undated, accessed 30 Oct 2026 | https://resourcehub.bakermckenzie.com/en/resources/cloud-compliance-center/emea/egypt |
| S6 | Mohamed Nasser Law, bank account confidentiality (Art. 140-143) | 23 May 2024 | https://mnasserlaw.com/bank-accounts/ |
| S7 | Matouk Bassiouny, New Banking Law alert (outsourcing, Art. 96) | 5 Oct 2020 | https://matoukbassiouny.com/new-law-alert-new-egyptian-banking-law-no-194-of-2020/ |
| S8 | CBE, Consumer Protection page | last updated 23 Mar 2023 | https://www.cbe.org.eg/en/consumer-protection |
| S9 | CBE, Financial Stability Report March 2024 (complaint regulations May 2024; instructions 19 Feb 2019) | 2024 | https://www.cbe.org.eg/-/media/project/cbe/page-content/rich-text/financial-stability/english/financial-stability-report-march-2024.pdf |
| S10 | Baker McKenzie, Egypt PDPL update | 7 Oct 2026 | https://www.bakermckenzie.com/en/insight/publications/2026/10/egypt-personal-data-protection-law-update |
| S11 | Baker McKenzie, Egypt: Important data protection update | 9-12 Jan 2026 | https://connectontech.bakermckenzie.com/egypt-important-data-protection-update/ |
| S12 | Legal 500 / Soliman Hashish, Executive Regulations and the PDPC | 6 Apr 2026 | https://www.legal500.com/intelligence/egypt/privacy/the-issuance-of-the-executive-regulations-of-the-data-protection-law-in-egypt-and-the-establishment-of-the-data-protection-centre |
| S13 | PDPC, Licences and Permits guideline (official; the PDF did not render in our tools, so the quoted sentence comes from the search index copy and is corroborated by Chambers and Legal 500 on the broad transfer definition) | undated, accessed 30 Oct 2026 | https://pdpc.gov.eg/assets/pdf-data/Guidelines/Licenses%20and%20Permits.pdf |
| S14 | NCAI, Egyptian Charter for Responsible AI | 2023 | https://ai.gov.eg/SynchedFiles/en/Resources/Egyptian%20Charter%20For%20Responsible%20AI.pdf |
| S15 | ECRAI/NCAI, Guide to Egypt's National AI Governance Framework | Mar 2026 (file dated 15 Mar 2026) | https://ai.gov.eg/SynchedFiles/ar/Resources/Guide%20to%20Egypt%E2%80%99s%20National%20AI%20Governance%20Framework%2015-3-2026.pdf |
| S16 | Law 151/2020, English translation (Matouk Bassiouny via ACC): sensitive data Art. 1, Art. 12, Art. 14-15, fee caps | 2020 | https://www.acc.com/sites/default/files/program-materials/upload/Data%20Protection%20Law%20-%20Egypt%20-%20EN%20-%20MBH.PDF |
| S17 | Al Tamimi, Egypt issues Executive Regulations (72h breach, 3 working days) | 4 Feb 2026 | https://www.tamimi.com/our-knowledge/publications/general/Articles/from-policy-to-practice-egypt-issues-executive-regulations-of-the-personal-data-protection-law/ |
| S18 | National Bank of Egypt, bulletin on CBE consumer protection instructions; NBE customer protection unit document | undated, accessed 30 Oct 2026 | https://www.nbe.com.eg/AssetsManager/2f65a6e7-e155-419d-9440-7903eb11eecc.pdf |
| S19 | Shalakany, New regulations on the protection of bank customers | 2019 | https://shalakany.com/new-regulations-on-the-protection-of-bank-customers/ |
| S20 | AABDC Egypt, Egypt data centres and cloud infrastructure (research note to 27 Aug 2026) | 27 Aug 2026 | https://www.aabdcegypt.com/blogs/post/egypt-data-centers-cloud-infrastructure |
| S21 | Tech.Africa / Techno Time, Huawei Cloud launches MaaS in Egypt | 25 Jun 2026 | https://tech.africa/huawei-cloud-maas-egypt/ |
| S22 | GlobeNewswire, Egypt data center market 2026-2031 | 27 Oct 2026 | https://www.globenewswire.com/news-release/2026/10/27/3389361/28124/en/ |
| S23 | ITIDA press release, Egypt launches Karnak national LLM | 11 Feb 2026 | https://itida.gov.eg/English/PressReleases/Pages/egypt-national-ai-karnak-llm-launch-Ai-Everything-MEA-2026.aspx |
| S24 | Daily News Egypt, CBE guidelines on handling customer complaints | 12 May 2024 | https://www.dailynewsegypt.com/2024/05/12/cbe-lays-down-guidelines-for-banks-on-handling-customer-complaints/ |
| S25 | Banque Misr, Customer Rights Protection Policy (implements CBE rules) | undated, accessed 30 Oct 2026 | https://banquemisr.com/-/media/Customer-Rights-Policy-EN-Translation.pdf |
| S26 | CBE, Financial Stability Report 2022 (complaints by product and channel) | 2022 | https://www.cbe.org.eg/-/media/project/cbe/page-content/rich-text/financial-stability/english/financial-stability-report-2022.pdf |
| S27 | CBE, Cybersecurity page (EG Financial Cybersecurity Framework) | accessed 30 Oct 2026 | https://www.cbe.org.eg/en/cybersecurity |
| S28 | Daily News Egypt, reporting CBE Financial Stability Report (second cyber framework with AI and cloud security) | 17 Oct 2026 | https://www.dailynewsegypt.com/2026/10/17/egyptian-banking-sector-demonstrates-strong-financial-resilience-ability-to-withstand-shocks-cbe/ |
| S29 | Bankygate, CBE preparing cloud computing rules (CBE FinTech Outlook 2022) | 19 Jul 2023 | https://www.bankygate.com/42594 |
| S30 | Nabdmal, CBE USD rate (sell 56.12, dated 29 Oct) | 30 Oct 2026 | https://nabdmal.com/en/currency-rates |
| S31 | FintechGate, CBE Governor on sector cloud and unified data centre | 24 Oct 2026 | http://www.fintechgate.net/255393 |
| S32 | UNESCO Global AI Ethics Observatory, Egypt (NAIS 2nd edition Jan 2025; Charter 2023) | 31 Aug 2026 | https://www.unesco.org/ethics-ai/en/egypt |
| S33 | Legal 500, Egypt: Artificial Intelligence comparative guide | accessed 30 Oct 2026 | https://www.legal500.com/guides/chapter/egypt-artificial-intelligence/ |
| S34 | ECRAI/NCAI, National Guidelines for Trustworthy and Responsible AI v2.0 | Mar 2026 | https://ai.gov.eg/SynchedFiles/ar/Resources/Egypt%20National%20Guidelines%20for%20Trustworthy%20and%20Responsible%20AI.pdf |
| S35 | MCIT/ECRAI, Egypt's National Generative AI Guidelines v1.0 | Mar 2026 | https://ai.gov.eg/SynchedFiles/ar/Resources/EGYPT%20National%20Guidlines%20for%20Generative%20AI.pdf |
| S36 | Consultancy-me, CBE launches AI in Banking Diploma | 10 Feb 2026 | https://www.consultancy-me.com/news/13127/injaz-consulting-group-named-delivery-partner-of-egypts-ai-for-banking-diploma |
| S37 | Irish FSPO decision 2022-0126 quoting Visa Core Rules (Dispute Condition 13.1) | 2022 | https://fspo.ie/complaint-outcomes/investigation-services/legally-binding-decisions/documents/2022-0126.pdf |
| S38 | UK Financial Ombudsman decision DRN-5881403 quoting Visa rules (540-day cap) | accessed 30 Oct 2026 | https://www.financial-ombudsman.org.uk/decision/DRN-5881403.pdf |
| S39 | Mastercard, Chargeback Guide | edition date [Unverified], accessed 30 Oct 2026 | https://brand.mastercard.com/content/dam/mccom/en-us/documents/rules/chargeback-guide.pdf |
| S40 | Soliman, Hashish & Partners, Panoramic Fintech (Cybercrime Law 175/2018) | Aug 2025 | https://www.shandpartners.com/wp-content/uploads/2025/08/egypt_fintech-2.pdf |
| S41 | ME Observer, Egypt's Karnak tests the economics of sovereign AI | 23 Aug 2026 | https://meobserver.news/technology/2026/08/23/egypts-karnak-tests-the-economics-of-sovereign-ai/ |
| S42 | SouthwardTech, Egypt AI data-centre tender (NTRA licence to Hassan Allam, 15 Jun 2026) | 3 Sep 2026 | https://southwardtech.com/egypt-ai-data-centre-tender-huawei/ |
| S43 | Anthropic, Supported regions (Egypt listed) | accessed 30 Oct 2026 | https://platform.claude.com/docs/en/api/supported-regions |
| S44 | CBE, Instructions on the complaint-handling mechanism in banks (Regulations Book 14, ch. 2; Governor's circular 7 May 2024; complements instructions of 19 Feb 2019) - Arabic, official | 7 May 2024 | https://www.cbe.org.eg/-/media/project/cbe/file/long-context/laws-and-regulations/book-14/%D8%A7%D9%84%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D8%B1%D8%A7%D8%A8%D8%B9-%D8%B9%D8%B4%D8%B1---%D8%A7%D9%84%D9%81%D8%B5%D9%84-%D8%A7%D9%84%D8%AB%D8%A7%D9%86%D9%8A---%D8%A7%D9%84%D8%AA%D8%B9%D9%84%D9%8A%D9%85%D8%A7%D8%AA-%D8%A7%D9%84%D9%85%D9%86%D8%B8%D9%85%D8%A9-%D9%84%D8%A2%D9%84%D9%8A%D8%A9-%D8%A7%D9%84%D8%AA%D8%B9%D8%A7%D9%85%D9%84-%D9%85%D8%B9-%D8%A7%D9%84%D8%B4%D9%83%D8%A7%D9%88%D9%89-%D8%A8%D8%A7%D9%84%D8%A8%D9%86%D9%88%D9%83.pdf |
| S45 | CBE, "Submit a complaint" page (2 working days, 15 working days, third-party exception, escalation) - Arabic, official | 23 Mar 2023 | https://www.cbe.org.eg/ar/consumer-protection/submit-a-complaint |
| S46 | Visa Core Rules and Visa Product and Service Rules, edition of 24 Oct 2026 (official) | 24 Oct 2026 | https://corporate.visa.com/content/dam/VCOM/download/about-visa/visa-rules-public.pdf |
| S47 | Federation of Egyptian Banks, CBE issues complaint-handling instructions (Board 30 Apr 2024; quarterly reports within 30 days; 6 months to comply) | 8 May 2024 | https://febanks.com/1306367/ |
| S48 | Visa, Interlink Core Rules (Oct 2026 edition, same dispute-condition wording) and Visa "Updates and clarifications to dispute rule language" (120 / 540 days) | Oct 2026; Oct 2021 | https://usa.visa.com/content/dam/VCOM/regional/na/us/support-legal/documents/interlink-operating-regulations.pdf ; https://usa.visa.com/content/dam/VCOM/global/support-legal/documents/updates-and-clarifications-to-dispute-rule-language.pdf |
| S49 | Chambers Global Practice Guides, Data Protection & Privacy 2026: Egypt (sensitive data consent, cross-border licence, 90 working days) | 10 Mar 2026 | https://practiceguides.chambers.com/practice-guides/data-protection-privacy-2026/egypt |

---

## 9. Eval checkpoint log

Method: `output-quality-eval`, checkpoint mode. Block: **Regulation**. Pass mark 4/5.
Criteria: (1) governing bodies named; (2) every rule cited from an official or authoritative source with a date; (3) risk per category (L/M/H) justified; (4) each rule mapped to a concrete design implication; (5) unverified or unclear items marked as such.

| Block | Attempts | Score per attempt | Why it was retried | What changed between attempts | Final status |
|---|---|---|---|---|---|
| Regulation | 2 | 3 → 4 | Criterion 2 was weak: card-scheme limits rested on 2022 ombudsman quotes, not the current Visa edition; CBE complaint rules were cited from news and bank policies instead of the CBE circular; the 2019 instruction date conflicted (13 vs 19 Feb); the load-bearing "CBE does not register foreign outsourcers" claim came from an undated law-firm page without its hedge | Searched in Arabic for the CBE circular (found the official CBE PDF dated 7 May 2024 and the CBE complaint page); domain-restricted search on visa.com (found the 24 Oct 2026 Visa Core Rules and Visa's own 120/540-day wording); re-fetched Baker McKenzie and quoted its hedge, marked [Unverified]; tried Bright Data on the PDPC PDF (unreadable) and labelled the source accordingly | ✓ Passed |

**Evidence for final score (4):** all five criteria met; 9 governing bodies, 10 rules each with a dated source (official CBE, PDPC, ai.gov.eg, ITIDA, Visa, Mastercard pages where reachable; named law firms otherwise), 9 risk categories each with a reason, every rule mapped to a design change, and grey areas flagged. Not a 5 because several sources are secondary or undated (below).

**Totals:** 1 checkpoint run, 0 passed first time, 1 needed a retry and then passed, 0 below threshold.

**Open gaps (minor, labelled in the text)**
- Undated or edition-unknown sources: PDPC licences guideline (PDF unreadable to our tools), Baker McKenzie Cloud Compliance Center, Mastercard Chargeback Guide edition, CBE Financial Cybersecurity Framework issue date.
- Article number for outsourcing registration (Art. 96 per Matouk Bassiouny) not checked against the Official Gazette.
- The full 2019 CBE consumer protection text was not opened; fee-disclosure duties come from NBE and Shalakany summaries.
- No published CBE cloud rule or CBE AI guidance found; the v2 cyber framework (AI and cloud security) is known only through press reports of the CBE Financial Stability Report.

**⏸ Needs your input (cannot be closed with public research)**
- Which card schemes Nova issues on (Visa, Mastercard, Meeza): decides which dispute timelines the copilot computes.
- A legal / CBE view on whether masked prompts count as disclosure under Art. 140 and whether an LLM provider counts as an outsourcing provider: decides whether any offshore model call is allowed in production. Weakens: hosting recommendation for production (Section 5) and risk score (Section 7, ±2).
- Nova's own retention policy for call and chat records: sets the audit-log retention beyond the 180-day floor.
