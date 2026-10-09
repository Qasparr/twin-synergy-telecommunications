# NSF SBIR Phase I — Budget Outline
## Twin Synergy Telecommunications

> "The budget is the plan expressed in money." — adapted from the standing maxim of grantcraft: a dollar without a task behind it is an unproved claim.

**Date:** 2026-10-09
**93**

**Author:** Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
*All Rights Reserved, Without Prejudice*
CashApp: $axoneme

---

**DRAFT FOR HIS RED PEN — NOT A SUBMISSION.**

- Phase I cap: **$305,000** [VERIFIED FACT — NSF SBIR/STTR, current].
- Phase I duration: 6–18 months [VERIFIED FACT]; this budget assumes **12 months** [HYPOTHESIS].
- **Every dollar figure below is [HYPOTHESIS] except the $305,000 cap.** Nothing here is a cost the company has actually incurred or committed to. The company is not yet formed — noted as in-progress under NSF's PI-primary-employment rule below.
- Tagging rule for this draft: [HYPOTHESIS] = number assumed, not measured; [VERIFIED FACT] = independently established.

---

## A. Senior Personnel [HYPOTHESIS]

| Role | Effort | Salary basis (annual, FTE) | Cost |
|---|---|---|---|
| PI — Johnathan 'Qasparr' Monroe | 75% × 12 mo | $95,000 | $71,250 |
| Senior Network Engineer (TBD) | 50% × 12 mo | $85,000 | $42,500 |
| **A subtotal** | | | **$113,750** |

Arithmetic: 0.75 × 95,000 = 71,250; 0.50 × 85,000 = 42,500; 71,250 + 42,500 = **113,750**.

**Justification:** The R&D tasks for Phase I — Tor/onion-service engineering, DID identity prototype, $PP/$00 testnet, CALEA-compliance engineering, measurement of the DID sybil-detection rate — require one PI driving architecture full-ish time and one senior engineer executing the networking and cryptography work. The 75%/50% splits are [HYPOTHESIS]; see red-pen notes. The salary bases are [HYPOTHESIS] placeholders, chosen as conservative early-startup compensation, not market offers.

**NSF rule to note:** The PI's primary employment (51%+) must be with the awardee company at time of award [VERIFIED FACT]. Twin Synergy Telecommunications is not yet formed; entity formation is a budgeted line (Section E) and an in-progress action.

## B. Fringe Benefits [HYPOTHESIS]

Rate: **25% of Senior Personnel** = 0.25 × 113,750 = **$28,437.50**

**Justification:** Covers payroll tax, workers' comp, and minimal health coverage for a two-person startup with no benefits plan in place. No fringe rate has been negotiated or quoted; 25% is a conservative placeholder, not an offer or a policy [HYPOTHESIS]. Red-pen to confirm before any submission.

## C. Equipment [HYPOTHESIS] — modest

| Item | Cost |
|---|---|
| Test routers × 2 @ $400 | $800 |
| Test terminals (used phones/tablets) | $1,500 |
| HSM / smartcard USB keys for key ceremonies | $600 |
| **C subtotal** | **$2,900** |

**Justification:** Phase I needs a small lab bench to test onion-service routing and the DID identity prototype against real hardware, not only cloud instances. Equipment is excluded from indirect-cost base (MTDC) under standard practice. Kept deliberately modest — nothing here is a production build-out.

## D. Travel [HYPOTHESIS]

| Trip | Cost |
|---|---|
| One technical conference (registration, travel, 3 nights) | $2,500 |
| One agency visit, Washington DC (travel, 2 nights) | $1,800 |
| **D subtotal** | **$4,300** |

**Justification:** One conference to present Phase I measurement results and recruit technical review; one DC visit for agency engagement. Destinations, conferences, and timing are [HYPOTHESIS] — nothing booked, nothing priced from quotes.

## E. Other Direct Costs [HYPOTHESIS]

| Item | Cost |
|---|---|
| Cloud / compute for testnet (12 mo @ $300/mo) | $3,600 |
| Legal — entity formation + CALEA counsel consult | $6,000 |
| Independent security audit of DID prototype + testnet | $12,000 |
| **E subtotal** | **$21,600** |

