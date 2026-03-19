"""
Profit Tracker v1
------------------
Reads Shopify Orders API to track real sales performance.

What it does:
  - Fetches all orders from Shopify
  - Matches orders to products we imported
  - Calculates real revenue, cost, profit per product
  - Updates the learning database with actual outcomes
  - Identifies best sellers and underperformers
  - Sends daily profit report via Telegram

Outputs:
  - data/profit_YYYY-MM-DD.json
  - Updates learning_db (dropship_brain.db)
  - Telegram profit report

Dependencies: shopify_importer (API helpers), learning_db
"""
import json
import time
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

from config import (
    SHOPIFY_STORE, SHOPIFY_TOKEN, DATA_DIR,
    get_logger,
)
from alert_bot import send_alert

log = get_logger("profit_tracker")

SHOPIFY_API_VERSION = "2024-10"


# ── Shopify API ──────────────────────────────────────────────

def _shopify_get(endpoint: str, _retry: int = 0) -> dict | None:
    """GET request to Shopify Admin API with rate-limit retry."""
    if not SHOPIFY_STORE or not SHOPIFY_TOKEN:
        log.error("SHOPIFY_STORE or SHOPIFY_TOKEN not set")
        return None

    url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/{endpoint}"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Content-Type": "application/json",
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 429:
            if _retry >= 3:
                log.error("Shopify rate limit: max retries exhausted")
                return None
            wait = 2 * (_retry + 1)
            log.warning(f"Rate limited, waiting {wait}s (retry {_retry + 1}/3)")
            time.sleep(wait)
            return _shopify_get(endpoint, _retry + 1)
        else:
            log.error(f"Shopify API {r.status_code}: {r.text[:300]}")
            return None
    except requests.RequestException as e:
        log.error(f"Shopify request failed: {e}")
        return None


def fetch_orders(days: int = 30) -> list:
    """Fetch recent orders from Shopify."""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00-05:00")
    orders = []
    endpoint = f"orders.json?status=any&created_at_min={since}&limit=250"

    while endpoint:
        data = _shopify_get(endpoint)
        if not data:
            break
        orders.extend(data.get("orders", []))
        log.info(f"Fetched {len(orders)} orders so far")
        # Pagination — check for next page link
        endpoint = None  # Basic implementation; Shopify cursor pagination if needed
        break

    log.info(f"Total orders fetched: {len(orders)}")
    return orders


def fetch_products() -> dict:
    """Fetch all products and return as {product_id: product_info}."""
    products = {}
    data = _shopify_get("products.json?limit=250&fields=id,title,variants,status")
    if not data:
        return products

    for p in data.get("products", []):
        pid = str(p["id"])
        cost = 0
        price = 0
        if p.get("variants"):
            v = p["variants"][0]
            price = float(v.get("price", 0))
            cost = float(v.get("cost", 0) or 0)  # may be null

        products[pid] = {
            "id": pid,
            "title": p["title"],
            "price": price,
            "cost": cost,
            "status": p.get("status", "active"),
        }

    log.info(f"Fetched {len(products)} products from Shopify")
    return products


# ── Analysis ─────────────────────────────────────────────────

