"""
Amazon Best Sellers Tracker v3
-------------------------------
v3: Fixed reviews, hardened selectors, ASIN dedup, USD-native, resilient HTTP.

Outputs: data/amazon_YYYY-MM-DD.json
"""

import json
import re
import time
import random
import glob
from datetime import datetime

from bs4 import BeautifulSoup

from config import (
    AMAZON_CATEGORIES, DATA_DIR, REQUEST_DELAY, get_logger, get_session,
    is_physical_product, is_major_brand, parse_price, resilient_fetch,
    DROPSHIP_PRICE_MIN, DROPSHIP_PRICE_MAX,
)
from validators import validate_price, validate_rating, validate_review_count, validate_asin, sanitize_title
from alert_bot import send_alert

log = get_logger("amazon_tracker")


def _load_yesterday() -> dict | None:
    files = sorted(glob.glob(str(DATA_DIR / "amazon_*.json")), reverse=True)
    today = datetime.now().strftime("%Y-%m-%d")
    for f in files:
        if today not in f:
            try:
                with open(f) as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, IOError):
                pass
    return None


def _build_asin_rank_map(yesterday: dict | None) -> dict:
    if not yesterday:
        return {}
    rank_map = {}
    for cat, products in yesterday.get("best_sellers", {}).items():
        for p in products:
            asin = p.get("asin", "")
            if asin:
                rank_map[asin] = {
                    "rank": p.get("rank", 999),
                    "category": cat,
                    "price": p.get("price_usd"),
                }
    return rank_map


def _extract_review_count(item) -> int:
    """Extract review count with multiple fallback strategies. Returns 0 if not found."""
    # Strategy 1: Span elements with pure numbers
    for selector in ["span.a-size-small", "[class*='review'] span", ".a-link-normal .a-size-small"]:
        elements = item.select(selector)
        for el in elements:
            text = el.get_text(strip=True).replace(",", "").replace(".", "")
            if text and text.isdigit() and int(text) > 0:
                return int(text)

    # Strategy 2: aria-label with review info
    for el in item.select("[aria-label]"):
        label = el.get("aria-label", "")
        match = re.search(r'([\d,]+)\s*(?:ratings?|reviews?)', label, re.IGNORECASE)
        if match:
            count = int(match.group(1).replace(",", ""))
            if count > 0:
                return count

    # Strategy 3: Link text that looks like review count
    for link in item.select("a.a-link-normal"):
        text = link.get_text(strip=True).replace(",", "")
        if text.isdigit() and int(text) > 0:
            return int(text)

    return 0  # Default to 0, not None — ensures downstream code always has an integer


def scrape_best_sellers(session, category: str, url: str, seen_asins: set) -> list[dict]:
    """Scrape top products from an Amazon Best Sellers page."""
    products = []

    response = resilient_fetch(url, session=session, timeout=20)
    if response is None:
        log.warning(f"Failed to fetch {category} after retries")
        return products

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("[data-asin]")
    if not items:
        items = soup.select(".zg-grid-general-faceout")
    if not items:
        items = soup.select("#zg-ordered-list li")

    for rank, item in enumerate(items[:30], 1):
        product = {"rank": rank, "category": category}

        # ASIN
        asin = item.get("data-asin", "")
        if not asin:
            link = item.select_one("a[href*='/dp/']")
            if link:
                match = re.search(r'/dp/([A-Z0-9]{10})', link.get("href", ""))
                if match:
                    asin = match.group(1)

        asin = validate_asin(asin)
        if asin:
            if asin in seen_asins:
                continue
            seen_asins.add(asin)
            product["asin"] = asin
            product["url"] = f"https://www.amazon.com/dp/{asin}"

        # Title
        title_el = (
            item.select_one("[data-asin] a span, .p13n-sc-truncate") or
            item.select_one("a[title]") or
            item.select_one(".a-link-normal span")
        )
        if title_el:
            raw_title = title_el.get_text(strip=True) or title_el.get("title", "")
            product["title"] = sanitize_title(raw_title)

        if not product.get("title") or not is_physical_product(product["title"]):
            continue

        product["is_brand"] = is_major_brand(product["title"])

        # Price — USD native
        price_el = (
            item.select_one(".a-price .a-offscreen") or
            item.select_one("[class*='price']") or
            item.select_one(".p13n-sc-price")
        )
        if price_el:
            price_text = price_el.get_text(strip=True)
            product["price_raw"] = price_text
            product["price_usd"] = validate_price(parse_price(price_text))

        # Rating
        rating_el = item.select_one(".a-icon-alt, [aria-label*='out of 5']")
        if rating_el:
            text = (
                rating_el.get_text(strip=True)
                if rating_el.name != "i"
                else rating_el.get("aria-label", "")
            )
            product["rating_raw"] = text
            try:
                product["rating"] = validate_rating(float(text.split()[0]))
            except (ValueError, IndexError):
                product["rating"] = None

        # Review count — FIXED
        product["review_count"] = validate_review_count(_extract_review_count(item))

        products.append(product)

    log.info(f"Scraped {len(products)} physical products from {category}")
    return products


