#!/usr/bin/env python3
"""
analyze.py — Classify scraped reviews with Claude into a fixed growth taxonomy.

Reads:  data/reviews_raw.json
Writes: data/reviews_classified.json   (raw fields + classification)
        data/synthesis.json            (one Opus synthesis pass for the teardown)

Efficiency (per the claude-api skill):
  * Fixed taxonomy lives in a CACHED system block (cache_control) so every
    request after the first reuses it at ~0 cost.
  * Reviews are sent in batches of N inside a single user turn; Claude returns
    a JSON array, one object per review.
  * Per-review classification uses Haiku (cheap); the final synthesis pass
    uses Opus (smart). Output is cached to disk so re-runs are free.

Requires: ANTHROPIC_API_KEY in the environment.
"""

import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic

DATA = Path(__file__).parent / "data"
RAW = DATA / "reviews_raw.json"
CLASSIFIED = DATA / "reviews_classified.json"
SYNTHESIS = DATA / "synthesis.json"

CLASSIFY_MODEL = "claude-haiku-4-5"
SYNTH_MODEL = "claude-opus-4-8"
BATCH = 25  # reviews per request

# --- The taxonomy (cached system prompt) -----------------------------------
TAXONOMY = """You are a senior growth analyst classifying app-store reviews for
Pronto, an on-demand + subscription home-services marketplace in India (home
cleaning, bathroom/kitchen, laundry, ironing; verified pros; 15-min instant or
recurring booking; flat transparent pricing). Its benchmark competitor is Urban
Company.

For EACH review, return an object with exactly these fields:

- "funnel_stage": one of
    "acquisition"   (discovery, install, first impression, pricing-to-try)
    "activation"    (the FIRST booking / first completed service experience)
    "retention"     (repeat use, subscription, reliability over time, churn)
    "referral"      (recommending, word of mouth, referral mechanics)
    "revenue"       (pricing fairness, value-for-money, billing, refunds)
    "none"          (no usable growth signal)

- "theme": one of
    "pro_quality"        (skill, behaviour, professionalism of the worker)
    "reliability"        (no-show, late, cancellation, auto-reassignment)
    "pricing_value"      (price, hidden charges, value for money, billing)
    "app_booking_ux"     (app usability, booking flow, OTP, address, slots)
    "support_refunds"    (customer support, complaint handling, refunds)
    "scheduling"         (availability of slots, timing, rescheduling)
    "supply_availability"(no pros in my area / pincode, service unavailable)
    "other"

- "jtbd": the underlying job/trigger if visible, one of
    "maid_gap"      (regular maid absent/quit/unreliable)
    "event_guests"  (guests, festival, party, deep-clean for an occasion)
    "post_event"    (post-renovation, post-construction, move-in/move-out)
    "life_change"   (new baby, elderly care, new city, no help network)
    "routine"       (ongoing routine upkeep / convenience)
    "unknown"

- "sentiment": "positive" | "negative" | "mixed" | "neutral"
- "competitor_mention": true | false (mentions UC/Urbanclap or another rival)
- "feature_request": short string of the concrete ask, or "" if none

Output ONLY a JSON array of these objects, in the SAME ORDER as the input
reviews, no prose. If a review is empty or unusable, still emit an object with
funnel_stage "none" and theme "other"."""


def classify(client: Anthropic, reviews: list[dict]) -> list[dict]:
    results: list[dict] = []
    total = len(reviews)
    for i in range(0, total, BATCH):
        chunk = reviews[i : i + BATCH]
        numbered = "\n".join(
            f"[{j}] (rating={r.get('rating')}) {r['text'][:600]}"
            for j, r in enumerate(chunk)
        )
        msg = client.messages.create(
            model=CLASSIFY_MODEL,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": TAXONOMY,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"Classify these {len(chunk)} reviews:\n\n{numbered}",
                }
            ],
        )
        text = msg.content[0].text.strip()
        # tolerate markdown fences
        if text.startswith("```"):
            text = text.split("```")[1].lstrip("json").strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            print(f"  ! batch {i}-{i+len(chunk)} unparseable; filling 'none'")
            parsed = [{"funnel_stage": "none", "theme": "other"} for _ in chunk]
        for r, c in zip(chunk, parsed):
            results.append({**r, **c})
        print(f"  classified {min(i+BATCH, total)}/{total}")
    return results


def synthesize(client: Anthropic, classified: list[dict]) -> dict:
    """One Opus pass over the aggregate to draft the teardown's spine."""
    pronto = [r for r in classified if r["brand"] == "pronto"]
    # Compact aggregate to keep the prompt small
    from collections import Counter

    def counts(key):
        return dict(Counter(r.get(key) for r in pronto if r.get("rating")))

    neg = [r for r in pronto if r.get("sentiment") == "negative"]
    sample_neg = [r["text"][:300] for r in neg[:40]]
    feature_reqs = [r["feature_request"] for r in pronto if r.get("feature_request")][:40]

    agg = {
        "n_pronto": len(pronto),
        "avg_rating": round(
            sum(r["rating"] for r in pronto if r.get("rating"))
            / max(1, sum(1 for r in pronto if r.get("rating"))),
            2,
        ),
        "by_funnel_stage": counts("funnel_stage"),
        "by_theme": counts("theme"),
        "by_jtbd": counts("jtbd"),
        "sample_negative": sample_neg,
        "feature_requests": feature_reqs,
    }

    prompt = f"""You are a world-class growth marketer applying Kunal Shah's
Delta-4 + India ARPU lens, Elena Verna's growth-loop thinking, and Bob Moesta's
JTBD. Here is aggregated review data for Pronto:

{json.dumps(agg, ensure_ascii=False, indent=2)}

Produce JSON with:
- "thesis": one sharp sentence on Pronto's single biggest growth gap.
- "top_growth_blockers": array of up to 5 {{"blocker","funnel_stage","evidence"}}.
- "delta4_read": is Pronto a >=4-point jump over the informal maid network? where it is / isn't.
- "experiments": array of 5 {{"name","hypothesis","funnel_stage","rice_estimate"}}.
Output ONLY the JSON object."""

    msg = client.messages.create(
        model=SYNTH_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip()
    return {"aggregate": agg, "synthesis": json.loads(text)}


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ERROR: set ANTHROPIC_API_KEY first (export ANTHROPIC_API_KEY=...)")
    if not RAW.exists():
        sys.exit("ERROR: run scrape.py first — data/reviews_raw.json missing")

    reviews = json.loads(RAW.read_text())
    print(f"Loaded {len(reviews)} reviews")
    client = Anthropic()

    classified = classify(client, reviews)
    CLASSIFIED.write_text(json.dumps(classified, ensure_ascii=False, indent=2))
    print(f"Wrote {CLASSIFIED}")

    synthesis = synthesize(client, classified)
    SYNTHESIS.write_text(json.dumps(synthesis, ensure_ascii=False, indent=2))
    print(f"Wrote {SYNTHESIS}")


if __name__ == "__main__":
    main()