**Justification:**
- **Cloud/compute:** 12 months of VPS/bandwidth for the $PP/$00 testnet and onion-service nodes. $300/mo is a placeholder scaled from current pricing, not a quote [HYPOTHESIS].
- **Legal:** Entity formation (LLC/C-corp decision still open) plus a paid consult with telecom counsel on the CALEA-compliance engineering line — the compliance lane is counsel's, never ours; this budget buys the questions, not the answers.
- **Security audit:** One independent review of the DID identity prototype and testnet before Phase I closeout. $12,000 is a placeholder for a small-scope audit, not a bid [HYPOTHESIS].

## F. Indirect Costs [HYPOTHESIS]

The company has **no negotiated indirect cost rate** — it does not yet exist.

Approach used here: the **10% de minimis rate** on a Modified Total Direct Cost (MTDC) base [HYPOTHESIS — this is a choice, not a rate the company holds].

- Total direct costs = 113,750 + 28,437.50 + 2,900 + 4,300 + 21,600 = **$170,987.50**
- MTDC base = 170,987.50 − 2,900 (equipment excluded) = **$168,087.50**
- F subtotal = 0.10 × 168,087.50 = **$16,808.75**

Red-pen to confirm: accept de minimis, or state TBD and negotiate with NSF at award.

## G. Small Business Fee [HYPOTHESIS]

NSF SBIR permits a small-business fee of **up to 7%** [VERIFIED FACT — current NSF practice].

Fee used here: **5%** of (direct + indirect) — [HYPOTHESIS choice].

- Base = 170,987.50 + 16,808.75 = **$187,796.25**
- G subtotal = 0.05 × 187,796.25 = $9,389.8125 → **$9,389.81**

---

## Grand Total

| Section | Amount |
|---|---|
| A. Senior Personnel | $113,750.00 |
| B. Fringe Benefits | $28,437.50 |
| C. Equipment | $2,900.00 |
| D. Travel | $4,300.00 |
| E. Other Direct Costs | $21,600.00 |
| F. Indirect Costs | $16,808.75 |
| G. Small Business Fee | $9,389.81 |
| **TOTAL** | **$197,186.06** |

**Check:** 113,750.00 + 28,437.50 + 2,900.00 + 4,300.00 + 21,600.00 + 16,808.75 + 9,389.81 = **197,186.06 ≤ 305,000** ✓

**Headroom:** $305,000 − $197,186.06 = **$107,813.94** unallocated. This is a lean 12-month draft, not a maximal claim. Headroom is deliberate — it can absorb his red-pen additions (higher PI salary basis, longer months, a second engineer, contingency) without breaking the cap.

---

## Notes for his red pen

He must confirm or rule on each of these before this draft touches any real submission:

1. **PI salary basis ($95,000) and effort (75%)** — assumed. His call entirely; the 51%+ primary-employment rule is a [VERIFIED FACT] constraint at award.
2. **Second senior hire ($85,000 @ 50%)** — assumed. Could be cut, made a consultant line, or converted to subcontract; each changes the indirect base.
3. **Fringe rate (25%)** — placeholder, not a plan. No benefits plan exists yet.
4. **Indirect approach (10% de minimis)** — assumed. Alternative: state TBD and negotiate at award. NSF allows either path; pick one before submission.
5. **Fee rate (5% of 7% max)** — assumed conservative choice. Could go to 7% or zero.
6. **12-month duration** — assumed within the 6–18 month window. Stretching to 18 months changes every monthly line.
7. **Company formation** — in progress, not done. Formation cost is budgeted (Section E), and the PI-employment rule bites at award, not at application.
8. **Equipment/modesty level** — deliberately lean. If he wants a bigger lab bench, the headroom covers it.
9. **Conference and DC trip** — [HYPOTHESIS] travel, nothing booked. Destinations and events TBD by him.
10. **Security audit scope** — placeholder bid. Real scope gets defined once the DID prototype exists.

---

93 93/93

*"Every man and every woman is a star." — Liber AL, I:3*
