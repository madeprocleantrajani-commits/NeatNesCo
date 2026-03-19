"""
Competitor Store Tracker v3
-----------------------------
Monitors competitor Shopify/e-commerce stores for:
  - New products added
  - Price changes
  - Best sellers (by collection/tag)

v3 changes:
  - Auto-discovery from intelligence data
  - Resilient HTTP via config.get_session()
  - Price tier analysis (where competitors cluster)
  - Niche overlap detection (what niches they sell in)
  - Trend correlation (are they selling trending products?)
  - Better Telegram alerts with context

Most Shopify stores expose their product catalog via:
  /products.json (public API)
  /collections/all/products.json

This is 100% legal — it's a public API endpoint.

Outputs: data/competitors_YYYY-MM-DD.json
Run: daily via cron
"""
import json
import time
import random
from datetime import datetime
from urllib.parse import urlparse

from config import (
    COMPETITOR_STORES, DATA_DIR, REQUEST_DELAY, SEED_KEYWORDS,
    get_logger, get_session, resilient_fetch,
)
from alert_bot import send_alert

log = get_logger("competitor_tracker")

# Persistent competitor data
COMPETITOR_DATA_FILE = DATA_DIR / "competitor_history.json"


def load_competitor_history() -> dict:
    if COMPETITOR_DATA_FILE.exists():
        try:
            with open(COMPETITOR_DATA_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_competitor_history(data: dict):
    # Prune old data — keep only last 14 days, max 50 products per store
    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(days=14)).isoformat()[:10]
    pruned = {}
    for store, snapshots in data.items():
        if isinstance(snapshots, list):
            recent = [s for s in snapshots if s.get("date", s.get("scan_date", "9999"))[:10] >= cutoff]
            if recent:
                pruned[store] = recent
        elif isinstance(snapshots, dict):
            # Check last_scan date — skip if too old
            last_scan = snapshots.get("last_scan", "9999")[:10]
            if last_scan < cutoff:
                continue
            # Limit products list to 50
            products = snapshots.get("products", [])
            if len(products) > 50:
                snapshots["products"] = products[:50]
            pruned[store] = snapshots
    with open(COMPETITOR_DATA_FILE, "w") as f:
        json.dump(pruned, f, indent=2)


def _get_all_seed_keywords() -> list[str]:
    """Flatten all seed keywords for matching."""
    all_kw = []
    for keywords in SEED_KEYWORDS.values():
        all_kw.extend(keywords)
    return all_kw


def _auto_discover_stores() -> list[str]:
    """
    Auto-discover competitor stores from intelligence data.
    Loads from competitors_discovered.json if available.
    """
    stores = list(COMPETITOR_STORES)
    store_domains = {urlparse(s).netloc for s in stores}

    # Load discovered competitors
    disc_file = DATA_DIR / "competitors_discovered.json"
    if disc_file.exists():
        try:
            with open(disc_file) as f:
                data = json.load(f)
            for domain, info in data.get("stores", {}).items():
                url = info.get("url", f"https://{domain}")
                if urlparse(url).netloc not in store_domains:
                    stores.append(url)
                    store_domains.add(urlparse(url).netloc)
        except (json.JSONDecodeError, IOError):
            pass

    return stores


