# Pronto Growth Teardown — Review-Mining Engine

An independent growth teardown of **Pronto** (withpronto.com, India home-services
marketplace), built to demonstrate full-stack / PLG growth-marketing craft for a
job application. Real public data → Claude classification → dashboard → strategy.

**Not affiliated with Pronto.** Uses only public app-store reviews.

## The headline
- **4,464** public reviews mined (Pronto 2,617 + Urban Company 1,847).
- **66%** of Pronto's negative reviews are about no-shows/cancellations — vs **11%** for Urban Company.
- **55%** of those hit at **activation** (the first booking). The product is loved when the pro shows up (**85% 5★**).
- → The growth lever is **first-booking reliability + humane recovery**, not acquisition.

## Deliverables
| File | What it is |
|---|---|
| `pronto-growth-teardown.md` / `.pdf` | The strategy doc — thesis, Delta-4 read, 30/60/90 experiments. **Start here.** |
| `dashboard.html` | Self-contained interactive dashboard (open in any browser). |
| `outreach-kit.md` | Cold DM, public post, and Loom script to get it in front of Pronto. |

## The pipeline
```
scrape.py            # pull public reviews (Google Play + Apple RSS) -> data/reviews_raw.json
analyze.py           # Claude classification at scale (needs ANTHROPIC_API_KEY)
sample.py            # build a stratified sample for review
classify_sample.py   # in-context (hand-judged) classifications -> data/reviews_classified.json
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
