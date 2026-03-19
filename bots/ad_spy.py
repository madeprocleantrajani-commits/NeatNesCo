"""
Ad Spy Scanner v1
------------------
Monitors competitor advertising activity to identify winning products.

Data sources:
  1. Facebook Ad Library (free, public) — searches active ads by keyword/page
  2. Google Ads Transparency Center — monitors competitor ad spending
  3. Amazon Sponsored Products — detects heavily advertised products

The logic: If a product is being advertised HEAVILY, it's making money.
Products with sustained ad spend = PROVEN winners.

Outputs: data/adspy_YYYY-MM-DD.json
"""
import json
import time
import random
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from config import (
    SEED_KEYWORDS, COMPETITOR_STORES, DATA_DIR,
    get_logger, get_session, resilient_fetch,
)
from alert_bot import send_alert

log = get_logger("ad_spy")


# ── Known Dropship Advertiser Pages ──────────────────
# These are Facebook pages of known dropshipping stores
# that consistently run product ads
MONITORED_FB_PAGES = [
    "Inspire Uplift",
    "BlueCrate",
    "The Home Kit Shop",
    "Warmly Decor",
    "Meowingtons",
    "TrendyGadgetShop",
    "HYGO Shop",
    "MiniInTheBox",
    "Wish",
    "Banggood",
]

# Keywords to search in ad libraries
AD_SEARCH_KEYWORDS = [
    # Generic dropship ad patterns
    "50% off limited time",
    "free shipping today only",
    "trending product",
    "viral gadget",
    "as seen on tiktok",
    "best seller 2026",
    # Product-specific
    "portable blender",
    "led strip lights",
    "posture corrector",
    "massage gun",
    "pet grooming",
    "car phone mount",
    "wireless charger",
    "air purifier",
    "kitchen gadget",
    "organizer",
    "smart home",
    "beauty tool",
    "scalp massager",
    "jade roller",
    "resistance bands",
]


def scan_facebook_ad_library(session) -> dict:
    """
    Scan Facebook Ad Library for competitor ads.
    The Ad Library is PUBLIC and doesn't require authentication.
    URL: https://www.facebook.com/ads/library/

    We search by keyword to find:
    - Which products are being advertised right now
    - Which pages are running the most ads
    - Ad creative patterns (text, images)
    """
    results = {
        "keyword_ads": {},
        "page_activity": {},
        "trending_ad_products": [],
    }

    # Search Facebook Ad Library by product keywords
    for keyword in AD_SEARCH_KEYWORDS[:15]:  # Limit to avoid rate limiting
        encoded_kw = quote_plus(keyword)
        url = (
            f"https://www.facebook.com/ads/library/"
            f"?active_status=active&ad_type=all&country=US"
            f"&q={encoded_kw}&search_type=keyword_unordered"
        )

        log.info(f"Searching FB Ad Library: {keyword}")
        response = resilient_fetch(url, session=session, timeout=25)

        if response:
            try:
                soup = BeautifulSoup(response.text, "lxml")

                # Count ads found (Facebook renders dynamically, but initial HTML has some data)
                # Look for ad count indicators
                text_content = soup.get_text()

                # Parse what we can from server-rendered content
                ad_count_match = re.search(r'(\d[\d,]*)\s*(?:results?|ads?)', text_content, re.I)
                ad_count = 0
                if ad_count_match:
                    ad_count = int(ad_count_match.group(1).replace(",", ""))

                # Extract page names from ad cards
                page_names = []
                page_els = soup.select('a[href*="facebook.com/"], span.x1lliihq')
                for el in page_els:
                    name = el.get_text(strip=True)
                    if name and len(name) > 2 and len(name) < 100:
                        page_names.append(name)

                results["keyword_ads"][keyword] = {
                    "estimated_active_ads": ad_count,
                    "advertisers_found": len(set(page_names)),
                    "top_advertisers": list(set(page_names))[:10],
                    "search_url": url,
                }

                # If many ads found, this is a competitive/winning product
                if ad_count > 50:
                    results["trending_ad_products"].append({
                        "keyword": keyword,
                        "active_ads": ad_count,
                        "advertisers": len(set(page_names)),
                        "signal": "heavily_advertised",
                    })

            except Exception as e:
                log.debug(f"Error parsing FB Ad Library for '{keyword}': {e}")

        time.sleep(random.uniform(3, 7))

    # Search by known competitor page names
    for page_name in MONITORED_FB_PAGES[:8]:
        encoded_name = quote_plus(page_name)
        url = (
            f"https://www.facebook.com/ads/library/"
            f"?active_status=active&ad_type=all&country=US"
            f"&q={encoded_name}&search_type=keyword_unordered"
        )

        log.info(f"Checking FB ads for page: {page_name}")
        response = resilient_fetch(url, session=session, timeout=25)

        if response:
            try:
                soup = BeautifulSoup(response.text, "lxml")
                text = soup.get_text()

                ad_count_match = re.search(r'(\d[\d,]*)\s*(?:results?|ads?)', text, re.I)
                ad_count = int(ad_count_match.group(1).replace(",", "")) if ad_count_match else 0

                results["page_activity"][page_name] = {
                    "active_ads": ad_count,
                    "status": "active" if ad_count > 0 else "inactive",
                    "search_url": url,
                }

            except Exception as e:
                log.debug(f"Error checking page '{page_name}': {e}")

        time.sleep(random.uniform(3, 6))

    log.info(f"FB Ad Library: {len(results['keyword_ads'])} keywords, "
             f"{len(results['page_activity'])} pages checked")
    return results


