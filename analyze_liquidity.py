#!/usr/bin/env python3
"""Split Pronto's reliability failures into root-cause buckets, to test the
v2 thesis that no-shows are a SYMPTOM of a supply-LIQUIDITY problem (we never
had a pro) vs a matching/quality problem (a pro was assigned, then flaked).

Heuristic keyword pass over ALL Pronto negative-leaning reviews. Directional,
not exact — a review can hit both buckets; we report overlap honestly.

Writes data/liquidity_split.json for the dashboard.
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).parent / "data"
raw = json.load(open(DATA / "reviews_raw.json"))
pr = [r for r in raw if r["brand"] == "pronto" and r.get("rating", 5) <= 2
      and len(r["text"]) > 20]

# "We never had a pro" — liquidity / demand-promise-failure signals
NEVER_ASSIGNED = re.compile(
    r"no\s+(one|professional|partner|maid|helper|service\s*provider|staff)\s+"
    r"(was\s+|is\s+|got\s+|gets\s+)?(assigned|available|allotted|allocated)|"
    r"not\s+(been\s+)?assigned|no\s+slots?\b|slots?\s+(are\s+)?(not\s+|never\s+)?available|"
    r"finding\s+(a\s+)?(professional|partner|maid|helper)|"
    r"unavailab|no\s+professional|never\s+assigned|under\s*staff|"
    r"not\s+available\s+in\s+(my\s+)?(area|location)|service\s+not\s+available|"
    r"couldn.?t\s+find|could\s+not\s+find|no\s+partner|no\s+resources|"
    r"don.?t\s+have\s+(enough\s+)?(staff|partners?|professionals?|resources)|"
    r"take\s+(the\s+)?booking.{0,40}(no\s+one|nobody|don.?t\s+send|cancel|can.?t\s+assign)|"
    r"no\s+helper|no\s+maid\s+(available|assigned)",
    re.I,
)
# "A pro was matched, then failed" — matching/quality/ops signals
PRO_FLAKED = re.compile(
    r"(came|arrived|reached|turned\s*up|showed\s*up)\s+(very\s+|too\s+)?late|"
    r"late\s+by|hours?\s+late|came\s+at\s+\d|on\s+break|"
    r"accepted.{0,30}(then|but|and).{0,30}cancel|assigned.{0,30}(then|but|and).{0,30}cancel|"
    r"partner\s+cancel|maid\s+cancel|she\s+cancel|he\s+cancel|"
    r"reschedul|didn.?t\s+(come|show|arrive)\s+(on\s+)?time|"
    r"not\s+(on\s+)?time|left\s+(early|halfway|within)|came\s+\d+\s*(min|hour)",
    re.I,
)

n = len(pr)
never = sum(1 for r in pr if NEVER_ASSIGNED.search(r["text"]))
flaked = sum(1 for r in pr if PRO_FLAKED.search(r["text"]))
both = sum(1 for r in pr if NEVER_ASSIGNED.search(r["text"]) and PRO_FLAKED.search(r["text"]))
# attribute "both" to liquidity (the more upstream cause); keep buckets disjoint
liquidity = never
matching = flaked - both
either = sum(1 for r in pr if NEVER_ASSIGNED.search(r["text"]) or PRO_FLAKED.search(r["text"]))
unclear = n - either  # says "scam/worst/fraud" etc. with no attributable cause

out = {
    "n_negative": n,
    "liquidity": liquidity,            # we never had a pro
    "matching": matching,              # a pro was matched, then failed
    "unclear": unclear,                # no attributable root cause in the review
    "liquidity_pct": round(100 * liquidity / n),
    "matching_pct": round(100 * matching / n),
    "unclear_pct": round(100 * unclear / n),
}
json.dump(out, open(DATA / "liquidity_split.json", "w"), indent=2)
print(json.dumps(out, indent=2))
print(f"\nOf {n} Pronto 1-2★ reviews: {out['liquidity_pct']}% point to 'we never "
      f"had a pro' (liquidity), {out['matching_pct']}% to 'a pro was matched then "
      f"failed', and {out['unclear_pct']}% give no attributable cause — the gap "
      f"event-instrumentation would close.")
