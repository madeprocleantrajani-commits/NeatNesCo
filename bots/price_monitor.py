"""
Price Monitor Bot v3
---------------------
Tracks prices of products you're actively selling/considering.
Alerts you when:
  - A supplier drops their price (better margins!)
  - A competitor changes their price
  - Price crosses your target threshold

v3 changes:
  - Auto-populate from AI analysis winners
  - Alert deduplication (no repeat alerts within 24 hours)
  - Resilient HTTP via config.resilient_fetch()
  - Structured data + meta tag price extraction prioritized
  - Price history sparklines in alerts

Outputs: data/prices_YYYY-MM-DD.json
Run: every 4-6 hours via cron
"""
import json
import re
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

from bs4 import BeautifulSoup

from config import (
    TRACKED_PRODUCTS, DATA_DIR, REQUEST_DELAY,
    get_logger, resilient_fetch, get_session,
)
from alert_bot import send_alert

log = get_logger("price_monitor")

# Price history file (persistent)
PRICE_HISTORY_FILE = DATA_DIR / "price_history.json"

# Alert dedup file — tracks which alerts were sent in last 24h
ALERT_DEDUP_FILE = DATA_DIR / "price_alert_dedup.json"


def load_price_history() -> dict:
    """Load existing price history."""
    if PRICE_HISTORY_FILE.exists():
        try:
            with open(PRICE_HISTORY_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_price_history(history: dict):
    """Save updated price history."""
    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def _load_dedup() -> dict:
    """Load alert dedup tracking."""
    if ALERT_DEDUP_FILE.exists():
        try:
            with open(ALERT_DEDUP_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def _save_dedup(dedup: dict):
    with open(ALERT_DEDUP_FILE, "w") as f:
        json.dump(dedup, f, indent=2)


def _is_duplicate_alert(dedup: dict, alert_key: str) -> bool:
    """Check if this alert was already sent within last 24 hours."""
    last_sent = dedup.get(alert_key)
    if not last_sent:
        return False
    try:
        last_time = datetime.fromisoformat(last_sent)
        return datetime.now() - last_time < timedelta(hours=24)
    except (ValueError, TypeError):
        return False


def _sparkline(prices: list) -> str:
    """Generate ASCII sparkline from price history."""
    if not prices or len(prices) < 2:
        return ""
    chars = "▁▂▃▄▅▆▇█"
    min_p = min(prices)
    max_p = max(prices)
    if max_p == min_p:
        return chars[3] * len(prices)
    span = max_p - min_p
    return "".join(chars[min(7, int((p - min_p) / span * 7))] for p in prices[-20:])


def _auto_populate_tracked() -> list[dict]:
    """
    Auto-populate tracked products from AI analysis winners.
    Supplements (doesn't replace) manual TRACKED_PRODUCTS.
    """
    tracked = list(TRACKED_PRODUCTS)
    tracked_urls = {p["url"] for p in tracked}

    # Load latest AI analysis
    files = sorted(DATA_DIR.glob("ai_analysis_*.json"), reverse=True)
    if not files:
        return tracked

    try:
        with open(files[0]) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return tracked

    winners = data.get("winners", [])
    for w in winners[:10]:
        title = w.get("shopify_title") or w.get("title", "Unknown")
        # Track the Amazon source URL if available
        url = w.get("url", "")
        if url and url not in tracked_urls:
            tracked.append({
                "name": title[:50],
                "url": url,
                "target_price": None,
                "auto_added": True,
            })
            tracked_urls.add(url)

    return tracked


def extract_price(url: str, session=None) -> dict:
    """
    Extract price from a product page.
    Supports: AliExpress, Amazon, generic e-commerce.
    Uses resilient_fetch for retries and bot detection.
    """
    result = {"url": url, "timestamp": datetime.now().isoformat()}

    response = resilient_fetch(url, session=session, timeout=20)
    if not response:
        result["error"] = "Failed to fetch (retries exhausted)"
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        # Strategy 1: Structured data (most reliable)
        # JSON-LD product data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                ld = json.loads(script.string)
                if isinstance(ld, list):
                    ld = ld[0]
                offers = ld.get("offers", ld.get("Offers"))
                if offers:
                    if isinstance(offers, list):
                        offers = offers[0]
                    price_val = _parse_price(str(offers.get("price", "")))
                    if price_val:
                        result["price"] = price_val
                        result["price_source"] = "json-ld"
            except (json.JSONDecodeError, AttributeError):
                continue

        # Strategy 2: Meta tags (second most reliable)
        if "price" not in result:
            meta_price = soup.find("meta", {"property": "product:price:amount"})
            if not meta_price:
                meta_price = soup.find("meta", {"itemprop": "price"})
            if meta_price:
                price_val = _parse_price(meta_price.get("content", ""))
                if price_val:
                    result["price"] = price_val
                    result["price_source"] = "meta"

        # Strategy 3: data-price attribute (reliable for Amazon)
        if "price" not in result:
            el = soup.select_one("[data-price]")
            if el:
                price_val = _parse_price(el.get("data-price", ""))
                if price_val:
                    result["price"] = price_val
                    result["price_source"] = "data-attr"

        # Strategy 4: CSS selectors (less reliable)
        if "price" not in result:
            price_selectors = [
                # Amazon
                ".a-price .a-offscreen",
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                "span.a-price-whole",
                # AliExpress
                "[class*='product-price'] .price--current",
                # Generic
                "[itemprop='price']",
                "[class*='price'] [class*='current']",
            ]

            for selector in price_selectors:
                el = soup.select_one(selector)
                if el:
                    price_text = el.get_text(strip=True) or el.get("content", "")
                    price_val = _parse_price(price_text)
                    if price_val:
                        result["price"] = price_val
                        result["price_raw"] = price_text
                        result["price_source"] = "css"
                        break

        # Strategy 5: Regex scan (last resort)
        if "price" not in result:
            text = soup.get_text()
            matches = re.findall(r"\$(\d+\.?\d*)", text)
            if matches:
                prices = [float(m) for m in matches if 0.5 < float(m) < 500]
                if prices:
                    result["price"] = min(prices)
                    result["price_source"] = "regex"
                    result["price_note"] = "extracted via regex (verify manually)"

        # Get product title
        title_el = soup.find("title")
        if title_el:
            result["page_title"] = title_el.get_text(strip=True)[:100]

    except Exception as e:
        result["error"] = str(e)
        log.error(f"Parse error for {url}: {e}")

    return result


def _parse_price(text: str) -> float | None:
    """Parse a price string into a float."""
    try:
        cleaned = text.replace(",", "").replace(" ", "")
        match = re.search(r"[\$]?([\d]+\.?\d*)", cleaned)
        if match:
            val = float(match.group(1))
            if 0.01 < val < 10000:
                return val
    except (ValueError, AttributeError):
        pass
    return None


def check_prices():
    """Check prices for all tracked products (manual + auto-populated)."""
    products = _auto_populate_tracked()

    if not products:
        log.info("No products being tracked. Add products to TRACKED_PRODUCTS or run ai_analyzer.py")
        return

    log.info(f"Checking prices for {len(products)} products...")
    history = load_price_history()
    dedup = _load_dedup()
    alerts = []
    session = get_session()

    for product in products:
        name = product["name"]
        url = product["url"]
        target = product.get("target_price")

        log.info(f"Checking: {name}")
        result = extract_price(url, session=session)

        if "error" in result:
            log.warning(f"Failed to get price for {name}: {result['error']}")
            continue

        current_price = result.get("price")
        if not current_price:
            log.warning(f"Could not extract price for {name}")
            continue

        # Initialize history for this product
        if name not in history:
            history[name] = {
                "url": url,
                "target_price": target,
                "price_log": [],
                "lowest_price": current_price,
                "highest_price": current_price,
                "auto_added": product.get("auto_added", False),
            }

        h = history[name]
        prev_price = h["price_log"][-1]["price"] if h["price_log"] else None

        # Log the price
        h["price_log"].append({
            "price": current_price,
            "timestamp": datetime.now().isoformat(),
            "source": result.get("price_source", "unknown"),
        })

        # Keep only last 90 days of data
        h["price_log"] = h["price_log"][-540:]  # ~6 checks/day * 90 days

        # Update bounds
        h["lowest_price"] = min(h["lowest_price"], current_price)
        h["highest_price"] = max(h["highest_price"], current_price)

        # Check for alerts (with dedup)
        if prev_price:
            change_pct = ((current_price - prev_price) / prev_price) * 100

            if change_pct <= -5:
                alert_key = f"drop_{name}"
                if not _is_duplicate_alert(dedup, alert_key):
                    # Price sparkline
                    recent_prices = [p["price"] for p in h["price_log"][-20:]]
                    spark = _sparkline(recent_prices)
                    alerts.append(
                        f"📉 PRICE DROP: {name}\n"
                        f"  Was: ${prev_price:.2f} → Now: ${current_price:.2f} ({change_pct:.1f}%)\n"
                        f"  {spark}"
                    )
                    dedup[alert_key] = datetime.now().isoformat()

            elif change_pct >= 10:
                alert_key = f"rise_{name}"
                if not _is_duplicate_alert(dedup, alert_key):
                    alerts.append(
                        f"📈 PRICE INCREASE: {name}\n"
                        f"  Was: ${prev_price:.2f} → Now: ${current_price:.2f} (+{change_pct:.1f}%)"
                    )
                    dedup[alert_key] = datetime.now().isoformat()

        if target and current_price <= target:
            alert_key = f"target_{name}"
            if not _is_duplicate_alert(dedup, alert_key):
                alerts.append(
                    f"🎯 TARGET HIT: {name}\n"
                    f"  Price: ${current_price:.2f} (target was ${target:.2f})"
                )
                dedup[alert_key] = datetime.now().isoformat()

        if current_price == h["lowest_price"] and len(h["price_log"]) > 1:
            alert_key = f"low_{name}"
            if not _is_duplicate_alert(dedup, alert_key):
                alerts.append(f"⬇️ ALL-TIME LOW: {name} at ${current_price:.2f}")
                dedup[alert_key] = datetime.now().isoformat()

        time.sleep(REQUEST_DELAY + random.uniform(1, 2))

    # Save updated history and dedup
    save_price_history(history)
    _save_dedup(dedup)
    log.info("Price history updated")

    # Send alerts
    if alerts:
        msg = "💰 <b>PRICE MONITOR ALERTS</b>\n\n" + "\n\n".join(alerts)
        send_alert(msg, parse_mode="HTML")
        log.info(f"Sent {len(alerts)} price alerts")

    # Save daily snapshot
    today = datetime.now().strftime("%Y-%m-%d")
    snapshot = {
        "scan_date": datetime.now().isoformat(),
        "products_checked": len(products),
        "alerts_sent": len(alerts),
        "current_prices": {
            p["name"]: {
                "price": history.get(p["name"], {}).get("price_log", [{}])[-1].get("price"),
                "lowest_ever": history.get(p["name"], {}).get("lowest_price"),
                "highest_ever": history.get(p["name"], {}).get("highest_price"),
                "auto_added": p.get("auto_added", False),
            }
            for p in products
            if p["name"] in history
        },
    }

    output_file = DATA_DIR / f"prices_{today}.json"
    with open(output_file, "w") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot


if __name__ == "__main__":
    check_prices()
