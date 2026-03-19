#!/usr/bin/env python3
"""
NEATNESTCO INTELLIGENCE DASHBOARD
Real-time business intelligence panel showing:
- Winning products & tiers
- Margins & profitability
- Store status
- Product performance scores
- Actionable recommendations

Generates HTML dashboard + sends Telegram summary
"""

import requests
import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SHOP = os.getenv("SHOPIFY_STORE", "8hendy-8i.myshopify.com")
TOKEN = os.getenv("SHOPIFY_TOKEN", "")
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
API = "https://%s/admin/api/2024-01" % SHOP
DATA_DIR = os.path.expanduser("~/dropship-bots/data")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID", "")

# Product cost data (supplier + shipping estimates)
COST_DATA = {
    "ProSpin Electric Scrubber": {"cost": 11.20, "ship": 3.50, "tier": "HERO"},
    "AlignPro Posture Corrector": {"cost": 4.50, "ship": 2.00, "tier": "HERO"},
    "BreezePro Portable Neck Fan": {"cost": 5.50, "ship": 2.50, "tier": "HERO"},
    "BlendJet Portable Blender": {"cost": 8.00, "ship": 3.00, "tier": "TEST"},
    "SteamPro Portable Garment Steamer": {"cost": 7.00, "ship": 3.00, "tier": "TEST"},
    "MiniGrid Waffle Maker": {"cost": 6.50, "ship": 3.50, "tier": "TEST"},
    "FlexFit Resistance Bands Set": {"cost": 5.00, "ship": 2.50, "tier": "TEST"},
    "FurBuster Pet Hair Remover Roller": {"cost": 3.50, "ship": 2.00, "tier": "TEST"},
    "GlamSpin Rotating Makeup Organizer": {"cost": 8.00, "ship": 3.50, "tier": "TEST"},
    "GlowSense LED Motion Sensor Night Light": {"cost": 4.00, "ship": 2.00, "tier": "BACKUP"},
    "FrothMaster Electric Milk Frother": {"cost": 2.80, "ship": 1.50, "tier": "BACKUP"},
    "BrightSmile LED Teeth Whitening Kit": {"cost": 5.00, "ship": 2.00, "tier": "BACKUP"},
    "ClearPatch Acne Pimple Patches": {"cost": 1.50, "ship": 1.00, "tier": "BACKUP"},
    "ChopMaster 8-in-1 Vegetable Chopper": {"cost": 5.00, "ship": 2.50, "tier": "BACKUP"},
    "ArcLite Electric Lighter": {"cost": 2.50, "ship": 1.50, "tier": "BACKUP"},
}


def get_shopify_products():
    """Get all products from Shopify"""
    r = requests.get(
        "%s/products.json?limit=250" % API,
        headers=HEADERS,
    )
    if r.status_code == 200:
        return r.json().get("products", [])
    return []


def get_shopify_orders():
    """Get recent orders"""
    r = requests.get(
        "%s/orders.json?status=any&limit=50" % API,
        headers=HEADERS,
    )
    if r.status_code == 200:
        return r.json().get("orders", [])
    return []


def calculate_metrics(products):
    """Calculate business metrics for each product"""
    metrics = []
    for p in products:
        title = p["title"]
        price = float(p["variants"][0]["price"]) if p["variants"] else 0
        compare = float(p["variants"][0].get("compare_at_price") or 0) if p["variants"] else 0
        images = len(p.get("images", []))
        status = p["status"]
        has_description = len(p.get("body_html", "")) > 100
        weight = float(p["variants"][0].get("weight", 0)) if p["variants"] else 0

        # Find cost data
        cost_info = None
        for key, val in COST_DATA.items():
            if key.lower() in title.lower() or title.lower().startswith(key.lower()[:15]):
                cost_info = val
                break

        if cost_info:
            total_cost = cost_info["cost"] + cost_info["ship"]
            shopify_fee = price * 0.029 + 0.30
            net_profit = price - total_cost - shopify_fee
            margin = (net_profit / price * 100) if price > 0 else 0
            tier = cost_info["tier"]
        else:
            total_cost = price * 0.35  # Estimate
            net_profit = price - total_cost
            margin = 65
            tier = "OTHER"

        # Product readiness score (0-100)
        score = 0
        if images >= 3: score += 20
        elif images >= 1: score += 10
        if has_description: score += 20
        if price > 0: score += 15
        if compare > price: score += 10
        if weight > 0: score += 10
        if status == "active": score += 25
        else: score += 5  # draft

        metrics.append({
            "title": title,
            "price": price,
            "compare_price": compare,
            "images": images,
            "status": status,
            "tier": tier,
            "cost": total_cost if cost_info else 0,
            "profit": round(net_profit, 2),
            "margin": round(margin, 1),
            "score": score,
            "weight": weight,
            "has_description": has_description,
            "id": p["id"],
        })

    return sorted(metrics, key=lambda x: x["score"], reverse=True)