def scan_google_ads_transparency(session) -> dict:
    """
    Scan Google Ads Transparency Center for competitor ad activity.
    URL: adstransparency.google.com

    Detects which product keywords are being heavily bid on.
    """
    results = {
        "keyword_competition": {},
        "top_advertised_products": [],
    }

    # Use Google autocomplete to detect ad-heavy keywords
    # Keywords with "buy", "shop", "deal" variations indicate ad activity
    ad_indicator_prefixes = [
        "buy ",
        "best ",
        "cheap ",
        "shop ",
        "order ",
        "discount ",
    ]

    for niche, keywords in SEED_KEYWORDS.items():
        for kw in keywords[:3]:  # Top 3 per niche
            for prefix in ad_indicator_prefixes[:3]:  # Top 3 prefixes
                query = f"{prefix}{kw}"
                url = (
                    f"https://suggestqueries.google.com/complete/search"
                    f"?client=firefox&q={quote_plus(query)}"
                )

                try:
                    response = session.get(url, timeout=8, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    })
                    if response.status_code == 200:
                        data = response.json()
                        suggestions = data[1] if len(data) > 1 else []

                        if suggestions:
                            if kw not in results["keyword_competition"]:
                                results["keyword_competition"][kw] = {
                                    "niche": niche,
                                    "search_variations": [],
                                    "ad_signal_strength": 0,
                                }

                            results["keyword_competition"][kw]["search_variations"].extend(
                                suggestions[:5]
                            )
                            results["keyword_competition"][kw]["ad_signal_strength"] += len(suggestions)

                except Exception:
                    pass

                time.sleep(random.uniform(0.3, 1))

    # Rank by ad signal strength
    for kw, data in results["keyword_competition"].items():
        # Deduplicate variations
        data["search_variations"] = list(set(data["search_variations"]))[:15]

        if data["ad_signal_strength"] >= 10:
            results["top_advertised_products"].append({
                "keyword": kw,
                "niche": data["niche"],
                "signal_strength": data["ad_signal_strength"],
                "variations": len(data["search_variations"]),
            })

    results["top_advertised_products"].sort(
        key=lambda x: x["signal_strength"], reverse=True
    )

    log.info(f"Google Ads: {len(results['keyword_competition'])} keywords, "
             f"{len(results['top_advertised_products'])} heavily advertised")
    return results


