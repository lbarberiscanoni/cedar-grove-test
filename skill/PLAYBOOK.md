# ESA Agent Playbook — Juicebox Enterprise Services Agreement

Audience: an LLM-driven agent that compares a counterparty's redlined ESA against this playbook and proposes Cedar Grove's responses.

Source: synthesized from 238 ESA-relevant negotiation threads (1063 clause-level observations) on the Juicebox account, plus the form ESA (v1.6) as baseline structure. Positions in this playbook appear only where the evidence supports them. Provenance for each position is recorded in `playbooks/_provenance.json`.

---

## General principles

These cross-cutting rules emerge from the correspondence. Apply them when calibrating any specific counter-redline.

1. **Calibrate by deal size.** Cedar Grove's posture is consistently proportional to ACV. On small or trial deals (<$25k), aggressive customer asks (e.g., $2M supercap on a $16k contract) draw firm pushback as "off-market relative to deal size." On large enterprise deals (Snowflake, Amazon, Citadel, Klaviyo), Cedar Grove will concede further on cap multipliers, refund mechanics, and renewal terms.

2. **Trade liability concessions for cap structure.** When a counterparty wants expanded indemnification scope, broader data carve-outs, or removed cap carve-outs, Cedar Grove almost always counters by attaching a super-cap (typically 3x-5x fees or a floor of $250k–$500k). Don't accept scope expansion without a corresponding cap.

3. **The three things to never give away.** (i) Output ownership — Juicebox cannot assign Output IP because Outputs incorporate proprietary multi-tenant models and third-party-licensed data. (ii) Subprocessor unilateral-block rights — customers get notice and termination-on-objection, not consent rights. (iii) Termination for convenience without prepaid annual fees and no-refund language.

4. **Use the third-party-licensing frame for AI/data positions.** When pushing back on Output assignment, derivative-data restrictions, or AI/ML training restrictions, frame the position around technical impossibility ("Outputs incorporate third-party-licensed data we cannot reassign," "shared multi-tenant models cannot be operationalized as customer-owned artifacts") rather than abstract licensing concerns. This framing has consistently held.

5. **Standard fallback patterns.**
   - Liability cap: form is 12-month fees → standard fallback 2x fees → high-end concession 3x-5x fees with floor.
   - Fee increase cap: form silent / discretionary → 7% annual cap is Cedar Grove's standard floor.
   - SLA helpdesk response: form "commercially reasonable" → 3 business days → 2 business days.
   - Breach notice (DPA): form "without undue delay" → 72h → 48h floor.
   - Payment: form Net 30 → Net 60 commonly accepted.
   - Auto-renewal: form auto-renews → fallback is "auto-renewal with 10-day non-renewal notice right."

6. **Sequencing.** First counter-redline should hold every non-negotiable and propose every standard fallback as the opening position. Save accept-with-comment items for round two when you can trade them. Escalate to business (Simran, David, Chris Duval) before conceding on logo rights, cap structure, or output ownership.

7. **Operational reality framing.** When pushing back on operationally infeasible asks (e.g., 24-hour breach notice, EU-only storage with 20 US subprocessors, 24/7 security officer on call, additional-insured endorsements), name the operational reason explicitly. This framing has won.

8. **Trial-stage carve-outs.** For trial / pilot / PoC deals, Cedar Grove routinely accepts narrower derivative-data restrictions, capped supercaps, and shorter terms — but the playbook reverts to standard on conversion to paid subscription. Flag any trial-specific concession with a sunset.

---

## Section 1 — Services / Access / Restrictions

### 1.1 Use Restrictions (Section 2 of form)

#### Opening position
Maintain Section 2 (General Restrictions and Output Restrictions) substantively unchanged. Counterparty may not (i) modify, create derivative works of the Services, (ii) build competitive products, (iii) copy features/functions, (iv) use Output to train ML/AI or develop competing foundation models, (v) reverse-engineer.

#### Non-negotiables
- **No removal of use restrictions.** When counterparties (ServiceTitan, eedccfb9, Samsung) tried to delete the no-modification / no-derivative / no-copying clauses, Cedar Grove reinserted them. Frame: "use restrictions protect Juicebox's IP and service integrity; non-negotiable."
- **No carve-out for building competing products.** Held firm against Samsung.
- **No clauses preventing Juicebox from using customer inputs to provide the Service.** Where customers (Immunome, ce7ed60b) tried to designate inputs as "Confidential Information not usable to provide Services," Cedar Grove rejected. Frame: "Juicebox needs the ability to use customer inputs to deliver the Service; this restriction would prevent service delivery."

