# Pronto Growth Teardown
### What 4,464 of your own reviews say about where growth breaks — and the 5 experiments I'd run first

*An independent teardown, built with Claude Code. Not affiliated with Pronto. Every number below is traceable to public app-store data; the pipeline that produced it is included.*

---

## The 60-second version

Pronto has the hardest part already solved: **when a pro shows up, customers love it.** 85% of your reviews are 5★, and the praise is specific — "settled into a new city," "sparkling before the puja," "lightning-fast when my maid didn't turn up." That's real product-market fit on the *job*.

The growth ceiling isn't demand. It's that **the promise breaks at the first booking.** In a hand-classified sample of your reviews:

- **66%** of Pronto's negative reviews are about **no-shows and last-minute cancellations** — versus **11%** for Urban Company in the same market.
- **55%** of those negative reviews strike at **activation** — the customer's *very first* visit.
- Because the model is **prepaid**, every failed first booking turns into a refund fight with no human to call — which is why the word "**scam**" appears again and again in 1★ reviews where the real failure was just *operational*.

This is a **Delta-4 problem** (Kunal Shah's framing): to win, Pronto must be a ≥4-point jump over the informal maid network. The maid is cheaper and already trusted — but unreliable. Pronto's entire right to exist is *"more reliable than your maid."* Right now, for a large slice of first-time users, **it isn't** — and they pay upfront to find out.

**The single highest-leverage growth lever is first-booking reliability + a no-questions recovery rail.** Fix that, and the loved product underneath finally compounds into word-of-mouth instead of refund threads. The five experiments in §6 are how I'd attack it in my first 30/60/90 days.

> **Honesty note:** app-store reviewers skew to extremes (85% 5★, 13% 1★ — almost nothing in between). I treat this as **directional signal to test**, not population truth. Where I estimate, I say so. The point of a growth hire isn't to be certain — it's to know which bet to run first.

---

## 1. What I did (method)

- **Scraped 4,464 public reviews** — Pronto (2,617) and benchmark competitor Urban Company (1,847) — from Google Play and the Apple App Store, India storefront. *(`scrape.py`)*
- **Classified a stratified sample of 265** reviews into funnel stage × friction theme × Jobs-to-be-Done trigger × sentiment × competitor mention × feature request. *(`analyze.py` runs this over the full set via the Claude API; for this draft I hand-classified the sample so every claim is auditable.)*
- **Built an interactive dashboard** (`dashboard.html`) so you can see the distributions yourself.
- **Walked the live app** as a new user to ground the data in the actual booking flow.

Tooling and raw data are all in the attached folder. This took an evening — imagine it pointed at your internal funnel data.

---

## 2. The funnel, with your reviews mapped onto it

Marketplace AARRR. Activation = **first completed booking**; Retention = **repeat + subscription**.

| Stage | What the reviews say | Read |
|---|---|---|
| **Acquisition** | "Not available in my area / no slots for a week." Instagram & founder-brand buzz is clearly pulling installs. | Top of funnel is **working** — don't over-invest here. |
| **Activation** ⚠️ | **55% of negative reviews.** "Booked my first service, no one came, no refund." | **This is the leak.** The first visit is where trust is won or torched. |
| **Retention** | "Used it 10 times, 95% get cancelled." "Daily customer, still no-show." | Even lovers churn when reliability is a coin-flip. |
| **Referral** | Promoters explicitly recommend; detractors explicitly *anti*-recommend ("I'm going to discourage people"). | The word-of-mouth loop runs **both** directions. Negative WoM is compounding too. |
| **Revenue** | Prepaid + "0% refund on cancel" + weekend price bumps = "scam" framing. | The monetization mechanic is **amplifying** the reliability failure. |

---

## 3. The core finding: same market, opposite failure modes

Pronto and Urban Company operate in the same cities for the same customers. Their **detractors complain about completely different things** — and that's the most important slide in this deck.

| Negative-review theme | **Pronto** | **Urban Company** |
|---|---|---|
| Reliability (no-show / cancel) | **66%** | 11% |
| Pro quality | 10% | **38%** |
| Pricing / overcharge | 2% | **22%** |
| Support & refunds | 11% | 18% |

**Interpretation.** UC has *solved liquidity* — pros show up; their problems are competence and upselling. Pronto hasn't crossed the liquidity threshold yet: the complaints are almost entirely "**nobody came.**" That's actually good news — reliability is an **operational + matching** problem you can engineer, not a brand problem. But until it's fixed, UC's worst-case ("my technician overcharged me") still beats Pronto's worst-case ("I prepaid and waited 3 hours for no one").

---

## 4. The Delta-4 read — is Pronto a ≥4-point jump over the maid?

Kunal Shah's test: a product must be a 4+ point efficiency jump (on 10) over the status quo to be *irreversible*, *forgiven for failures*, and *bragged about*. The status quo here is **the informal maid/cleaner network.**

| Dimension | Informal maid | Pronto (when it works) | Pronto (when it fails) |
|---|---|---|---|
| Price | Cheapest | Higher | Higher **and** prepaid |
| Trust / safety | Known but unverified | Verified, rated | — |
| **Reliability** | Unreliable | **15-min, on-demand** | **Worse than the maid** |
| Convenience | Manage yourself | One tap | One tap → no-show |

When Pronto works, it's a clear Delta-4 — that's why the 5★ reviews are euphoric. When it fails the first booking, it collapses **below** the maid on the one dimension that justifies the price premium. There's no middle: you're either the magic or the scam. **Reliability is the hinge the entire Delta-4 swings on.**

### Messaging corollary (Shah's "time-valuation gap")
Indians historically under-value time, so "save time" is a weak hook. The promoters don't talk about time — they talk about **trust, dignity, and rescue** ("when my maid didn't show," "settled me into a new city," "before the puja"). **Sell reliability-as-peace-of-mind, not speed.** "The house help that actually shows up" is a sharper UBP than "house help in minutes."

---

## 5. The one lever (if you only fix one thing)

> **Make the *first* booking near-100% reliable, and when it does fail, recover it instantly and humanely — before the customer has to ask.**

Everything compounds off this: activation → repeat → subscription → referral are all gated by whether visit #1 happened. And the prepaid model means a failed first booking isn't neutral — it's a refund fight that manufactures a 1★ "scam" review and negative word-of-mouth. Fixing first-booking reliability simultaneously lifts activation, retention, *and* referral, and defuses the revenue-mechanic backlash.

---

## 6. The 30/60/90 experiment backlog (RICE-scored)

RICE = Reach × Impact × Confidence ÷ Effort. Scores are my directional estimates to sequence the work, not promises — I'd recalibrate against your real funnel data on day 1. Each ties to a review-evidence citation and a JTBD trigger.

### First 30 days — stop the bleeding at activation

**E1 · "Guaranteed First Visit" — over-provision + free recovery on booking #1.** `RICE: High`
First-ever bookings get redundant pro assignment (back-up pro pre-committed) and, if it still fails, an **automatic instant full refund + apology credit before the customer complains.** *Hypothesis:* converting the first no-show from a refund-fight into a "wow, they made it right" moment flips 1★ would-be churners into retained users. *Evidence:* the entire reliability + support cluster (66% + 11% of negatives). *Lever:* Elena Verna — *give the first visit away aggressively as a marketing cost; CAC you'd have spent on ads, spent on trust instead.*

**E2 · Kill the prepaid trust-bomb on first booking — pay-after or pre-auth-only.** `RICE: High`
Authorize, don't capture, until the pro checks in. *Hypothesis:* removing upfront capture on visit #1 collapses the "scam" perception and lowers first-booking abandonment. *Evidence:* "they take money in advance then ghost you," repeated across dozens of 1★ reviews.

**E3 · Honest ETA + one-tap human.** `RICE: Med-High`
Replace the fake "2 minutes away" loop with a real, possibly-bad ETA and a **live human** (not an AI-chat that closes itself). *Hypothesis:* honesty + a reachable human cuts rage-cancels even when ops are slow. *Evidence:* "'2 minutes away' for an hour," "AI chat closes after 10 mins."

### 60 days — convert the saved first-timers into a habit

**E4 · Supply-density-aware booking + waitlist instead of false confirms.** `RICE: Med`
Only show instant slots where pro density actually supports the 15-min promise; elsewhere, an honest scheduled slot or waitlist. *Hypothesis:* never confirming a booking you can't fulfil is the cheapest reliability gain available. *Evidence:* "confirmed then no one assigned," "no slots for a week." *Lever:* Anuj Rathi — marketplace liquidity per pincode is the real constraint.

**E5 · The "second-clean" trust loop → subscription.** `RICE: Med`
After a *successful* first visit, trigger a one-tap rebook-the-same-pro + a soft subscription nudge ("same Reena, every Tuesday"). *Hypothesis:* a great visit #1 + same-pro continuity is the natural on-ramp to recurring revenue — the ARPU lever that matters in a low-ARPU market. *Evidence:* "will call the same resource again"; the India DAU/ARPU paradox (Shah) — installs are cheap, *repeat* is the money.

### 90 days — turn reliability into the brand & the loop

- **Reposition on reliability** ("the house help that *shows up*") and let saved-first-timers fuel a **referral/RWA-WhatsApp loop** (Verna's word-of-mouth engine), now that the experience is worth referring.
- **JTBD-triggered campaigns** for the real pushes the reviews reveal — *new-city move-in, festival/guests, maid-just-quit* — where reliability is most desperately valued and willingness-to-pay is highest (Moesta).

---

## 7. What I'd measure

- **North Star:** *Successful first visits per week* (booked → pro actually completed). It captures acquisition × activation × reliability in one number.
- **Inputs:** first-booking fulfilment rate · first-booking → second-booking conversion · time-to-human-support · refund-resolution time · 30-day repeat rate · subscription attach.
- **Guardrail:** 1★-review rate and reliability-complaint share (this teardown is the baseline — re-run `analyze.py` monthly to watch it move).

---

## 8. Why I built this

I want to do growth at Pronto, so I did a slice of the job instead of describing it. The reliability thesis might be wrong in ways your internal data would correct in a day — but the *way* I got here (real data → classification → a falsifiable lever → sequenced experiments → a metric) is how I'd work on the team. Happy to walk through the dashboard live and pressure-test any of it.

*Happy to walk through the dashboard live and pressure-test any of it.*
