# Pronto Growth Teardown
### The growth ceiling is supply liquidity. No-shows are the symptom. The subscription flywheel is the cure.

*An independent teardown, built with Claude Code and pressure-tested against marketplace operators' frameworks. Every number traces to public app-store data; the pipeline is included. Findings are directional signals to test — not population truth.*

---

## 1. The 60-second version

Pronto has the hard part solved: **when a pro shows up, customers love it** (85% 5★, with specific praise — "settled me into a new city," "sparkling before the puja," "lightning-fast when my maid didn't show"). Demand and product-love are not the constraint.

The constraint is **supply liquidity** — whether a qualified pro is actually available in your pincode, in your slot, right now. When liquidity is thin, the booking fails, and because Pronto is **prepaid**, the failure converts into a refund fight and a "scam" review. The data:

- **66%** of Pronto's negative reviews are no-shows/cancellations — vs **11%** for Urban Company. Same market, opposite failure mode: **UC has crossed the liquidity threshold; Pronto hasn't yet.**
- Of the harshest reviews, where a cause is even stateable: **more point to "no pro was ever available" (liquidity) than to "a pro flaked" (matching).** But **~72% state no cause at all** — which is exactly why you can't run this on reviews; you instrument it.

**The lever isn't acquisition, and it isn't a demand-side UX patch. It's building liquidity — and the cheapest way to build liquidity is a subscription flywheel:** recurring bookings turn unpredictable demand into *forecastable* demand, which lets you pre-position supply, which makes reliability a *consequence* instead of a hope. That flywheel is the strategy. The experiments in §6 feed it.

---

## 2. What this data can NOT see (and what I'd pull on day one)

*The most important section, and the one most growth applicants skip.* App-store reviews are a self-selected sample of the furious and the delighted — there is no denominator and no cohort. They tell you the **loudest** problem, not necessarily the **biggest**. I would not run a growth strategy on them; I'd use them to form hypotheses, then validate against instrumentation. Concretely, day one I'd ask for:

| Question reviews can't answer | What I'd instrument / pull |
|---|---|
| Is a failed booking "**no pro existed**" or "**a pro flaked**"? (totally different fixes) | Event split: `booking_requested → pro_assigned → pro_checked_in → completed`, per pincode/slot. |
| How bad is the **silent** churn? (non-rebookers leave no review) | **First→second-booking cohort retention**, weekly cohorts. |
| Where is liquidity actually thin? | **Supply density**: available pro-hours ÷ requested pro-hours, by pincode × time-slot. |
| Is the "15-min" promise real or aspirational? | **Promise-to-fulfilment delta**: promised ETA vs actual check-in. |
| Does the prepaid model gate fraud / no-show, or just friction? | No-show rate and chargeback/fraud rate, prepaid vs. authorize-only test cells. |

The honest split I *can* show from reviews: of 352 of the harshest reviews, **~16% clearly point to liquidity** ("no one was assigned," "no slots," "unavailable"), **~12% to a matched pro failing** (late, on-break, assigned-then-cancelled), and **~72% give no attributable cause.** That 72% is not noise — it's the argument for event data.

---

## 3. Method

- **Scraped 4,464 public reviews** — Pronto (2,617) + benchmark Urban Company (1,847) — Google Play + Apple App Store, India. *(`scrape.py`)*
- **Classified a stratified sample of 265** into funnel stage × friction theme × JTBD × sentiment × competitor × feature request. *(`analyze.py` does this at full scale via the Claude API; the sample is hand-classified so every claim is auditable.)*
- **Root-cause split** of the harshest reviews via keyword attribution. *(`analyze_liquidity.py`)*
- **Walked the live app** as a new user.
- Tooling and data included. This was an evening's work on *public* data — point it at internal funnel data and it gets sharp fast.

---

## 4. The core finding: same market, opposite failure modes

| Negative-review theme | **Pronto** | **Urban Company** |
|---|---|---|
| Reliability (no-show / cancel) | **66%** | 11% |
| Pro quality | 10% | **38%** |
| Pricing / overcharge | 2% | **22%** |
| Support & refunds | 11% | 18% |

UC's detractors complain their pro *overcharged* — which means a pro reliably *showed up*. Pronto's complain *nobody came*. UC is past liquidity and fighting quality/trust; Pronto is still establishing liquidity. That's good news: **liquidity is an operations + matching + demand-shaping problem you can engineer** — not a brand problem.

---

## 5. The strategy: a subscription flywheel that manufactures its own liquidity

