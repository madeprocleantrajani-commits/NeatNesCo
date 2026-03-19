"""
Metrics Tracker — Robot Memory System
---------------------------------------
Records daily snapshots of ALL key metrics so the robot
can track its own development over time.

Tracks:
  1. Daily pipeline health (which bots ran, data quality)
  2. Product recommendations history (STRONG_BUY/BUY changes)
  3. Score progression per product (is it getting stronger?)
  4. Winner stability (how long has a product been recommended?)
  5. Sales data (when available — links recommendations to real revenue)

Outputs: data/metrics_history.json (persistent, grows over time)
Run: daily after winner_analyzer (cron 11:00 AM)
"""
import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR, get_logger, is_major_brand

log = get_logger("metrics_tracker")

METRICS_FILE = DATA_DIR / "metrics_history.json"
PRODUCT_HISTORY_FILE = DATA_DIR / "product_history.json"
SALES_FILE = DATA_DIR / "sales_log.json"


def load_json(path: Path) -> dict:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _load_latest(prefix: str) -> dict | None:
    files = sorted(DATA_DIR.glob(f"{prefix}_*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


# ── Daily Snapshot ──────────────────────────────────────


def record_daily_snapshot():
    """Record today's key metrics — called after winner_analyzer."""
    today = datetime.now().strftime("%Y-%m-%d")
    log.info(f"Recording daily snapshot for {today}")

    history = load_json(METRICS_FILE)
    if "daily" not in history:
        history["daily"] = {}

    # Load all data sources
    trends = _load_latest("trends")
    tiktok = _load_latest("tiktok")
    amazon = _load_latest("amazon")
    demand = _load_latest("demand")
    ebay = _load_latest("ebay")
    aliexpress = _load_latest("aliexpress")
    adspy = _load_latest("adspy")
    competitors = _load_latest("competitors")
    analysis = _load_latest("analysis")
    winners = _load_latest("winners")

    # Pipeline health
    pipeline = {
        "trends": {
            "ok": bool(trends and trends.get("hot_products")),
            "hot_products": len(trends.get("hot_products", [])) if trends else 0,
            "discoveries": len(trends.get("discoveries", [])) if trends else 0,
        },
        "tiktok": {
            "ok": bool(tiktok and tiktok.get("top_picks")),
            "top_picks": len(tiktok.get("top_picks", [])) if tiktok else 0,
        },
        "amazon": {
            "ok": bool(amazon and amazon.get("total_products_scanned", 0) > 0),
            "products": amazon.get("total_products_scanned", 0) if amazon else 0,
            "movers": amazon.get("total_movers_found", 0) if amazon else 0,
        },
        "demand": {
            "ok": bool(demand and demand.get("stats", {}).get("total_unique_suggestions", 0) > 0),
            "suggestions": demand.get("stats", {}).get("total_unique_suggestions", 0) if demand else 0,
        },
        "ebay": {
            "ok": bool(ebay and ebay.get("stats", {}).get("total_sold_found", 0) > 0),
            "sold": ebay.get("stats", {}).get("total_sold_found", 0) if ebay else 0,
        },
        "aliexpress": {
            "ok": bool(aliexpress and aliexpress.get("total_products_found", 0) > 0),
            "products": aliexpress.get("total_products_found", 0) if aliexpress else 0,
            "deals": len(aliexpress.get("best_deals", [])) if aliexpress else 0,
        },
        "adspy": {
            "ok": bool(adspy and adspy.get("stats", {}).get("intelligence_total", 0) > 0),
            "intelligence": adspy.get("stats", {}).get("intelligence_total", 0) if adspy else 0,
        },
        "competitors": {
            "ok": bool(competitors and competitors.get("stores")),
            "stores": len(competitors.get("stores", {})) if competitors else 0,
        },
    }
    active_sources = sum(1 for v in pipeline.values() if v["ok"])

    # Winner metrics
    winner_stats = {}
    top_products = []
    if winners:
        stats = winners.get("stats", {})
        winner_stats = {
            "total_analyzed": stats.get("total_products", 0),
            "strong_buy": stats.get("strong_buy_count", 0),
            "buy": stats.get("buy_count", 0),
            "watch": stats.get("watch_count", 0),
            "avg_viability": stats.get("avg_viability", 0),
            "tiktok_validated": stats.get("tiktok_validated", 0),
            "ad_proven": stats.get("ad_proven", 0),
            "trend_matches": stats.get("trend_matches", 0),
            "evergreen": stats.get("evergreen", 0),
        }

        # Top 20 products snapshot (for tracking over time)
        for w in winners.get("strong_buys", [])[:10]:
            top_products.append({
                "title": w["title"][:60],
                "price": w.get("price", 0),
                "viability": w.get("viability", 0),
                "type": w.get("type", ""),
                "signal_count": w.get("signal_count", 0),
                "recommendation": "STRONG_BUY",
            })
        for w in winners.get("buys", [])[:10]:
            top_products.append({
                "title": w["title"][:60],
                "price": w.get("price", 0),
                "viability": w.get("viability", 0),
                "type": w.get("type", ""),
                "signal_count": w.get("signal_count", 0),
                "recommendation": "BUY",
            })

    # Analysis quality
    analysis_stats = {}
    if analysis:
        analysis_stats = {
            "active_sources": active_sources,
            "candidates": len(analysis.get("amazon", {}).get("dropship_candidates", [])),
            "cross_refs": len(analysis.get("cross_references", [])),
        }

    # Save snapshot
    history["daily"][today] = {
        "timestamp": datetime.now().isoformat(),
        "pipeline": pipeline,
        "active_sources": active_sources,
        "winner_stats": winner_stats,
        "analysis_stats": analysis_stats,
        "top_products": top_products,
    }

    # Keep only last 90 days
    dates = sorted(history["daily"].keys())
    if len(dates) > 90:
        for old_date in dates[:-90]:
            del history["daily"][old_date]

    save_json(METRICS_FILE, history)
    log.info(f"Snapshot saved: {active_sources}/8 sources, "
             f"{winner_stats.get('strong_buy', 0)} STRONG_BUY, "
             f"{winner_stats.get('buy', 0)} BUY")

    return history["daily"][today]


# ── Product History ──────────────────────────────────────


def update_product_history():
    """
    Track each product's journey over time:
    - When it first appeared
    - Score/viability progression
    - How many days it's been recommended
    - Recommendation changes (WATCH → BUY → STRONG_BUY)
    """
    today = datetime.now().strftime("%Y-%m-%d")
    winners = _load_latest("winners")
    if not winners:
        return

    product_hist = load_json(PRODUCT_HISTORY_FILE)
    if "products" not in product_hist:
        product_hist["products"] = {}
    if "last_updated" not in product_hist:
        product_hist["last_updated"] = today

    all_winners = winners.get("all_winners", [])

    # Track each product
    seen_today = set()
    for w in all_winners:
        title = w.get("title", "")[:60]
        if not title:
            continue

        key = title.lower().strip()
        seen_today.add(key)

        if key not in product_hist["products"]:
            # New product — first sighting
            product_hist["products"][key] = {
                "title": title,
                "first_seen": today,
                "last_seen": today,
                "days_seen": 1,
                "best_viability": w.get("viability", 0),
                "best_recommendation": w.get("recommendation", "SKIP"),
                "current_price": w.get("price", 0),
                "history": [{
                    "date": today,
                    "viability": w.get("viability", 0),
                    "recommendation": w.get("recommendation", "SKIP"),
                    "price": w.get("price", 0),
                    "signal_count": w.get("signal_count", 0),
                    "type": w.get("type", ""),
                }],
            }
        else:
            # Existing product — update
            prod = product_hist["products"][key]
            prod["last_seen"] = today
            prod["days_seen"] = prod.get("days_seen", 0) + 1
            prod["current_price"] = w.get("price", 0)

            # Update best scores
            if w.get("viability", 0) > prod.get("best_viability", 0):
                prod["best_viability"] = w["viability"]
            rec_rank = {"SKIP": 0, "WATCH": 1, "BUY": 2, "STRONG_BUY": 3}
            if rec_rank.get(w.get("recommendation"), 0) > rec_rank.get(prod.get("best_recommendation"), 0):
                prod["best_recommendation"] = w["recommendation"]

            # Add daily entry (keep last 30 entries per product)
            prod["history"].append({
                "date": today,
                "viability": w.get("viability", 0),
                "recommendation": w.get("recommendation", "SKIP"),
                "price": w.get("price", 0),
                "signal_count": w.get("signal_count", 0),
                "type": w.get("type", ""),
            })
            if len(prod["history"]) > 30:
                prod["history"] = prod["history"][-30:]

    # Mark products not seen today
    for key, prod in product_hist["products"].items():
        if key not in seen_today and prod["last_seen"] != today:
            # Product disappeared — don't delete, just track
            if prod.get("days_missing") is None:
                prod["days_missing"] = 0
            prod["days_missing"] = prod.get("days_missing", 0) + 1

    # Prune products not seen in 30+ days
    stale_keys = [
        k for k, v in product_hist["products"].items()
        if v.get("days_missing", 0) > 30
    ]
    for k in stale_keys:
        del product_hist["products"][k]
    if stale_keys:
        log.info(f"Pruned {len(stale_keys)} stale products from history")

    product_hist["last_updated"] = today
    product_hist["total_tracked"] = len(product_hist["products"])

    # Stats
    prods = product_hist["products"]
    product_hist["summary"] = {
        "total_tracked": len(prods),
        "strong_buy_ever": sum(1 for p in prods.values() if p.get("best_recommendation") == "STRONG_BUY"),
        "consistent_winners": sum(1 for p in prods.values() if p.get("days_seen", 0) >= 3 and p.get("best_recommendation") in ("STRONG_BUY", "BUY")),
        "rising_stars": sum(1 for p in prods.values() if _is_rising(p)),
        "falling": sum(1 for p in prods.values() if _is_falling(p)),
    }

    save_json(PRODUCT_HISTORY_FILE, product_hist)
    log.info(f"Product history updated: {len(prods)} tracked, "
             f"{product_hist['summary']['consistent_winners']} consistent winners")

    return product_hist


def _is_rising(product: dict) -> bool:
    """Check if product viability is increasing over time."""
    hist = product.get("history", [])
    if len(hist) < 2:
        return False
    recent = hist[-1].get("viability", 0)
    older = hist[0].get("viability", 0)
    return recent > older + 3  # At least 3 points improvement


def _is_falling(product: dict) -> bool:
    """Check if product viability is decreasing over time."""
    hist = product.get("history", [])
    if len(hist) < 2:
        return False
    recent = hist[-1].get("viability", 0)
    older = hist[0].get("viability", 0)
    return recent < older - 5  # At least 5 points drop


# ── Sales Tracking ──────────────────────────────────────


def record_sale(product_title: str, revenue: float, cost: float,
                platform: str = "shopify", notes: str = ""):
    """
    Record a sale — links real revenue to product recommendations.
    Call this manually or via webhook when a sale happens.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    sales = load_json(SALES_FILE)
    if "sales" not in sales:
        sales["sales"] = []
    if "totals" not in sales:
        sales["totals"] = {"revenue": 0, "cost": 0, "profit": 0, "count": 0}

    profit = revenue - cost

    sales["sales"].append({
        "date": today,
        "timestamp": datetime.now().isoformat(),
        "product": product_title[:80],
        "revenue": round(revenue, 2),
        "cost": round(cost, 2),
        "profit": round(profit, 2),
        "platform": platform,
        "notes": notes,
    })

    sales["totals"]["revenue"] = round(sales["totals"]["revenue"] + revenue, 2)
    sales["totals"]["cost"] = round(sales["totals"]["cost"] + cost, 2)
    sales["totals"]["profit"] = round(sales["totals"]["profit"] + profit, 2)
    sales["totals"]["count"] += 1

    # Link to product history
    product_hist = load_json(PRODUCT_HISTORY_FILE)
    key = product_title[:60].lower().strip()
    if key in product_hist.get("products", {}):
        prod = product_hist["products"][key]
        if "sales" not in prod:
            prod["sales"] = []
        prod["sales"].append({
            "date": today,
            "revenue": round(revenue, 2),
            "profit": round(profit, 2),
        })
        prod["total_revenue"] = round(sum(s["revenue"] for s in prod["sales"]), 2)
        prod["total_profit"] = round(sum(s["profit"] for s in prod["sales"]), 2)
        save_json(PRODUCT_HISTORY_FILE, product_hist)

    save_json(SALES_FILE, sales)
    log.info(f"Sale recorded: {product_title[:40]} — ${revenue:.2f} revenue, ${profit:.2f} profit")

    return sales


# ── Development Report ──────────────────────────────────


def get_development_report() -> str:
    """
    Generate a development report showing how the robot is performing over time.
    Shows trends, improvements, and areas that need attention.
    """
    history = load_json(METRICS_FILE)
    product_hist = load_json(PRODUCT_HISTORY_FILE)
    sales = load_json(SALES_FILE)

    daily = history.get("daily", {})
    dates = sorted(daily.keys())

    if not dates:
        return "No metrics history yet. Run record_daily_snapshot() first."

    report = []
    report.append("=" * 60)
    report.append("ROBOT DEVELOPMENT REPORT")
    report.append("=" * 60)
    report.append(f"Tracking since: {dates[0]}")
    report.append(f"Days tracked: {len(dates)}")
    report.append(f"Latest: {dates[-1]}")

    # Pipeline health trend
    report.append("\n--- PIPELINE HEALTH ---")
    if len(dates) >= 2:
        first = daily[dates[0]]
        last = daily[dates[-1]]
        first_sources = first.get("active_sources", 0)
        last_sources = last.get("active_sources", 0)
        direction = "UP" if last_sources > first_sources else ("DOWN" if last_sources < first_sources else "STABLE")
        report.append(f"  Sources: {first_sources}/8 -> {last_sources}/8 ({direction})")
    else:
        last = daily[dates[-1]]
        report.append(f"  Sources: {last.get('active_sources', 0)}/8")

    # Winner trends
    report.append("\n--- WINNER TRENDS ---")
    if len(dates) >= 2:
        first_ws = daily[dates[0]].get("winner_stats", {})
        last_ws = daily[dates[-1]].get("winner_stats", {})
        for key in ["strong_buy", "buy", "avg_viability"]:
            f_val = first_ws.get(key, 0)
            l_val = last_ws.get(key, 0)
            diff = l_val - f_val
            sign = "+" if diff > 0 else ""
            report.append(f"  {key}: {f_val} -> {l_val} ({sign}{diff})")

    # Product stability
    report.append("\n--- PRODUCT STABILITY ---")
    prods = product_hist.get("products", {})
    summary = product_hist.get("summary", {})
    report.append(f"  Total tracked: {summary.get('total_tracked', len(prods))}")
    report.append(f"  Consistent winners (3+ days): {summary.get('consistent_winners', 0)}")
    report.append(f"  Rising stars: {summary.get('rising_stars', 0)}")
    report.append(f"  Falling: {summary.get('falling', 0)}")

    # Top consistent products
    consistent = sorted(
        [(k, v) for k, v in prods.items()
         if v.get("days_seen", 0) >= 2 and v.get("best_recommendation") in ("STRONG_BUY", "BUY")],
        key=lambda x: (-x[1].get("days_seen", 0), -x[1].get("best_viability", 0))
    )
    if consistent:
        report.append("\n  TOP CONSISTENT WINNERS:")
        for key, prod in consistent[:10]:
            report.append(
                f"    [{prod['best_recommendation']}] {prod['title'][:45]} "
                f"(V:{prod['best_viability']:.0f}, {prod['days_seen']} days)"
            )

    # Sales summary
    report.append("\n--- SALES ---")
    totals = sales.get("totals", {})
    if totals.get("count", 0) > 0:
        report.append(f"  Total sales: {totals['count']}")
        report.append(f"  Revenue: ${totals['revenue']:.2f}")
        report.append(f"  Profit: ${totals['profit']:.2f}")
        report.append(f"  Avg profit/sale: ${totals['profit'] / totals['count']:.2f}")
    else:
        report.append("  No sales recorded yet.")
        report.append("  Use: record_sale('Product Name', revenue, cost)")

    return "\n".join(report)


# ── Telegram Summary ──────────────────────────────────


def send_daily_metrics():
    """Send daily metrics summary to Telegram."""
    from alert_bot import send_alert

    history = load_json(METRICS_FILE)
    product_hist = load_json(PRODUCT_HISTORY_FILE)
    sales = load_json(SALES_FILE)

    daily = history.get("daily", {})
    dates = sorted(daily.keys())
    if not dates:
        return

    today_data = daily[dates[-1]]
    ws = today_data.get("winner_stats", {})
    summary = product_hist.get("summary", {})

    msg = "📊 <b>DAILY METRICS SNAPSHOT</b>\n"
    msg += f"📅 {dates[-1]} | Day #{len(dates)}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Pipeline
    msg += f"🔌 <b>Pipeline:</b> {today_data.get('active_sources', 0)}/8 sources\n"

    # Winners
    msg += f"\n🏆 <b>Winners Today:</b>\n"
    msg += f"  🔴 STRONG_BUY: {ws.get('strong_buy', 0)}\n"
    msg += f"  🟡 BUY: {ws.get('buy', 0)}\n"
    msg += f"  📊 Avg Viability: {ws.get('avg_viability', 0)}\n"

    # Product stability
    msg += f"\n📈 <b>Product Tracking:</b>\n"
    msg += f"  Total tracked: {summary.get('total_tracked', 0)}\n"
    msg += f"  Consistent winners: {summary.get('consistent_winners', 0)}\n"
    msg += f"  Rising: {summary.get('rising_stars', 0)} | Falling: {summary.get('falling', 0)}\n"

    # Trend comparison (if we have >1 day)
    if len(dates) >= 2:
        yesterday_data = daily[dates[-2]]
        yw = yesterday_data.get("winner_stats", {})
        sb_diff = ws.get("strong_buy", 0) - yw.get("strong_buy", 0)
        v_diff = ws.get("avg_viability", 0) - yw.get("avg_viability", 0)
        if sb_diff != 0 or v_diff != 0:
            msg += f"\n📉 <b>vs Dje:</b>\n"
            if sb_diff != 0:
                msg += f"  STRONG_BUY: {'+' if sb_diff > 0 else ''}{sb_diff}\n"
            if v_diff != 0:
                msg += f"  Viability: {'+' if v_diff > 0 else ''}{v_diff:.1f}\n"

    # Sales
    totals = sales.get("totals", {})
    if totals.get("count", 0) > 0:
        msg += f"\n💰 <b>Sales Total:</b>\n"
        msg += f"  {totals['count']} sales | ${totals['revenue']:.2f} revenue | ${totals['profit']:.2f} profit\n"

    send_alert(msg, parse_mode="HTML")
    log.info("Daily metrics sent to Telegram")


# ── Main ──────────────────────────────────────────────


def run_metrics_tracker():
    """Full metrics tracking run."""
    log.info("=" * 60)
    log.info("METRICS TRACKER — Recording Daily Snapshot")
    log.info("=" * 60)

    snapshot = record_daily_snapshot()
    product_hist = update_product_history()
    send_daily_metrics()

    # Print development report
    report = get_development_report()
    print(report)

    return snapshot


if __name__ == "__main__":
    run_metrics_tracker()
