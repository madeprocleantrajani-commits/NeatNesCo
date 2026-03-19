"""
TikTok Trend Scanner v1
------------------------
Scans TikTok Creative Center for trending products, hashtags, and viral content.
Uses multiple data sources:
  1. TikTok Creative Center API — trending hashtags & products
  2. Google Trends TikTok-related searches — "tiktok made me buy it"
  3. Social listening — product mentions trending on TikTok

Outputs: data/tiktok_YYYY-MM-DD.json
"""
import json
import time
import random
import re
from datetime import datetime
from bs4 import BeautifulSoup

from config import (
    SEED_KEYWORDS, DATA_DIR, get_logger, get_session, resilient_fetch,
)
from alert_bot import send_alert

log = get_logger("tiktok_scanner")

# ── TikTok-specific product keywords ──────────────────
# These are phrases that indicate TikTok-viral products
TIKTOK_VIRAL_SIGNALS = [
    "tiktok made me buy",
    "tiktok viral",
    "tiktok trending",
    "tiktok famous",
    "as seen on tiktok",
    "tiktok find",
    "tiktok must have",
    "tiktok gadget",
    "tiktok beauty",
    "tiktok hack",
    "tiktok kitchen",
    "tiktok pet",
    "tiktok fitness",
    "tiktok home",
    "tiktok clean",
    "tiktok organization",
]

# Categories mapped to TikTok hashtags for monitoring
TIKTOK_HASHTAG_MAP = {
    "home_gadgets": [
        "homedecor", "homehacks", "homegadgets", "smartgadgets",
        "homeorganization", "homelighting", "smarthome",
    ],
    "fitness": [
        "fitnessgadgets", "workoutequipment", "homegym",
        "fitnesshacks", "workouthacks", "gymaccessories",
    ],
    "pet_products": [
        "petproducts", "dogtok", "cattok", "pethacks",
        "dogproducts", "catproducts", "pettiktok",
    ],
    "beauty_health": [
        "beautytok", "skincare", "beautyhacks", "beautygadgets",
        "skincareroutine", "glowup", "beautytips",
    ],
    "kitchen_gadgets": [
        "kitchengadgets", "kitchenhacks", "cookinghacks",
        "kitchenmusthaves", "foodtok", "airfryer",
    ],
    "tech_accessories": [
        "techtok", "techgadgets", "techfinds", "musthavetech",
        "gadgets", "coolgadgets",
    ],
    "eco_friendly": [
        "ecofriendly", "sustainability", "zerowaste",
        "ecoproducts", "greenproducts",
    ],
    "car_accessories": [
        "cartok", "caraccessories", "carhacks", "carmusthaves",
        "carorganization",
    ],
    "home_office": [
        "desksetup", "officesetup", "wfh", "homeofficehacks",
        "deskaccessories", "deskorganization",
    ],
    "outdoor": [
        "campinggear", "hikinggear", "outdoorgadgets",
        "campinghacks", "survivalkit",
    ],
}


def scan_amazon_tiktok_products(session) -> list[dict]:
    """
    Search Amazon for TikTok-viral products.
    Amazon has a "TikTok Made Me Buy It" section and related searches.
    """
    results = []
    search_queries = [
        "tiktok made me buy it",
        "as seen on tiktok",
        "tiktok viral products 2026",
        "trending tiktok products",
        "tiktok famous gadgets",
        "tiktok beauty products",
        "tiktok kitchen gadgets",
        "tiktok pet products",
        "tiktok home gadgets",
        "tiktok fitness equipment",
    ]

    for query in search_queries:
        url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}&s=review-rank"
        log.info(f"Searching Amazon for: {query}")

        response = resilient_fetch(url, session=session, timeout=20)
        if not response:
            log.warning(f"No response for query: {query}")
            time.sleep(random.uniform(3, 6))
            continue

        try:
            soup = BeautifulSoup(response.text, "lxml")

            # Parse product cards
            cards = soup.select('[data-component-type="s-search-result"]')
            log.info(f"  Found {len(cards)} product cards for '{query}'")

            for card in cards[:15]:  # Top 15 per query
                try:
                    # Title
                    title_el = card.select_one("h2 a span, h2 span")
                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    # ASIN
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

                    # Review count
                    review_el = card.select_one('span[aria-label*="stars"] + span a span, .a-size-base.s-underline-text')
                    reviews = 0
                    if review_el:
                        try:
                            reviews = int(review_el.get_text(strip=True).replace(",", "").replace("+", ""))
                        except ValueError:
                            pass

                    # Skip if out of price range or no price
                    if not price or price < 10 or price > 100:
                        continue

                    results.append({
                        "title": title[:120],
                        "asin": asin,
                        "price_usd": price,
                        "rating": rating,
                        "review_count": reviews,
                        "source_query": query,
                        "source": "amazon_tiktok_search",
                        "url": f"https://www.amazon.com/dp/{asin}" if asin else "",
                    })

                except Exception as e:
                    log.debug(f"Error parsing card: {e}")
                    continue

        except Exception as e:
            log.error(f"Error parsing Amazon results for '{query}': {e}")

        time.sleep(random.uniform(4, 8))

    # Deduplicate by ASIN
    seen = set()
    unique = []
    for p in results:
        key = p.get("asin") or p["title"]
        if key not in seen:
            seen.add(key)
            unique.append(p)

    log.info(f"Found {len(unique)} unique TikTok-viral products on Amazon")
    return unique