def generate_html_dashboard(metrics, orders):
    """Generate HTML dashboard"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    heroes = [m for m in metrics if m["tier"] == "HERO"]
    tests = [m for m in metrics if m["tier"] == "TEST"]
    backups = [m for m in metrics if m["tier"] == "BACKUP"]
    others = [m for m in metrics if m["tier"] == "OTHER"]

    total_products = len(metrics)
    avg_margin = sum(m["margin"] for m in metrics) / len(metrics) if metrics else 0
    avg_price = sum(m["price"] for m in metrics) / len(metrics) if metrics else 0
    total_potential = sum(m["profit"] for m in metrics)
    active_count = len([m for m in metrics if m["status"] == "active"])
    draft_count = len([m for m in metrics if m["status"] == "draft"])

    # Revenue projections
    orders_day_low = 5
    orders_day_mid = 11
    orders_day_high = 25
    avg_profit = sum(m["profit"] for m in metrics) / len(metrics) if metrics else 0
    rev_low = orders_day_low * avg_profit * 30
    rev_mid = orders_day_mid * avg_profit * 30
    rev_high = orders_day_high * avg_profit * 30

    def product_row(m):
        tier_colors = {"HERO": "#e74c3c", "TEST": "#f39c12", "BACKUP": "#3498db", "OTHER": "#95a5a6"}
        status_color = "#27ae60" if m["status"] == "active" else "#e67e22"
        score_color = "#27ae60" if m["score"] >= 80 else "#f39c12" if m["score"] >= 60 else "#e74c3c"
        return """<tr>
