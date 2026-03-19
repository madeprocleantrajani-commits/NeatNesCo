"""
AliExpress Product Research Bot v3
------------------------------------
v3: Real profit math (no fantasy multipliers), supplier scoring,
    shipping cost extraction, order count validation, resilient HTTP.

Outputs: data/aliexpress_YYYY-MM-DD.json
"""
import json
import time
import random
import re
from datetime import datetime
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from config import DATA_DIR, REQUEST_DELAY, USER_AGENTS, get_logger, get_session, resilient_fetch
from validators import validate_price, parse_order_count, calculate_real_profit
from alert_bot import send_alert

log = get_logger("aliexpress_scanner")


def search_aliexpress(keyword: str, session, max_pages: int = 2) -> list[dict]:
    """Search AliExpress for a product keyword with retry + UA rotation."""
    products = []

    for page in range(1, max_pages + 1):
        url = (
            f"https://www.aliexpress.com/wholesale"
            f"?SearchText={quote_plus(keyword)}"
            f"&page={page}"
            f"&SortType=total_tranpro_desc"
        )

        # Rotate User-Agent per request for better anti-bot evasion
        session.headers["User-Agent"] = random.choice(USER_AGENTS)

        response = resilient_fetch(url, session=session, timeout=20)
        if response is None:
            # Retry once with simplified keyword (first 2-3 words)
            short_kw = " ".join(keyword.split()[:3])
            if short_kw != keyword:
                retry_url = (
                    f"https://www.aliexpress.com/wholesale"
                    f"?SearchText={quote_plus(short_kw)}"
                    f"&page={page}&SortType=total_tranpro_desc"
                )
                time.sleep(random.uniform(3, 6))
                session.headers["User-Agent"] = random.choice(USER_AGENTS)
                response = resilient_fetch(retry_url, session=session, timeout=20)
            if response is None:
                log.warning(f"AliExpress fetch failed for '{keyword}' page {page}")
                continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Try DOM selectors first
        items = soup.select("[class*='product-card'], [class*='search-card']")

        if not items:
            # Fallback: extract from embedded JSON
            scripts = soup.find_all("script")
            for script in scripts:
                text = script.string or ""
                if "searchResult" in text or "itemList" in text:
                    products.extend(_parse_json_products(text, keyword))
                    break

        for item in items:
            product = {"search_keyword": keyword}

            # Title
            title_el = item.select_one("h1, h3, [class*='title'] a, a[title]")
            if title_el:
                product["title"] = title_el.get_text(strip=True) or title_el.get("title", "")

            # Price
            price_el = item.select_one("[class*='price'], .mGXnE")
            if price_el:
                price_text = price_el.get_text(strip=True)
                product["price_raw"] = price_text
                match = re.search(r"\$?([\d.]+)", price_text)
                if match:
                    product["price_usd"] = validate_price(float(match.group(1)))

            # Orders / sold count
            sold_el = item.select_one("[class*='sold'], [class*='trade']")
            if sold_el:
                raw_orders = sold_el.get_text(strip=True)
                product["orders_raw"] = raw_orders
                product["orders"] = parse_order_count(raw_orders)

            # Rating
            rating_el = item.select_one("[class*='rating'], [class*='star']")
            if rating_el:
                rating_text = rating_el.get_text(strip=True)
                product["rating_raw"] = rating_text
                try:
                    product["rating"] = float(re.search(r"[\d.]+", rating_text).group())
                except (ValueError, AttributeError):
                    product["rating"] = None

            # Store name
            store_el = item.select_one("[class*='store'], [class*='seller']")
            if store_el:
                product["store"] = store_el.get_text(strip=True)

            # Shipping info
            ship_el = item.select_one("[class*='shipping'], [class*='delivery']")
            if ship_el:
                ship_text = ship_el.get_text(strip=True).lower()
                product["shipping_raw"] = ship_text
                if "free" in ship_text:
                    product["shipping_cost"] = 0.0
                else:
                    ship_match = re.search(r"\$?([\d.]+)", ship_text)
                    if ship_match:
                        product["shipping_cost"] = float(ship_match.group(1))

            # Product URL
            link_el = item.select_one("a[href*='/item/']")
            if link_el:
                href = link_el.get("href", "")
                if href.startswith("//"):
                    href = "https:" + href
                product["url"] = href

            # Image
            img_el = item.select_one("img[src]")
            if img_el:
                product["image"] = img_el.get("src", "")

            if product.get("title"):
                products.append(product)

        log.info(f"Found {len(items)} items for '{keyword}' page {page}")
        time.sleep(random.uniform(4, 8))  # Longer delay to avoid rate limiting

    return products