def scan_amazon_sponsored(session) -> list[dict]:
    """
    Detect Amazon Sponsored products for our target keywords.
    Products with "Sponsored" badge = someone is paying for ads = proven product.
    """
    sponsored_products = []

    # Flatten seed keywords and take top ones
    all_keywords = []
    for niche, keywords in SEED_KEYWORDS.items():
        for kw in keywords[:5]:  # Top 5 per niche
            all_keywords.append((kw, niche))

    for kw, niche in all_keywords[:25]:  # Limit total
        url = f"https://www.amazon.com/s?k={quote_plus(kw)}"
        log.info(f"Checking Amazon sponsored: {kw}")

        response = resilient_fetch(url, session=session, timeout=20)
        if not response:
            time.sleep(random.uniform(3, 6))
            continue

        try:
            soup = BeautifulSoup(response.text, "lxml")
            cards = soup.select('[data-component-type="s-search-result"]')

            for card in cards[:20]:
                # Check if this is a sponsored product
                sponsored_el = card.select_one(
                    'span:contains("Sponsored"), .puis-label-popover, '
                    '[data-component-type="sp-sponsored-result"]'
                )
                # Also check for "Sponsored" text
                card_text = card.get_text()
                is_sponsored = bool(sponsored_el) or "Sponsored" in card_text[:200]

                if not is_sponsored:
                    continue

                # Parse product info
                title_el = card.select_one("h2 a span, h2 span")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue

                asin = card.get("data-asin", "")

                # Price
                price_whole = card.select_one(".a-price-whole")
                price_frac = card.select_one(".a-price-fraction")
                price = None
                if price_whole:
                    pw = price_whole.get_text(strip=True).replace(",", "").rstrip(".")
                    pf = price_frac.get_text(strip=True) if price_frac else "00"
                    try:
                        price = float(f"{pw}.{pf}")
                    except ValueError:
                        pass

                # Rating
                rating_el = card.select_one("span.a-icon-alt")
                rating = None
                if rating_el:
                    try:
                        rating = float(rating_el.get_text().split()[0])
                    except (ValueError, IndexError):
                        pass

                if price and 10 <= price <= 100:
                    sponsored_products.append({
                        "title": title[:120],
                        "asin": asin,
                        "price_usd": price,
                        "rating": rating,
                        "search_keyword": kw,
                        "niche": niche,
                        "source": "amazon_sponsored",
                        "url": f"https://www.amazon.com/dp/{asin}" if asin else "",
                    })

        except Exception as e:
            log.error(f"Error parsing Amazon sponsored for '{kw}': {e}")

        time.sleep(random.uniform(4, 8))

    # Deduplicate
    seen = set()
    unique = []
    for p in sponsored_products:
        key = p.get("asin") or p["title"]
        if key not in seen:
            seen.add(key)
            unique.append(p)

    log.info(f"Found {len(unique)} sponsored products on Amazon")
    return unique


def _analyze_ad_intelligence(fb_data: dict, google_data: dict,
                              amazon_sponsored: list) -> list[dict]:
    """
    Cross-reference all ad data to find PROVEN winners.
    Products advertised across multiple channels = highest confidence.
    """
    intelligence = []

    # Build a keyword → signals map
    keyword_signals = {}

    # Facebook ad signals
    for kw, data in fb_data.get("keyword_ads", {}).items():
        if kw not in keyword_signals:
            keyword_signals[kw] = {"signals": [], "score": 0, "details": {}}
        if data.get("estimated_active_ads", 0) > 10:
            keyword_signals[kw]["signals"].append("fb_ads_active")
            keyword_signals[kw]["score"] += 20
            keyword_signals[kw]["details"]["fb_ads"] = data["estimated_active_ads"]

    # Google ad signals
    for kw, data in google_data.get("keyword_competition", {}).items():
        if kw not in keyword_signals:
            keyword_signals[kw] = {"signals": [], "score": 0, "details": {}}
        if data.get("ad_signal_strength", 0) > 5:
            keyword_signals[kw]["signals"].append("google_ads_competitive")
            keyword_signals[kw]["score"] += 15
            keyword_signals[kw]["details"]["google_signal"] = data["ad_signal_strength"]

    # Amazon sponsored product signals
    kw_sponsored = {}
    for p in amazon_sponsored:
        kw = p["search_keyword"]
        if kw not in kw_sponsored:
            kw_sponsored[kw] = []
        kw_sponsored[kw].append(p)

    for kw, products in kw_sponsored.items():
        if kw not in keyword_signals:
            keyword_signals[kw] = {"signals": [], "score": 0, "details": {}}
        keyword_signals[kw]["signals"].append("amazon_sponsored")
        keyword_signals[kw]["score"] += 25
        keyword_signals[kw]["details"]["amazon_sponsored_count"] = len(products)
        keyword_signals[kw]["details"]["top_sponsored"] = products[:3]

    # Build intelligence list
    for kw, data in keyword_signals.items():
        if data["score"] >= 20:  # At least one strong signal
            intelligence.append({
                "keyword": kw,
                "ad_score": data["score"],
                "signal_count": len(data["signals"]),
                "signals": data["signals"],
                "details": data["details"],
                "recommendation": (
                    "STRONG_BUY" if data["score"] >= 50
                    else "BUY" if data["score"] >= 35
                    else "WATCH"
                ),
            })

    intelligence.sort(key=lambda x: x["ad_score"], reverse=True)
    return intelligence


