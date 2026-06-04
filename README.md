# Pronto Growth Teardown — Review-Mining Engine

An independent growth teardown of **Pronto** (withpronto.com, India home-services
marketplace), built to demonstrate full-stack / PLG growth-marketing craft for a
job application. Real public data → Claude classification → dashboard → strategy.

**Not affiliated with Pronto.** Uses only public app-store reviews.

## The headline (v2)
- **4,464** public reviews mined (Pronto 2,617 + Urban Company 1,847).
- **66%** of Pronto's negative reviews are about no-shows/cancellations — vs **11%** for Urban Company. Same market, opposite failure mode.
- Of the harshest reviews, **~72% give no attributable root cause** — the case for event instrumentation over review-mining.
- → The growth ceiling is **supply liquidity** (no-shows are the symptom). The cure is a **subscription flywheel** that turns demand into a forecast you can pre-staff. The product is loved when the pro shows up (**85% 5★**).

> **v2 note:** v1 framed this as "first-booking reliability." After pressure-testing the thesis against five marketplace operators' frameworks (Lauzier, Hockenmaier, Tavel, Widjaja, Verna), it was rebuilt: reliability is a *symptom*; the disease is *supply liquidity*. v2 also adds a "what this data can't see / what I'd instrument day one" layer. See `pronto-growth-teardown-v2.md`.

## Deliverables
| File | What it is |
|---|---|
| `pronto-growth-teardown-v2.md` / `.pdf` | **The current strategy doc** — liquidity thesis, subscription flywheel, day-1→90 plan. **Start here.** |
| `dashboard.html` | Self-contained interactive dashboard (open in any browser). |
| `pronto-growth-teardown.md` | v1 (kept for the v1→v2 delta). |
| `outreach-kit.md` | Cold DM, public post, and Loom script (kept private / git-ignored). |

## The pipeline
```
scrape.py            # pull public reviews (Google Play + Apple RSS) -> data/reviews_raw.json
analyze.py           # Claude classification at scale (needs ANTHROPIC_API_KEY)
sample.py            # build a stratified sample for review
classify_sample.py   # in-context (hand-judged) classifications -> data/reviews_classified.json
analyze_liquidity.py # root-cause split: liquidity vs matching vs unclear
build_dashboard.py   # render dashboard.html from the data
```

## Run it
```bash
python3 -m venv .venv && .venv/bin/pip install google-play-scraper anthropic
.venv/bin/python scrape.py            # ~3 min, writes data/reviews_raw.json
export ANTHROPIC_API_KEY=sk-...       # to classify the FULL set with Claude
.venv/bin/python analyze.py           # -> data/reviews_classified.json + synthesis.json
.venv/bin/python build_dashboard.py   # -> dashboard.html
```
This draft used `classify_sample.py` (a hand-classified 265-review sample) so every
number is auditable without an API key; `analyze.py` is the same taxonomy at full scale.

## Method & honesty
App-store reviewers skew to extremes (85% 5★ / 13% 1★). Volume/rating stats use the
full Pronto set; theme/stage breakdowns use the classified sample. Treat findings as
**directional signal to test**, not population truth.

## Frameworks behind the analysis
Kunal Shah (Delta-4 + India ARPU paradox) · Elena Verna (growth loops, give-the-first-visit-away) ·
Bob Moesta (Jobs-to-be-Done triggers) · Anuj Rathi (marketplace liquidity).

*Built with Claude Code.*