def _parse_json_products(script_text: str, keyword: str) -> list[dict]:
    """Extract product data from AliExpress embedded JSON."""
    products = []
    try:
        patterns = [
            r'"itemList"\s*:\s*(\[.+?\])',
            r'"items"\s*:\s*(\[.+?\])',
        ]
        for pattern in patterns:
            match = re.search(pattern, script_text, re.DOTALL)
            if match:
                items = json.loads(match.group(1))
                for item in items[:30]:
                    product = {
                        "search_keyword": keyword,
                        "title": item.get("title", ""),
                        "price_raw": item.get("price", ""),
                        "orders_raw": str(item.get("trade", {}).get("tradeDesc", "")),
                        "orders": parse_order_count(str(item.get("trade", {}).get("tradeDesc", ""))),
                        "rating_raw": str(item.get("evaluation", {}).get("starRating", "")),
                        "url": item.get("productDetailUrl", ""),
                        "image": item.get("image", {}).get("imgUrl", ""),
                    }
                    # Price
                    price_str = str(item.get("price", {}).get("minPrice", ""))
                    if price_str:
                        product["price_usd"] = validate_price(price_str)

                    # Rating
                    try:
                        product["rating"] = float(product["rating_raw"])
                    except (ValueError, TypeError):
                        product["rating"] = None

                    if product["title"]:
                        products.append(product)
                break
    except (json.JSONDecodeError, KeyError):
        pass
    return products


def calculate_margins(products: list[dict]) -> list[dict]:
    """
    Calculate REAL profit margins — no more fantasy multipliers.
    Uses: source_price + shipping + platform_fee(15%) + ad_cost(30%) = total_cost
    """
    for product in products:
        source_price = product.get("price_usd")
        if source_price and source_price > 0:
            shipping = product.get("shipping_cost", 3.0)  # Default $3 if unknown

            # Calculate at different retail points
            retail_2x = round(source_price * 2, 2)
            retail_2_5x = round(source_price * 2.5, 2)
            retail_3x = round(source_price * 3, 2)

            product["margin_analysis"] = {
                "source_price": source_price,
                "shipping_est": shipping,
                "at_2x_retail": calculate_real_profit(source_price, retail_2x, shipping),
                "at_2_5x_retail": calculate_real_profit(source_price, retail_2_5x, shipping),
                "at_3x_retail": calculate_real_profit(source_price, retail_3x, shipping),
            }

            # Supplier quality score (0-100)
            supplier_score = 0
            orders = product.get("orders", 0)
            rating = product.get("rating")

            if orders >= 10000:
                supplier_score += 40
            elif orders >= 1000:
                supplier_score += 30
            elif orders >= 100:
                supplier_score += 15

            if rating and rating >= 4.8:
                supplier_score += 30
            elif rating and rating >= 4.5:
                supplier_score += 20
            elif rating and rating >= 4.0:
                supplier_score += 10

            if product.get("shipping_cost", 99) == 0:
                supplier_score += 15  # Free shipping is a plus
            elif product.get("shipping_cost", 99) < 5:
                supplier_score += 10

            if product.get("store"):
                supplier_score += 15  # Has identifiable store

            product["supplier_score"] = min(supplier_score, 100)

    return products


def scan_for_keywords(keywords: list[str]) -> dict:
    """Scan AliExpress for a list of keywords."""
    log.info(f"Scanning AliExpress for {len(keywords)} keywords...")
    session = get_session(use_proxy=True)
    all_results = {}

    for kw in keywords:
        log.info(f"Searching: {kw}")
        products = search_aliexpress(kw, session, max_pages=2)

        # Retry with simplified keyword if no results (take first 2 words)
        if not products and len(kw.split()) > 2:
            simple_kw = " ".join(kw.split()[:2])
            log.info(f"Retrying with simplified keyword: {simple_kw}")
            time.sleep(REQUEST_DELAY + random.uniform(2, 4))
            products = search_aliexpress(simple_kw, session, max_pages=1)

        products = calculate_margins(products)

        # Sort by orders (most popular first)
        products.sort(key=lambda x: x.get("orders", 0), reverse=True)

        all_results[kw] = products
        time.sleep(REQUEST_DELAY + random.uniform(2, 5))

    return all_results