#### Accept-with-comment patterns
- Customer-imposed AI-tool restrictions on Juicebox personnel and subcontractors (Hinge Health's "shall not include sensitive Personal Data or trade secrets in prompts for Generative AI Tools") — accepted.
- Customer-specific safe-harbor for non-competing internal ML/AI use of Output (Whatnot pattern: "Customer may use Output in internal systems that do not compete with Juicebox") — accepted.
- Narrowing language confirming Juicebox does not source private social profiles, job-board resumes, or personal content beyond public professional data (Micron pattern) — accept and craft language defining data boundaries.

#### Rationale snippets
- "Use restrictions are necessary to protect Juicebox's IP and service integrity."
- "Juicebox needs the ability to use customer inputs to deliver the Service; restricting this would prevent service delivery."

---

## Section 2 — Fees and Payment Terms

### 2.1 Payment Timing

#### Opening position
Annual upfront payment in advance, Net 30, USD, by bank wire or check. Form default.

#### Standard fallback
- **Net 60** is the predominant accepted fallback (FE, Snowflake, Crusoe, Contentful, Ellucian, Lovable, Docker, Intercom Net 45, Micron, dcf6b31a). Accept Net 60 unless deal is unusually small or unusual currency-handling exposure.
- **Quarterly installments** acceptable as commercial accommodation (Wonderful 01fb7e/10c4a8 — four quarterly installments at Net 60).
- **Monthly billing**: rejected (Squint AI — "Cedar Grove pushed back against monthly payments"; Strala — "Juicebox's standard billing practice is strictly annual"). Accept only if structured as monthly minimums against an annual commitment floor (DesignArena pattern: 1/12 annual commitment per month).

#### Non-negotiables
- **No monthly subscription with prorated refunds.** This collapses the annual subscription model. Hold firm.
- **Annual upfront required if termination-for-convenience granted.** Whenever counterparty insists on TFC, the price of admission is full annual prepayment and no refund (Squint AI, Hover, 2a7e5e — "Cedar Grove framed annual upfront as floor to protect Juicebox's subscription revenue model").

#### Accept-with-comment patterns
- Customer-portal invoicing requirements (Addepar Coupa) — accept once product confirms capability.
- Removal of late-payment interest accrual (Anchor Labs) — minor concession, give if traded.
- 15-day grace period before interest accrues (Paradigm Health) — accept.

### 2.2 Fee Increase Caps

#### Opening position
Form ESA reserves Juicebox's unilateral right to modify pricing for renewal terms with 30 days' notice (Section 3.2). No fee-increase cap.

#### Standard fallback
- **7% annual cap.** This is Cedar Grove's firm floor and explicitly described as "Juicebox's standard fee increase percentage" across many threads (Klaviyo, Vercel, Measured, TRM, Wonderful, GoodLeap, Givebutter, 32160d1, 4483abe, 5255a74, c1ca10, 6dcda58). Always counter customer requests for 2%, 3%, 5%, or CPI-based caps with 7%.
- **60-day advance notice** of increases (vs. form's 30 days) — acceptable when paired with the 7% cap and a customer termination/decline window (Anchor Labs, GoodLeap, Palmetto, Castleton).

#### Non-negotiables
- **No cap below 7%.** Klaviyo, Vercel, TRM, Snowflake — Cedar Grove held firm at 7% against 2% / CPI / 3% asks. Frame: "7% aligns with Juicebox's standard fee increase percentage."
- **No written consent / mutual agreement** requirement for renewal increases (Satellogic, Juniper Square). Customer right is to decline renewal, not to gate the increase.

#### Accept-with-comment patterns
- Fees fixed during Initial Service Period (first 12 months) with cap on renewal increases — accept (Multiverse 15c574, 17bd0e: "fixed initial fees and capped renewal increases as reasonable commercial protection for multi-year enterprise customer").
- 60-day advance notice — accept (Castleton, Anchor Labs, Palmetto).
- Customer right to terminate / decline if increase exceeds threshold — accept (ServiceTitan 29859af: "Fee increases limited to 3% per renewal term, but with customer termination right rather than mutual approval gate").

#### Rationale snippets
- "7% is Juicebox's standard fee increase percentage and provides fair balance for vendor flexibility."
- "CPI is unpredictable and volatile for Juicebox's business planning; flat cap preferred."

### 2.3 Overage Fees

#### Standard fallback
- Written notice + customer confirmation before charging overage fees (ID.me, Castleton, Rula). Standard accommodation; accept.

---

## Section 3 — Term, Termination, Effects

### 3.1 Auto-Renewal

#### Opening position
Form ESA Section 4.1 — auto-renewal for additional periods of the same duration as the Initial Service Period, unless either party requests termination at least 30 days prior.

#### Standard fallback
- **Keep auto-renewal but grant non-renewal notice right up to 10 days before renewal.** This is the most common Cedar Grove compromise (Lovable 159a957/193cfd, Binti 80c46be7, e7caae1: "Cedar Grove held firm on auto-renewal but offered counterparty flexibility via notice provision").
- **Mutual written agreement required** for renewal — accept when customer is large/sophisticated and other terms are good (Zip 379d25e, Positron, Multiverse 17bd0e, Clara f03d331, Counsel AI c6eba0).
- **Auto-renewal with customer-friendly notice provisions** (extending notice from 30 → 14 days when customer pushes back per 7a69f1aa).

#### Non-negotiables — context: large enterprise
Cedar Grove holds firm on auto-renewal when the deal is strategic and other concessions have been given. Klaviyo 24bf4b7, 4483abe, 32160d1f — "Cedar Grove's position on renewals is firm: mutual written agreement required for each renewal term. This is Juicebox-favorable." But in many smaller deals Cedar Grove folds (see accept-with-comment).

#### Accept-with-comment patterns
Cedar Grove accepts removal of auto-renewal frequently (42 of 79 observations). Typical pattern: customer requests no auto-renewal → Cedar Grove accepts, particularly when customer makes the request a priority or is willing to give elsewhere (Wonderful, OnePay, FE, Crypto.com, Vercel, Ellucian, ID.me, Airtable, Applovin, Flywire, Applied Intuition, Fonoa, etc.).

**Agent rule:** Push back first with the 10-day non-renewal notice fallback. If customer presses, accept removal — this is a frequent Cedar Grove concession.

#### Rationale snippets
- "Automatic renewal is required and tied to pricing quoted." (firm position, Ampere)
- "Cedar Grove restored auto-renewal but enabled [customer] to send notice of non-renewal up to 10 days before renewal." (standard fallback, Lovable)

### 3.2 Termination for Convenience

#### Opening position
No termination for convenience. Form ESA Section 4.3: termination for material breach with 30-day cure only. "Each Service Period is a non-cancellable commitment for the full duration."

#### Standard fallback
- **TFC permitted only if all annual fees paid upfront with no refund.** This is Cedar Grove's hard structural fallback (Squint 4b97dd0, Hover d3f0c60, Mistplay a352b7b, Ellucian 25f9aa7). Frame: "termination for convenience cannot coexist with ongoing refund obligations."
- **TFC after Initial Service Period only** — at renewal mechanics, not within committed term.

#### Non-negotiables
- **No TFC during committed term with refund.** Held firm against CIM Group (4916c75, ab126ded), Battery Ventures (51df656), Sentry (33773483, 9a39232), Decagon AI (e1d226d), Insider (488df05), Castleton (380a1da). Frame: "Termination for convenience converts annual commitments to month-to-month, undermining revenue predictability needed to invest in and support the platform."
- **No TFC during trial period when trial itself is the evaluation mechanism** (f900546, Decagon).

#### Accept-with-comment patterns
- **Refund right on suspension caused by third-party vendor failure** (GoodLeap 24716f, Buildots 34adb7b, Teramind, Airtable 2bd0fde, Quizlet 03cc202). Standard small concession.
- **Prorated refund on Juicebox uncured material breach** (Applovin, b63a5dd, ServiceTitan eedccf, Quizlet). Accept — narrowly scoped.
- **30-day cure period on material breach** — form default; hold firm (The Knot 306cf4d).
- **Termination for service availability failures** (3 consecutive months / 3 in rolling 6) — accept (ChanMed e2b8b63, ChenMed 92f21008, OpenTable 6ce4702, Bumble 777d51e, fcff0b97).

#### Rationale snippets
- "Termination for convenience converts annual commitments to month-to-month, undermining revenue predictability needed to invest in and support the platform." (CIM Group)
- "Trial period allows customer to evaluate Juicebox performance before committing to paid subscription; non-cancellable term expected once customer moves to paid tier." (Decagon)

### 3.3 Suspension

Form ESA Section 4.2 — Juicebox may suspend without liability for nonpayment, restrictions breach, security risk, vendor termination, or legal requirement.

#### Accept-with-comment patterns
- **Notice before suspension for nonpayment** (Paradigm Health 445f25b: "Juicebox may suspend only after providing prior written notice for nonpayment 30+ days overdue"). Accept.
- **Cure-then-reinstate language** — accept but reserve Juicebox's sole discretion to determine cure (eedccfb9, ServiceTitan 29859af).

---

## Section 4 — Data (Section 5 of form)

### 4.1 Output Ownership

#### Opening position
Juicebox retains ownership of all Outputs. Customer receives non-exclusive license to use Output for internal business purposes during term. This is the most consistently held position in the corpus (19 non-negotiable threads).

#### Non-negotiables
- **No assignment of Output ownership to customer.** Held firm against: Klaviyo (4483abe, b9722af, 24bf4b7), ServiceTitan (49a2a62, 55a7abf, e08b350, 44619cb), Snowflake (5ee0145, 64942415), Rivian, Bumble (777d51e, f9c573e), Astrix, Sigma, Decagon, Whatnot, Sesame, OpenAI, Buildots, Chainlink Labs, ChenMed.
- **Standard rationale (use verbatim):** "Outputs are generated using shared multi-tenant models and proprietary candidate datasets with third-party-licensed components that cannot be assigned. Treating Outputs as owned artifacts creates ambiguity Juicebox cannot operationalize."

#### Standard fallback
- **Customer owns only Output portions that directly include their Customer Data.** (Klaviyo 24bf4b7, Ellucian 25f9aa7 — "Customer owns only Output portions that directly include Customer Data; Juicebox retains IP in third-party licensed data.")
- **Perpetual license to Output instead of assignment** (Blue Origin a6f0224, Bumble f9c573e). Acceptable substitute when customer insists on something.
- **Term-limited internal use license** is the Juicebox-stickiness preference (Service Titan e08b350: "rights terminate upon expiration").

#### Accept-with-comment patterns
- Customer-owned Customer Data (input) — always accept; this is form position.
- Mutual reservation of rights — accept (Gem 97dfbe).
- Carve-out preserving Juicebox IP within Customer-owned systems — accept (Samsara ffb4b72).

#### Rationale snippets
- "Outputs are generated using shared multi-tenant models and Juicebox's proprietary candidate dataset with third-party licensing that cannot be assigned. Full assignment to [customer] cannot be operationalized and creates ownership ambiguity." (Klaviyo b9722af)
- "Juicebox has invested significant capital in proprietary data from third-party providers. Assigning ownership to Customer would compromise Juicebox's proprietary data rights and breach third-party licensing agreements." (ServiceTitan)

### 4.2 Deidentified Data / Analytic Data

#### Opening position
Form Sections 5.3, 5.4 — Juicebox owns Deidentified Data and Analytic Data and may use them to operate, maintain, and improve products/services.

#### Standard fallback
- **Irreversibility / GDPR Recital 26 standard** for deidentified data — anonymized data usable only where re-identification is not reasonably possible (Lovable 159a957, 33967ec, 43921d2). Accept; gives customer comfort while preserving rights.
- **No use to train AI/ML** — accept this restriction when customer requests it (Chainguard 2317ccd, 94d5ab1; Cynet 4371f52). Common concession.
- **Preserve right to Analytic Data only** if Deidentified Data is removed (OnePay 05f7eef). Accept narrowing.

#### Accept-with-comment patterns
- Restriction limiting Deidentified Data use to "internal" products and services (One Brief 530a3d4) — accept for defense/compliance-sensitive customers.
- Removal of Deidentified Data rights, preserving Analytic Data rights (Airtable 2bd0fde, OnePay) — accept when relationship warrants.
- Explicit "stripped of all identifiers" clarification (Nextdoor eee372e) — accept.

#### Non-negotiables
- **Preserve right to create some form of derivative/analytic data.** Cedar Grove will not accept blanket prohibition on Juicebox using customer data for product improvement (Givebutter 5499fdd). Operationally critical. Move to anonymized/aggregated only with irreversibility standard if pressed.

#### Rationale snippets
- "Cedar Grove explained that Juicebox normally creates de-identified analytics data for platform improvement; irreversibility standard balances privacy concerns while maintaining analytics capability, tracking GDPR Recital 26 framework." (Lovable)

### 4.3 Data Processing Scope (cross-references DPA)

#### Opening position
Juicebox processes Customer Data solely to provide and support the Services, maintain the account, and comply with law. No use to improve Services, train AI/ML/LLMs, or include in Juicebox's proprietary profile database.

#### Non-negotiables
- **Processor-only model.** Reject controller-controller or hybrid characterizations (ClickUp 9bb4c9a, b2c0875; Check Point 4af559c, d9c8d46; eedccfb, ServiceTitan 29859af). Frame: "Processor-only model reflects Juicebox's actual data flows and legal role in multi-tenant SaaS architecture."
- **No deidentified/aggregated pre-processing requirement.** ServiceTitan tried to require Juicebox process inputs only in aggregated/deidentified form; rejected — would break product (29859af, eedccfb).
- **DPA scope limited to data Juicebox processes as processor.** Reject scope expansion to candidate data sourced independently from third-party brokers (ClickUp 41550f8, Contentful 3f15bff). Frame: "DPA addresses only data flows where Juicebox is processor; data sourced from other channels falls outside processor scope."

#### Accept-with-comment patterns
- Confirmatory language that Juicebox uses analytics but does not train models on Customer Data (Sigma 6941b63, Dow Jones 607d52c, b605029). Accept and write framing.
- Narrow data category to actual use case (Gilat: deletion of billing/payment categories when customer doesn't submit those) — accept if accurate.
- DPA subject to MSA liability cap with narrow indemnification scope — Cedar Grove's preferred framing (Vercel 19ec6b8, c1ca10).

### 4.4 Data Retention / Deletion

#### Opening position
Form does not specify timelines for deletion. Juicebox retains data per Privacy Policy / Trust commitments; deletion supported on customer request.

#### Standard fallback
- **30-day deletion post-termination** with prior export window — most common landing point (Castleton 380a1da, One Brief 530a3d4, HubSpot a39733a, Form Energy 53f9317/dcf6b31).
- **45-day automatic deletion** — Cedar Grove confirmed this aligns with Juicebox's actual operational practice (HiBob 9d8c99c).
- **60-day retention** post-cancellation — confirmed standard at PA Consulting edab48b7.
- **30-day export window** + deletion thereafter (Castleton, Measured 3379c11, Citadel 0c9a006).

#### Accept-with-comment patterns
- Customer-directed deletion within 30/60/90 days of termination (Airtable 90-day, One Brief 30-day, others) — accept the specific number; this is operationally feasible.
- Written certification of deletion upon request (Lovable 43921d2) — accept.

#### Non-negotiables
- **Backup-copy carve-out preserved.** Juicebox must retain operational backups (Phaidon 8c6a4f3). Form DPA §12(1) language: "except for backup copies, insofar as they are necessary for ensuring data is processed correctly."
- **Cannot indemnify or warrant against legally-mandated retention** (Kin e0fdee0c). Frame: "Cedar Grove cannot indemnify compliance with legal data-retention obligations; retention mandated by applicable law is outside Juicebox's control."

---

## Section 5 — Confidentiality (Section 6 of form)

#### Opening position
Form ESA Section 6 — mutual confidentiality, 5-year survival, trade-secret protection while it remains a trade secret. Generally light editing.

#### Accept-with-comment patterns
- Standard customer redlines broadening "reasonably understood to be confidential" definition (b63a5dd) — accept; many customers add this.
- Detailed permitted-recipient lists (counsel, financing, M&A, regulatory) — accept (Moloco b9c63a4).
- Reasonableness standard on confidentiality obligations — accept (Biofire 6e8a5ab).

#### Non-negotiables
- **Feedback as Juicebox Confidential Information / freely usable.** Hold firm; standard form provision (RainXYZ e7a9c2f, OnePay 05f7eef). Standard fallback if pressed: restore feedback rights but exclude feedback containing customer's confidential information (Applied Intuition 54628ef, ee6951d).
- **Confidentiality sunset.** Form says 5 years; Cedar Grove will not extend indefinitely (form is non-negotiable position even where customer prefers indefinite — see d8db571).

---

## Section 6 — Representations and Warranties (Section 7 of form)

#### Opening position
Form Section 7 — narrow corporate authority reps only (existence, authority, enforceability). All other warranties disclaimed (Section 8).

#### Standard fallback
- **Lawful-sourcing warranty for Licensed Data** — accept narrowed-scope warranty when customer presses on data brokerage concerns (ClickHouse 1cbcb6f, 5c8f149, d27ed88; Harvey 75f9a6f). Frame: "Juicebox warrants licensed data comes from established providers collecting lawfully, with rights to license under applicable privacy laws."
- **Materially-in-accordance-with-documentation warranty** — Cedar Grove's middle ground for enterprise customers demanding performance warranty (Sigma 318431c, Sayari cebfec0). Form acceptable.
- **Commercially-reasonable security warranty** — accept (Gravity 2cc3c07: "Juicebox maintains commercially reasonable administrative, technical, physical security measures; SOC 2 Type II consistent; will provide SOC 2 report on request").

#### Non-negotiables
- **No AI bias / unfairness warranty.** Hold firm (Chainlink 1a9f957, d371357, d7f0704; SmartContract). Frame: "Any AI system can be shown biased in some way, creating day-one breach risk; bias indemnity would make Juicebox an insurer for Customer's use."
- **No strict liability for upstream data supply chain** (Harvey 75f9a6f, ClickHouse). Narrow warranty to what Juicebox controls; exclude platform-ToS-violation strict liability.

#### Accept-with-comment patterns
- AI human-in-the-loop warranty — accept conditionally if engineering confirms all agentic features require human review per GDPR Article 22 (Gilat bcce5f6).
- Knowledge qualifier on third-party IP reps — accept (B2D 857412b).

### Disclaimer (Section 8)
Aggressive AS-IS / AS-AVAILABLE disclaimer — preserve. Generally non-controversial; Harvey AI 787aa05 accepted form language.

---

## Section 7 — Indemnification (Section 9 of form)

### 7.1 Juicebox Indemnification (Section 9.1)

#### Opening position
Juicebox indemnifies for (i) Services as delivered infringing third-party IP, (ii) Juicebox's gross negligence or willful misconduct, (iii) Juicebox's violation of applicable law (final determination). Standard carve-outs: Customer Data, modifications not by Juicebox, combinations not contemplated, Customer breach.

#### Non-negotiables
- **Maintain final-judgment / final-determination requirement** for compliance-related indemnities (TwelveLabs 9e6e5d0). Frame: "Standard protection for Juicebox exposure on compliance-related indemnity obligations."
- **Reject indemnity for hiring-practice non-compliance / AI bias / employment-decision claims.** Cedar Grove will not accept indemnity for customer's hiring decisions, even when Customer-named-as-employer-of-record (Wonderful 01fb7ef/10c4a8e, BuildOps 3e85745/96f138d). Frame: "Indemnities make sense only where one side has full control; AI regulatory landscape is forming with principle to keep humans in loop."
- **Reject broad no-fault indemnity for upstream data provider claims.** ClickHouse 0ee69a9, 1cbcb6f, 5c8f149, d27ed88 — narrow to unlawful collection/lack of legal rights, exclude platform-ToS disputes. Frame: "Broad no-fault indemnity would pull in routine privacy activity and private ToS disputes without legal violation. Platform ToS enforcement is private contractual dispute between platform and upstream provider, rarely creating downstream liability."
- **Mutual indemnity.** Reject unilateral indemnity drafts (OpenAI 5256860, Binti 80c46be, e7caae1, Multiverse — though see standard fallback). Frame: "Mutual risk allocation; vendor should not bear all indemnity burden in service agreement."

#### Standard fallback
- **Accept expanded scope conditional on liability cap.** Klaviyo pattern (24bf4b7, 32160d1, 4483abe): Cedar Grove accepted broader indemnification, paired with a 3x-fees DPA-breach super-cap. Always pair scope expansion with cap.
- **Hold-harmless and "liabilities, settlements" additions** — accept (Paradigm 445f25b).
- **Accept ordinary-negligence trigger replaced with gross-negligence-or-willful-misconduct** — Cedar Grove pushes this direction (Aleron 3c7de0f, 5570a2c, aafacac, fafbbe7).

### 7.2 Customer Indemnification (Section 9.2)

#### Opening position
Customer indemnifies for (i) Customer Data, (ii) Customer breach of Section 2 (Restrictions), (iii) Customer gross negligence/willful misconduct, (iv) Customer violation of applicable law.

#### Non-negotiables
- **Customer Data indemnity must remain.** Reject removal (Drivenets 9440576, Cynet 4371f52). Cedar Grove may narrow to "unaltered Customer Data" exception where customer failed to secure rights/consents (Cynet 6c0619a) but keeps core obligation.
- **Restrictions-breach indemnity must remain** (Apollo 683d203, Sayari cebfec0).
- **Reject removal of "violation of applicable law" indemnity** (Applovin 4c29a1, OnePay 0dca90, b63a5dd).

#### Standard fallback
- **Limit indemnity to third-party claims only** — Samsara ffb4b72; reasonable carve-out.
- **Reasonable scope qualifier**: indemnity for matters "solely within Customer's control" (Deliveroo 32ee660, 405502e).
- **Carve-out for claims arising from Juicebox's misuse / not-in-accordance-with-Agreement use** (Whatnot ce1f6b4: "limit Customer's indemnity to Customer Data 'solely to the extent such Customer Data is used by Juicebox in accordance with Agreement'").
- **Multiverse pattern** — accept removal of customer indemnity for sophisticated regulated-industry counterparties (15c5745, 17bd0e7), but only when vendor indemnity remains substantive AND counterparty is recruiting/regulated industry where this is global policy.

#### Accept-with-comment patterns
- Indemnity for AI bias / hiring-discrimination claims, structured with proportionality reduction for customer's material breach or improper use — accept reluctantly when customer presses (BuildOps 96f138d). Pair with super-cap.

#### Rationale snippets
- "Cedar Grove pushed back ensuring coverage for third-party claims from customer data and law violations." (Anchor Labs)
- "If [Customer] grossly misuses the product and Juicebox is sued, ensure no caps on indemnification." (Givebutter 5499fdd)
- "Removing carve-outs would wipe out substantive protections." (Chainlink, SmartContract)

---

## Section 8 — Limitation of Liability (Section 10 of form)

### 8.1 General Liability Cap

#### Opening position
Form ESA Section 10.2 — cap at Service Fees actually paid during Service Period within which damages occurred. Carve-outs: Section 2 (Restrictions), Section 6 (Confidentiality), IP infringement, Customer payment obligations, gross negligence/willful misconduct, indemnification.

#### Standard fallback
- **2x fees paid in trailing 12 months.** Most common landing point for general cap (Multiverse 15c574, 17bd0e7; Kong bb7b09b; OpenTable; e2b8b63 ChanMed; Citadel 0c9a006; Klaviyo 24bf4b7).
- **3x fees** when customer presses harder (Quizlet 03cc202 for privacy-specific; Givebutter 710ddf8; Lovable 193cfdc).
- **5x fees** as outer-end mutual super-cap concession (Citadel 0c9a006: "Cedar Grove proposed 5x fees as top-end market-supported cap").

#### Non-negotiables
- **Indemnification obligations carved out from cap.** Hold firm (Anchor 17d3ef0, Squint 4b97dd0, Teramind 115c091, Chainlink/SmartContract 1a9f957/8d7efc4, Gem 97dfbe8, Immunome 36cb883, Service Titan, Counsel AI a91674, Docker 551d626f, SimpliGov e3dc59f, Klaviyo).
- **IP infringement uncapped.** Hold firm (Anchor 17d3ef0, Chainlink, SimpliGov, Klaviyo).
- **Confidentiality breach uncapped.** Hold firm (Merge d941bff, Teramind 115c091). Frame: "Confidentiality breaches carry heightened risk of substantial damages and must remain uncapped."
- **Reps/warranties breach carve-outs preserved.** Reject removal of standard carve-outs (OnePay 05f7eef, 537068a; Teramind 115c091; SmartContract 8d7efc4; Squint 4b97dd0). Frame: "Removal of exceptions to liability cap (carve-outs for indemnification, IP infringement, etc.) is substantially off-market."

#### Accept-with-comment patterns
- **Mutual cap** (favors customer only → mutual) — Cedar Grove will accept (DesignArena 3f31cab).
- **12-month trailing lookback** instead of "Service Period within which damages occurred" — accept (Measured 3379c11, ServiceTitan).
- **Flat-dollar cap for small deals** at customer's request — accept when reasonable to deal size (Wonderful 01fb7ef/10c4a8 2x fee cap on a small deal accepted with comment).

#### Context-dependent: cap level by deal size
- Sub-$25k trial/PoC: 10x fees or $100k-$250k floor — Squint 4b97dd0 (10x for $10-13.9k deal), OnePay 0dca90a (greater of 10x fees or $250k).
- $25k-$100k mid-market: 2x-3x fees.
- $100k+ enterprise: 12-month-trailing or 1x-2x with super-caps (Snowflake, Klaviyo, Amazon).

#### Rationale snippets
- "Carving out indemnifiable claims from liability limitation is customary and necessary." (Gem)
- "Without carve-outs, the cap would effectively eliminate protections for indemnity and other core obligations." (Chainlink)
- "Confidentiality breaches carry heightened risk of substantial damages and must remain uncapped." (Merge)

### 8.2 Super-Caps for Data / DPA Breaches

#### Opening position
Data-privacy-law / DPA-breach liability inside the general cap (form position).

#### Standard fallback
- **3x fees super-cap for data-privacy / DPA breach** — Cedar Grove's most common landing (Quizlet 03cc202 — "3x service fee liability cap for violations of applicable data privacy laws"; Klaviyo 24bf4b7 — "added super-cap of 3x fees for data privacy obligation breaches"; 2a17fe2). This is the canonical position.
- **Greater of 3x fees or $100k–$500k floor** — for larger deals or when 3x fees is too low (Battery 51df656 — "greater of 3x fees and $100k for data privacy breach"; Lovable 193cfd, 159a957 — "greater of 3x fees or $500k"; Vercel 19ec6b8 — "3x fees or $100k whichever is greater").
- **4x-5x fees** when high-stakes data deal (Sigma 6941b63, 318431c — "4x fees or $500,000 as final compromise"; Airtable 2bd0fd — "DPA breaches capped at 5x fees"; Citadel 0c9a006 — 4x supercap).
- **For trial/pilot deals, $50k flat super-cap** (Lovable DPA 33967ec/43921d2; Forward Financing a6ce164 — "$50k anchor appropriate for trial deal").

#### Non-negotiables
- **No uncapped DPA liability.** Hold firm (Decagon e1d226d, Vercel 5255a74, OpenAI 5256860). Frame: "Juicebox does not accept uncapped liability for data privacy law violations as a matter of policy."
- **DPA carve-outs anchored to MSA cap framework.** Reject standalone uncapped DPA super-caps (Vercel c1ca10, 5d9e383). Frame: "DPA remains subject to overall liability cap in MSA; carve-out for violations is bounded by MSA cap framework."

#### Context-dependent
- Amazon (6fba3ec) — Cedar Grove accepted uncapped DPA liability + $2.5M indemnification cap, deferring to business given non-negotiability and deal size. Mark as exception, not precedent.

#### Rationale snippets
- "Data-handling indemnities expose Juicebox to potentially unlimited third-party claims; Cedar Grove negotiated a floor cap indexed to scale to balance risk with deal size." (Battery)
- "Carve-out cap protects against disproportionate exposure from customer conduct that violates core restrictions." (Decagon)

### 8.3 Consequential Damages Waiver

Form Section 10.1 — preserve. Generally non-controversial.

### 8.4 IP Infringement Remedies (Section 10.4)

Preserve form language on Juicebox's sole-discretion remedies (replace, modify, procure rights, terminate with refund). Generally non-controversial.

---

## Section 9 — General Provisions (Section 11)

### 9.1 Governing Law / Venue

#### Opening position
California governing law, exclusive jurisdiction in California state/federal courts. Form Section 11.1.

#### Standard fallback
- **Delaware** — common neutral landing (Mistplay a352b7b, Culligan 6eb38dc/ab5ea2d, IPEX 8f4eabe).
- **New York** — alternative neutral (Matillion 321daba, fcff0b97). "Standard neutral commercial jurisdiction" framing (fcff0b97).
- **Florida + arbitration** — accepted for crypto / regulated customers requiring confidentiality (Crypto.com 0d319d3).

#### Accept-with-comment patterns
- Where customer's preferred state happens to be California (many SaaS customers), confirm form already satisfies — no change needed (Counsel AI, SimpliGov, Harvey).

### 9.2 Customer Marks / Publicity

#### Opening position
Form Section 11.3 — Juicebox may list customer name and customer-approved logo on website, customer lists, general marketing materials. Any other public use (press releases, case studies) requires consent.

#### Standard fallback
- **Pre-approved, revocable website-listing right** — most common landing (Lovable 159a957, Sesame ef9f094, Balderton 4f625de — "may list customer name and logo with express advance written permission of two named Balderton contacts").
- **Customer roster only** (no press / case study) — accept (Counsel AI c6eba0/a9167495, Chainlink d371357).
- **Prior written consent for any use** — accept frequently (very common across 45 accept-with-comment threads).

#### Non-negotiables — context: tied to pricing
- **Logo rights when pricing is contingent on them.** Internal request from Juicebox business (Chris Duval, David P., Simran) sometimes elevates this. Docker f1c8f8d, Notion cbf322e, Ampere c2b4cfb — held firm because pricing was tied to logo rights. Frame: "Pricing was contingent on logo rights; restored Juicebox's marketing rights per internal request."

#### Accept-with-comment patterns
Cedar Grove accepts customer-imposed prior-consent requirement in roughly 60% of cases. Pattern: counterparty wants pre-approval → Cedar Grove accepts unless flagged by business. Default to accepting unless internal stakeholder has flagged.

#### Agent rule
First-pass: hold form position. Second-pass: drop to pre-approved website logo. Third-pass: drop to roster-only or full removal — only if business team confirms not material.

### 9.3 Assignment

#### Opening position
Form Section 11.6 — no assignment without consent, except M&A/asset sale carve-out.

#### Accept-with-comment patterns
- **Mutual written consent with M&A carve-out** — accept (SimpliGov d6b3633/df1a5d2/e3dc59f, Samsara 9554153).
- **Carve-out preserving Juicebox's Confidential Information / IP in outputs** — accept (ServiceTitan eedccfb).

### 9.4 Feedback

Preserve form Section 11.2 — feedback as Juicebox Confidential Information, freely usable. Standard fallback: restore right while excluding customer confidential information (Applied Intuition 54628ef/ee6951d).

### 9.5 Force Majeure / Electronic Comms / Amendments
Generally non-controversial. Accept reasonable customer edits.

### 9.6 Insurance (typically in Exhibit/Order)

#### Opening position
Juicebox carries $2M CGL, $5M umbrella, $1M cyber. Form does not require additional-insured endorsement.

#### Non-negotiables
- **No additional-insured endorsements.** Hold firm (Blue Origin 2dc561c/94f066d/a6f0224, Aleron 3c7de0f/73ffc95/5570a2c/fafbbe7, Rivian 6387d86, Lendbuzz c84b258). Frame: "Adding counterparty as additional insured bypasses the liability framework and pre-determines insurance outcomes before facts are known. Appropriate only for physical on-site relationships."
- **No cyber liability above $1M.** Current carrier (Vouch) capped at $1M; increasing requires new carrier (Blue Origin 2dc561c/94f066d/a6f0224 — held at $1M against $2M ask).

#### Standard fallback
- Provide Certificate of Insurance reflecting actual program — accept (Drivenets 9440576, 8d7efc4).
- Scale insurance requirements to deal value when counterparty asks are disproportionate — accept (Bridgewater 0adaeb1, 6c4b580, Chainlink Labs d371357).

#### Rationale snippets
- "Additional insured status grants direct claim rights under the policy. Unreasonable for [$X] ARR contract." (Aleron 73ffc95 on $19k ARR)
- "Cedar Grove's current provider only supports coverage up to $1M; increasing would require new carrier and significant time/expense." (Blue Origin a6f0224)

---

## Section 10 — Service Levels (Exhibit A)

### 10.1 Uptime

#### Opening position
Form Exhibit A: 99% uptime measured monthly, excluding holidays, weekends, scheduled maintenance, third-party outages.

#### Standard fallback
- **99.5%** — accept as moderate uplift (Binti 80c46be7, e7caae1).
- **99.9%** — accept for sophisticated customers (Wayve 710e0f5/99118ab, TRM 6dcda58/97fd6d7). Pair with termination right only for 3 consecutive months below threshold.
- **99.95%** — accept as middle-ground compromise on aggressive 99.99% asks (OnePay 05f7eef/537068a).

#### Non-negotiables
- **Preserve scheduled-maintenance / third-party-outage carve-outs.** Reject removal (Satellogic 9eae03e).
- **No 99.99% uptime SLA.** Form-level operational reality. Counter aggressive uptime requests with 99.5% or 99.9%.

#### Accept-with-comment patterns
- Termination right for 3 consecutive months or 3 months in rolling 6-month period below SLA — accept (Bumble 777d51e, ChanMed e2b8b63, OpenTable 6ce4702, fcff0b97).

### 10.2 Helpdesk Response Times

#### Opening position
"Commercially reasonable efforts" with no specific SLA (form).

#### Standard fallback
- **3 business days** — Cedar Grove's standard helpdesk response SLA (ServiceTitan 29859af/eedccfb — "3 business day helpdesk response SLA. Standard Juicebox position"). Hold firm against 48-hour asks.
- **2 business days** — secondary fallback when customer presses (Buildots 34adb7b/bc07bc1, TapTapSend 97498c3, Stack 725df07, Hover d3f0c60).

#### Non-negotiables
- **No 24-hour or 48-hour helpdesk SLA.** Counter to 2-3 business days. Frame: "Cedar Grove countered customer's aggressive 24-hour SLA with [2 business days] as more operationally feasible standard."

### 10.3 Service Credits

#### Standard fallback
- **5% of Service Fees per 45+-minute downtime, capped 1 credit/day, max 1 week's fees per month** — form structure (Culligan).
- **30% of monthly Service Fees per calendar month** — accept as market-aligned cap (fcff0b97).
- **Two weeks of fees cumulative** with cross-month application — accept (2a17fe2, CSC 9b27b65).

#### Non-negotiables
- **No cash redemption of credits.** Hold firm (Wonderful 01fb7ef — "maintained form position on credit non-redemption as cash").
- **Anti-double-dipping mechanisms** preserved (Culligan 6eb38dc/ab5ea2d).

### 10.4 Termination for Chronic SLA Failure

Accept termination right for repeated/chronic SLA failures (e.g., 3 months in rolling 6-month period). Pair with cure period and tie triggers to Juicebox-controlled causes (Sigma 820a5a0). Standard fallback.

---

## Section 11 — Audit Rights

### Opening position
DPA Section 8 — Controller may carry out inspections; Processor entitled to reasonable audit fees, with ACV < $100k customers required to pay.

### Non-negotiables
- **Reasonable audit fees for sub-$100k ACV customers.** Hold firm (Chainguard 2317ccd/94d5ab1). Frame: "Audit fees are standard and reasonable; non-negotiable on this point."
- **No third-party / subprocessor audit rights extending past Juicebox.** Reject (Rivian 6387d86/9a7f928). Frame: "Juicebox cannot bind its subprocessors to third-party audit rights; exceeds what vendor can commit."

### Standard fallback
- **Third-party reports (SOC 2 Type II, ISO 27001) in lieu of customer audit** — Cedar Grove's preferred mechanism (Chainlink 1a9f957/8d7efc4/d371357). Frame: "Third-party reports are the market standard for assurance."
- **Reasonable notice + reasonable fees** — accept (Match 7fa32ad, Procore e84bc74).
- **One free audit per year + fee schedule for additional** — Gilat compromise (b7acdc81, bcce5f6).
- **Fee waiver if audit triggered by Security Incident or Processor failure** — accept (Procore e84bc74).

### Accept-with-comment patterns
- Audit window expiring 1 year post-termination — accept against 4-year asks (Forward Financing a6ce164, FF 976d12b).
- AI-system-specific audit rights with reasonable notice — accept for regulated customers (Multiverse 17bd0e7).

---

## Source provenance

Every position above is grounded in observations in `extracted/by_doctype/ESA_clause_rollup.json` and the per-thread extractions in `extracted/<thread_key>.json`. Thread-key references are listed in `playbooks/_provenance.json` under `ESA_agent.<clause_key>.<position_type>`.

Insufficient-evidence flags: clauses with fewer than 3 observations or where the rollup signal is genuinely ambiguous are marked `tentative` in the provenance file and should be treated as starting points for attorney review rather than firm firm-wide positions.
