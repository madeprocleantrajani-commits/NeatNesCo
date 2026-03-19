"""
Saturation Detector v1
-----------------------
Detects oversaturated products that should be REJECTED.

A product is saturated when too many sellers are already competing:
  - Too many Facebook ads running
  - Too many Shopify stores selling it
  - Too many TikTok creatives

Saturation Index = weighted(ad_density + store_count + creative_count)

Thresholds:
  ads > 200 AND stores > 100  =>  SATURATED (reject)
  ads > 100 OR stores > 50    =>  HIGH_COMPETITION (caution)
  ads < 50 AND stores < 20    =>  LOW_COMPETITION (opportunity)

Outputs: data/saturation_YYYY-MM-DD.json
"""
import json
import re
import time
import random
from datetime import datetime
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from config import (
    DATA_DIR, SEED_KEYWORDS, get_logger, get_session, resilient_fetch,
)
from alert_bot import send_alert

log = get_logger("saturation_detector")


def _load_latest_json(prefix: str) -> dict | None:
    files = sorted(DATA_DIR.glob(f"{prefix}_*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def count_fb_ads(keyword: str, session) -> int:
    """Count active Facebook ads for a keyword."""
    encoded = quote_plus(keyword)
    url = (
        f"https://www.facebook.com/ads/library/"
        f"?active_status=active&ad_type=all&country=US"
        f"&q={encoded}&search_type=keyword_unordered"
    )
    response = resilient_fetch(url, session=session, timeout=25)
    if not response:
        return 0

    try:
        soup = BeautifulSoup(response.text, "lxml")
        text = soup.get_text()
        match = re.search(r'(\d[\d,]*)\s*(?:results?|ads?)', text, re.I)
        if match:
            return int(match.group(1).replace(",", ""))
    except Exception as e:
        log.debug(f"FB ad count error for '{keyword}': {e}")
    return 0


def count_shopify_stores(keyword: str, session) -> int:
    """Estimate how many Shopify stores sell this product via Google."""
    query = f'{keyword} site:myshopify.com OR site:shopify.com "add to cart"'
    url = f"https://www.google.com/search?q={quote_plus(query)}&num=10"

    response = resilient_fetch(url, session=session, timeout=15)
    if not response:
        return 0

    try:
        text = response.text.lower()
        # Google shows "About X results"
        match = re.search(r'about\s+([\d,]+)\s+results', text)
        if match:
            return int(match.group(1).replace(",", ""))
        # Count actual result links with shopify
        soup = BeautifulSoup(response.text, "lxml")
        links = soup.select("a[href*='shopify'], a[href*='myshopify']")
        return len(links) * 50  # Rough estimate
    except Exception:
        return 0


def count_google_shopping(keyword: str, session) -> int:
    """Count Google Shopping results as competition proxy."""
    url = f"https://www.google.com/search?q={quote_plus(keyword)}&tbm=shop"
    response = resilient_fetch(url, session=session, timeout=15)
    if not response:
        return 0

    try:
        text = response.text
        match = re.search(r'About\s+([\d,]+)\s+results', text)
        if match:
            return int(match.group(1).replace(",", ""))
        soup = BeautifulSoup(text, "lxml")
        items = soup.select(".sh-dgr__content, .sh-dlr__list-result")
        return len(items) * 10
    except Exception:
        return 0


def calculate_saturation_index(ad_count: int, store_count: int,
                                shopping_count: int) -> dict:
    """
    Calculate Saturation Index (0-100).

    Formula:
      ad_score = min(ad_count / 5, 40)         # 200 ads = 40 points max
      store_score = min(store_count / 5, 30)    # 150 stores = 30 points max
      shopping_score = min(shopping_count / 50, 30)  # 1500 = 30 points max
      index = ad_score + store_score + shopping_score
    """
    ad_score = min(ad_count / 5, 40)
    store_score = min(store_count / 5, 30)
    shopping_score = min(shopping_count / 50, 30)

    index = round(ad_score + store_score + shopping_score, 1)

    if index >= 70:
        level = "SATURATED"
        action = "REJECT"
    elif index >= 45:
        level = "HIGH_COMPETITION"
        action = "CAUTION"
    elif index >= 20:
        level = "MODERATE"
        action = "PROCEED"
    else:
        level = "LOW_COMPETITION"
        action = "OPPORTUNITY"

    return {
        "saturation_index": index,
        "level": level,
        "action": action,
        "breakdown": {
            "ad_score": round(ad_score, 1),
            "store_score": round(store_score, 1),
            "shopping_score": round(shopping_score, 1),
        },
        "raw_counts": {
            "fb_ads": ad_count,
            "shopify_stores": store_count,
            "google_shopping": shopping_count,
        },
    }


def run_saturation_scan() -> dict:
    """
    Run saturation analysis on winning product keywords.
    Uses data from winners/analysis to know WHICH products to check.
    """
    log.info("=" * 60)
    log.info("SATURATION DETECTOR — Starting")
    log.info("=" * 60)

    session = get_session()

    # Load winner products to check saturation for
    winners_data = _load_latest_json("winners")
    analysis_data = _load_latest_json("analysis")

    keywords_to_check = set()

    # Get keywords from winners (STRONG_BUY and BUY only)
    if winners_data:
        for w in winners_data.get("strong_buys", []):
            title = w.get("title", "")
            # Extract key product phrase (first 3-4 meaningful words)
            words = [wd for wd in title.split() if len(wd) > 2][:4]
            if words:
                keywords_to_check.add(" ".join(words))
        for w in winners_data.get("buys", [])[:10]:
            words = [wd for wd in w.get("title", "").split() if len(wd) > 2][:4]
            if words:
                keywords_to_check.add(" ".join(words))

    # Get top candidates from analysis
    if analysis_data:
        candidates = analysis_data.get("amazon", {}).get("dropship_candidates", [])
        for c in candidates[:15]:
            words = [wd for wd in c.get("title", "").split() if len(wd) > 2][:4]
            if words:
                keywords_to_check.add(" ".join(words))

    # Also check seed keywords (top niche products)
    for niche, kws in SEED_KEYWORDS.items():
        for kw in kws[:2]:  # Top 2 per niche
            keywords_to_check.add(kw)

    keywords_to_check = list(keywords_to_check)[:30]  # Limit to 30

    log.info(f"Checking saturation for {len(keywords_to_check)} products/keywords")

    report = {
        "scan_date": datetime.now().isoformat(),
        "products_checked": len(keywords_to_check),
        "results": {},
        "saturated": [],
        "opportunities": [],
        "stats": {},
    }

    for kw in keywords_to_check:
        log.info(f"Checking saturation: {kw[:40]}")

        ad_count = count_fb_ads(kw, session)
        time.sleep(random.uniform(2, 4))

        store_count = count_shopify_stores(kw, session)
        time.sleep(random.uniform(2, 4))

        shopping_count = count_google_shopping(kw, session)
        time.sleep(random.uniform(2, 4))

        sat = calculate_saturation_index(ad_count, store_count, shopping_count)
        sat["keyword"] = kw

        report["results"][kw] = sat

        if sat["action"] == "REJECT":
            report["saturated"].append(sat)
            log.warning(f"  SATURATED: {kw} (index: {sat['saturation_index']})")
        elif sat["action"] == "OPPORTUNITY":
            report["opportunities"].append(sat)
            log.info(f"  OPPORTUNITY: {kw} (index: {sat['saturation_index']})")
        else:
            log.info(f"  {sat['level']}: {kw} (index: {sat['saturation_index']})")

    # Stats
    report["stats"] = {
        "total_checked": len(keywords_to_check),
        "saturated_count": len(report["saturated"]),
        "opportunity_count": len(report["opportunities"]),
        "high_competition": sum(
            1 for r in report["results"].values() if r["level"] == "HIGH_COMPETITION"
        ),
        "moderate": sum(
            1 for r in report["results"].values() if r["level"] == "MODERATE"
        ),
        "avg_saturation": round(
            sum(r["saturation_index"] for r in report["results"].values())
            / max(1, len(report["results"])), 1
        ),
    }

    # Save
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"saturation_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Saturation report saved: {output_file}")
    log.info(
        f"Results: {report['stats']['saturated_count']} saturated, "
        f"{report['stats']['opportunity_count']} opportunities"
    )

    # Telegram alert
    msg = f"🔍 <b>SATURATION SCAN COMPLETE</b>\n📅 {today}\n\n"

    msg += (
        f"📊 Checked: {report['stats']['total_checked']} products\n"
        f"🔴 Saturated: {report['stats']['saturated_count']}\n"
        f"🟡 High competition: {report['stats']['high_competition']}\n"
        f"🟢 Opportunities: {report['stats']['opportunity_count']}\n"
        f"📈 Avg saturation: {report['stats']['avg_saturation']}\n\n"
    )

    if report["saturated"]:
        msg += "🚫 <b>REJECT — Saturated Products:</b>\n"
        for s in report["saturated"][:5]:
            msg += (
                f"  • <b>{s['keyword'][:35]}</b> (idx:{s['saturation_index']})\n"
                f"    Ads:{s['raw_counts']['fb_ads']} "
                f"Stores:{s['raw_counts']['shopify_stores']} "
                f"Shopping:{s['raw_counts']['google_shopping']}\n"
            )

    if report["opportunities"]:
        msg += "\n💎 <b>OPPORTUNITY — Low Competition:</b>\n"
        for o in report["opportunities"][:5]:
            msg += (
                f"  • <b>{o['keyword'][:35]}</b> (idx:{o['saturation_index']})\n"
                f"    Ads:{o['raw_counts']['fb_ads']} "
                f"Stores:{o['raw_counts']['shopify_stores']}\n"
            )

    msg += f"\n📁 <code>data/saturation_{today}.json</code>"
    send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_saturation_scan()
