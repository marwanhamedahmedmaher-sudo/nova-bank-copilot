# Competition research: AI support copilot for retail bank contact centers

Block 1D Competition. Product: an AI copilot for Nova Bank contact-center agents (dispute status, fee explanations, card replacement). It starts as agent-assist and becomes customer-facing in Phase 2. Every answer cites policy or the customer's own records, and a human approves any action that moves money. Nova Bank is fictional.

- Region: Egypt first. Anything outside Egypt is labelled **[Global]**.
- Checked: 30 Oct 2026. Every price, rating and claim below has a source URL and date.
- FX: USD 1 = EGP 56.12. This is the CBE sell rate dated 29 Oct 2026, as reported by nabdmal.com (https://nabdmal.com/en/currency-rates). I did not open cbe.org.eg directly; EdgeConsultancy reported the CBE rate at 56.23/56.33 on 26 Oct 2026, so the rate moves day to day.
- Labels: **[Assumption]** marks an estimate, not a fact. "(unverified)" marks a cell that no current source in this pass confirms.

---

## 1. Competitor list

Types follow the skill's taxonomy:
- **Direct**: sells an AI copilot or agent to bank contact centers.
- **Indirect**: solves the same contacts another way.
- **Alternative**: competes for the same budget.

### a) How Egyptian banks handle these contacts today (Indirect, the status quo)

| Bank | What they do for disputes, fees and cards today | Status check |
|---|---|---|
| **National Bank of Egypt (NBE)** | **Channels:** hotline 19623, the "Al Ahly WhatsApp" info service and a website chatbot. The chatbot shows this disclaimer: "the service is for inquiries only about products and services", and it warns customers not to share card or account data. **App:** NBE Mobile is rated 3.5★ (30,776 reviews, about 7.7M installs). Its Play listing names no card dispute or replacement flow. | **Live.** Contact page and chatbot widget: https://www.nbe.com.eg/NBE/E/#/AR/ContactUs. WhatsApp page: https://srv.nbe.com.eg/NBEWhatsApp_AR. App pull via Bright Data, 30 Oct 2026. |
| **Banque Misr** | **Channels:** the "ABKARINO" chatbot answers questions about services and products and finds the nearest ATM or branch. Hotline 19888. **App:** BM Online is rated 4.7★ (281,957 reviews, about 8.35M installs). The app reports lost cards and recently added a "Temporary Card Lock". | **Live.** Chatbot page: https://www.banquemisr.com/en/CONTACT-US/Chat-bot. App pull via Bright Data, 30 Oct 2026. |
| **CIB Egypt** | **Channels:** phone banking and IVR let customers activate cards, deactivate lost or stolen cards, submit complaints and requests, and arrange card delivery. Cards can be stopped and replaced via online banking, IVR or the call center. The legacy app listing includes "dispute credit card transactions". **App:** the new app is rated 3.1★ (11,588 reviews). Its 2026 reviews are dominated by crashes. | **Live.** Phone banking: https://www.cibeg.com/en/personal/ways-to-bank/phone-banking. FAQ: https://www.cibeg.com/en/personal/faqs?ct=3&search=Online%20Banking. App pull via Bright Data, 30 Oct 2026. |
| **QNB Egypt** | **Channels:** a WhatsApp service (+20 2 19700) for bank inquiries plus **live chat with an agent**, in-app chat with a bank representative, and hotline 19700. **App:** customers can deactivate a lost or stolen card in the app. The app is rated 4.3★ (68,260 reviews). | **Live.** https://www.qnb.com.eg/sites/qnb/qnbegypt/page/en/enwhatsapp.html. App pull via Bright Data, 30 Oct 2026. |
| **Bank ABC Egypt** (found in search) | Its app lets customers stop or freeze cards. It is rated 2.4★ in a search snippet (unverified live). | Play listing: https://play.google.com/store/apps/details?id=com.bankabc.egyapp |
| **GenAI at Egyptian banks** | I found **no verified 2025–26 public launch** of a generative-AI agent-assist tool, chatbot or Egyptian-Arabic voice bot at NBE, Banque Misr, CIB, QNB, Banque du Caire, AAIB or the digital banks. I searched in English and Arabic via Perplexity, Firecrawl and WhatsApp/chatbot pages. This is absence of evidence: private pilots may exist. | ⏸ Needs human input (see eval log) |

### b) Bank and fintech AI assistants abroad [Global] (Indirect, benchmarks)

| Assistant | What it does for this problem | Status check |
|---|---|---|
| **Bank of America Erica + EricaAssist** [Global] | **Customer-facing:** Erica passed 3 billion client interactions (Aug 2025) and 3.2 billion (Mar 2026). BofA says more than 98% of users find the information they need, which "significantly" reduces call-center volume. **Agent-facing:** EricaAssist supports about 18,000 customer-service employees and cuts average call time by almost one minute. | **Live.** https://newsroom.bankofamerica.com/content/newsroom/press-releases/2025/08/a-decade-of-ai-innovation--bofa-s-virtual-assistant-erica-surpas.html and https://newsroom.bankofamerica.com/content/newsroom/press-releases/2026/03/bofa-ai-and-digital-innovations-fuel-30-billion-client-interacti.html. The EricaAssist figures come from https://www.bankingdive.com/news/bank-of-america-generative-ai-erica-assist-customer-service/825839/ via a Perplexity summary; I did not open the article. |
| **Klarna AI assistant** [Global] | A customer-facing assistant built with OpenAI, plus AI on the human agents' desktop. It claimed the work of 700 FTE in Feb 2024 and 853 FTE in Nov 2025. In May 2025 Klarna re-introduced a guaranteed human option. | **Live.** See Lessons. |
| **Commonwealth Bank of Australia voice bot** [Global] | An inbound voice bot. CBA cut 45 call-center roles in Jul 2025, then reversed the cuts on 21 Aug 2025. | **Live** (the bank keeps the bot). See Lessons. |
| Wells Fargo Fargo, Capital One Eno, NatWest Cora+, Emirates NBD, Mashreq, Al Rajhi, ADCB, FAB [Global] | Named in the brief. No dated source in this pass shows their dispute, fee or card capability or outcomes. | Not verified, excluded from the feature map |

### c) Vendors selling AI to contact centers (Direct, the buy option for Nova)

| Vendor | What it does for this problem | Status check |
|---|---|---|
| **Intercom Fin + Copilot** [Global] | **Fin:** a customer-facing AI agent with procedures and handoff to humans, billed per outcome. **Copilot:** agent-assist, billed per seat. Fin's language list says "Arabic (Modern)". | **Live.** Pricing pages checked 30 Oct 2026 |
| **Salesforce Agentforce** [Global] | Customer-facing Service agents and employee agents. Arabic is listed as **Beta**. | **Live.** Pricing page checked 30 Oct 2026 |
| **Zendesk AI agents + Copilot** [Global] | AI agents billed per automated resolution, plus a Copilot add-on per agent. Arabic is listed, with no dialect named. | **Live.** Pricing page checked 30 Oct 2026 |
| **Google Cloud Agent Assist / Customer Engagement Suite** [Global] | Real-time knowledge assist, summarization, AI coach and sentiment. Customer-facing Conversational Agents are a separate SKU. Generative features list generic Arabic ("ar"). | **Live.** Pricing page checked 30 Oct 2026 |
| **Amazon Connect Customer** (formerly Amazon Connect / Q in Connect) [Global] | A full cloud contact center with "real-time agent assist", agentic self-service and post-contact summaries, all inside per-minute or per-message pricing. Docs list Arabic as MSA (ar-SA) and Gulf (ar-AE), **not Egyptian**. | **Live.** Pricing page scraped via Bright Data, 30 Oct 2026 |
| **Microsoft Dynamics 365 Contact Center / Customer Service (Copilot)** [Global] | A representative desktop with Copilot: Q&A over knowledge, case and conversation summaries, real-time translation. Agents run on Copilot Credits. Docs list Arabic for summaries, with no dialect. | **Live.** Pricing pages checked 30 Oct 2026 |
| **Maqsam** (Jordan/KSA, MENA) | A contact-center platform with a voice-first AI agent. It says the agent serves **Egyptian Arabic** as well as Gulf, Levantine and MSA (vendor claim). | **Live.** Blog dated 8 Dec 2025 (https://maqsam.com/blog/what-is-an-ai-agent-8-clear-answers-to-the-most-common-questions) and LEAP 2026 event page (https://maqsam.com/events/leap-2026) |
| **intella** (Egypt) | Arabic speech recognition and call-center analytics, used for call audits. A secondary source reports 25+ dialects and a Visa partnership for MENA financial institutions. | **Live as of 25 Sep 2025.** https://www.thisweekinfintech.com/p/finance-finds-its-voice-twif-mena-25-09/ |
| **WideBot** (Egypt) | Arabic chatbot builder and Arabic LLM, with 2025 funding. Its contact-center capability is unverified. | Mar 2025 coverage: https://aibase.ng/ai-africa/the-five-countries-capturing-90-of-africas-ai-funding/ |
| **SMB Arabic chat vendors**: Nateq, Entagl, Modeer 360 | WhatsApp and web AI agents that claim Egyptian Arabic **and Franco-Arabic (Arabizi)**. They target SMBs. I found no bank-grade compliance evidence. | Vendor blogs dated Aug–Oct 2026: https://nateq.io/blog/franco-arabic, https://www.entagl.com/blog/arabic-ai-customer-service-gulf-dialects, https://modeer360.com/en/blog/arabic-dialect-chatbot |
| Sprinklr, Yellow.ai, Kore.ai, Arabot, Lucidya | Commonly cited in MENA. Perplexity found no dated source confirming Egyptian-dialect contact-center capability or an Egyptian bank customer. | Not verified, excluded from the feature map |

**Alternative competitors (same budget, not AI):**
- hiring more agents to absorb volume growth of +15% a year;
- outsourcing to a BPO;
- investing in app self-service instead. The BM Online "Temporary Card Lock" shows banks already doing this.

---

## 2. Feature map

Legend:
- ✅ = present, confirmed by a current source
- ⚠️ = partial or limited
- ❌ = absent
- (unverified) = no current source found, so the cell is a best reading

Egyptian-bank rows describe the bank's own customer channels, not a vendor product.

| Competitor | Agent-assist | Customer-facing | Cites sources / grounding | Arabic + Egyptian dialect | Human handoff | Actions with human approval | Audit trail | Pricing model |
|---|---|---|---|---|---|---|---|---|
| **Nova copilot (planned)** | ✅ Phase 1 | ⚠️ Phase 2 | ✅ policy + customer record on every answer (design) | ✅ EN, formal Arabic, Egyptian, Franco (design, not yet tested) | ✅ agent is the human in Phase 1 | ✅ money moves need agent approval (design) | ✅ (design) | Internal build **[Assumption: in-house cost]** |
| NBE | ❌ (unverified) | ⚠️ web chatbot + WhatsApp, inquiries only | ❌ (unverified) | ⚠️ Arabic UI; dialect handling (unverified) | ⚠️ hotline 19623 listed; in-bot handoff (unverified) | ❌ bot is inquiries-only | (unverified) | n/a, in-house |
| Banque Misr | ❌ (unverified) | ⚠️ ABKARINO FAQ/locator bot | ❌ (unverified) | ⚠️ Arabic (unverified dialect) | ⚠️ hotline 19888; in-bot handoff (unverified) | ⚠️ app self-service card lock; not AI | (unverified) | n/a, in-house |
| CIB | ❌ (unverified) | ⚠️ IVR + app self-service (dispute, replace card); no AI bot found | ❌ (unverified) | ⚠️ Arabic (unverified dialect) | ✅ call center via IVR | ⚠️ self-service flows; not AI | (unverified) | n/a, in-house |
| QNB Egypt | ❌ (unverified) | ✅ WhatsApp + in-app chat with live agent | ❌ (unverified) | ⚠️ Arabic (unverified dialect) | ✅ live chat to a representative | ⚠️ app card deactivation; not AI | (unverified) | n/a, in-house |
| BofA Erica / EricaAssist [Global] | ✅ EricaAssist, about 18k agents | ✅ Erica | ⚠️ (unverified) | ❌ US market | ⚠️ (unverified) | ⚠️ (unverified) | ⚠️ (unverified) | n/a, in-house |
| Klarna AI assistant [Global] | ✅ AI on agent desktop (CX Dive, Nov 2025) | ✅ | ⚠️ (unverified) | ❌ not documented | ✅ "always a human" since May 2025 | ⚠️ (unverified) | ⚠️ (unverified) | n/a, built on OpenAI |
| Intercom Fin + Copilot [Global] | ✅ Copilot | ✅ Fin | ⚠️ knowledge-grounded; citation display (unverified) | ⚠️ "Arabic (Modern)" only | ✅ procedure handoff is a billed outcome | ⚠️ procedures; approval gate (unverified) | ⚠️ (unverified) | Per outcome + per seat |
| Salesforce Agentforce [Global] | ✅ employee agents | ✅ Service agents | ⚠️ (unverified) | ⚠️ Arabic **Beta**, no dialect | ⚠️ (unverified) | ⚠️ (unverified) | ⚠️ (unverified) | Per conversation / credits / per seat |
| Zendesk AI [Global] | ✅ Copilot add-on | ✅ AI agents | ⚠️ (unverified) | ⚠️ Arabic, no dialect | ✅ escalation is part of the resolution definition | ⚠️ (unverified) | ⚠️ (unverified) | Per resolution + per seat |
| Google Agent Assist [Global] | ✅ knowledge assist, summary, coach | ⚠️ separate Conversational Agents SKU | ⚠️ knowledge assist over data stores; citations (unverified) | ⚠️ generic "ar" for gen features; no ar-EG listed | ⚠️ depends on CCaaS (unverified) | ⚠️ (unverified) | ⚠️ (unverified) | Usage (per message / minute) |
| Amazon Connect Customer [Global] | ✅ real-time agent assist | ✅ agentic self-service | ⚠️ (unverified) | ⚠️ MSA (ar-SA) + Gulf (ar-AE), no Egyptian | ✅ native contact-center routing | ⚠️ (unverified) | ⚠️ (unverified) | Usage, AI included |
| Microsoft D365 Contact Center [Global] | ✅ Copilot in rep desktop | ✅ self-service IVR / agents (credits) | ⚠️ Q&A over knowledge; citations (unverified) | ⚠️ "Arabic", no dialect | ✅ native routing | ⚠️ (unverified) | ⚠️ (unverified) | Per seat + credits |
| Maqsam (MENA) | ⚠️ human–AI collaboration (unverified detail) | ✅ voice AI agent | ❌ (unverified) | ✅ Egyptian Arabic listed (vendor claim) | ✅ contact-center platform (unverified detail) | ❌ (unverified) | (unverified) | Not published |
| intella (Egypt) | ⚠️ speech analytics / call audits | ❌ | ❌ n/a | ⚠️ 25+ dialects; Egyptian not explicitly confirmed | ❌ n/a | ❌ n/a | ⚠️ call-audit use (unverified) | Not published |

Sources for the Arabic column:
- Google: https://docs.cloud.google.com/agent-assist/docs/languages
- Salesforce: https://help.salesforce.com/s/articleView?id=service.service_agent_considerations.htm&language=en_US&type=5
- Zendesk: https://support.zendesk.com/hc/en-us/articles/8357749663130-Languages-supported-by-AI-agents
- Amazon: https://docs.aws.amazon.com/connect/latest/adminguide/supported-languages.html
- Microsoft: https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/cs-region-availability-service-limits
- Intercom: https://www.intercom.com/help/en/articles/8322387-set-up-fin-ai-agent-s-multilingual-support

Perplexity read these docs, and I opened the Intercom page directly. Checked 30 Oct 2026.

---

## 3. Pricing benchmarks [Global list prices, USD]

Prices are shown as EGP (USD) at USD 1 = EGP 56.12. None of these vendors publishes an Egypt-specific price list, so treat every row as a global list price.

| Vendor | Pricing model | Published price | Source URL | Date checked |
|---|---|---|---|---|
| Intercom Fin AI Agent | **Per resolution/outcome** | EGP 55.6 ($0.99) per outcome, billed with a base plan from EGP 2,750 ($49)/month, plus helpdesk seats | https://www.intercom.com/help/en/articles/8205718-fin-ai-agent-outcomes ; https://fin.ai/help/en/articles/13975800-fin-pricing-outcomes | 30 Oct 2026 |
| Intercom Copilot (agent-assist) | **Per seat** | EGP 1,627 ($29)/agent/month annual; EGP 1,964 ($35) monthly; unlimited use | https://www.intercom.com/pricing | 30 Oct 2026 |
| Salesforce Agentforce | **Per conversation** | EGP 112 ($2) per conversation (customer-facing) | https://www.salesforce.com/agentforce/pricing/ | 30 Oct 2026 |
| Salesforce Agentforce | **Per resolution** | EGP 112 ($2) per Help Agent resolution | https://www.salesforce.com/agentforce/pricing/ | 30 Oct 2026 |
| Salesforce Agentforce | **Usage** (Flex Credits) | EGP 28,060 ($500) per 100,000 credits. That is about $0.10 per standard action, per third-party analysis (https://pluno.ai/blog/salesforce-agentforce-pricing) | https://www.salesforce.com/agentforce/pricing/ | 30 Oct 2026 |
| Salesforce Agentforce | **Per seat** | EGP 7,015 ($125)/user/month flat-fee access; or EGP 281 ($5)/user/month license plus credits | https://www.salesforce.com/agentforce/pricing/ | 30 Oct 2026 |
| Zendesk AI agents | **Per resolution** | EGP 84 ($1.50) committed or EGP 112 ($2.00) pay-as-you-go per automated resolution beyond the plan allowance | Third-party: https://helply.com/blog/zendesk-pricing ; https://www.mavenagi.com/blog/zendesk-ai-agents-pricing (official model: https://support.zendesk.com/hc/en-us/articles/5352026794010) | 30 Oct 2026, **rate not confirmed on a Zendesk page** |
| Zendesk Copilot (agent-assist) | **Per seat** | EGP 2,806 ($50)/agent/month, paid yearly, on Suite Professional and above | https://www.zendesk.com/pricing/ | 30 Oct 2026 |
| Google Agent Assist | **Usage** | Chat EGP 0.11–0.17 ($0.002–$0.003) per message; voice EGP 1.68 ($0.03)/min Standard, EGP 2.81 ($0.05)/min Enterprise | https://cloud.google.com/agent-assist/pricing | 30 Oct 2026 |
| Google Agent Assist | **Per conversation** ⚠️ conflicts with the row above | EGP 3.37 ($0.06) per chat session; voice "contact your representative" | https://cloud.google.com/gemini-enterprise-cx/agent-assist | 30 Oct 2026 |
| Google Conversational Agents (CX Agent Studio) | **Per conversation** | EGP 28 ($0.50) per session | Third-party: https://www.getmacha.com/blog/google-customer-engagement-suite-complete-guide (dated 24 Sep 2026) | 30 Oct 2026, **not confirmed on a Google page** |
| Amazon Connect Customer | **Usage** (AI included, no seats) | Voice EGP 2.13 ($0.038)/min plus telephony; chat EGP 0.56 ($0.010)/message; email EGP 4.49 ($0.080); SMS/3P messaging EGP 0.79 ($0.014) | https://aws.amazon.com/products/connect/customer/pricing/ | 30 Oct 2026 |
| Microsoft D365 Contact Center | **Per seat** | EGP 6,173 ($110)/user/month (Digital or Voice only: EGP 5,331, $95); AI agents need Copilot Credits | https://www.microsoft.com/en-us/dynamics-365/products/contact-center/pricing | 30 Oct 2026 |
| Microsoft D365 Customer Service | **Per seat** | Enterprise, Copilot included: EGP 5,893 ($105)/user/month; Premium: EGP 10,943 ($195) | https://www.microsoft.com/en-us/dynamics-365/products/customer-service/pricing | 30 Oct 2026 |
| Microsoft Copilot Credits | **Usage** | EGP 0.56 ($0.01) per credit pay-as-you-go; EGP 11,224 ($200) per 25,000-credit pack per month | https://www.microsoft.com/licensing/guidance/Microsoft-Copilot-Studio ; https://www.microsoft.com/en-us/copilot/pricing/copilot-studio | 30 Oct 2026 |
| Maqsam / intella / WideBot | Not published | No public price found | — | 30 Oct 2026, ⏸ quote needed |

**Conflicts and caveats:**
- **Google: two official pages disagree.** The pricing page has per-message and per-minute SKUs; the product page says $0.06 per chat session. Use the pricing page, which has SKU IDs, and ask Google sales before quoting either on a slide.
- **Microsoft Copilot for Service at $50/user/month.** A third party calls this "the last confirmed" price (https://coworker.ai/blog/microsoft-copilot-enterprise-pricing). Current Microsoft pages show Copilot Credits instead, so I left the $50 figure out of the table.
- **Amazon Q in Connect at $40/agent/month** is quoted by Nextiva (https://www.nextiva.com/blog/amazon-connect-pricing.html). The current AWS page bundles AI into per-minute pricing, so treat $40 as legacy.

**What this means for Nova at its volume [Assumption-based illustration]:**
- **Inputs:** 120 agents and 45,000 contacts a month, 60% in scope (27,000).
- **[Assumption]** Average voice handle time is 6 minutes.
- **[Assumption]** Phase 2 AI resolution rate is 50%.

| Option | Monthly cost |
|---|---|
| Intercom Copilot, 120 seats | EGP 195,298 ($3,480) |
| Zendesk Copilot, 120 seats | EGP 336,720 ($6,000) |
| Google Agent Assist Voice Standard, 270,000 min | EGP 454,572 ($8,100) |
| Google Agent Assist Voice Enterprise | EGP 757,620 ($13,500) |
| Microsoft D365 Contact Center, 120 seats (a full platform, not only a copilot) | EGP 740,784 ($13,200) |
| Phase 2: Fin, 13,500 outcomes | EGP 750,044 ($13,365) |
| Phase 2: Zendesk, 13,500 resolutions at $1.50 | EGP 1,136,430 ($20,250) |
| Phase 2: Salesforce, 27,000 conversations at $2 | EGP 3,030,480 ($54,000) |

**Takeaway for the pricing slide:** agent-assist is a per-seat market ($29–$50/agent/month), while customer-facing AI is priced per resolution or per conversation ($0.99–$2.00). Usage pricing (Google, AWS) is cheapest per contact but scales with call minutes.

---

## 4. Lessons: what worked and what backfired [Global]

**What worked**
- **Agent-first assist at scale (BofA).** EricaAssist supports about 18,000 service employees and cuts average call time by almost one minute. Customer-facing Erica passed 3.2 billion interactions by Mar 2026, and BofA says more than 98% of users find what they need.
  - https://www.bankingdive.com/news/bank-of-america-generative-ai-erica-assist-customer-service/825839/ (via Perplexity summary)
  - https://newsroom.bankofamerica.com/content/newsroom/press-releases/2026/03/bofa-ai-and-digital-innovations-fuel-30-billion-client-interacti.html
- **Routine volume automates well (Klarna).**
  - Feb 2024: two-thirds of chats (2.3M) handled in the first month, with resolution in under 2 minutes against 11 for humans. https://openai.com/index/klarna/
  - Nov 2025: the work of 853 FTE, with $60M saved. https://finance.yahoo.com/news/klarna-says-ai-agent-doing-070000869.html (CX Dive, 20 Nov 2025)

**What backfired**
- **Klarna cut too deep and quality fell.**
  - In May 2025 the CEO told Bloomberg that when cost is "too predominant" an evaluation factor, "what you end up having is lower quality." Klarna started rehiring so customers always have a human option. https://www.customerexperiencedive.com/news/klarna-reinvests-human-talent-customer-service-AI-chatbot/747586/ ; https://www.bloomberg.com/news/articles/2025-05-08/klarna-turns-from-ai-to-real-person-customer-service
  - In Nov 2025 customers still reported the AI could not handle nuanced questions, and Klarna had laid off agents with institutional knowledge. Customer service and operations cost rose to $50M in Q3 2025 from $42M a year earlier. https://finance.yahoo.com/news/klarna-says-ai-agent-doing-070000869.html
  - ⚠️ **Conflicting framing:** Klarna says it is "not reversing on AI", that the assistant does the work of 800+ roles, and that it still uses several thousand outsourced agents (statement quoted by Forbes, 18 May 2025: https://www.forbes.com/sites/quickerbettertech/2025/05/18/business-tech-news-klarna-reverses-on-ai-says-customers-like-talking-to-people/). Read it as a **scope correction**: AI keeps routine volume and humans take complex cases. It was not a full reversal.
- **CBA linked job cuts to a voice bot and had to undo them.**
  - In Jul 2025 CBA cut 45 call-center roles, citing a voice bot. On 21 Aug 2025 it reversed the cuts after a Fair Work Commission challenge.
  - ⚠️ **Conflict:** the bank said the bot cut 2,000 calls a week, but the union said volumes were rising and staff were on overtime.
  - CBA keeps using the bot. https://www.bloomberg.com/news/articles/2025-08-21/commonwealth-bank-reverses-job-cuts-decision-over-ai-chatbots ; https://www.afr.com/work-and-careers/workplace/cba-u-turns-on-ai-job-cuts-calls-back-humans-20250820-p5moif
- **The company is liable for what its bot says about policy.** In *Moffatt v. Air Canada* (BC Civil Resolution Tribunal, 14 Feb 2024), a chatbot misstated a refund policy and the airline was held liable. https://www.americanbar.org/groups/business_law/resources/business-law-today/2024-february/bc-tribunal-confirms-companies-remain-liable-information-provided-ai-chatbot/
- **Regulators react to "doom loops".** The CFPB (6 Jun 2023) warned that chatbots blocking access to live human support "can lead to law violations". https://www.consumerfinance.gov/data-research/research-reports/chatbots-in-consumer-finance/chatbots-in-consumer-finance/

**Implication for Nova:**
- Lead with agent-assist, as BofA did.
- Keep a guaranteed human path, the lesson from Klarna and CBA.
- Make citations a liability control, the lesson from Air Canada.
- Do not sell it as headcount reduction. Volume is growing 15% a year, so the pitch is to absorb growth, not cut staff.

---

## 5. Gaps we can own

1. **Bank-grade Egyptian Arabic and Franco-Arabic.**
   - **Evidence:** no global vendor documents Egyptian Arabic:
     - Intercom: "Arabic (Modern)" only.
     - Amazon: MSA and Gulf only.
     - Salesforce: Arabic in Beta.
     - Google, Zendesk, Microsoft: generic "Arabic".
   - Dialect and Franco support exists only at SMB chat vendors (Nateq, Entagl, Modeer 360) and in a voice vendor's claim (Maqsam). None of them shows bank-grade grounding, approval or audit.
   - **The gap:** dialect plus bank compliance in one product.
2. **Agent-assist inside Egyptian bank contact centers is unclaimed.**
   - **Evidence:** the bots at NBE and Banque Misr are inquiries-only or FAQ bots; NBE's chatbot tells customers not to share card or account data. No genAI agent-assist launch was found at the big four.
   - BofA's EricaAssist (about 18k agents, about 1 minute off each call) shows the agent-first model works at scale.
3. **Answers built from the customer's own records, with citations, for dispute status and fees.**
   - **Evidence:** Egyptian bank bots do not touch customer records. Global vendors ground answers in generic knowledge bases; linking bank policy to core-banking records is integration work they leave to the buyer (unverified for each vendor).
   - Fee questions are concrete: CIB publishes card replacement and renewal fees per card on its product pages (https://www.cibeg.com/en/personal/cards/debit/debit).
   - The Air Canada ruling turns "cite the policy" from a nice-to-have into a liability control.
4. **Human approval designed in, not bolted on.**
   - **Evidence:** the Klarna and CBA episodes plus the CFPB warning show that "replace the agent" positioning backfires. Nova's design (suggest only, human approves money moves, always a human) is the counter-position.
   - Most vendor pages sell autonomous resolution per outcome; I found no vendor that markets approval-gated money actions. This is unverified and should be checked in demos.
5. **Spillover from digital failures is a hidden driver of contacts.**
   - **Evidence:** Oct 2026 Play reviews show login, OTP and crash failures pushing customers to the call center or branch. A BM Online review on 4 Oct 2026 says the app sends the customer to customer service, but the line is busy. NBE (Sep 2026) and CIB (Apr–Sep 2026) show similar failures.
   - The copilot's intent set should include "card locked / app or OTP failed" triage next to card replacement. **[Assumption]** the share of these contacts at Nova is unknown.

**Summary:** Nova's copilot competes most closely with Intercom Fin/Copilot and Zendesk Copilot on the buy side, and with BofA's EricaAssist as the reference model. The biggest differentiation opportunity is grounded, cited, approval-gated answers in Egyptian Arabic and Franco-Arabic inside an Egyptian bank's contact center.

**Competitor differentiation outlook:**
- **Global contact-center AI:** intensity is **high**, with many funded vendors and published price points.
- **Egypt, bank-grade, dialect-native agent-assist:** intensity is **low to medium**. No incumbent was found, but global platforms could add dialect support quickly.
- **Competition score: 6/10 [judgement].** The tools are saturated, but this niche is open.

---

## 6. Eval checkpoint log (output-quality-eval, checkpoint mode)

**Block:** 1D Competition. **Pass mark:** 4 of 5.

**Criteria:**
1. Competitor status verified as current.
2. Conflicting sources flagged.
3. Feature map uses ✅/⚠️/❌ consistently, with unverified cells marked.
4. Gaps tied to evidence.
5. Vendor prices have a source and date.

| Attempt | Score | Why it fell short / what changed |
|---|---|---|
| 1 | **3** | **Approach:** Perplexity and Firecrawl search snippets. **Weak points:** the Microsoft price relied on a third-party "$50/user" claim; the two Google pricing pages conflicted and were unresolved; app ratings came from search snippets that disagreed with each other and with the live data (NBE 2.7★ and 3.0★ in snippets against 3.5★ live; CIB 2.8★ against 3.1★); the Franco-Arabic gap was asserted without a targeted search. |
| 2 | **4** | **Changed approach:** a live Bright Data Play Store pull (4 records) replaced the snippet ratings; the AWS pricing page was scraped directly with Bright Data; Microsoft prices were confirmed in the official Copilot Studio licensing guidance through a domain-restricted search, after the Bright Data scrape failed; both Google pages were re-read and the conflict is flagged, not resolved; I ran a targeted Arabizi/Franco search, which found SMB vendors and sharpened gap 1. Firecrawl ran out of credits mid-run, so Perplexity and Bright Data covered the rest. |

**Final:** ✓ Passed (4/5), 2 attempts.

**Per-criterion check:**
1. Met. Egyptian bank pages and app data are dated Oct 2026; vendor pricing pages were checked 30 Oct 2026.
2. Met. Flagged conflicts: Google pricing, Klarna framing, CBA call volumes, Microsoft $50, Amazon Q $40, snippet against live app ratings.
3. Met. Symbols are consistent and unverified cells are marked.
4. Met. Each gap cites evidence.
5. Met, except that the Zendesk per-resolution rate and the Google CX Agent Studio rate rest on third-party pages, as labelled.

**Open gaps:**
- ⏸ **Private genAI pilots at Egyptian banks.** Public sources show none; confirming needs an industry contact or a CBE or bank insider. This weakens gap 2.
- ⏸ **MENA vendor pricing** (Maqsam, intella, WideBot) needs sales quotes. This weakens the pricing slide for the "buy local" option.
- ⏸ **The CBE complaint deadline.** A secondary source says banks must respond within 15 days (https://www.upstreamworks.com/answers/cisco-finesse-banking-egypt/), but I did not find the primary CBE circular. Hand this to the regulation block (research/regulation.md).
- ⚠️ Many feature-map cells for grounding, approval and audit stay "(unverified)" for global vendors. Public docs do not settle them; vendor demos would.
- The EricaAssist figures come from a Perplexity summary of Banking Dive; I did not open the article.

**Bright Data credits used:**
- 4 `web_data` records: Google Play Store collect_by_url for NBE, Banque Misr, CIB and QNB.
- 3 `scrape_as_markdown` requests: AWS succeeded; Google returned "endpoint not supported"; Microsoft failed to parse.
- Total ≈ 7 of the 100-record cap.

Firecrawl ran out of credits during the run; its daily allowance refreshes in about 18 hours.