def analyze_orders(orders: list, products: dict) -> dict:
    """Analyze orders and calculate per-product metrics."""
    product_sales = defaultdict(lambda: {
        "title": "",
        "units_sold": 0,
        "gross_revenue": 0,
        "total_cost": 0,
        "total_profit": 0,
        "refunds": 0,
        "orders": [],
        "first_sale": None,
        "last_sale": None,
    })

    total_revenue = 0
    total_orders = 0
    total_refunded = 0

    for order in orders:
        # Skip cancelled orders
        if order.get("cancelled_at"):
            continue

        order_date = order.get("created_at", "")[:10]
        financial_status = order.get("financial_status", "")

        is_refunded = financial_status in ("refunded", "partially_refunded")

        for item in order.get("line_items", []):
            pid = str(item.get("product_id", ""))
            if not pid or pid == "None":
                continue

            title = item.get("title", "Unknown")
            quantity = item.get("quantity", 1)
            line_price = float(item.get("price", 0)) * quantity

            # Get cost from product catalog
            product_info = products.get(pid, {})
            unit_cost = product_info.get("cost", 0)
            line_cost = unit_cost * quantity

            ps = product_sales[pid]
            ps["title"] = title
            ps["units_sold"] += quantity
            ps["gross_revenue"] += line_price
            ps["total_cost"] += line_cost
            ps["total_profit"] += (line_price - line_cost)
            ps["orders"].append(order_date)

            if is_refunded:
                ps["refunds"] += quantity
                total_refunded += line_price

            if not ps["first_sale"] or order_date < ps["first_sale"]:
                ps["first_sale"] = order_date
            if not ps["last_sale"] or order_date > ps["last_sale"]:
                ps["last_sale"] = order_date

            total_revenue += line_price

        if not order.get("cancelled_at"):
            total_orders += 1

    # Calculate per-product metrics
    results = {}
    for pid, ps in product_sales.items():
        if ps["first_sale"] and ps["last_sale"]:
            days_active = max(1, (
                datetime.strptime(ps["last_sale"], "%Y-%m-%d") -
                datetime.strptime(ps["first_sale"], "%Y-%m-%d")
            ).days + 1)
        else:
            days_active = 1

        results[pid] = {
            "product_id": pid,
            "title": ps["title"],
            "units_sold": ps["units_sold"],
            "gross_revenue": round(ps["gross_revenue"], 2),
            "total_cost": round(ps["total_cost"], 2),
            "net_profit": round(ps["total_profit"], 2),
            "profit_margin": round(
                ps["total_profit"] / max(0.01, ps["gross_revenue"]) * 100, 1
            ),
            "refunds": ps["refunds"],
            "refund_rate": round(
                ps["refunds"] / max(1, ps["units_sold"]) * 100, 1
            ),
            "days_active": days_active,
            "daily_sales_rate": round(ps["units_sold"] / days_active, 2),
            "daily_revenue": round(ps["gross_revenue"] / days_active, 2),
            "first_sale": ps["first_sale"],
            "last_sale": ps["last_sale"],
            "avg_order_value": round(
                ps["gross_revenue"] / max(1, ps["units_sold"]), 2
            ),
        }

    summary = {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "total_refunded": round(total_refunded, 2),
        "net_revenue": round(total_revenue - total_refunded, 2),
        "products_with_sales": len(results),
        "period_days": 30,
    }

    return {"summary": summary, "products": results}


def classify_products(analysis: dict) -> dict:
    """Classify products into winners, average, and losers."""
    products = analysis.get("products", {})

    winners = []    # Products performing well
    average = []    # Decent but not great
    losers = []     # Underperforming — consider removing
    no_sales = []   # Zero sales

    for pid, data in products.items():
        if data["units_sold"] == 0:
            no_sales.append(data)
        elif data["daily_sales_rate"] >= 1.0 and data["refund_rate"] < 15:
            winners.append(data)
        elif data["daily_sales_rate"] >= 0.3 and data["refund_rate"] < 25:
            average.append(data)
        else:
            losers.append(data)

    # Sort each by profit
    winners.sort(key=lambda x: x["net_profit"], reverse=True)
    average.sort(key=lambda x: x["net_profit"], reverse=True)
    losers.sort(key=lambda x: x["net_profit"])

    return {
        "winners": winners,
        "average": average,
        "losers": losers,
        "no_sales": no_sales,
    }


# ── Learning DB Integration ─────────────────────────────────

def update_learning_db(analysis: dict):
    """Feed sales data back into the self-learning database."""
    try:
        from learning_db import update_sales, get_db
    except ImportError:
        log.warning("learning_db not available, skipping DB update")
        return

    products = analysis.get("products", {})
    updated = 0

    for pid, data in products.items():
        try:
            update_sales(
                shopify_product_id=pid,
                units=data["units_sold"],
                revenue=data["gross_revenue"],
                cost=data["total_cost"],
                returns=data["refunds"],
            )
            updated += 1
        except Exception as e:
            log.error(f"Failed to update learning DB for {pid}: {e}")

    log.info(f"Updated learning DB with {updated} product outcomes")