def run_aliexpress_scan(keywords: list[str] = None):
    """Run AliExpress scan."""
    if not keywords:
        keywords = _load_trending_keywords()

    # If trending keywords are too few, supplement with seed keywords
    if len(keywords) < 10:
        from config import SEED_KEYWORDS
        seed_kws = []
        for niche_kws in SEED_KEYWORDS.values():
            seed_kws.extend(niche_kws[:2])
        # Add seeds that aren't already in trending
        existing = {k.lower() for k in keywords}
        for sk in seed_kws:
            if sk.lower() not in existing:
                keywords.append(sk)
                existing.add(sk.lower())
            if len(keywords) >= 15:
                break
        if len(keywords) > len(_load_trending_keywords()):
            log.info(f"Supplemented {len(_load_trending_keywords())} trending with seed keywords → {len(keywords)} total")

    if not keywords:
        log.warning("No keywords to scan.")
        return None

    results = scan_for_keywords(keywords)

    report = {
        "scan_date": datetime.now().isoformat(),
        "keywords_scanned": len(keywords),
        "total_products_found": sum(len(v) for v in results.values()),
        "results": {},
        "best_deals": [],
    }

    for kw, products in results.items():
        report["results"][kw] = products[:15]

        # Find best deals — products with real profit potential
        for p in products[:5]:
            source = p.get("price_usd")
            if not source or source <= 0:
                continue

            margin = p.get("margin_analysis", {}).get("at_2_5x_retail", {})
            if margin.get("viable"):
                report["best_deals"].append({
                    "keyword": kw,
                    "title": p.get("title", "")[:80],
                    "source_price": source,
                    "shipping": p.get("shipping_cost", "N/A"),
                    "orders": p.get("orders", 0),
                    "supplier_score": p.get("supplier_score", 0),
                    "retail_price": margin.get("retail_price"),
                    "real_profit": margin.get("profit"),
                    "margin_pct": margin.get("margin_pct"),
                })

    # Save
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"aliexpress_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"AliExpress report saved: {output_file}")

    # Telegram alert
    if report["best_deals"]:
        msg = f"🏭 <b>ALIEXPRESS SCAN COMPLETE</b>\n"
        msg += f"📅 {today}\n"
        msg += f"🔍 Produkte gjetur: <b>{report['total_products_found']}</b>\n\n"
        msg += f"💰 <b>MARREVESHJE TE MIRA</b> ({len(report['best_deals'])} me fitim real):\n"
        for deal in report["best_deals"][:5]:
            score_icon = "🟢" if deal["supplier_score"] >= 60 else "🟡" if deal["supplier_score"] >= 30 else "🔴"
            msg += f"\n  {score_icon} <b>{deal['title'][:40]}</b>\n"
            msg += f"     Burim: ${deal['source_price']:.2f} → Shitje: ${deal.get('retail_price', 0):.2f}\n"
            msg += f"     Fitimi REAL: <b>${deal.get('real_profit', 0):.2f}</b> ({deal.get('margin_pct', 0)}%)\n"
            msg += f"     Porosi: {deal['orders']:,} | Supplier: {deal['supplier_score']}/100\n"
        msg += f"\n📁 <code>data/aliexpress_{today}.json</code>"
        send_alert(msg, parse_mode="HTML")
    else:
        send_alert(
            f"🏭 ALIEXPRESS SCAN\n"
            f"Produkte: {report['total_products_found']}\n"
            f"Asnje marreveshje fitimprurese u gjet."
        )

    return report


def _is_product_keyword(query: str) -> bool:
    """Filter out non-product queries (questions, brand names, how-tos)."""
    q = query.lower().strip()
    # Skip questions and informational queries
    if any(q.startswith(w) for w in ["what ", "how ", "why ", "can ", "where ", "when ",
                                      "is ", "are ", "do ", "does ", "should "]):
        return False
    # Skip single words (too generic) and very long queries (questions)
    word_count = len(q.split())
    if word_count < 2 or word_count > 6:
        return False
    # Skip queries with question-like patterns
    if "?" in q or " not working" in q or " vs " in q:
        return False
    return True


def _load_trending_keywords() -> list[str]:
    """Load hot keywords from the latest trend scan, filtered for product relevance."""
    import glob
    trend_files = sorted(glob.glob(str(DATA_DIR / "trends_*.json")), reverse=True)
    if not trend_files:
        return []
    try:
        with open(trend_files[0]) as f:
            data = json.load(f)
        keywords = []
        # Hot products are already product-like
        for hp in data.get("hot_products", []):
            keywords.append(hp["keyword"])
        # Discoveries need filtering — many are questions or brand names
        for d in data.get("discoveries", []):
            query = d["query"]
            if _is_product_keyword(query):
                keywords.append(query)
            else:
                log.debug(f"Skipping non-product discovery: '{query}'")
        # Deduplicate
        seen = set()
        unique = []
        for kw in keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique.append(kw)
        return unique[:15]
    except (json.JSONDecodeError, KeyError):
        return []


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_aliexpress_scan(sys.argv[1:])
    else:
        run_aliexpress_scan()