def _get_shopify_session() -> "requests.Session":
    """
    Create a session optimized for Shopify JSON API.
    Key differences from get_session():
      - Accept: application/json (not text/html)
      - No bot-detection checks (JSON won't have "access denied" etc.)
      - No proxy (Shopify public API doesn't need it)
    """
    import requests as req
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    session = req.Session()
    session.headers.update({
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        ]),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })

    retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def fetch_shopify_products(store_url: str, session=None) -> list[dict]:
    """
    Fetch all products from a Shopify store using the public products.json API.

    Uses a dedicated Shopify session with Accept: application/json header
    and NO bot-detection filtering (which caused false positives on JSON).
    """
    products = []
    base_url = store_url.rstrip("/")
    page = 1

    # Always use Shopify-optimized session (ignore passed session)
    session = _get_shopify_session()

    while True:
        url = f"{base_url}/products.json?limit=250&page={page}"

        try:
            response = session.get(url, timeout=20)

            if response.status_code != 200:
                # Try alternative endpoint
                alt_url = f"{base_url}/collections/all/products.json?limit=250&page={page}"
                response = session.get(alt_url, timeout=20)

                if response.status_code != 200:
                    log.warning(f"Store {base_url} returned HTTP {response.status_code}")
                    break

            data = response.json()
            page_products = data.get("products", [])

            if not page_products:
                break

            for p in page_products:
                product = {
                    "id": p.get("id"),
                    "title": p.get("title", ""),
                    "handle": p.get("handle", ""),
                    "vendor": p.get("vendor", ""),
                    "product_type": p.get("product_type", ""),
                    "tags": p.get("tags", []),
                    "created_at": p.get("created_at", ""),
                    "updated_at": p.get("updated_at", ""),
                    "url": f"{base_url}/products/{p.get('handle', '')}",
                    "variants": [],
                    "images": [],
                }

                # Get pricing from variants
                for v in p.get("variants", []):
                    product["variants"].append({
                        "title": v.get("title", ""),
                        "price": v.get("price", ""),
                        "compare_at_price": v.get("compare_at_price"),
                        "available": v.get("available", True),
                        "sku": v.get("sku", ""),
                    })

                # Get first image
                images = p.get("images", [])
                if images:
                    product["images"] = [img.get("src", "") for img in images[:3]]

                # Main price (first variant)
                if product["variants"]:
                    try:
                        product["price"] = float(product["variants"][0]["price"])
                    except (ValueError, TypeError):
                        product["price"] = None

                products.append(product)

            page += 1
            time.sleep(REQUEST_DELAY)

        except json.JSONDecodeError:
            log.warning(f"Invalid JSON from {url} — store may not be Shopify or has Cloudflare")
            break
        except Exception as e:
            log.error(f"Failed to fetch {url}: {e}")
            break

    log.info(f"Found {len(products)} products from {base_url}")
    return products


def analyze_store_changes(store_url: str, current_products: list[dict], history: dict) -> dict:
    """Compare current products with previous scan to find changes."""
    store_key = urlparse(store_url).netloc
    changes = {
        "new_products": [],
        "removed_products": [],
        "price_changes": [],
    }

    prev_data = history.get(store_key, {})
    prev_products = {p["id"]: p for p in prev_data.get("products", [])}
    curr_products = {p["id"]: p for p in current_products}

    # New products
    for pid, product in curr_products.items():
        if pid not in prev_products:
            changes["new_products"].append({
                "title": product["title"],
                "price": product.get("price"),
                "url": product["url"],
                "type": product["product_type"],
            })

    # Removed products
    for pid, product in prev_products.items():
        if pid not in curr_products:
            changes["removed_products"].append({
                "title": product["title"],
                "price": product.get("price"),
            })

    # Price changes
    for pid, product in curr_products.items():
        if pid in prev_products:
            old_price = prev_products[pid].get("price")
            new_price = product.get("price")
            if old_price and new_price and old_price != new_price:
                changes["price_changes"].append({
                    "title": product["title"],
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_pct": round(((new_price - old_price) / old_price) * 100, 1),
                    "url": product["url"],
                })

    return changes


