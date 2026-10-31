# 1B Customer pain points: Egyptian retail bank customers

Prepared 30 Oct 2026 for the Nova Bank AI copilot capstone. Nova Bank is fictional, so this file looks at real customers of Egyptian banks: NBE, Banque Misr (BM), CIB, QNB Egypt, Banque du Caire (BDC), AAIB, HSBC Egypt, plus InstaPay.

Method: customer posts were coded into themes by keyword and then checked by reading them. No reviewer names, usernames or profile links appear here. Each source is cited by its post or listing URL, as Egypt's Personal Data Protection Law 151/2020 requires. Quotes are verbatim and trimmed with "...", with an English translation in brackets. A quote marked *paraphrase* came from a search excerpt and is not the poster's exact words.

## Coverage

| Item | Detail |
| --- | --- |
| Window | Nov 2025 to 30 Oct 2026. The last 90 days are weighted highest: 211 of the 230 app reviews date from 1 Aug to 29 Oct 2026 |
| Languages | Arabic (formal and Egyptian dialect) and English. No separate Franco-Arabic search was run (gap) |
| Google Play (Bright Data, Google Play reviews scraper) | 230 reviews from the Egyptian store (`country=EG`, `gl=eg`; every record shows app_country EG), dated 1 Jul to 29 Oct 2026. 30 each for NBE Mobile, BM Online, CIB Mobile Banking, QNB Egypt Mobile Banking, BDC Digital Banking, AAIB Mobile and HSBC EG, plus 20 for InstaPay. Reviews came newest first |
| Reddit (Bright Data, Reddit Posts scraper; threads found with Perplexity) | 7 threads with comments, from r/PersonalFinanceEgypt, r/Egypt and r/askegypt, Nov 2025 to Oct 2026. 3 more threads are cited from search excerpts only (marked *paraphrase*) |
| Instagram (Bright Data, Instagram Posts and Comments scrapers) | Banque Misr's 6 most recent posts (Aug to Oct 2026), plus all 61 comments on one reel (2 Oct 2026) |
| News, regulator and complaint guides (Perplexity for discovery; 2 pages read in full with Bright Data) | CBE Financial Stability Report coverage, CBE deputy governor statements, Cabinet complaints-platform releases, Al-Ahram Weekly, Al Jazeera, Al-Masry Al-Youm, El Watan, EgyptInOrder complaint guides |
| Firecrawl | Used only to find app package IDs (2 searches, 5 app lookups). Its credits then ran out, so its review pulls were refused |
| Skipped or blocked | YouTube (blocked on Bright Data until compliance approval). Facebook: no public bank posts with complaints were found, and groups are out of scope. Apple App Store, X, TikTok and Trustpilot were not pulled for lack of Bright Data budget. The almaal.org NBE hotline page has 580 comments, but all are dated 2019 to 2023, so they were left out as too old |
| Bright Data dataset records | 304, against a cap of 300 (4 over). See the eval log |

Assumption: a few posters are Egyptians living abroad. They are customers of Egyptian banks and are kept as local users. No tourist posts were used.

## Pain-point themes, ranked

Each theme was ranked on three things:

- **Frequency:** dated customer mentions within the window, and on how many platforms.
- **Severity:** 1 is an annoyance, 2 needs a workaround, 3 blocks the job or loses money or trust.
- **Impact:** how many customers it hits and how it links to repeat calls, complaints, regulatory escalation or churn.

The "Copilot intent" column maps each theme to the copilot's scope.