# ── Reporting ────────────────────────────────────────────────

def generate_report(analysis: dict, classification: dict) -> str:
    """Generate Telegram profit report."""
    summary = analysis["summary"]
    today = datetime.now().strftime("%Y-%m-%d")

    msg = f"💰 <b>PROFIT REPORT</b>\n📅 {today}\n\n"

    # Summary
    msg += (
        f"📊 <b>Summary (Last 30 days):</b>\n"
        f"  Orders: {summary['total_orders']}\n"
        f"  Revenue: ${summary['total_revenue']:,.2f}\n"
        f"  Refunds: ${summary['total_refunded']:,.2f}\n"
        f"  Net Revenue: ${summary['net_revenue']:,.2f}\n"
        f"  Products selling: {summary['products_with_sales']}\n\n"
    )

    # Winners
    if classification["winners"]:
        msg += "🏆 <b>WINNERS:</b>\n"
        for p in classification["winners"][:5]:
            msg += (
                f"  ✅ {p['title'][:30]}\n"
                f"     {p['units_sold']} sold | ${p['net_profit']:.2f} profit | "
                f"{p['daily_sales_rate']}/day\n"
            )
        msg += "\n"

    # Average
    if classification["average"]:
        msg += "📊 <b>AVERAGE:</b>\n"
        for p in classification["average"][:5]:
            msg += (
                f"  ➡️ {p['title'][:30]}\n"
                f"     {p['units_sold']} sold | ${p['net_profit']:.2f} profit\n"
            )
        msg += "\n"

    # Losers — action needed
    if classification["losers"]:
        msg += "⚠️ <b>UNDERPERFORMING (Consider removing):</b>\n"
        for p in classification["losers"][:5]:
            msg += (
                f"  ❌ {p['title'][:30]}\n"
                f"     {p['units_sold']} sold | Refund rate: {p['refund_rate']}%\n"
            )
        msg += "\n"

    # No sales
    no_sales_count = len(classification["no_sales"])
    if no_sales_count > 0:
        msg += f"🔇 <b>{no_sales_count} products with ZERO sales</b>\n\n"

    # Recommendations
    msg += "<b>🤖 Recommendations:</b>\n"
    if classification["winners"]:
        msg += "  → Scale ad spend on winners\n"
    if classification["losers"]:
        msg += "  → Remove or reprice underperformers\n"
    if no_sales_count > 5:
        msg += "  → Too many products with no sales — focus on fewer\n"
    if summary["total_orders"] == 0:
        msg += "  → No orders yet. Check: payment provider, password, ads\n"

    msg += f"\n📁 <code>data/profit_{today}.json</code>"
    return msg


# ── Main ─────────────────────────────────────────────────────

def run():
    """Run the full profit tracking pipeline."""
    log.info("=" * 60)
    log.info("PROFIT TRACKER — Starting")
    log.info("=" * 60)

    today = datetime.now().strftime("%Y-%m-%d")

    # Fetch data
    products = fetch_products()
    orders = fetch_orders(days=30)

    # Analyze
    analysis = analyze_orders(orders, products)
    classification = classify_products(analysis)

    # Update learning database
    update_learning_db(analysis)

    # Save report
    report = {
        "date": today,
        "summary": analysis["summary"],
        "classification": {
            "winners": classification["winners"],
            "average": classification["average"],
            "losers": classification["losers"],
            "no_sales_count": len(classification["no_sales"]),
        },
        "all_products": analysis["products"],
    }

    output_file = DATA_DIR / f"profit_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Profit report saved: {output_file}")

    # Send Telegram alert
    msg = generate_report(analysis, classification)
    send_alert(msg, parse_mode="HTML")

    log.info(f"Orders: {analysis['summary']['total_orders']}")
    log.info(f"Revenue: ${analysis['summary']['total_revenue']:.2f}")
    log.info(f"Winners: {len(classification['winners'])}")
    log.info(f"Losers: {len(classification['losers'])}")
    log.info("PROFIT TRACKER — Done")

    return report


if __name__ == "__main__":
    run()
