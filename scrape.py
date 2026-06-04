#!/usr/bin/env python3
"""
scrape.py — Pull public app-store reviews for Pronto and its benchmark
competitor Urban Company, from both Google Play and the Apple App Store.

Output: data/reviews_raw.json  (a flat list of normalized review dicts)

Public data only. Reasonable volume, polite pauses between pages.
"""

import json
import time
import urllib.request
from pathlib import Path

from google_play_scraper import Sort, reviews as gp_reviews

DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)
OUT = DATA / "reviews_raw.json"

# --- App identifiers -------------------------------------------------------
APPS = {
    "pronto": {
        "play_id": "com.company.pronto",
        "ios_name": "pronto-house-help-in-minutes",
        "ios_id": 6743402816,
    },
    "urban_company": {
        "play_id": "com.urbanclap.urbanclap",
        "ios_name": "urban-company-prev-urbanclap",
        "ios_id": 1032480595,
    },
}

# Pull targets. Pronto is the subject (pull deep); UC is a benchmark (lighter).
PLAY_TARGET = {"pronto": 4000, "urban_company": 1500}
IOS_TARGET = {"pronto": 1500, "urban_company": 600}
COUNTRY = "in"  # India


def scrape_play(brand: str, app_id: str, target: int) -> list[dict]:
    """Page through Google Play reviews until we hit `target` or run dry."""
    collected: list[dict] = []
    token = None
    while len(collected) < target:
        batch, token = gp_reviews(
            app_id,
            lang="en",
            country=COUNTRY,
            sort=Sort.NEWEST,
            count=min(200, target - len(collected)),
            continuation_token=token,
        )
        if not batch:
            break
        for r in batch:
            collected.append(
                {
                    "brand": brand,
                    "source": "google_play",
                    "rating": r.get("score"),
                    "text": (r.get("content") or "").strip(),
                    "date": r.get("at").isoformat() if r.get("at") else None,
                    "app_version": r.get("reviewCreatedVersion"),
                    "thumbs_up": r.get("thumbsUpCount"),
                }
            )
        print(f"  [play/{brand}] {len(collected)}/{target}")
        if token is None:
            break
        time.sleep(0.6)
    return collected


def scrape_ios(brand: str, name: str, app_id: int, target: int) -> list[dict]:
    """Apple App Store reviews via the public RSS customer-reviews feed.

    The feed is paginated (~50/page, up to 10 pages = ~500 max per store).
    Stdlib only — no third-party HTTP deps.
    """
    out: list[dict] = []
    headers = {"User-Agent": "Mozilla/5.0 (review-analysis; growth teardown)"}
    for page in range(1, 11):
        if len(out) >= target:
            break
        url = (
            f"https://itunes.apple.com/{COUNTRY}/rss/customerreviews/"
            f"page={page}/id={app_id}/sortby=mostrecent/json"
        )
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            entries = data.get("feed", {}).get("entry", [])
            # First entry is app metadata when present; keep only review entries
            review_entries = [e for e in entries if "im:rating" in e]
            if not review_entries:
                break
            for e in review_entries:
                out.append(
                    {
                        "brand": brand,
                        "source": "app_store",
                        "rating": int(e["im:rating"]["label"]),
                        "text": (e.get("content", {}).get("label") or "").strip(),
                        "date": e.get("updated", {}).get("label"),
                        "app_version": e.get("im:version", {}).get("label"),
                        "thumbs_up": None,
                    }
                )
            print(f"  [ios/{brand}] page {page} -> {len(out)} total")
        except Exception as e:  # noqa: BLE001 — keep going if one page fails
            print(f"  [ios/{brand}] page {page} FAILED: {e}")
            break
        time.sleep(0.6)
    return out


def main() -> None:
    all_reviews: list[dict] = []
    for brand, ids in APPS.items():
        print(f"== {brand} ==")
        all_reviews += scrape_play(brand, ids["play_id"], PLAY_TARGET[brand])
        all_reviews += scrape_ios(
            brand, ids["ios_name"], ids["ios_id"], IOS_TARGET[brand]
        )

    # Drop empties, dedupe on (brand, source, text)
    seen = set()
    cleaned = []
    for r in all_reviews:
        if not r["text"]:
            continue
        key = (r["brand"], r["source"], r["text"])
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(r)

    OUT.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2))

    # Summary
    from collections import Counter

    by = Counter((r["brand"], r["source"]) for r in cleaned)
    print("\n=== SAVED", len(cleaned), "reviews to", OUT, "===")
    for (brand, source), n in sorted(by.items()):
        print(f"  {brand:14} {source:12} {n}")


if __name__ == "__main__":
    main()
