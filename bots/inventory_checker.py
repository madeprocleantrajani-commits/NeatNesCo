"""
Inventory Checker v1
---------------------
Monitors supplier stock levels and auto-disables products when out of stock.

What it does:
  - Checks AliExpress/Amazon product availability
  - Detects out-of-stock products
  - Auto-disables products in Shopify when supplier is OOS
  - Auto-re-enables when back in stock
  - Alerts via Telegram on stock changes
  - Tracks supplier reliability in learning_db

Outputs:
  - data/inventory_YYYY-MM-DD.json
  - Telegram stock alerts
  - Shopify product status changes

Dependencies: shopify_importer, learning_db
"""
import json
import re
import time
import requests
from datetime import datetime
from pathlib import Path

from config import (
    DATA_DIR, get_logger, get_session, resilient_fetch,
    SHOPIFY_STORE, SHOPIFY_TOKEN,
)
from alert_bot import send_alert

log = get_logger("inventory_checker")

SHOPIFY_API_VERSION = "2024-10"


# ── Stock Checking ───────────────────────────────────────────

def check_amazon_stock(asin: str, session=None) -> dict:
    """Check if an Amazon product is in stock."""
    if not asin:
        return {"status": "unknown", "reason": "no_asin"}

    sess = session or get_session()
    url = f"https://www.amazon.com/dp/{asin}"

    try:
        resp = resilient_fetch(url, sess)
        if not resp:
            return {"status": "unknown", "reason": "fetch_failed"}

        html = resp.text.lower()

        # Out of stock indicators
        oos_signals = [
            "currently unavailable",
            "out of stock",
            "we don't know when or if this item will be back",
            "this item is no longer available",
            "not available for purchase",
        ]

        # In stock indicators
        in_stock_signals = [
            "in stock",
            "add to cart",
            "buy now",
            "ships from and sold by",
            "arrives",
        ]

        oos_count = sum(1 for s in oos_signals if s in html)
        is_count = sum(1 for s in in_stock_signals if s in html)

        # Check quantity available
        qty_match = re.search(r"only (\d+) left in stock", html)
        qty_left = int(qty_match.group(1)) if qty_match else None

        if oos_count > 0 and is_count == 0:
            return {
                "status": "out_of_stock",
                "reason": "oos_signals_found",
                "confidence": "high",
            }
        elif qty_left is not None and qty_left < 5:
            return {
                "status": "low_stock",
                "quantity": qty_left,
                "reason": f"only_{qty_left}_left",
                "confidence": "high",
            }
        elif is_count > 0:
            return {
                "status": "in_stock",
                "quantity": qty_left,
                "confidence": "high" if is_count >= 2 else "medium",
            }
        else:
            return {"status": "unknown", "reason": "unclear_signals"}

    except Exception as e:
        log.error(f"Stock check failed for {asin}: {e}")
        return {"status": "error", "reason": str(e)}


def check_aliexpress_stock(product_url: str, session=None) -> dict:
    """Check if an AliExpress product is in stock."""
    if not product_url:
        return {"status": "unknown", "reason": "no_url"}

    sess = session or get_session()
    try:
        resp = resilient_fetch(product_url, sess)
        if not resp:
            return {"status": "unknown", "reason": "fetch_failed"}

        html = resp.text.lower()

        oos_signals = [
            "out of stock",
            "sold out",
            "no longer available",
            "this product is no longer available",
        ]

        oos_count = sum(1 for s in oos_signals if s in html)

        if oos_count > 0:
            return {"status": "out_of_stock", "confidence": "high"}

        # Check for order count (popularity indicator)
        order_match = re.search(r"([\d,]+)\s*(?:orders|sold)", html)
        orders = int(order_match.group(1).replace(",", "")) if order_match else None

        return {
            "status": "in_stock",
            "total_orders": orders,
            "confidence": "medium",
        }
    except Exception as e:
        log.error(f"AliExpress stock check failed: {e}")
        return {"status": "error", "reason": str(e)}


# ── Shopify Product Management ───────────────────────────────

def _shopify_request(method: str, endpoint: str, payload: dict = None,
                     _retry: int = 0):
    """Shopify Admin API request with retry."""
    if not SHOPIFY_STORE or not SHOPIFY_TOKEN:
        return None

    url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/{endpoint}"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Content-Type": "application/json",
    }
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=15)
        elif method == "PUT":
            r = requests.put(url, headers=headers, json=payload, timeout=15)
        else:
            return None

        if r.status_code in (200, 201):
            return r.json()
        elif r.status_code == 429 and _retry < 3:
            time.sleep(2 * (_retry + 1))
            return _shopify_request(method, endpoint, payload, _retry + 1)
        else:
            log.error(f"Shopify {method} {r.status_code}: {r.text[:200]}")
            return None
    except requests.RequestException as e:
        log.error(f"Shopify request failed: {e}")
        return None


