#!/usr/bin/env python3
"""Build a stratified review sample for in-context classification.

Writes data/sample.json (full records, with a stable 'sid') and
data/sample.txt (compact, numbered, for reading).
"""
import json
import random
from pathlib import Path

DATA = Path(__file__).parent / "data"
raw = json.load(open(DATA / "reviews_raw.json"))
random.seed(42)


def pick(brand, lo, hi, n):
    pool = [r for r in raw if r["brand"] == brand and lo <= r["rating"] <= hi
            and len(r["text"]) > 30]
    random.shuffle(pool)
    return pool[:n]


sample = (
    pick("pronto", 1, 2, 150)        # Pronto detractors — the growth signal
    + pick("pronto", 5, 5, 55)       # Pronto promoters — what works
    + pick("pronto", 3, 4, 15)       # Pronto passives
    + pick("urban_company", 1, 2, 45)  # UC detractors — benchmark
)
for i, r in enumerate(sample):
    r["sid"] = i

json.dump(sample, open(DATA / "sample.json", "w"), ensure_ascii=False, indent=2)
with open(DATA / "sample.txt", "w") as f:
    for r in sample:
        txt = " ".join(r["text"].split())[:300]
        f.write(f"{r['sid']}\t{r['brand'][:2]}\t{r['rating']}*\t{txt}\n")
print(f"Wrote {len(sample)} reviews to sample.json / sample.txt")