<td><span style="background:%s;color:white;padding:2px 8px;border-radius:4px;font-size:11px">%s</span></td>
<td style="max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">%s</td>
<td>$%.2f</td>
<td style="color:%s">$%.2f</td>
<td>%.1f%%</td>
<td>%d</td>
<td><span style="color:%s;font-weight:bold">%s</span></td>
<td><span style="background:%s;color:white;padding:2px 8px;border-radius:10px;font-size:12px">%d/100</span></td>
</tr>""" % (
            tier_colors.get(m["tier"], "#999"), m["tier"],
            m["title"][:45],
            m["price"],
            "#27ae60" if m["profit"] > 0 else "#e74c3c", m["profit"],
            m["margin"],
            m["images"],
            status_color, m["status"].upper(),
            score_color, m["score"],
        )

    rows = "\n".join([product_row(m) for m in metrics])

    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>NeatNestCo Intelligence Dashboard</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1419; color: #e1e8ed; }
.header { background: linear-gradient(135deg, #1a1a2e 0%%, #16213e 50%%, #0f3460 100%%); padding: 30px; text-align: center; }
.header h1 { font-size: 28px; margin-bottom: 5px; }
.header p { color: #8899a6; font-size: 14px; }
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
.card { background: #192734; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #253341; }
.card .value { font-size: 32px; font-weight: bold; margin: 8px 0; }
.card .label { font-size: 12px; color: #8899a6; text-transform: uppercase; letter-spacing: 1px; }
.card.green .value { color: #27ae60; }
.card.blue .value { color: #3498db; }
.card.orange .value { color: #f39c12; }
.card.red .value { color: #e74c3c; }
.card.purple .value { color: #9b59b6; }
.section { background: #192734; border-radius: 12px; padding: 20px; margin: 20px 0; border: 1px solid #253341; }
.section h2 { margin-bottom: 15px; font-size: 18px; display: flex; align-items: center; gap: 8px; }
table { width: 100%%; border-collapse: collapse; }
th { text-align: left; padding: 10px; border-bottom: 2px solid #253341; color: #8899a6; font-size: 12px; text-transform: uppercase; }
td { padding: 10px; border-bottom: 1px solid #253341; font-size: 13px; }
tr:hover { background: #1c2e3f; }
.projections { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
.proj-card { background: #1c2e3f; border-radius: 8px; padding: 15px; text-align: center; }
.proj-card .scenario { font-size: 12px; color: #8899a6; margin-bottom: 5px; }
.proj-card .amount { font-size: 24px; font-weight: bold; }
.proj-card .detail { font-size: 11px; color: #8899a6; margin-top: 5px; }
.recommendations { list-style: none; }
.recommendations li { padding: 10px; border-left: 3px solid #3498db; margin: 8px 0; background: #1c2e3f; border-radius: 0 8px 8px 0; }
.recommendations li.urgent { border-left-color: #e74c3c; }
.recommendations li.good { border-left-color: #27ae60; }
.tier-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }
.tier-card { padding: 15px; border-radius: 8px; text-align: center; }
.tier-hero { background: linear-gradient(135deg, #e74c3c22, #c0392b22); border: 1px solid #e74c3c44; }
.tier-test { background: linear-gradient(135deg, #f39c1222, #e67e2222); border: 1px solid #f39c1244; }
.tier-backup { background: linear-gradient(135deg, #3498db22, #2980b922); border: 1px solid #3498db44; }
</style>
</head>
<body>

<div class="header">
<h1>NeatNestCo Intelligence Dashboard</h1>
<p>Last updated: %s | Powered by Dropship Intelligence Bots</p>
</div>

<div class="container">

<!-- KPI Cards -->
<div class="cards">
<div class="card blue">
<div class="label">Total Products</div>
<div class="value">%d</div>
</div>
<div class="card green">
<div class="label">Avg Margin</div>
<div class="value">%.1f%%</div>
</div>
<div class="card orange">
<div class="label">Avg Price</div>
<div class="value">$%.2f</div>
</div>
<div class="card purple">
<div class="label">Avg Profit/Sale</div>
<div class="value">$%.2f</div>
</div>
<div class="card green">
<div class="label">Active</div>
<div class="value">%d</div>
</div>
<div class="card orange">
<div class="label">Draft</div>
<div class="value">%d</div>
</div>
</div>

<!-- Tier Summary -->
<div class="section">
<h2>Product Tiers</h2>
<div class="tier-summary">
<div class="tier-card tier-hero">
<div style="font-size:24px;font-weight:bold;color:#e74c3c">%d</div>
<div style="font-size:14px;margin:5px 0">HERO Products</div>
<div style="font-size:12px;color:#8899a6">Viral potential, highest priority</div>
</div>
<div class="tier-card tier-test">
<div style="font-size:24px;font-weight:bold;color:#f39c12">%d</div>
<div style="font-size:14px;margin:5px 0">TEST Products</div>
<div style="font-size:12px;color:#8899a6">Ad testing candidates</div>
</div>
<div class="tier-card tier-backup">
<div style="font-size:24px;font-weight:bold;color:#3498db">%d</div>
<div style="font-size:14px;margin:5px 0">BACKUP Products</div>
<div style="font-size:12px;color:#8899a6">Reserve inventory</div>
</div>
</div>
</div>

<!-- Revenue Projections -->
<div class="section">
<h2>Revenue Projections (Monthly)</h2>
<div class="projections">
<div class="proj-card">
<div class="scenario">Conservative</div>
<div class="amount" style="color:#f39c12">$%.0f</div>
<div class="detail">%d orders/day x $%.2f avg profit</div>
</div>
<div class="proj-card">
<div class="scenario">Target</div>
<div class="amount" style="color:#27ae60">$%.0f</div>
<div class="detail">%d orders/day x $%.2f avg profit</div>
</div>
<div class="proj-card">
<div class="scenario">Scale</div>
<div class="amount" style="color:#3498db">$%.0f</div>
<div class="detail">%d orders/day x $%.2f avg profit</div>
</div>
</div>
</div>

<!-- Product Table -->
<div class="section">
<h2>All Products Performance</h2>
<table>
<tr><th>Tier</th><th>Product</th><th>Price</th><th>Profit</th><th>Margin</th><th>Images</th><th>Status</th><th>Score</th></tr>
%s
</table>
</div>

<!-- Recommendations -->
<div class="section">
<h2>Actionable Recommendations</h2>
<ul class="recommendations">
<li class="urgent">Activate all draft products - %d products are still in draft status</li>
<li>Set up Meta Pixel and start running ads on the 3 HERO products first</li>
<li>Create Facebook/Instagram ad creatives for top 3 products with highest margins</li>
<li class="good">Product catalog is diversified across %d categories - good coverage</li>
<li>Set up abandoned cart email recovery (average 10-15%% recovery rate)</li>
<li>Install reviews app (Judge.me or Loox) - social proof increases conversion 15-25%%</li>
<li>Consider replacing lowest-margin products if they underperform after 2 weeks of ads</li>
</ul>
</div>

</div>
</body>
</html>""" % (
        now,
        total_products, avg_margin, avg_price, avg_profit, active_count, draft_count,
        len(heroes), len(tests), len(backups),
        rev_low, orders_day_low, avg_profit,
        rev_mid, orders_day_mid, avg_profit,
        rev_high, orders_day_high, avg_profit,
        rows,
        draft_count,
        len(set(m.get("tier", "") for m in metrics)),
    )

    return html