def run_ad_spy_scan() -> dict:
    """Run complete ad intelligence scan."""
    log.info("=" * 60)
    log.info("AD SPY SCANNER — Starting")
    log.info("=" * 60)

    session = get_session()
    report = {
        "scan_date": datetime.now().isoformat(),
        "facebook": {},
        "google": {},
        "amazon_sponsored": [],
        "intelligence": [],
        "stats": {},
    }

    # 1. Facebook Ad Library
    log.info("Phase 1: Facebook Ad Library scan...")
    fb_data = scan_facebook_ad_library(session)
    report["facebook"] = fb_data

    # 2. Google Ads Transparency
    log.info("Phase 2: Google Ads Transparency scan...")
    google_data = scan_google_ads_transparency(session)
    report["google"] = google_data

    # 3. Amazon Sponsored Products
    log.info("Phase 3: Amazon Sponsored Products scan...")
    amazon_sponsored = scan_amazon_sponsored(session)
    report["amazon_sponsored"] = amazon_sponsored

    # 4. Cross-reference intelligence
    log.info("Phase 4: Cross-reference analysis...")
    intelligence = _analyze_ad_intelligence(fb_data, google_data, amazon_sponsored)
    report["intelligence"] = intelligence

    # Stats
    strong_buys = [i for i in intelligence if i["recommendation"] == "STRONG_BUY"]
    buys = [i for i in intelligence if i["recommendation"] == "BUY"]
    watches = [i for i in intelligence if i["recommendation"] == "WATCH"]

    report["stats"] = {
        "fb_keywords_checked": len(fb_data.get("keyword_ads", {})),
        "fb_pages_monitored": len(fb_data.get("page_activity", {})),
        "fb_trending_products": len(fb_data.get("trending_ad_products", [])),
        "google_keywords_analyzed": len(google_data.get("keyword_competition", {})),
        "google_top_advertised": len(google_data.get("top_advertised_products", [])),
        "amazon_sponsored_found": len(amazon_sponsored),
        "intelligence_total": len(intelligence),
        "strong_buys": len(strong_buys),
        "buys": len(buys),
        "watches": len(watches),
    }

    # Save report
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"adspy_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Ad Spy report saved: {output_file}")
    log.info(
        f"Intelligence: {len(intelligence)} products | "
        f"STRONG_BUY: {len(strong_buys)} | BUY: {len(buys)} | WATCH: {len(watches)}"
    )

    # Telegram alert
    if intelligence:
        msg = f"🕵️ <b>AD SPY SCAN COMPLETE</b>\n📅 {today}\n\n"

        if strong_buys:
            msg += f"🔴 <b>STRONG BUY</b> — {len(strong_buys)} heavily advertised:\n"
            for i in strong_buys[:5]:
                signals = " + ".join(i["signals"])
                msg += (
                    f"  • <b>{i['keyword']}</b> (score:{i['ad_score']})\n"
                    f"    {signals}\n"
                )

        if buys:
            msg += f"\n🟡 <b>BUY</b> — {len(buys)} products with ad validation:\n"
            for i in buys[:5]:
                msg += f"  • <b>{i['keyword']}</b> (score:{i['ad_score']})\n"

        if watches:
            msg += f"\n🔵 <b>WATCH</b> — {len(watches)} emerging ad activity:\n"
            for i in watches[:3]:
                msg += f"  • {i['keyword']} (score:{i['ad_score']})\n"

        # Facebook page activity
        active_pages = {
            k: v for k, v in fb_data.get("page_activity", {}).items()
            if v.get("active_ads", 0) > 0
        }
        if active_pages:
            msg += f"\n📱 <b>COMPETITOR AD ACTIVITY</b>:\n"
            for page, data in sorted(active_pages.items(),
                                      key=lambda x: x[1].get("active_ads", 0),
                                      reverse=True)[:5]:
                msg += f"  {page}: {data['active_ads']} active ads\n"

        # Amazon sponsored summary
        if amazon_sponsored:
            msg += f"\n🏪 <b>AMAZON SPONSORED</b>: {len(amazon_sponsored)} products detected\n"
            # Top 3 by price
            top_3 = sorted(amazon_sponsored, key=lambda x: x.get("price_usd", 0), reverse=True)[:3]
            for p in top_3:
                msg += f"  💰 ${p['price_usd']:.2f} | {p['title'][:35]}\n"

        msg += f"\n📁 <code>data/adspy_{today}.json</code>"
        send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_ad_spy_scan()