def scrape_movers_and_shakers(session, category: str, seen_asins: set) -> list[dict]:
    """Scrape Movers & Shakers."""
    cat_slug = category.replace("-", "")
    url = f"https://www.amazon.com/gp/movers-and-shakers/{cat_slug}"
    movers = []

    response = resilient_fetch(url, session=session, timeout=20)
    if response is None:
        log.warning(f"Movers fetch failed for {category}")
        return movers

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("[data-asin]")

    for item in items[:20]:
        product = {"category": category}

        title_el = item.select_one(".p13n-sc-truncate, a span")
        if title_el:
            product["title"] = sanitize_title(title_el.get_text(strip=True))

        if not product.get("title") or not is_physical_product(product["title"]):
            continue

        product["is_brand"] = is_major_brand(product["title"])

        change_el = item.select_one(".zg-percent-change, .a-color-success")
        if change_el:
            product["rank_change"] = change_el.get_text(strip=True)

        price_el = item.select_one(".a-price .a-offscreen, .p13n-sc-price")
        if price_el:
            product["price_raw"] = price_el.get_text(strip=True)
            product["price_usd"] = validate_price(parse_price(product["price_raw"]))

        asin = validate_asin(item.get("data-asin", ""))
        if asin:
            product["asin"] = asin
            product["url"] = f"https://www.amazon.com/dp/{asin}"

        movers.append(product)

    log.info(f"Found {len(movers)} physical movers in {category}")
    return movers


def add_bsr_history(products: dict, movers: dict, yesterday_map: dict):
    if not yesterday_map:
        return
    for cat, prod_list in products.items():
        for p in prod_list:
            asin = p.get("asin", "")
            if asin in yesterday_map:
                old = yesterday_map[asin]
                old_rank = old["rank"]
                new_rank = p["rank"]
                p["rank_yesterday"] = old_rank
                p["rank_change"] = old_rank - new_rank
                if p["rank_change"] > 0:
                    p["rank_direction"] = "up"
                elif p["rank_change"] < 0:
                    p["rank_direction"] = "down"
                else:
                    p["rank_direction"] = "stable"
            else:
                p["rank_yesterday"] = None
                p["rank_direction"] = "new"


def run_amazon_scan():
    """Run full Amazon scan."""
    log.info("Starting Amazon scan...")
    session = get_session()

    yesterday = _load_yesterday()
    yesterday_map = _build_asin_rank_map(yesterday)
    if yesterday_map:
        log.info(f"Loaded {len(yesterday_map)} products from previous scan")

    all_best_sellers = {}
    all_movers = {}
    seen_asins = set()

    for category, url in AMAZON_CATEGORIES.items():
        log.info(f"Scanning: {category}")
        best = scrape_best_sellers(session, category, url, seen_asins)
        all_best_sellers[category] = best
        time.sleep(REQUEST_DELAY + random.uniform(1, 3))

        movers = scrape_movers_and_shakers(session, category, seen_asins)
        all_movers[category] = movers
        time.sleep(REQUEST_DELAY + random.uniform(1, 3))

    add_bsr_history(all_best_sellers, all_movers, yesterday_map)

    total_products = sum(len(v) for v in all_best_sellers.values())
    total_movers = sum(len(v) for v in all_movers.values())
    brand_count = sum(1 for prods in all_best_sellers.values() for p in prods if p.get("is_brand"))
    rising_count = sum(1 for prods in all_best_sellers.values() for p in prods if p.get("rank_direction") == "up")
    review_found = sum(1 for prods in all_best_sellers.values() for p in prods if p.get("review_count"))

    report = {
        "scan_date": datetime.now().isoformat(),
        "best_sellers": all_best_sellers,
        "movers_and_shakers": all_movers,
        "total_products_scanned": total_products,
        "total_movers_found": total_movers,
        "brand_flagged": brand_count,
        "rising_products": rising_count,
        "review_data_found": review_found,
        "unique_asins": len(seen_asins),
        "has_bsr_history": bool(yesterday_map),
    }

    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"amazon_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(
        f"Amazon report saved: {output_file} | Products: {total_products} | "
        f"Movers: {total_movers} | Brands: {brand_count} | Reviews: {review_found}/{total_products}"
    )

    # Telegram alert
    msg = f"🛒 <b>AMAZON SCAN COMPLETE</b>\n📅 {today}\n\n"
    msg += f"📦 Produkte fizike: <b>{total_products}</b>\n"
    msg += f"📈 Movers &amp; Shakers: <b>{total_movers}</b>\n"
    msg += f"🏷 Brande te medha: <b>{brand_count}</b>\n"
    msg += f"🔢 Me reviews: <b>{review_found}/{total_products}</b>\n"
    if rising_count:
        msg += f"⬆️ Po ngjiten ne rank: <b>{rising_count}</b>\n"

    non_brand = [
        p for prods in all_best_sellers.values() for p in prods
        if not p.get("is_brand") and p.get("price_usd")
        and DROPSHIP_PRICE_MIN <= p["price_usd"] <= DROPSHIP_PRICE_MAX
    ]
    non_brand.sort(key=lambda x: x.get("rank", 999))
    if non_brand:
        msg += f"\n🎯 <b>TOP KANDIDATE DROPSHIP:</b>\n"
        for p in non_brand[:3]:
            price = f"${p['price_usd']:.2f}" if p.get("price_usd") else "N/A"
            rating = f"★{p['rating']:.1f}" if p.get("rating") else ""
            reviews = f"({p['review_count']:,} rev)" if p.get("review_count") else ""
            msg += f"  • <b>{p['title'][:40]}</b>\n"
            msg += f"    #{p['rank']} | {price} | {rating} {reviews}\n"

    msg += f"\n📁 Data: <code>data/amazon_{today}.json</code>"
    send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_amazon_scan()
