"""
Self-Learning Database v1
--------------------------
SQLite-backed memory for the dropship bot suite.

Tracks every product decision and its outcome so the robot
LEARNS from its own history instead of repeating mistakes.

Tables:
  - products: every product analyzed (ASIN, title, scores, decision)
  - outcomes: what actually happened (sold?, revenue, profit)
  - score_calibration: weekly accuracy metrics per score band
  - supplier_history: supplier reliability over time

Key features:
  - Records every BUY/SKIP decision with full score breakdown
  - Links decisions to real Shopify sales outcomes
  - Calculates accuracy: "of products I said BUY, how many sold?"
  - Auto-adjusts score thresholds based on hit rate
  - Tracks supplier reliability over time

Outputs: data/dropship_brain.db (persistent SQLite)
"""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from config import DATA_DIR, get_logger
from alert_bot import send_alert

log = get_logger("learning_db")

DB_PATH = DATA_DIR / "dropship_brain.db"


def get_db() -> sqlite3.Connection:
    """Get database connection with WAL mode for performance."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT,
            title TEXT NOT NULL,
            price REAL,
            category TEXT,
            source TEXT,

            -- Scores at time of analysis
            viability_score REAL,
            dna_score REAL,
            wow_factor REAL,
            problem_solving REAL,
            shipping_score REAL,
            return_risk REAL,
            tiktok_score REAL,
            ad_score REAL,
            momentum_score REAL,
            saturation_level TEXT,
            council_score REAL,
            council_decision TEXT,

            -- Final decision
            decision TEXT NOT NULL,
            decision_reason TEXT,

            -- Metadata
            scan_date TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),

            UNIQUE(asin, scan_date)
        );

        CREATE TABLE IF NOT EXISTS outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER REFERENCES products(id),
            shopify_product_id TEXT,

            -- Sales data
            units_sold INTEGER DEFAULT 0,
            total_revenue REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            total_profit REAL DEFAULT 0,
            avg_order_value REAL DEFAULT 0,

            -- Performance
            days_active INTEGER DEFAULT 0,
            daily_sales_rate REAL DEFAULT 0,
            return_count INTEGER DEFAULT 0,
            return_rate REAL DEFAULT 0,

            -- Status
            status TEXT DEFAULT 'imported',

            -- Dates
            imported_at TEXT,
            first_sale_at TEXT,
            last_updated TEXT DEFAULT (datetime('now')),

            UNIQUE(product_id)
        );

        CREATE TABLE IF NOT EXISTS score_calibration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT NOT NULL,
            score_band TEXT NOT NULL,
            total_products INTEGER DEFAULT 0,
            sold_products INTEGER DEFAULT 0,
            hit_rate REAL DEFAULT 0,
            avg_revenue REAL DEFAULT 0,
            avg_profit REAL DEFAULT 0,

            -- Recommended adjustments
            recommended_threshold REAL,
            confidence TEXT,

            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(week_start, score_band)
        );

        CREATE TABLE IF NOT EXISTS supplier_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id TEXT,
            supplier_name TEXT,
            platform TEXT DEFAULT 'aliexpress',

            rating REAL,
            positive_feedback_pct REAL,
            total_orders INTEGER,
            response_time_hours REAL,

            -- Quality tracking
            products_sourced INTEGER DEFAULT 0,
            quality_complaints INTEGER DEFAULT 0,
            shipping_delays INTEGER DEFAULT 0,
            avg_shipping_days REAL,

            -- Status
            status TEXT DEFAULT 'active',
            blacklisted INTEGER DEFAULT 0,
            blacklist_reason TEXT,

            checked_at TEXT DEFAULT (datetime('now')),
            UNIQUE(supplier_id, checked_at)
        );

        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT,
            title TEXT,
            source TEXT,
            price REAL NOT NULL,
            previous_price REAL,
            price_change_pct REAL,
            currency TEXT DEFAULT 'USD',
            recorded_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_products_asin ON products(asin);
        CREATE INDEX IF NOT EXISTS idx_products_decision ON products(decision);
        CREATE INDEX IF NOT EXISTS idx_products_scan_date ON products(scan_date);
        CREATE INDEX IF NOT EXISTS idx_outcomes_status ON outcomes(status);
        CREATE INDEX IF NOT EXISTS idx_price_history_asin ON price_history(asin);
        CREATE INDEX IF NOT EXISTS idx_supplier_status ON supplier_history(status);
    """)
    conn.commit()
    conn.close()
    log.info(f"Database initialized: {DB_PATH}")