def scan_google_tiktok_trends(session) -> list[dict]:
    """
    Search Google for trending TikTok products using autocomplete.
    This reveals what people are searching for: "tiktok viral [product]"
    """
    results = []
    prefixes = [
        "tiktok viral product ",
        "tiktok made me buy ",
        "tiktok famous ",
        "tiktok trending ",
        "as seen on tiktok ",
        "tiktok must have ",
        "tiktok gadget ",
        "tiktok find ",
    ]

    for prefix in prefixes:
        # Google Autocomplete API (free, no auth)
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={prefix.replace(' ', '+')}"

        try:
            response = session.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if response.status_code == 200:
                data = response.json()
                suggestions = data[1] if len(data) > 1 else []
                for s in suggestions:
                    if s != prefix.strip():
                        # Extract the product keyword (remove the prefix)
                        product = s.replace(prefix.strip(), "").strip()
                        if len(product) > 2:
                            results.append({
                                "query": s,
                                "product_keyword": product,
                                "source_prefix": prefix.strip(),
                                "source": "google_autocomplete",
                            })
        except Exception as e:
            log.debug(f"Google autocomplete failed for '{prefix}': {e}")

        time.sleep(random.uniform(1, 3))

    # Amazon autocomplete for TikTok products
    amazon_prefixes = [
        "tiktok ",
        "viral ",
        "trending ",
        "as seen on tiktok ",
    ]

    for prefix in amazon_prefixes:
        url = (
            f"https://completion.amazon.com/api/2017/suggestions"
            f"?mid=ATVPDKIKX0DER&alias=aps&prefix={prefix.replace(' ', '+')}"
        )

        try:
            response = session.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if response.status_code == 200:
                data = response.json()
                for sug in data.get("suggestions", []):
                    value = sug.get("value", "")
                    if value and value != prefix.strip():
                        product = value.replace(prefix.strip(), "").strip()
                        if len(product) > 2:
                            results.append({
                                "query": value,
                                "product_keyword": product,
                                "source_prefix": f"amazon_{prefix.strip()}",
                                "source": "amazon_autocomplete",
                            })
        except Exception as e:
            log.debug(f"Amazon autocomplete failed for '{prefix}': {e}")

        time.sleep(random.uniform(1, 2))

    log.info(f"Found {len(results)} TikTok trend suggestions from autocomplete")
    return results