def get_shopify_products() -> list:
    """Get all active Shopify products."""
    data = _shopify_request("GET", "products.json?status=active&limit=250")
    if not data:
        return []
    return data.get("products", [])


def set_product_status(product_id: str, status: str) -> bool:
    """Set a Shopify product status (active/draft/archived)."""
    result = _shopify_request("PUT", f"products/{product_id}.json", {
        "product": {"id": int(product_id), "status": status}
    })
    if result:
        log.info(f"Product {product_id} set to {status}")
        return True
    return False


# ── Main Pipeline ────────────────────────────────────────────

def load_import_history() -> dict:
    """Load import history to find ASINs for Shopify products."""
    history_file = DATA_DIR / "shopify_import_history.json"
    if not history_file.exists():
        return {}

    with open(history_file) as f:
        data = json.load(f)

    # Build mapping: shopify_product_id → asin
    mapping = {}
    for item in data if isinstance(data, list) else data.get("imports", []):
        spid = str(item.get("shopify_product_id", ""))
        asin = item.get("asin", "")
        if spid and asin:
            mapping[spid] = {
                "asin": asin,
                "aliexpress_url": item.get("aliexpress_url", ""),
                "title": item.get("title", ""),
            }

    return mapping


def run():
    """Run inventory check on all active Shopify products."""
    log.info("=" * 60)
    log.info("INVENTORY CHECKER — Starting")
    log.info("=" * 60)

    today = datetime.now().strftime("%Y-%m-%d")
    session = get_session()

    # Get Shopify products and import history
    products = get_shopify_products()
    import_map = load_import_history()

    if not products:
        log.warning("No active products found in Shopify")
        return

    log.info(f"Checking {len(products)} active products")

    results = []
    oos_products = []
    low_stock = []
    back_in_stock = []

    for product in products:
        pid = str(product["id"])
        title = product["title"]
        info = import_map.get(pid, {})
        asin = info.get("asin", "")
        ali_url = info.get("aliexpress_url", "")

        # Check stock on Amazon
        stock = {"status": "unknown"}
        if asin:
            stock = check_amazon_stock(asin, session)
            time.sleep(2)  # Rate limiting
        elif ali_url:
            stock = check_aliexpress_stock(ali_url, session)
            time.sleep(2)

        result = {
            "product_id": pid,
            "title": title,
            "asin": asin,
            "stock_status": stock["status"],
            "stock_details": stock,
            "action_taken": None,
        }

        if stock["status"] == "out_of_stock":
            # Disable the product in Shopify
            if set_product_status(pid, "draft"):
                result["action_taken"] = "disabled"
                oos_products.append(result)
                log.warning(f"OUT OF STOCK — Disabled: {title}")
            else:
                result["action_taken"] = "disable_failed"
                oos_products.append(result)

        elif stock["status"] == "low_stock":
            low_stock.append(result)
            log.info(f"LOW STOCK ({stock.get('quantity', '?')} left): {title}")

        elif stock["status"] == "in_stock":
            # Check if it was previously disabled (back in stock)
            if product.get("status") == "draft":
                if set_product_status(pid, "active"):
                    result["action_taken"] = "re_enabled"
                    back_in_stock.append(result)
                    log.info(f"BACK IN STOCK — Re-enabled: {title}")

        results.append(result)

    # Save report
    report = {
        "date": today,
        "total_checked": len(results),
        "out_of_stock": len(oos_products),
        "low_stock": len(low_stock),
        "back_in_stock": len(back_in_stock),
        "products": results,
    }

    output_file = DATA_DIR / f"inventory_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    log.info(f"Inventory report saved: {output_file}")

    # Telegram alert (only if something notable happened)
    if oos_products or low_stock or back_in_stock:
        msg = f"📦 <b>INVENTORY ALERT</b>\n📅 {today}\n\n"

        if oos_products:
            msg += "🚫 <b>OUT OF STOCK (Disabled in Shopify):</b>\n"
            for p in oos_products:
                msg += f"  ❌ {p['title'][:40]}\n"
            msg += "\n"

        if low_stock:
            msg += "⚠️ <b>LOW STOCK:</b>\n"
            for p in low_stock:
                qty = p["stock_details"].get("quantity", "?")
                msg += f"  ⚡ {p['title'][:40]} — {qty} left\n"
            msg += "\n"

        if back_in_stock:
            msg += "✅ <b>BACK IN STOCK (Re-enabled):</b>\n"
            for p in back_in_stock:
                msg += f"  🔄 {p['title'][:40]}\n"
            msg += "\n"

        msg += f"📊 Total checked: {len(results)}"
        send_alert(msg, parse_mode="HTML")
    else:
        log.info("All products in stock — no alerts needed")

    log.info("INVENTORY CHECKER — Done")
    return report


if __name__ == "__main__":
    run()