def get_store_stats(products: list[dict]) -> dict:
    """Calculate store statistics with price tier analysis."""
    prices = [p["price"] for p in products if p.get("price")]
    types = {}
    for p in products:
        t = p.get("product_type", "unknown") or "unknown"
        types[t] = types.get(t, 0) + 1

    # Price tier analysis
    tiers = {
        "under_15": sum(1 for p in prices if p < 15),
        "15_to_30": sum(1 for p in prices if 15 <= p < 30),
        "30_to_50": sum(1 for p in prices if 30 <= p < 50),
        "50_to_80": sum(1 for p in prices if 50 <= p < 80),
        "over_80": sum(1 for p in prices if p >= 80),
    }

    # Dropship sweet spot (what % of their products are in our target range)
    sweet_spot_count = sum(1 for p in prices if 15 <= p <= 80)
    sweet_spot_pct = round(sweet_spot_count / len(prices) * 100, 1) if prices else 0

    return {
        "total_products": len(products),
        "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
        "median_price": round(
            sorted(prices)[len(prices) // 2], 2
        ) if prices else 0,
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
        "price_range": f"${min(prices):.2f} - ${max(prices):.2f}" if prices else "N/A",
        "price_tiers": tiers,
        "sweet_spot_pct": sweet_spot_pct,
        "product_types": dict(sorted(types.items(), key=lambda x: x[1], reverse=True)),
    }


def _detect_niche_overlap(products: list[dict]) -> dict:
    """
    Detect which of our tracked niches the competitor is selling in.
    Returns dict of niche -> count of matching products.
    """
    overlaps = {}
    all_titles = " ".join(p.get("title", "").lower() for p in products)

    for niche, keywords in SEED_KEYWORDS.items():
        matches = 0
        matched_keywords = []
        for kw in keywords:
            if kw.lower() in all_titles:
                matches += 1
                matched_keywords.append(kw)
        if matches > 0:
            overlaps[niche] = {
                "match_count": matches,
                "matched_keywords": matched_keywords,
            }

    return overlaps


def run_competitor_scan():
    """Scan all competitor stores (manual + auto-discovered)."""
    all_stores = _auto_discover_stores()

    if not all_stores:
        log.info("No competitor stores configured or discovered. Add URLs to COMPETITOR_STORES in config.py")
        return

    log.info(f"Scanning {len(all_stores)} competitor stores...")
    history = load_competitor_history()
    all_changes = {}
    session = get_session()
    report = {
        "scan_date": datetime.now().isoformat(),
        "stores_scanned": len(all_stores),
        "stores": {},
    }

    for store_url in all_stores:
        store_key = urlparse(store_url).netloc
        log.info(f"Scanning: {store_key}")

        products = fetch_shopify_products(store_url, session=session)

        if not products:
            log.warning(f"No products found for {store_key}")
            continue

        # Analyze changes
        changes = analyze_store_changes(store_url, products, history)
        stats = get_store_stats(products)
        niche_overlap = _detect_niche_overlap(products)

        report["stores"][store_key] = {
            "url": store_url,
            "stats": stats,
            "changes": changes,
            "niche_overlap": niche_overlap,
            "top_products": sorted(
                products, key=lambda x: x.get("price", 0) or 0, reverse=True
            )[:10],
        }

        if any(changes.values()):
            all_changes[store_key] = changes

        # Update history
        history[store_key] = {
            "last_scan": datetime.now().isoformat(),
            "products": products,
        }

        time.sleep(REQUEST_DELAY + random.uniform(1, 3))

    # Save history
    save_competitor_history(history)

    # Save daily report
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"competitors_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Competitor report saved: {output_file}")

    # Alert on changes
    if all_changes:
        msg_parts = ["🔍 <b>COMPETITOR TRACKER ALERTS</b>\n"]

        for store, changes in all_changes.items():
            msg_parts.append(f"\n<b>── {store} ──</b>")

            if changes["new_products"]:
                msg_parts.append(f"  🆕 {len(changes['new_products'])} NEW products:")
                for p in changes["new_products"][:3]:
                    price_str = f"${p.get('price', 0):.2f}" if p.get("price") else "N/A"
                    msg_parts.append(f"    + {p['title'][:40]} ({price_str})")

            if changes["removed_products"]:
                msg_parts.append(f"  🗑 {len(changes['removed_products'])} REMOVED products")

            if changes["price_changes"]:
                msg_parts.append(f"  💲 {len(changes['price_changes'])} price changes:")
                for p in changes["price_changes"][:3]:
                    msg_parts.append(
                        f"    {p['title'][:30]}: ${p['old_price']:.2f} → ${p['new_price']:.2f} "
                        f"({p['change_pct']:+.1f}%)"
                    )

        msg = "\n".join(msg_parts)
        send_alert(msg, parse_mode="HTML")

    # Summary alert with niche overlap
    overlap_stores = {
        k: v for k, v in report["stores"].items()
        if v.get("niche_overlap")
    }
    if overlap_stores:
        overlap_msg = ["🎯 <b>NICHE OVERLAP</b>\n"]
        for store_key, store_data in overlap_stores.items():
            for niche, data in store_data["niche_overlap"].items():
                kw_list = ", ".join(data["matched_keywords"][:3])
                overlap_msg.append(
                    f"  {store_key} → {niche} ({data['match_count']} matches: {kw_list})"
                )
        if len(overlap_msg) > 1:
            send_alert("\n".join(overlap_msg), parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_competitor_scan()