def scan_tiktok_creative_center(session) -> dict:
    """
    Scan TikTok Creative Center for trending hashtags and products.
    Public endpoint: ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag
    """
    trending_data = {
        "hashtags": [],
        "product_hashtags": [],
    }

    # TikTok Creative Center trending hashtags API
    # This is a public page that shows trending hashtags
    url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"

    response = resilient_fetch(url, session=session, timeout=25)
    if response:
        try:
            soup = BeautifulSoup(response.text, "lxml")

            # Look for hashtag data in the page
            # TikTok loads data dynamically, but some is in initial HTML
            scripts = soup.find_all("script")
            for script in scripts:
                text = script.string or ""
                # Look for JSON data embedded in scripts
                if "hashtag" in text.lower() and "trending" in text.lower():
                    # Try to extract JSON data
                    json_matches = re.findall(r'\{[^{}]{50,}\}', text)
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if "hashtag_name" in str(data) or "hashtagName" in str(data):
                                trending_data["raw_data"] = data
                        except json.JSONDecodeError:
                            continue

            log.info("Scanned TikTok Creative Center")
        except Exception as e:
            log.warning(f"TikTok Creative Center parse error: {e}")
    else:
        log.warning("Could not access TikTok Creative Center")

    # Scan hashtag trends via alternative method: Google trends for TikTok hashtags
    product_hashtags = []
    all_hashtags = []
    for niche, tags in TIKTOK_HASHTAG_MAP.items():
        all_hashtags.extend([(tag, niche) for tag in tags])

    # Sample check: Are these hashtags trending in Google?
    for tag, niche in all_hashtags[:20]:  # Check top 20
        url = (
            f"https://suggestqueries.google.com/complete/search"
            f"?client=firefox&q=tiktok+%23{tag}"
        )
        try:
            response = session.get(url, timeout=8, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if response.status_code == 200:
                data = response.json()
                suggestions = data[1] if len(data) > 1 else []
                if suggestions:
                    product_hashtags.append({
                        "hashtag": f"#{tag}",
                        "niche": niche,
                        "google_suggestions": len(suggestions),
                        "related_searches": suggestions[:5],
                    })
        except Exception:
            pass
        time.sleep(random.uniform(0.5, 1.5))

    trending_data["product_hashtags"] = product_hashtags
    log.info(f"Found {len(product_hashtags)} product-related TikTok hashtags")
    return trending_data


def _score_tiktok_product(product: dict, trends_data: list, hashtag_data: list) -> dict:
    """
    Score a TikTok product for dropshipping potential.
    Returns enriched product with tiktok_score and signals.
    """
    title_lower = product.get("title", "").lower()
    score = 0
    signals = []

    # Price sweet spot for TikTok products ($15-$50 impulse buy range)
    price = product.get("price_usd", 0)
    if 15 <= price <= 50:
        score += 20
        signals.append("impulse_price")
    elif 10 <= price <= 70:
        score += 10

    # Rating quality
    rating = product.get("rating", 0) or 0
    if rating >= 4.5:
        score += 15
        signals.append("high_rated")
    elif rating >= 4.0:
        score += 10

    # Review count (viral products usually have many reviews)
    reviews = product.get("review_count", 0) or 0
    if 100 <= reviews <= 5000:
        score += 15  # Good validation without saturation
        signals.append("validated")
    elif reviews > 5000:
        score += 5   # Saturated but proven
        signals.append("saturated_warning")
    elif reviews > 0:
        score += 8

    # TikTok viral keyword signals in title
    viral_keywords = [
        "viral", "trending", "tiktok", "popular", "famous",
        "best seller", "must have", "aesthetic", "satisfying",
        "oddly satisfying", "gadget", "hack", "organizer",
    ]
    for kw in viral_keywords:
        if kw in title_lower:
            score += 5
            signals.append(f"viral_kw:{kw}")

    # UGC potential (products that work well in short-form video)
    ugc_keywords = [
        "before after", "transform", "clean", "organize",
        "beauty", "skin", "glow", "light", "led", "color",
        "satisfying", "oddly", "spray", "foam", "gel",
        "kitchen", "cooking", "food", "gadget",
        "pet", "dog", "cat", "baby",
        "fitness", "workout", "massage",
    ]
    ugc_matches = [kw for kw in ugc_keywords if kw in title_lower]
    if ugc_matches:
        score += len(ugc_matches) * 3
        signals.append(f"ugc_potential:{len(ugc_matches)}")

    # Check against Google trend suggestions
    for trend in trends_data:
        trend_kw = trend.get("product_keyword", "").lower()
        if trend_kw and (trend_kw in title_lower or any(
            w in title_lower for w in trend_kw.split() if len(w) > 3
        )):
            score += 10
            signals.append(f"trend_match:{trend_kw[:20]}")
            break

    # Check against TikTok hashtag data
    for ht in hashtag_data:
        niche_keywords = SEED_KEYWORDS.get(ht.get("niche", ""), [])
        if any(keyword_match_simple(kw, title_lower) for kw in niche_keywords):
            score += 5
            signals.append(f"hashtag_niche:{ht['niche']}")
            break

    product["tiktok_score"] = min(score, 100)
    product["tiktok_signals"] = signals
    return product


def keyword_match_simple(keyword: str, text: str) -> bool:
    """Simple keyword matching for TikTok products."""
    kw_lower = keyword.lower()
    if kw_lower in text:
        return True
    # Word-level match
    kw_words = [w for w in kw_lower.split() if len(w) > 3]
    if len(kw_words) >= 2:
        matches = sum(1 for w in kw_words if w in text)
        return matches >= len(kw_words) * 0.6
    return False


def run_tiktok_scan() -> dict:
    """Run a complete TikTok trend scan."""
    log.info("=" * 60)
    log.info("TIKTOK TREND SCANNER — Starting")
    log.info("=" * 60)

    session = get_session()
    report = {
        "scan_date": datetime.now().isoformat(),
        "viral_products": [],
        "trend_suggestions": [],
        "creative_center": {},
        "top_picks": [],
        "stats": {},
    }

    # 1. Scan TikTok Creative Center
    log.info("Phase 1: TikTok Creative Center...")
    creative_data = scan_tiktok_creative_center(session)
    report["creative_center"] = creative_data

    # 2. Scan Google/Amazon autocomplete for TikTok trends
    log.info("Phase 2: Google/Amazon autocomplete for TikTok trends...")
    trend_suggestions = scan_google_tiktok_trends(session)
    report["trend_suggestions"] = trend_suggestions

    # 3. Scan Amazon for TikTok-viral products
    log.info("Phase 3: Amazon TikTok viral products...")
    viral_products = scan_amazon_tiktok_products(session)

    # 4. Score all products
    log.info("Phase 4: Scoring products...")
    hashtag_data = creative_data.get("product_hashtags", [])
    scored_products = []
    for p in viral_products:
        scored = _score_tiktok_product(p, trend_suggestions, hashtag_data)
        scored_products.append(scored)

    # Sort by TikTok score
    scored_products.sort(key=lambda x: x.get("tiktok_score", 0), reverse=True)
    report["viral_products"] = scored_products

    # Top picks: score >= 30 and in price sweet spot
    top_picks = [
        p for p in scored_products
        if p.get("tiktok_score", 0) >= 30
        and 12 <= p.get("price_usd", 0) <= 70
    ]
    report["top_picks"] = top_picks[:25]

    # Stats
    report["stats"] = {
        "total_products_found": len(viral_products),
        "total_trend_suggestions": len(trend_suggestions),
        "hashtags_analyzed": len(hashtag_data),
        "top_picks_count": len(top_picks),
        "avg_tiktok_score": round(
            sum(p.get("tiktok_score", 0) for p in scored_products) /
            max(1, len(scored_products)), 1
        ),
    }

    # Save report
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"tiktok_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"TikTok report saved: {output_file}")
    log.info(
        f"Products: {len(viral_products)} | Trends: {len(trend_suggestions)} | "
        f"Top picks: {len(top_picks)}"
    )

    # Telegram alert
    if top_picks or trend_suggestions:
        msg = f"🎵 <b>TIKTOK TREND SCAN COMPLETE</b>\n📅 {today}\n\n"

        if top_picks:
            msg += f"🔥 <b>TOP TIKTOK PICKS</b> — {len(top_picks)} viral products:\n"
            for i, p in enumerate(top_picks[:8], 1):
                signals = ", ".join(p.get("tiktok_signals", [])[:3])
                msg += (
                    f"  {i}. <b>{p['title'][:45]}</b>\n"
                    f"     ${p['price_usd']:.2f} | TikTok:{p['tiktok_score']} | "
                    f"⭐{p.get('rating', 0) or 0:.1f}\n"
                )
                if signals:
                    msg += f"     📌 {signals}\n"

        if trend_suggestions:
            msg += f"\n📈 <b>TRENDING TIKTOK SEARCHES</b> — {len(trend_suggestions)} suggestions:\n"
            seen_products = set()
            count = 0
            for t in trend_suggestions:
                kw = t.get("product_keyword", "")
                if kw and kw not in seen_products and count < 10:
                    seen_products.add(kw)
                    msg += f"  ▲ <i>{t['query']}</i>\n"
                    count += 1

        if hashtag_data:
            msg += f"\n#️⃣ <b>ACTIVE HASHTAGS</b> — {len(hashtag_data)} tracked:\n"
            for ht in hashtag_data[:5]:
                msg += f"  {ht['hashtag']} ({ht['niche']})\n"

        msg += f"\n📁 <code>data/tiktok_{today}.json</code>"
        send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_tiktok_scan()