def send_telegram_summary(metrics):
    """Send dashboard summary to Telegram"""
    heroes = [m for m in metrics if m["tier"] == "HERO"]
    tests = [m for m in metrics if m["tier"] == "TEST"]
    backups = [m for m in metrics if m["tier"] == "BACKUP"]

    avg_margin = sum(m["margin"] for m in metrics) / len(metrics) if metrics else 0
    avg_profit = sum(m["profit"] for m in metrics) / len(metrics) if metrics else 0
    active = len([m for m in metrics if m["status"] == "active"])
    draft = len([m for m in metrics if m["status"] == "draft"])

    msg = "NEATNESTCO DASHBOARD\n"
    msg += "=" * 25 + "\n\n"
    msg += "Products: %d total\n" % len(metrics)
    msg += "Tiers: %d HERO | %d TEST | %d BACKUP\n" % (len(heroes), len(tests), len(backups))
    msg += "Status: %d active | %d draft\n\n" % (active, draft)
    msg += "Avg Margin: %.1f%%\n" % avg_margin
    msg += "Avg Profit/Sale: $%.2f\n\n" % avg_profit
    msg += "Revenue Targets:\n"
    msg += "  5/day = $%.0f/mo\n" % (5 * avg_profit * 30)
    msg += "  11/day = $%.0f/mo\n" % (11 * avg_profit * 30)
    msg += "  25/day = $%.0f/mo\n\n" % (25 * avg_profit * 30)
    msg += "Top 3 by margin:\n"
    top3 = sorted(metrics, key=lambda x: x["margin"], reverse=True)[:3]
    for m in top3:
        msg += "  %s: %.1f%% ($%.2f profit)\n" % (m["title"][:30], m["margin"], m["profit"])

    try:
        requests.post(
            "https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN,
            json={"chat_id": TG_CHAT, "text": msg},
        )
        print("Telegram summary sent!")
    except:
        pass


def main():
    print("=" * 60)
    print("NEATNESTCO INTELLIGENCE DASHBOARD")
    print("=" * 60)

    print("\nFetching Shopify data...")
    products = get_shopify_products()
    orders = get_shopify_orders()
    print("Found %d products, %d orders" % (len(products), len(orders)))

    print("\nCalculating metrics...")
    metrics = calculate_metrics(products)

    for m in metrics:
        print("  [%s] %s | $%.2f | %.1f%% margin | %d imgs | %s | Score: %d" % (
            m["tier"], m["title"][:35], m["price"], m["margin"], m["images"], m["status"], m["score"]
        ))

    print("\nGenerating HTML dashboard...")
    html = generate_html_dashboard(metrics, orders)

    dashboard_path = os.path.join(DATA_DIR, "dashboard.html")
    with open(dashboard_path, "w") as f:
        f.write(html)
    print("Dashboard saved to: %s" % dashboard_path)

    # Save metrics JSON
    with open(os.path.join(DATA_DIR, "dashboard_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print("\nSending Telegram summary...")
    send_telegram_summary(metrics)

    print("\nDone!")


if __name__ == "__main__":
    main()