The Delta-4 logic (Kunal Shah): to beat the informal maid, Pronto must be a ≥4-point jump on the one axis the maid loses on — and the maid's weakness is *reliability*, not price. So Pronto's entire right to charge a premium is "more reliable than your maid." Thin liquidity breaks that, dropping Pronto *below* the maid. Reliability is the hinge — and liquidity is what the hinge turns on.

You don't fix liquidity by begging more pros to sit idle. You fix it by making demand **predictable**:

```
 Great first visit ─▶ Same-pro recurring subscription ─▶ Forecastable demand
        ▲                                                         │
        │                                                         ▼
 Reliability that's   ◀── Pre-positioned, fuller-utilized  ◀── Density you can
 worth referring          supply in dense pincodes             actually plan
```

Subscriptions are not a retention afterthought; they are the **engine input**. A book of weekly recurring cleans is a demand forecast, and a forecast is what lets ops guarantee a pro is there. This is also the only real **moat** thesis: you can't moat on supply *count* (cleaners are interchangeable, and UC can hire the same ones). You moat by **cornering the high-frequency buyer** — own the household's recurring slot and the loved same-pro relationship — and by owning **"reliable" as a brand** before UC's instant-help product does.

---

## 6. The experiments — one primary bet, sequenced

Everything serves **liquidity**. RICE scores are directional, to sequence — I'd recalibrate against real data day one.

### The primary bet — manufacture liquidity through forecastable demand

**E1 · The subscription flywheel: same-pro recurring after a great first visit.** `RICE: High · flagship`
After a successful first clean, one-tap "rebook Reena, every Tuesday." *Hypothesis:* recurring bookings convert unpredictable demand into a forecast ops can staff against, lifting density and reliability for *everyone* in that pincode — while locking the loved same-pro relationship UC can't easily copy. *This is the loop; the rest are enablers.* *(Evidence: "will call the same resource again"; India ARPU reality — repeat, not installs, is the money.)*

**E2 · Supply-density-aware booking — never confirm what you can't fulfil.** `RICE: High`
Only surface instant slots where available pro-hours actually cover the pincode×slot; elsewhere offer an honest scheduled slot or waitlist. *Hypothesis:* the cheapest reliability gain is refusing to promise liquidity you don't have. *(Evidence: "confirmed then no one assigned," "no slots for a week." This is the true liquidity fix.)*

### Enablers — make the failures that remain humane, and protect supply economics

**E3 · Guaranteed first visit via supply over-provisioning.** `RICE: Med-High`
For first-ever bookings, pre-commit a backup pro (over-provision the way ride-share floods a surge zone); if it still fails, **auto-refund + apology credit before the customer asks.** This is a *supply* mechanism, not just a refund policy. *(Spend the CAC you'd have burned on ads on guaranteeing the first impression instead.)*

**E4 · Fix prepaid without killing it: authorize-and-capture-on-arrival.** `RICE: Med`
Don't remove prepay — it gates fraud and supply-side no-shows and funds working capital. Instead **authorize at booking, capture only when the pro checks in.** *Hypothesis:* kills the "they took my money and ghosted" review without re-opening the fraud/no-show hole. *(Evidence: the "scam" cluster — but the fix is escrow, not removal.)*

**E5 · Honest ETA + one-tap human.** `RICE: Med · hygiene, ship first`
Replace the fake "2 minutes away" loop with a real ETA and a reachable human (not a self-closing AI chat). Lowest-leverage but fastest to ship; honesty cuts rage-cancels even when ops are slow.

---

## 7. Day-1 → 90 operating plan

- **Day 1–14:** instrument the `requested→assigned→checked-in→completed` funnel by pincode×slot; build the supply-density heatmap; pull first→second cohort retention. *Stop guessing from reviews.*
- **Day 15–45:** ship E2 (density-aware booking) + E5 (honest ETA/human) in 1–2 thin pincodes; stand up E3 over-provisioning for first bookings there.
- **Day 45–90:** launch E1 (same-pro subscription) in the proven pincodes; A/B authorize-on-arrival (E4); measure the flywheel — does subscription density lift completion rate?

**The one metric I'd stake the role on:** **first-booking completion rate** (booked → pro actually completed) in target pincodes — the single number that gates activation, retention, referral, and the "scam"-review problem at once. Secondary: first→second-booking cohort retention.

---

## 8. Why I built this

I want to do growth at Pronto, so I did a slice of the job instead of describing it — formed a thesis from real data, stress-tested it against how marketplace operators think, and pressure-tested my own assumptions. The liquidity diagnosis could still be wrong in ways your internal data would correct in a day. But forming a falsifiable thesis, naming what I can't see, and knowing the one metric I'd own — that's how I'd work on the team.

*Happy to walk through the dashboard live and pressure-test any of it.*