def record_product(product: dict, decision: str, reason: str = "") -> int:
    """Record a product analysis decision. Returns product ID."""
    conn = get_db()
    try:
        cursor = conn.execute("""
            INSERT OR REPLACE INTO products
            (asin, title, price, category, source,
             viability_score, dna_score, wow_factor, problem_solving,
             shipping_score, return_risk, tiktok_score, ad_score,
             momentum_score, saturation_level, council_score, council_decision,
             decision, decision_reason, scan_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.get("asin", ""),
            product.get("title", "Unknown"),
            product.get("price", 0),
            product.get("category", ""),
            product.get("source", "amazon"),
            product.get("viability", 0),
            product.get("dna_score", 0),
            product.get("wow_factor", 0),
            product.get("problem_solving", 0),
            product.get("shipping_score", 0),
            product.get("return_risk", 0),
            product.get("tiktok_score", 0),
            product.get("ad_score", 0),
            product.get("momentum_score", 0),
            product.get("saturation_level", "unknown"),
            product.get("council_score", 0),
            product.get("council_decision", ""),
            decision,
            reason,
            datetime.now().strftime("%Y-%m-%d"),
        ))
        conn.commit()
        product_id = cursor.lastrowid
        return product_id
    finally:
        conn.close()


def record_outcome(product_id: int, shopify_id: str, status: str = "imported"):
    """Record that a product was imported to Shopify."""
    conn = get_db()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO outcomes
            (product_id, shopify_product_id, status, imported_at)
            VALUES (?, ?, ?, ?)
        """, (product_id, shopify_id, status, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()


def update_sales(shopify_product_id: str, units: int, revenue: float,
                 cost: float, returns: int = 0):
    """Update sales data for a product."""
    conn = get_db()
    try:
        profit = revenue - cost
        conn.execute("""
            UPDATE outcomes SET
                units_sold = ?,
                total_revenue = ?,
                total_cost = ?,
                total_profit = ?,
                return_count = ?,
                return_rate = CASE WHEN ? > 0 THEN CAST(? AS REAL) / ? ELSE 0 END,
                avg_order_value = CASE WHEN ? > 0 THEN ? / ? ELSE 0 END,
                days_active = CAST(
                    julianday('now') - julianday(imported_at) AS INTEGER
                ),
                daily_sales_rate = CASE
                    WHEN julianday('now') - julianday(imported_at) > 0
                    THEN CAST(? AS REAL) / (julianday('now') - julianday(imported_at))
                    ELSE 0 END,
                first_sale_at = CASE WHEN first_sale_at IS NULL AND ? > 0
                    THEN datetime('now') ELSE first_sale_at END,
                status = CASE
                    WHEN ? > 0 THEN 'selling'
                    ELSE status END,
                last_updated = datetime('now')
            WHERE shopify_product_id = ?
        """, (
            units, revenue, cost, profit,
            returns,
            units, returns, units,      # return_rate
            units, revenue, units,      # avg_order_value
            units,                       # daily_sales_rate
            units,                       # first_sale_at
            units,                       # status
            shopify_product_id,
        ))
        conn.commit()
    finally:
        conn.close()


def record_price(asin: str, title: str, source: str, price: float):
    """Record a price observation for historical tracking."""
    conn = get_db()
    try:
        # Get previous price
        row = conn.execute("""
            SELECT price FROM price_history
            WHERE asin = ? AND source = ?
            ORDER BY recorded_at DESC LIMIT 1
        """, (asin, source)).fetchone()

        prev_price = row["price"] if row else None
        change_pct = ((price - prev_price) / prev_price * 100) if prev_price else 0

        conn.execute("""
            INSERT INTO price_history (asin, title, source, price, previous_price, price_change_pct)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (asin, title, source, price, prev_price, round(change_pct, 1)))
        conn.commit()
    finally:
        conn.close()


def record_supplier(supplier_id: str, name: str, rating: float,
                    feedback_pct: float, orders: int, **kwargs):
    """Record a supplier observation."""
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO supplier_history
            (supplier_id, supplier_name, rating, positive_feedback_pct,
             total_orders, response_time_hours, avg_shipping_days)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            supplier_id, name, rating, feedback_pct, orders,
            kwargs.get("response_time", 0),
            kwargs.get("shipping_days", 0),
        ))
        conn.commit()
    finally:
        conn.close()


def blacklist_supplier(supplier_id: str, reason: str):
    """Blacklist a problematic supplier."""
    conn = get_db()
    try:
        conn.execute("""
            UPDATE supplier_history SET
                blacklisted = 1,
                blacklist_reason = ?,
                status = 'blacklisted'
            WHERE supplier_id = ?
        """, (reason, supplier_id))
        conn.commit()
        log.warning(f"Supplier blacklisted: {supplier_id} — {reason}")
    finally:
        conn.close()


def get_accuracy_report() -> dict:
    """Calculate how accurate our BUY decisions have been."""
    conn = get_db()
    try:
        report = {"bands": [], "overall": {}}

        # Overall stats
        total_buys = conn.execute(
            "SELECT COUNT(*) as c FROM products WHERE decision IN ('STRONG_BUY', 'BUY')"
        ).fetchone()["c"]

        sold = conn.execute("""
            SELECT COUNT(*) as c FROM outcomes o
            JOIN products p ON o.product_id = p.id
            WHERE p.decision IN ('STRONG_BUY', 'BUY') AND o.units_sold > 0
        """).fetchone()["c"]

        total_revenue = conn.execute("""
            SELECT COALESCE(SUM(o.total_revenue), 0) as r FROM outcomes o
            JOIN products p ON o.product_id = p.id
            WHERE p.decision IN ('STRONG_BUY', 'BUY')
        """).fetchone()["r"]

        total_profit = conn.execute("""
            SELECT COALESCE(SUM(o.total_profit), 0) as p FROM outcomes o
            JOIN products p ON o.product_id = p.id
            WHERE p.decision IN ('STRONG_BUY', 'BUY')
        """).fetchone()["p"]

        report["overall"] = {
            "total_buy_decisions": total_buys,
            "products_that_sold": sold,
            "hit_rate": round(sold / max(1, total_buys) * 100, 1),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
        }

        # By score band
        for band_name, low, high in [
            ("90-100", 90, 100), ("80-89", 80, 89), ("70-79", 70, 79),
            ("60-69", 60, 69), ("50-59", 50, 59), ("0-49", 0, 49),
        ]:
            row = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN o.units_sold > 0 THEN 1 ELSE 0 END) as sold,
                    COALESCE(AVG(o.total_revenue), 0) as avg_rev,
                    COALESCE(AVG(o.total_profit), 0) as avg_profit
                FROM products p
                LEFT JOIN outcomes o ON o.product_id = p.id
                WHERE p.viability_score BETWEEN ? AND ?
                AND p.decision IN ('STRONG_BUY', 'BUY')
            """, (low, high)).fetchone()

            total = row["total"]
            sold_count = row["sold"] or 0
            report["bands"].append({
                "band": band_name,
                "total": total,
                "sold": sold_count,
                "hit_rate": round(sold_count / max(1, total) * 100, 1),
                "avg_revenue": round(row["avg_rev"], 2),
                "avg_profit": round(row["avg_profit"], 2),
            })

        return report
    finally:
        conn.close()


def get_calibration_recommendation() -> dict:
    """Analyze historical accuracy and recommend threshold adjustments."""
    conn = get_db()
    try:
        # Need at least 20 products with outcomes to calibrate
        count = conn.execute("""
            SELECT COUNT(*) as c FROM outcomes WHERE units_sold >= 0
        """).fetchone()["c"]

        if count < 20:
            return {
                "status": "insufficient_data",
                "message": f"Need 20+ tracked products, have {count}",
                "recommendations": [],
            }

        # Find the score threshold that maximizes profit
        rows = conn.execute("""
            SELECT p.viability_score, o.total_profit, o.units_sold
            FROM products p
            JOIN outcomes o ON o.product_id = p.id
            WHERE p.decision IN ('STRONG_BUY', 'BUY')
            ORDER BY p.viability_score DESC
        """).fetchall()

        # Test different thresholds
        best_threshold = 60
        best_avg_profit = 0
        recommendations = []

        for threshold in range(50, 90, 5):
            above = [r for r in rows if r["viability_score"] >= threshold]
            if not above:
                continue
            avg_profit = sum(r["total_profit"] for r in above) / len(above)
            hit_rate = sum(1 for r in above if r["units_sold"] > 0) / len(above) * 100

            recommendations.append({
                "threshold": threshold,
                "products_above": len(above),
                "hit_rate": round(hit_rate, 1),
                "avg_profit": round(avg_profit, 2),
            })

            if avg_profit > best_avg_profit:
                best_avg_profit = avg_profit
                best_threshold = threshold

        return {
            "status": "ready",
            "current_threshold": 60,
            "recommended_threshold": best_threshold,
            "expected_improvement": f"+{round(best_avg_profit, 2)} avg profit",
            "recommendations": recommendations,
        }
    finally:
        conn.close()


def get_winning_patterns() -> dict:
    """Identify what score patterns lead to actual sales."""
    conn = get_db()
    try:
        # Products that actually sold well
        winners = conn.execute("""
            SELECT p.*, o.units_sold, o.total_profit, o.daily_sales_rate
            FROM products p
            JOIN outcomes o ON o.product_id = p.id
            WHERE o.units_sold > 3
            ORDER BY o.total_profit DESC
            LIMIT 20
        """).fetchall()

        # Products that failed
        losers = conn.execute("""
            SELECT p.*, o.units_sold, o.total_profit
            FROM products p
            JOIN outcomes o ON o.product_id = p.id
            WHERE o.days_active > 7 AND o.units_sold = 0
            LIMIT 20
        """).fetchall()

        if not winners:
            return {"status": "no_winners_yet", "patterns": []}

        # Calculate average scores for winners vs losers
        def avg_scores(products):
            if not products:
                return {}
            n = len(products)
            return {
                "avg_viability": round(sum(p["viability_score"] or 0 for p in products) / n, 1),
                "avg_dna": round(sum(p["dna_score"] or 0 for p in products) / n, 1),
                "avg_wow": round(sum(p["wow_factor"] or 0 for p in products) / n, 1),
                "avg_problem_solving": round(sum(p["problem_solving"] or 0 for p in products) / n, 1),
                "avg_shipping": round(sum(p["shipping_score"] or 0 for p in products) / n, 1),
                "avg_return_risk": round(sum(p["return_risk"] or 0 for p in products) / n, 1),
            }

        winner_avg = avg_scores(winners)
        loser_avg = avg_scores(losers)

        # Find which scores differentiate winners from losers
        patterns = []
        for key in winner_avg:
            diff = winner_avg[key] - loser_avg.get(key, 0)
            if abs(diff) > 5:
                metric = key.replace("avg_", "")
                direction = "higher" if diff > 0 else "lower"
                patterns.append({
                    "metric": metric,
                    "winner_avg": winner_avg[key],
                    "loser_avg": loser_avg.get(key, 0),
                    "difference": round(diff, 1),
                    "insight": f"Winners have {direction} {metric} ({winner_avg[key]} vs {loser_avg.get(key, 0)})",
                })

        return {
            "status": "ready",
            "total_winners": len(winners),
            "total_losers": len(losers),
            "winner_profile": winner_avg,
            "loser_profile": loser_avg,
            "key_patterns": sorted(patterns, key=lambda x: abs(x["difference"]), reverse=True),
        }
    finally:
        conn.close()


def get_price_trend(asin: str, days: int = 30) -> list:
    """Get price history for a product."""
    conn = get_db()
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute("""
            SELECT source, price, price_change_pct, recorded_at
            FROM price_history
            WHERE asin = ? AND recorded_at > ?
            ORDER BY recorded_at
        """, (asin, cutoff)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_supplier_reliability(supplier_id: str) -> dict:
    """Get supplier reliability history."""
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT * FROM supplier_history
            WHERE supplier_id = ?
            ORDER BY checked_at DESC
            LIMIT 30
        """, (supplier_id,)).fetchall()

        if not rows:
            return {"status": "unknown"}

        latest = dict(rows[0])
        avg_rating = sum(r["rating"] for r in rows) / len(rows)
        rating_trend = rows[0]["rating"] - rows[-1]["rating"] if len(rows) > 1 else 0

        return {
            "status": latest.get("status", "active"),
            "current_rating": latest["rating"],
            "avg_rating": round(avg_rating, 2),
            "rating_trend": round(rating_trend, 2),
            "observations": len(rows),
            "blacklisted": bool(latest.get("blacklisted", 0)),
        }
    finally:
        conn.close()


def get_stats_summary() -> dict:
    """Quick stats for Telegram report."""
    conn = get_db()
    try:
        products = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
        buys = conn.execute(
            "SELECT COUNT(*) as c FROM products WHERE decision IN ('STRONG_BUY', 'BUY')"
        ).fetchone()["c"]
        tracked = conn.execute("SELECT COUNT(*) as c FROM outcomes").fetchone()["c"]
        selling = conn.execute(
            "SELECT COUNT(*) as c FROM outcomes WHERE units_sold > 0"
        ).fetchone()["c"]
        revenue = conn.execute(
            "SELECT COALESCE(SUM(total_revenue), 0) as r FROM outcomes"
        ).fetchone()["r"]
        profit = conn.execute(
            "SELECT COALESCE(SUM(total_profit), 0) as p FROM outcomes"
        ).fetchone()["p"]
        prices_tracked = conn.execute(
            "SELECT COUNT(DISTINCT asin) as c FROM price_history"
        ).fetchone()["c"]
        suppliers_tracked = conn.execute(
            "SELECT COUNT(DISTINCT supplier_id) as c FROM supplier_history"
        ).fetchone()["c"]

        return {
            "total_products_analyzed": products,
            "buy_decisions": buys,
            "products_tracked": tracked,
            "products_selling": selling,
            "hit_rate": round(selling / max(1, tracked) * 100, 1),
            "total_revenue": round(revenue, 2),
            "total_profit": round(profit, 2),
            "prices_tracked": prices_tracked,
            "suppliers_tracked": suppliers_tracked,
        }
    finally:
        conn.close()


def run_learning_report():
    """Generate and send learning report via Telegram."""
    log.info("=" * 60)
    log.info("SELF-LEARNING REPORT — Starting")
    log.info("=" * 60)

    init_db()

    stats = get_stats_summary()
    accuracy = get_accuracy_report()
    calibration = get_calibration_recommendation()
    patterns = get_winning_patterns()

    today = datetime.now().strftime("%Y-%m-%d")

    # Save report
    report = {
        "date": today,
        "stats": stats,
        "accuracy": accuracy,
        "calibration": calibration,
        "patterns": patterns,
    }

    output_file = DATA_DIR / f"learning_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Learning report saved: {output_file}")

    # Telegram alert
    msg = f"🧠 <b>SELF-LEARNING REPORT</b>\n📅 {today}\n\n"

    msg += (
        f"📊 Products analyzed: {stats['total_products_analyzed']}\n"
        f"✅ BUY decisions: {stats['buy_decisions']}\n"
        f"📦 Tracked in Shopify: {stats['products_tracked']}\n"
        f"💰 Products selling: {stats['products_selling']}\n"
        f"🎯 Hit rate: {stats['hit_rate']}%\n"
        f"💵 Total revenue: ${stats['total_revenue']}\n"
        f"📈 Total profit: ${stats['total_profit']}\n\n"
    )

    # Accuracy by score band
    if accuracy.get("bands"):
        msg += "<b>Accuracy by Score Band:</b>\n"
        for band in accuracy["bands"]:
            if band["total"] > 0:
                msg += f"  {band['band']}: {band['hit_rate']}% hit ({band['total']} products)\n"
        msg += "\n"

    # Calibration recommendation
    if calibration.get("status") == "ready":
        msg += (
            f"🔧 <b>Calibration:</b>\n"
            f"  Current threshold: {calibration['current_threshold']}\n"
            f"  Recommended: {calibration['recommended_threshold']}\n"
            f"  Expected: {calibration['expected_improvement']}\n\n"
        )

    # Winning patterns
    if patterns.get("key_patterns"):
        msg += "<b>Key Patterns:</b>\n"
        for p in patterns["key_patterns"][:3]:
            msg += f"  💡 {p['insight']}\n"

    msg += f"\n📁 <code>data/learning_{today}.json</code>"
    send_alert(msg, parse_mode="HTML")

    return report


# Initialize database on import
init_db()


if __name__ == "__main__":
    run_learning_report()