| # | Theme | Frequency | Severity | Impact | Platforms | Representative quote (source, date) | Recent 90 days trend | Copilot intent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **The app, login, OTP or token fails, so the customer has to call or visit a branch** | 89 of 230 reviews (39%), at all 8 apps; plus 1 Reddit thread and 1 Instagram comment | 3 | Very high. It is the largest single source of contacts: customers locked out of their money call the hotline or go to a branch. Android versions below 12 were dropped by QNB, AAIB and HSBC | Google Play, Reddit, Instagram | "app have bug for 2 days now for hundred of android user" (Google Play, NBE Mobile, 15 Oct 2026). "a physical branch is faster and more reliable than opening this thing" (Google Play, CIB, 14 Oct 2026) | Rising. An update wave in mid-October: at least 9 NBE reviews on 15 Oct 2026 alone describe the same token or login outage | other (triage and workaround) |
| 2 | **The contact center can't be reached, gives no resolution, and customers have to call again and again** | 18 of 230 reviews (8%), at all 8 apps; 4 Reddit threads; 3 Instagram comments | 3 | High. Long holds, dropped calls and conflicting answers lead to repeat calls and branch visits. About 63k complaints a year reach the CBE because banks did not resolve them (see Numbers) | Google Play, Reddit, Instagram, plus CBE data | "خدمة العملاء بيعلقوا المكالمه وقت طويل وبعد كده الخط يفصل" [customer service leave you on hold a long time, then the line drops] (Google Play, BDC, 1 Oct 2026). "I already made about 7 complaints since last May ... but all complaints in vain" (Google Play, CIB, 27 Oct 2026). "خسرت أكتر من ألفين جنيه رصيد مكالمات دولية وفي الآخر محدش رد" [I lost over EGP 2,000 in international call credit and in the end no one answered] (Instagram, Banque Misr reel, 29 Oct 2026) | Rising. Most of these mentions are from Oct 2026 | other (wait time and repeat contact; the copilot cuts handle time) |
| 3 | **Unexplained deductions, holds and fees** | 7 reviews (3%) across 5 apps; 3 Reddit threads; 1 Instagram comment; 2 news features | 2 to 3 | High trust impact. Customers read an unexplained deduction as theft ("حرامي", "نهب" [thief, robbery]), and fee questions are routine contact-center work | Google Play, Reddit, Instagram, news | "خصم 200 جنيه بحجة مصاريف للكارت ده غير خصم 30 كل شهر لو الحساب أقل من 3000" [EGP 200 taken as a card fee, plus 30 every month if the balance is under 3,000] (Google Play, BM Online, 24 Oct 2026). "the new application doesn't tell you why money is on hold" (Google Play, BDC, 29 Oct 2026). "I recieved a SMS saying I was charged 35 EGP" after a refund was approved (Reddit r/askegypt, 8 Nov 2025) | Stable to rising. A national news feature on hidden bank fees ran on 10 Jul 2026, and a guide to deductions from dormant accounts on 18 Oct 2026, both signs of public interest | **fee_explanation** |
| 4 | **Disputed or unknown transactions, failed ATM cash or deposits, and tracking refunds or transfers** | 4 Reddit threads; 1 Instagram comment; 3 Play reviews about unexplained holds; 2 news cases | 3 | High. Money is at stake. The fraud wave makes it worse (57% of digital finance users have been targeted by phishing). Customers lose track of the complaint reference and the 15-working-day clock | Reddit, Instagram, Google Play, news | "I was given several conflicting stories: that there were no visible transactions, or that my support tickets were rejected" (Reddit r/PersonalFinanceEgypt, BM wire transfer, 25 Jan 2026). "عملت شكوى في التيليفون وقولتوا لي خلاص ... ولسة الرسايل بتيجي" [I complained by phone, you said it's sorted ... and the transaction texts still come] (Instagram, Banque Misr reel, 3 Oct 2026). *Paraphrase:* an EGP 800 ATM deposit failed and the hotline promised a reply within 10 days (Reddit r/Egypt, 14 Jun 2026) | Steady. Each case is high-stakes, and fraud warnings are a constant theme in bank posts (Oct 2026) | **dispute_status** |
| 5 | **Card lifecycle: activation, delivery, cancellation and replacement** | 4 Reddit threads; 1 Play review; 1 Instagram comment; 2 news items. **Low evidence for lost or stolen replacement delays specifically**: no direct Egyptian customer complaint was found in the window | 2 to 3 | Medium. A replacement costs EGP 150 to 300 at NBE. Cards held at the branch, wrong addresses and requests that loop all cause repeat calls | Reddit, Google Play, Instagram, news | "قالوا ان لا معلش انت الكارت الجديد تم إصداره ومحتاجين الرقم بتاعه" [they said sorry, a new card was issued and we need its number] (Reddit r/PersonalFinanceEgypt, BM, 8 Dec 2025). "I can't activation my credit card" (Google Play, AAIB, 25 Jul 2026). "بتصل بخدمه العملاء القي العنوان بتاعي مش موجود" [I call customer service and find my address isn't on file] (Reddit r/PersonalFinanceEgypt, CIB, 30 Mar 2026) | Unclear. NBE now promotes card blocking and replacement in its app (Sep 2026), which may shift volume toward "where is my card" calls | **card_replacement** |
| 6 | **Customers abroad are locked out because OTP and soft tokens are tied to an Egyptian SIM, so they have to phone in** | 4 reviews (BM ×2, InstaPay ×2); 1 Instagram comment | 3 | Narrow but severe: the customer can't get to their money from abroad, and international calls cost them | Google Play, Instagram | "لازم تتصل برقم واحنا عايشين بره مصر مش قادرين نتصل" [you have to call a number, and we live outside Egypt and can't call] (Google Play, BM Online, 15 Oct 2026) | Rising (all mentions are from Oct 2026) | other (Phase 2 customer-facing) |

Why this ranking. Theme 1 is by far the most frequent and is severity 3, but it sits in "other": it is what generates calls. It is not one of the copilot's three intents. Themes 2 to 4 are all severity 3 and show up across platforms. The contact-center theme (2) comes before fees and disputes (3, 4) because it appears at every bank and is the problem the copilot attacks most directly. Fees come before disputes on frequency, but disputes are worse per case. Card replacement ranks 5th because its customer-voice evidence is thin.

Assumption: reviews were pulled newest first in a month of app updates, so app-crash complaints (theme 1) are probably over-represented compared with a full-year sample. These shares are for the sample only, not the population.

Sentiment in the review sample: 175 of 230 (76%) gave 1 or 2 stars and 50 (22%) gave 4 or 5. Average rating by app: BDC 1.13, HSBC EG 1.13, CIB 1.27, AAIB 1.53, NBE 1.93, QNB 2.27, InstaPay 2.55, BM Online 3.73.

## Unmet needs

| Need | Evidence (source, date) |
| --- | --- |
| See why money is held or deducted (merchant, date, reason) without calling | Google Play: BM Online (19 Oct 2026) says pending transactions show no merchant or date; CIB (12 Oct 2026) "doesn't show held transactions"; BDC (29 Oct 2026) |
| Track a complaint, cancellation or dispute against its reference number and get one consistent answer | Reddit: BM credit card cancellation dragged on for 1.5 months (8 Dec 2025); BM wire transfer gave "conflicting stories" (25 Jan 2026) |
| Get through without long holds | Google Play: BDC (1 Oct 2026), HSBC (29 Jul 2026); Instagram (29 Oct 2026) |
| Reset a token or OTP from abroad | Google Play: BM (15 and 27 Oct 2026); Instagram (29 Oct 2026) |

## Feature requests

| Request | Evidence (source, date) |
| --- | --- |
| A call-back instead of waiting on hold (QNB already offers this and is praised for it) | Reddit r/PersonalFinanceEgypt (30 Mar 2026) |
| A written explanation of fees, for example a paper statement fee | Instagram, Banque Misr reel (20 Oct 2026) |
| Fingerprint login | Google Play: HSBC EG (4 and 7 Oct 2026), BDC (1 and 5 Oct 2026) |
| More services in the app (funds, certificates) so customers don't need to call | Instagram, Banque Misr (28 Oct 2026); Google Play, BM Online (25 Oct 2026) |

## Positives to protect

- Instant transfers: "الحاجة بتتحول في ساعتها" [money moves instantly] (Google Play, CIB, 28 Oct 2026).
- An instant SMS for every debit or credit (Google Play, BM Online, 19 Oct 2026). Customers rely on these alerts to spot disputes early.
- A queue call-back: "لو هيطول ... هما بيكلموك" [if the wait is long ... they call you back] (Reddit, QNB, 30 Mar 2026).
- Agents who answer quickly: "CIB for sure, top-notch customer service." (Reddit, 29 Oct 2026). Arab Bank's phone support "never put me on hold waiting" (Reddit, 30 Mar 2026).
- BM Online is the clear outlier in the sample, with an average of 3.73 and a 4.7 store rating.

## Summary

1. The top three pains are: apps and tokens failing, which pushes customers onto the phone (39% of sampled reviews); a contact center they can't reach or that doesn't resolve the problem; and unexplained deductions, holds and fees, with disputed transactions close behind on severity.
2. They hit everyday mobile-first customers at every bank, worst at BDC, HSBC EG, CIB and AAIB, and they hit Egyptians abroad hardest, since they depend on SIM-bound OTPs and costly international calls.
3. The clearest opportunity for the copilot is to give agents one view, for any held, unknown or disputed transaction or fee, of what happened, which fee rule applied, and where the case stands against the CBE's 15-working-day clock. That cuts the repeat calls and conflicting answers customers complain about most.

## Numbers we can use in the business case

| # | Number | Source and date |
| --- | --- | --- |
| 1 | Banks in Egypt received **3.4 million customer complaints in 2025, up 24% on 2024**. **97% were resolved within 15 working days** | CBE Financial Stability Report, reported by Benokinvest, 21 Oct 2026: https://www.benokinvest.com/archives/194133 |
| 2 | About **3 million complaints in 2025, of which about 63,000 (about 2%) were escalated to the CBE** after banks failed to resolve them. The CBE uses complaint data to find patterns by product and sales practice | CBE First Deputy Governor May Abou El Naga, 29 Sep 2026: https://fintechgate.net/253099 and https://economyplusme.com/185891/ |
| 3 | **Q1 2026: 953,000 complaints, against 746,000 in Q1 2025 (+28%)**. Bank customers grew from 52 million to 54.7 million. The CBE attributes the rise to digital channels and greater awareness of rights | CBE Financial Stability Report, reported by Cairo24, 15 Oct 2026: https://www.cairo24.com/2512078 |
| 4 | The Cabinet's unified complaints platform passed the CBE **3,869 banking complaints and requests in Nov 2025 (2,153 closed, 56%)** and **3,422 in the month reported on 7 Mar 2026, probably Feb 2026 (1,735 closed, 51%)**, including ATM outages | Ismailia Governorate, 8 Dec 2025: http://www.ismailia.gov.eg/pages/NewsDetails.aspx?newsid=4282. El Balad, 7 Mar 2026: https://www.elbalad.news/6893840 |
| 5 | CBE complaint rules: a reference number **within 2 working days**; a response **within 15 working days** (cases involving third parties are excepted); the customer has **15 working days** to object; escalation to the CBE only after that | CBE customer protection guide, as summarised by EgyptInOrder, 29 Jul and 10 Sep 2026: https://egyptinorder.com/file-bank-complaint-egypt/. NBE's own steps, Bankygate, 29 Nov 2025: https://www.bankygate.com/67025 |
| 6 | **EGP 4 billion in fraudulent transactions prevented in 2025 (+268% on 2024)** | CBE Governor Hassan Abdalla, Egyptian Bankers, 30 Jan 2026: https://egyptian-bankers.com/3767/ |
| 7 | **57% of digital financial service users in Egypt have faced phishing attempts**. Of EGP 4bn in fraud attempts detected, only EGP 116,800 was recovered | Al-Ahram Weekly, 6 Jun 2026: https://english.ahram.org.eg/UI/Front/Inner.aspx?NewsContentID=570009 |
| 8 | The CBE ordered every bank to set up a dedicated anti-fraud unit within 6 months | Egyptian Bankers, 5 Apr 2026: https://egyptian-bankers.com/4768/ |
| 9 | NBE charges **EGP 150 to 300** to replace a lost or damaged credit card | El Watan News, 15 Jan 2026: https://www.elwatannews.com/news/details/8208037 |
| 10 | Google Play ratings in the Egyptian store on 30 Oct 2026: BM Online 4.7, QNB 4.3, InstaPay 4.3, NBE Mobile 3.5, CIB 3.1, AAIB 2.6, HSBC EG 1.7, BDC 1.5 | Google Play search (`gl=EG`), 30 Oct 2026 |
| 11 | In our sample of 230 Egyptian reviews (Jul to Oct 2026): 76% gave 1 or 2 stars; 39% describe app or login failures; 8% describe failures of the contact center | This research (Bright Data Google Play scraper, 30 Oct 2026) |

**Derived estimates for Nova Bank (assumption: Nova matches the sector average).**

- **Complaint rate.** The sector logs 3.4M complaints for 54.7M customers, about 6.2 per 100 customers a year. The Q1 2026 run-rate is about 7.0 per 100 (953k × 4 / 54.7M).
- **Nova's complaint volume.** For Nova's 2M customers that is about **124k to 140k formal complaints a year, or 10k to 12k a month**. That would be roughly a quarter of the 45k monthly contacts. The rest would be inquiries and requests.
- **Escalations and SLA misses.** At the sector rates, about **2.5k to 2.8k complaints a year** would escalate to the CBE (2%), and about **3.7k to 4.2k a year** would miss the 15-day SLA (3%).

Caveats on these estimates:

- The two official 2025 totals differ: 3M is the deputy governor's rounded figure and 3.4M comes from the Financial Stability Report. Use 3.4M and cite both.
- The 54.7M customer base is the Q1 2026 figure, so the 2025 rate per customer is a little high.

## Eval phrasings

These are anonymized customer utterances paraphrased from what was found above, for use as eval test questions. Amounts are illustrative.

Franco-Arabic uses digits for some letters: 2 = ء or ق, 3 = ع, 5 = خ, 7 = ح.

| # | Language | Utterance | Intent | Grounded in |
| --- | --- | --- | --- | --- |
| 1 | English | I asked an online store for a refund two weeks ago and it still hasn't reached my card. Where is it? | dispute_status | Theme 4 |
| 2 | English | There's a 1,300 EGP subscription charge I never signed up for. I already reported it. What's happening with my case? | dispute_status | Theme 4 |
| 3 | English | The app shows money on hold but doesn't say who it's from or why. Is this something I need to dispute? | dispute_status | Themes 3, 4 |
| 4 | English | Why was I charged 35 pounds when the merchant refunded me? | fee_explanation | Theme 3 |
| 5 | English | What is this quarterly account charge, and the 200 EGP card fee on my statement? | fee_explanation | Theme 3 |
| 6 | English | My debit card was stolen this morning. How do I block it, and how long until I get a new one? | card_replacement | Theme 5 |
| 7 | English | I'm abroad and my soft token stopped working, so I can't transfer anything. | other | Theme 6 |
| 8 | Formal Arabic | تم خصم مبلغ من بطاقتي مقابل عملية شراء لم أقم بها، وقدمت اعتراضاً منذ أسبوع. ما حالة الاعتراض؟ | dispute_status | Theme 4 |
| 9 | Formal Arabic | سحبت من ماكينة الصراف الآلي ولم تخرج النقود، لكن المبلغ خُصم من حسابي. متى يُرد؟ | dispute_status | Theme 4 |
| 10 | Formal Arabic | أرجو توضيح سبب خصم مصروفات إدارية من حسابي هذا الشهر. | fee_explanation | Theme 3 |
| 11 | Formal Arabic | ما رسوم كشف الحساب الورقي؟ خُصم مني مبلغ مقابل كشف من تسع وعشرين صفحة. | fee_explanation | Theme 3 |
| 12 | Formal Arabic | فقدت بطاقة الخصم المباشر، كيف أطلب بطاقة بدل فاقد وما الرسوم المطلوبة؟ | card_replacement | Theme 5 |
| 13 | Formal Arabic | انتهت صلاحية بطاقتي الائتمانية ولم تصلني البطاقة الجديدة حتى الآن. | card_replacement | Theme 5 |
| 14 | Formal Arabic | تصلني رسائل بعمليات على بطاقة لا أملكها رغم أنني قدمت شكوى بالفعل. | other | Theme 4 (routing edge case) |
| 15 | Egyptian Arabic | لو سمحت أنا عامل شكوى على عملية مش بتاعتي من عشر أيام ومحدش رد عليا، الشكوى وصلت لفين؟ | dispute_status | Themes 2, 4 |
| 16 | Egyptian Arabic | ليه البنك بيخصم مني 30 جنيه كل شهر؟ أنا ما عملتش أي حاجة. | fee_explanation | Theme 3 |
| 17 | Egyptian Arabic | فيه 4000 جنيه اتخصموا من حسابي من غير سبب، عايز أعرف راحوا فين. | fee_explanation | Theme 3 (fee or dispute edge case) |
| 18 | Egyptian Arabic | الكارت ضاع مني امبارح، عايز أوقفه وأطلع بدل فاقد. هستلمه امتى؟ | card_replacement | Theme 5 |
| 19 | Egyptian Arabic | الكارت الجديد وصلني بس مش راضي يتفعل، أعمل إيه؟ | card_replacement | Theme 5 |
| 20 | Egyptian Arabic | بقالي ساعة على الخط ومحدش بيرد، وكل ما أكلمكم حد يقولي كلام شكل. | other | Theme 2 |
| 21 | Egyptian Arabic | طلبت ألغي الكريديت كارد من شهر ونص وكل مرة يقولولي الورق ناقص، والمديونية بتزيد. | other | Themes 2, 5 |
| 22 | Franco-Arabic | ana 3amalt refund men site w el flous lessa mawsletsh el card, ha5odha emta? | dispute_status | Theme 4 |
| 23 | Franco-Arabic | fi 7araka 3ala el 7esab ana mesh 3amelha, 3ayez a3mel e3terad w a3raf el status | dispute_status | Theme 4 |
| 24 | Franco-Arabic | leh et5asamli 200 geneh 3ala el card? ana ma3meltesh 7aga | fee_explanation | Theme 3 |
| 25 | Franco-Arabic | eh el masarif el edareya di elli betet5esem kol 3 shohor? | fee_explanation | Theme 3 |
| 26 | Franco-Arabic | el card bta3ty etsara2et, 3ayez a2felha w atala3 wa7da gdeda | card_replacement | Theme 5 |
| 27 | Franco-Arabic | el card 5elset w el gdeda lessa mawsletsh, a3mel eh? | card_replacement | Theme 5 |
| 28 | Franco-Arabic | el app mabyeftahsh w el token bey2ool expired, mesh 3aref a7awel 7aga | other | Theme 1 |

Mix: 7 per language. By intent: dispute_status 8, fee_explanation 8, card_replacement 7, other 5. Items 3, 14, 17 and 21 are deliberate edge cases for testing intent routing.

## Eval checkpoint log: 1B Pain points

| Block | Attempts | Score per attempt | Why it was retried | What changed between attempts | Final status |
| --- | --- | --- | --- | --- | --- |
| 1B Pain points | 2 | 3 → 3 | Attempt 1: the evidence for disputes and card replacement (two of the three copilot intents) was thin, and the Bright Data cap was exceeded | Attempt 2: new searches in Egyptian Arabic on swallowed cards, failed ATM transactions and card delivery or activation. This added 3 Reddit threads (Nov 2025, Feb 2026, Jun 2026) to themes 4 and 5. No new Bright Data calls were made | ⚠ Accepted below threshold, with ⏸ items that need your input |

Scoring against the criteria (attempt 2):

- **Recency and Egypt: met.** All 230 reviews are from the Egyptian store, 92% from the last 90 days. All other sources are dated Nov 2025 to Oct 2026.
- **Local users: met.** Egyptian bank customers only; the few posters abroad are Egyptian customers.
- **Several platforms: met.** Google Play, Reddit, Instagram, plus news and regulator sources.
- **Each theme has a quote and source: met.** Theme 5 is flagged Low evidence for lost or stolen replacement delays.
- **Ranking justified: mostly met.** Mentions were counted and severity and impact stated, but the coding is by keyword and the sample is skewed toward app updates.
- **No names or usernames: met.**
- **Bright Data within budget: not met.** 304 records against a cap of 300.

The score stays at 3 because one hard criterion failed. Why it can't be fixed by retrying:

- The overshoot came from the Instagram Comments scraper. It has no limit setting and returned 61 records for a reel that showed 34 comments.
- The records are already billed, so a retry cannot undo it.
- A further retry would need more Bright Data (no headroom left) or Firecrawl (no credits left).

Open gaps:

1. **⏸ Needs your input:** please accept or reject the 4-record overshoot (304 of 300). Bright Data usage:
   - Dataset records: Google Play 230, Reddit 7, Instagram Posts 6, Instagram Comments 61.
   - Not counted as dataset records, but billed separately: 3 page scrapes and 2 search-engine queries.
2. **⏸ Needs your input:** the customer-voice evidence on lost or stolen card replacement delays is Low. Real contact-center reason codes or call samples, from a partner bank or the course, would close this gap. Until then, the card_replacement eval phrasings rest on the bank's own procedures and fees rather than on customer complaints.
3. Gaps that could be fixed with more budget or credits:
   - Sources not pulled: Apple App Store, X, TikTok, public Facebook comments, Trustpilot.
   - No dedicated Franco-Arabic search was run.
   - The review sample was pulled newest first; a full review history from the Bright Data dashboard (CSV) would correct the bias toward app updates.
4. What this weakens downstream: any business-case slide that sizes the card_replacement share should treat it as an assumption. The dispute_status and fee_explanation sizing rests on firmer ground.

Eval status line: `1B 3→3 ⚠ (2 attempts) · ⏸ budget overshoot sign-off + card-replacement call data`
