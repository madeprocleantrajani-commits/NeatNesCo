"""
Daily Intelligence Report Generator v4
----------------------------------------
Dense, structured, data-rich reports powered by 7 data sources.

v4 changes:
  - Data quality scores per source (completeness indicator)
  - Real profit breakdown in candidate section
  - Risk warnings (brand, saturation, low margin)
  - Emerging products from trend regression
  - eBay competition level + daily velocity
  - Supplier scoring in AliExpress section
  - Confidence indicators on cross-references
  - Sparkline trend visualization

Outputs:
  - reports/daily_YYYY-MM-DD.txt   (plain text for logs/terminal)
  - reports/daily_YYYY-MM-DD.html  (styled HTML for Telegram)
  - data/analysis_YYYY-MM-DD.json
  - Telegram: summary message + HTML report document
"""

import json
from datetime import datetime

from config import DATA_DIR, REPORTS_DIR, get_logger
from alert_bot import send_alert, send_document
from intelligence import DropshipIntelligence
from validators import calculate_real_profit
from html_report import generate_html_report

log = get_logger("report_generator")


def bar(value: float, max_val: float = 100, width: int = 10) -> str:
    if max_val <= 0:
        return "░" * width
    filled = min(int(value / max_val * width), width)
    return "█" * filled + "░" * (width - filled)


def fp(price, currency="$") -> str:
    """Format price."""
    if price is None:
        return "  N/A  "
    return f"{currency}{price:.2f}"


def t(text: str, length: int) -> str:
    """Truncate."""
    if not text:
        return ""
    return text if len(text) <= length else text[: length - 1] + "…"


def _quality_score(sources: dict) -> dict:
    """Calculate data quality score for each source."""
    quality = {}
    for name, info in sources.items():
        if not info.get("active"):
            quality[name] = {"score": 0, "label": "offline", "icon": "✗"}
            continue

        # Simple heuristic: active = at least 50 quality
        score = 50
        if name == "amazon":
            products = info.get("products", 0)
            if products >= 100:
                score = 95
            elif products >= 50:
                score = 80
            elif products > 0:
                score = 60
        elif name == "ebay":
            sold = info.get("total_sold", 0)
            if sold >= 200:
                score = 95
            elif sold >= 50:
                score = 75
            elif sold > 0:
                score = 55
        elif name == "trends":
            hot = info.get("hot_products", 0)
            score = min(95, 50 + hot * 5)
        elif name == "aliexpress":
            products = info.get("products", 0)
            if products >= 50:
                score = 90
            elif products >= 20:
                score = 70
            elif products > 0:
                score = 55
        elif name == "competitors":
            stores = info.get("stores", 0)
            score = min(90, 50 + stores * 10)
        elif name == "demand":
            suggestions = info.get("suggestions", 0)
            score = min(90, 50 + suggestions // 5)
        elif name == "prices":
            tracked = info.get("tracked", 0)
            score = min(90, 50 + tracked * 5)

        if score >= 80:
            label, icon = "excellent", "★"
        elif score >= 60:
            label, icon = "good", "●"
        else:
            label, icon = "partial", "◐"

        quality[name] = {"score": score, "label": label, "icon": icon}

    return quality


# ── Sections ──────────────────────────────────────────────


def section_header(today: str) -> list[str]:
    return [
        "",
        "╔" + "═" * 58 + "╗",
        "║" + " DROPSHIP INTELLIGENCE REPORT ".center(58) + "║",
        "║" + f" {today} ".center(58) + "║",
        "║" + " Signal Pilot v4 ".center(58) + "║",
        "╚" + "═" * 58 + "╝",
        "",
    ]


def section_sources(sources: dict) -> list[str]:
    active = sum(1 for s in sources.values() if s.get("active"))
    total = len(sources)
    quality = _quality_score(sources)

    lines = ["─" * 60, f"  DATA SOURCES ({active}/{total} active)", "─" * 60, ""]

    defs = [
        ("amazon", "Amazon BSR",
         f"{sources['amazon']['products']} products, "
         f"{sources['amazon']['movers']} movers"),
        ("demand", "Amazon Demand",
         f"{sources['demand']['suggestions']} suggestions, "
         f"{sources['demand']['discoveries']} discoveries"),
        ("ebay", "eBay Sold",
         f"{sources['ebay']['total_sold']} sold items, "
         f"{sources['ebay']['keywords_with_sales']} keywords"),
        ("trends", "Google Trends",
         f"{sources['trends']['hot_products']} hot, "
         f"{sources['trends']['discoveries']} discoveries"),
        ("aliexpress", "AliExpress",
         f"{sources['aliexpress']['products']} products"),
        ("competitors", "Competitors",
         f"{sources['competitors']['stores']} stores"),
        ("prices", "Price Monitor",
         f"{sources['prices']['tracked']} tracked"),
    ]

    for key, name, detail in defs:
        status_icon = "✓" if sources[key]["active"] else "✗"
        q = quality.get(key, {})
        q_icon = q.get("icon", "?")
        q_label = q.get("label", "?")
        lines.append(f"  {status_icon} {name:<18} {detail:<36} {q_icon} {q_label}")

    lines.append("")
    return lines


def section_cross_refs(cross_refs: list) -> list[str]:
    if not cross_refs:
        return [
            "─" * 60,
            "  CROSS-SOURCE MATCHES — None found",
            "  Products must appear in 2+ data sources to qualify.",
            "",
        ]

    lines = [
        "─" * 60,
        f"  CROSS-SOURCE MATCHES ({len(cross_refs)} multi-signal products)",
        "─" * 60,
        "",
    ]

    for i, ref in enumerate(cross_refs[:15], 1):
        signals = " + ".join(ref["signals"])
        brand_tag = " [BRAND]" if ref.get("is_brand") else ""
        confidence = ref.get("signal_count", 1)
        conf_bar = "●" * min(confidence, 6) + "○" * max(0, 6 - confidence)

        lines.append(f"  #{i:<2} [{confidence} signals {conf_bar}]  {t(ref['title'], 40)}{brand_tag}")
        lines.append(f"      Signals: {signals}")

        details = []
        if ref.get("amazon_rank"):
            details.append(
                f"Amazon #{ref['amazon_rank']} {ref.get('amazon_category', '')}  "
                f"{fp(ref.get('amazon_price_usd'))}"
            )
        if ref.get("ebay_sold"):
            comp = ref.get("ebay_competition", "unknown")
            details.append(
                f"eBay: {ref['ebay_sold']} sold  "
                f"avg {fp(ref.get('ebay_avg_price'))}  competition: {comp}"
            )
        if ref.get("source_price"):
            viable = "✓ VIABLE" if ref.get("profit_viable") else "✗ LOW"
            details.append(
                f"Source: {fp(ref['source_price'])}  "
                f"Profit: {fp(ref.get('real_profit'))} ({ref.get('margin_pct', '?')}%)  {viable}"
            )
        if ref.get("trend_interest"):
            details.append(f"Trend: {ref['trend_interest']}/100")

        # Risk warnings
        risks = []
        if ref.get("is_brand"):
            risks.append("BRAND-GATED")
        if ref.get("review_count") and ref["review_count"] > 5000:
            risks.append("SATURATED")
        if ref.get("margin_pct") and ref["margin_pct"] < 15:
            risks.append("LOW-MARGIN")
        if risks:
            details.append(f"⚠ RISK: {', '.join(risks)}")

        for d in details:
            lines.append(f"      {d}")
        lines.append("")

    return lines


def section_amazon(amazon: dict) -> list[str]:
    if amazon.get("status") == "no_data":
        return ["─" * 60, "  AMAZON — No data", ""]

    lines = ["─" * 60, "  AMAZON BEST SELLERS (physical products only)", "─" * 60, ""]

    # Price distribution (USD)
    dist = amazon.get("price_distribution", {})
    if dist:
        total = dist.get("total", 0)
        lines.append(f"  Price Distribution ({total} products, USD):")
        for label, key in [("<$10", "under_10"), ("$10-25", "10_to_25"),
                           ("$25-50", "25_to_50"), ("$50-100", "50_to_100"),
                           (">$100", "over_100")]:
            count = dist.get(key, 0)
            pct = round(count / total * 100) if total else 0
            lines.append(f"    {label:<8} {count:>3}  {bar(count, total, 20)}  {pct}%")
        lines.append(f"    Avg: {fp(dist.get('avg'))}  |  Median: {fp(dist.get('median'))}")
        lines.append("")

    # Category breakdown
    for cat_name, cat in amazon.get("categories", {}).items():
        display = cat_name.upper().replace("-", " & ").replace("_", " ")
        pr = cat.get("price_range", {})

        lines.append(f"  ┌─ {display} ({cat['total']} products)")
        lines.append(
            f"  │  Avg: {fp(cat.get('avg_price'))}  │  "
            f"Range: {fp(pr.get('min'))}–{fp(pr.get('max'))}  │  "
            f"Rating: {cat.get('avg_rating', 0):.1f}/5"
        )
        lines.append("  │")

        for p in cat.get("top_5", []):
            rank_arrow = ""
            if p.get("rank_direction") == "up":
                rank_arrow = f" ↑{p.get('rank_change', '')}"
            elif p.get("rank_direction") == "down":
                rank_arrow = f" ↓{abs(p.get('rank_change', 0))}"
            elif p.get("rank_direction") == "new":
                rank_arrow = " NEW"

            brand = " [B]" if p.get("is_brand") else ""
            rating_s = f"★{p['rating']:.1f}" if p.get("rating") else " —  "
            reviews = f"({p['review_count']:,})" if p.get("review_count") else ""

            lines.append(
                f"  │  #{p['rank']:<3}{rank_arrow:<6} {t(p['title'], 35)}{brand}  "
                f"{fp(p.get('price_usd')):>8}  {rating_s} {reviews}"
            )

        lines.append("  └─")
        lines.append("")

    # Rising products (BSR improved)
    rising = amazon.get("rising_products", [])
    if rising:
        lines.append(f"  BSR RISING ({len(rising)} products climbing in rank):")
        for p in rising[:10]:
            lines.append(
                f"    ↑{p.get('rank_change', '?'):>3} ranks  "
                f"#{p.get('rank_yesterday', '?')}→#{p['rank']}  "
                f"{t(p['title'], 38)}  {fp(p.get('price_usd'))}"
            )
        lines.append("")

    # Movers
    movers = amazon.get("movers", [])
    if movers:
        lines.append(f"  MOVERS & SHAKERS ({len(movers)} trending):")
        for m in movers[:15]:
            brand = " [B]" if m.get("is_brand") else ""
            cat = m.get("category", "?")[:12]
            lines.append(
                f"    ↑ [{cat:<12}]  {t(m['title'], 40)}{brand}  {fp(m.get('price_usd'))}"
            )
        lines.append("")

    # Dropship candidates with REAL profit
    candidates = amazon.get("dropship_candidates", [])
    if candidates:
        lines.append(f"  DROPSHIP CANDIDATES ({len(candidates)} found  │  ${15}-${80} + ★4.0+ + non-brand)")
        lines.append("")
        lines.append(f"    {'SCORE':<8} {'#':>3}  {'PRODUCT':<30}  {'PRICE':>7}  {'★':>4}  {'REVIEWS':>7}  {'RISK'}")
        lines.append("    " + "─" * 80)
        for c in candidates[:20]:
            score_b = bar(c.get("dropship_score", 0), 100, 5)
            score_n = c.get("dropship_score", 0)
            rating_s = f"{c['rating']:.1f}" if c.get("rating") else " — "
            reviews = f"{c['review_count']:,}" if c.get("review_count") else "—"

            # Risk indicators
            risks = c.get("skip_reasons", [])
            risk_str = ", ".join(r.replace("_", " ") for r in risks) if risks else "—"

            lines.append(
                f"    {score_b}{score_n:>3}  "
                f"#{c.get('rank', '?'):<3} {t(c['title'], 30)}  "
                f"{fp(c.get('price_usd')):>7}  {rating_s:>4}  {reviews:>7}  {risk_str}"
            )

            # Show confidence sources if available
            if c.get("confidence_sources", 0) > 1:
                lines.append(f"          └ {c['confidence_sources']} confirming sources")

        lines.append("")

    return lines


def section_demand(demand: dict) -> list[str]:
    if demand.get("status") == "no_data":
        return ["─" * 60, "  AMAZON DEMAND — No data (run amazon_demand.py)", ""]

    lines = [
        "─" * 60,
        "  AMAZON DEMAND (what buyers are searching for)",
        "─" * 60,
        "",
        f"  Keywords scanned: {demand.get('keywords_scanned', 0)}  │  "
        f"Suggestions: {demand.get('total_suggestions', 0)}  │  "
        f"New ideas: {demand.get('new_discoveries', 0)}",
        "",
    ]

    # Top discoveries
    discoveries = demand.get("top_discoveries", [])
    if discoveries:
        lines.append(f"  NEW PRODUCT IDEAS ({len(discoveries)} discovered):")
        for d in discoveries[:15]:
            lines.append(
                f"    • {d.get('suggestion', '?')}"
                f"  (from: {d.get('source_keyword', '?')})"
            )
        lines.append("")

    # Per-keyword breakdown
    for kw, data in demand.get("keywords", {}).items():
        total = data.get("total_ideas", 0)
        if total > 0:
            top = data.get("top_suggestions", [])
            lines.append(f"  {kw}: {total} ideas")
            for s in top[:3]:
                lines.append(f"    → {s}")
        lines.append("")

    return lines


def section_ebay(ebay: dict) -> list[str]:
    if ebay.get("status") == "no_data":
        return ["─" * 60, "  EBAY SOLD LISTINGS — No data (run ebay_scanner.py)", ""]

    lines = [
        "─" * 60,
        "  EBAY SOLD LISTINGS (real transaction validation)",
        "─" * 60,
        "",
        f"  Total sold items found: {ebay.get('total_sold', 0)}  │  "
        f"Keywords with sales: {ebay.get('keywords_with_sales', 0)}/{ebay.get('keywords_scanned', 0)}",
        "",
    ]

    # Top sellers with competition level and velocity
    top_sellers = ebay.get("top_sellers", [])
    if top_sellers:
        lines.append("  MOST SOLD (by keyword):")
        lines.append(f"    {'KEYWORD':<24}  {'SOLD':>6}  {'AVG':>8}  {'MED':>8}  {'COMP':<8}  {'VEL'}")
        lines.append("    " + "─" * 68)
        for ts in top_sellers[:12]:
            # Get extra data from results if available
            results = ebay.get("results", {})
            kw_data = results.get(ts.get("keyword", ""), {})
            comp = kw_data.get("competition", "?")
            vel = kw_data.get("daily_velocity", 0)

            vel_str = f"{vel:.1f}/day" if vel else "—"
            lines.append(
                f"    {t(ts['keyword'], 24):<24}  "
                f"{ts.get('sold_count', 0):>6}  "
                f"{fp(ts.get('avg_price')):>8}  "
                f"{fp(ts.get('median_price')):>8}  "
                f"{comp:<8}  "
                f"{vel_str}"
            )
        lines.append("")

    # Price insights
    insights = ebay.get("price_insights", [])
    if insights:
        lines.append("  PRICE INSIGHTS (avg sold >= $15, validated demand):")
        for pi in insights[:8]:
            lines.append(
                f"    {t(pi['keyword'], 25):<25}  "
                f"{pi.get('sold_count', 0)} sold  "
                f"avg {fp(pi.get('avg_sold_price'))}  "
                f"range {pi.get('price_range', 'N/A')}"
            )
        lines.append("")

    return lines


def section_trends(trends: dict) -> list[str]:
    if trends.get("status") == "no_data":
        return [
            "─" * 60, "  GOOGLE TRENDS — No data",
            "  ⚠ Rate-limited. Add PROXY_URL to .env", "",
        ]

    lines = ["─" * 60, "  GOOGLE TRENDS", "─" * 60, ""]

    hot = trends.get("hot_products", [])
    if hot:
        lines.append(f"  HOT ({len(hot)} rising):")
        for p in hot:
            trend_dir = p.get("trend", "unknown")
            dir_icon = {"rising_fast": "⬆⬆", "rising": "⬆", "stable": "→",
                        "falling": "⬇", "falling_fast": "⬇⬇"}.get(trend_dir, "?")
            lines.append(
                f"    {bar(p.get('current_interest', 0), 100, 8)}  "
                f"{p['keyword']}  ({p.get('current_interest', 0)}/100)  {dir_icon}"
            )
        lines.append("")

    # Emerging products (new in v4)
    emerging = trends.get("emerging_products", [])
    if emerging:
        lines.append(f"  🌱 EMERGING ({len(emerging)} low-interest + steep growth):")
        for e in emerging:
            lines.append(
                f"    {e['keyword']}  interest: {e.get('current_interest', 0)}/100  "
                f"slope: {e.get('slope', 0):.2f}  accel: {e.get('acceleration', 0):.2f}"
            )
        lines.append("")

    disc = trends.get("discoveries", [])
    if disc:
        lines.append(f"  BREAKOUT QUERIES ({len(disc)}):")
        for d in disc:
            lines.append(f"    ▲ \"{d['query']}\" +{d.get('growth', 0)}%  from: {d.get('source_keyword', '?')}")
        lines.append("")

    return lines


def section_aliexpress(aliexpress: dict) -> list[str]:
    if aliexpress.get("status") == "no_data":
        return [
            "─" * 60, "  ALIEXPRESS — No data",
            "  ⚠ IP blocked. Add PROXY_URL to .env", "",
        ]
    total = aliexpress.get("total_products", 0)
    if total == 0:
        return ["─" * 60, f"  ALIEXPRESS — 0 products returned", "  ⚠ Blocked", ""]

    lines = ["─" * 60, "  ALIEXPRESS SOURCING", "─" * 60, ""]

    deals = aliexpress.get("best_deals", [])
    if deals:
        lines.append("  BEST DEALS (real profit after ALL costs):")
        lines.append(f"    {'SOURCE':>8}  {'RETAIL':>8}  {'PROFIT':>8}  {'MARGIN':>7}  {'ORDERS':>8}  PRODUCT")
        lines.append("    " + "─" * 72)
        for d in deals[:10]:
            source_p = d.get("source_price") or d.get("price_usd", 0)
            retail_p = d.get("retail_price") or d.get("potential_retail") or (source_p * 2.5 if source_p else 0)
            shipping = d.get("shipping_cost", 0)

            profit_info = calculate_real_profit(source_p, retail_p, shipping)
            profit = profit_info.get("profit", 0)
            margin = profit_info.get("margin_pct", 0)
            viable = "✓" if profit_info.get("viable") else "✗"

            orders = d.get("orders", "N/A")
            title = t(d.get("title", "?"), 40)

            lines.append(
                f"    {fp(source_p):>8}  {fp(retail_p):>8}  "
                f"{fp(profit):>8}  {margin:>5.1f}% {viable}  "
                f"{orders:>8}  {title}"
            )

        lines.append("")
        lines.append("    Cost breakdown: source + shipping + platform 15% + ads 30%")
        lines.append("")

    return lines


def section_competitors(competitors: dict) -> list[str]:
    if competitors.get("status") == "no_data":
        return [
            "─" * 60, "  COMPETITORS — None discovered yet",
            "  Configure COMPETITOR_STORES in config.py", "",
        ]

    stores = competitors.get("stores", {})
    lines = ["─" * 60, f"  COMPETITORS ({len(stores)} stores discovered)", "─" * 60, ""]

    for domain, info in list(stores.items())[:10]:
        products = info.get("product_count", info.get("total_products", 0))
        avg = info.get("avg_price", 0)
        pr = info.get("price_range", "N/A")
        via = info.get("found_via", "")

        lines.append(f"  ┌─ {domain}")
        lines.append(f"  │  Products: {products}  │  Avg: {fp(avg)}  │  Range: {pr}")
        if via:
            lines.append(f"  │  Found via: \"{via}\"")

        # Sample products
        samples = info.get("sample_titles", [])
        if samples:
            for s in samples[:3]:
                lines.append(f"  │    • {t(s, 50)}")

        lines.append("  └─")
        lines.append("")

    return lines


def section_niche_matrix(niche_scores: dict) -> list[str]:
    if not niche_scores:
        return []

    lines = [
        "─" * 60,
        "  NICHE ANALYSIS MATRIX",
        "─" * 60,
        "",
        f"  {'NICHE':<18}  {'TREND':>6}  {'DEMAND':>6}  "
        f"{'SOURCE':>6}  {'VALID':>6}  {'TOTAL':>6}  GR",
        "  " + "─" * 56,
    ]

    sorted_n = sorted(niche_scores.values(), key=lambda x: x["total"], reverse=True)
    for ns in sorted_n:
        name = ns["name"].replace("_", " ")[:16]
        lines.append(
            f"  {name:<18}  "
            f"{bar(ns['trend_score'], 25, 5):>6}  "
            f"{bar(ns['demand_score'], 25, 5):>6}  "
            f"{bar(ns['source_score'], 25, 5):>6}  "
            f"{bar(ns['validation_score'], 25, 5):>6}  "
            f"{ns['total']:>4}/100  {ns['grade']}"
        )

    lines.append("")

    # Grade legend
    lines.append("  Grades: A(75+)=Strong opportunity  B(60+)=Good  C(40+)=Moderate  D(20+)=Weak  F=Poor")
    lines.append("")

    return lines


def section_actions(analysis: dict) -> list[str]:
    lines = ["─" * 60, "  ACTION ITEMS", "─" * 60, ""]

    sources = analysis.get("sources", {})
    amazon = analysis.get("amazon", {})
    ebay = analysis.get("ebay", {})
    demand = analysis.get("demand", {})
    cross_refs = analysis.get("cross_references", [])

    high, monitor, fix = [], [], []

    # High priority
    candidates = amazon.get("dropship_candidates", [])
    if candidates:
        top = candidates[0]
        high.append(
            f"Research top candidate: \"{t(top['title'], 35)}\" "
            f"(Score: {top.get('dropship_score', 0)}/100, {fp(top.get('price_usd'))})"
        )
    if len(candidates) > 5:
        high.append(f"Review all {len(candidates)} candidates above")

    if cross_refs:
        viable_refs = [r for r in cross_refs if r.get("profit_viable")]
        if viable_refs:
            high.append(f"Act on {len(viable_refs)} PROFIT-VIABLE multi-signal products")
        else:
            high.append(f"Deep-dive {len(cross_refs)} multi-signal products")

    if ebay.get("top_sellers"):
        top_ebay = ebay["top_sellers"][0]
        high.append(
            f"eBay validates \"{top_ebay['keyword']}\" — "
            f"{top_ebay.get('sold_count', 0)} sold at avg {fp(top_ebay.get('avg_price'))}"
        )

    if demand.get("top_discoveries"):
        count = len(demand["top_discoveries"])
        high.append(f"Explore {count} new product ideas from Amazon autocomplete")

    # Monitor
    movers = amazon.get("movers", [])
    if movers:
        monitor.append(f"Track {len(movers)} Amazon movers")
    rising = amazon.get("rising_products", [])
    if rising:
        monitor.append(f"Watch {len(rising)} products climbing BSR")

    # Fix
    for key, name, hint in [
        ("trends", "Google Trends", "Add PROXY_URL to .env"),
        ("aliexpress", "AliExpress", "Add PROXY_URL to .env"),
        ("demand", "Amazon Demand", "Run: python amazon_demand.py"),
        ("ebay", "eBay Sold", "Run: python ebay_scanner.py"),
        ("competitors", "Competitors", "Add stores to COMPETITOR_STORES"),
    ]:
        if not sources.get(key, {}).get("active"):
            fix.append(f"{name} inactive — {hint}")

    if high:
        lines.append("  🔴 HIGH PRIORITY:")
        for i, a in enumerate(high, 1):
            lines.append(f"    {i}. {a}")
        lines.append("")
    if monitor:
        lines.append("  🟡 MONITOR:")
        for a in monitor:
            lines.append(f"    • {a}")
        lines.append("")
    if fix:
        lines.append("  ⚠ FIX:")
        for a in fix:
            lines.append(f"    ⚠ {a}")
        lines.append("")

    return lines


# ── Telegram Summary ──────────────────────────────────────


def telegram_summary(analysis: dict, today: str) -> str:
    sources = analysis.get("sources", {})
    amazon = analysis.get("amazon", {})
    ebay_data = analysis.get("ebay", {})
    demand_data = analysis.get("demand", {})
    cross_refs = analysis.get("cross_references", [])
    niche_scores = analysis.get("niche_scores", {})
    active = sum(1 for s in sources.values() if s.get("active"))
    total = len(sources)

    lines = [
        f"🧠 <b>DROPSHIP INTELLIGENCE REPORT</b>",
        f"📅 {today}  |  Signal Pilot v4",
        f"📡 Burime aktive: <b>{active}/{total}</b>",
        "",
    ]

    # === TOP CANDIDATES ===
    candidates = amazon.get("dropship_candidates", [])
    if candidates:
        lines.append(f"🎯 <b>TOP KANDIDATE DROPSHIP</b> ({len(candidates)} gjetur):")
        for c in candidates[:5]:
            score = c.get('dropship_score', 0)
            score_bar = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
            price = fp(c.get('price_usd'))
            conf = c.get('confidence_sources', 1)
            lines.append(f"  {score_bar} <b>{t(c['title'], 35)}</b>")
            lines.append(f"     Score: {score}/100 | Cmimi: {price} | {conf} burime")
        lines.append("")

    # === CROSS-SOURCE (Multi-signal) with profit viability ===
    if cross_refs:
        viable = [r for r in cross_refs if r.get("profit_viable")]
        lines.append(f"🔗 <b>MULTI-SIGNAL</b> ({len(cross_refs)} produkte, {len(viable)} me fitim te mjaftueshem):")
        for ref in cross_refs[:4]:
            signals = " + ".join(ref["signals"])
            viable_icon = "✅" if ref.get("profit_viable") else "⚠️"
            lines.append(f"  {viable_icon} <b>{t(ref['title'], 35)}</b>")
            lines.append(f"     {ref['signal_count']} sinjale: <i>{signals}</i>")
            if ref.get("real_profit"):
                lines.append(f"     Fitim real: {fp(ref['real_profit'])} ({ref.get('margin_pct', 0)}%)")
        lines.append("")

    # === EBAY VALIDATED ===
    if ebay_data.get("top_sellers"):
        lines.append(f"✅ <b>VALIDUAR NE EBAY:</b>")
        for ts in ebay_data["top_sellers"][:4]:
            lines.append(
                f"  • <b>{ts['keyword']}</b> — {ts['sold_count']} shitje | avg {fp(ts.get('avg_price'))}"
            )
        lines.append("")

    # === NEW IDEAS ===
    if demand_data.get("top_discoveries"):
        count = len(demand_data["top_discoveries"])
        lines.append(f"💡 <b>IDE TE REJA:</b> {count} nga Amazon autocomplete")
        for d in demand_data["top_discoveries"][:4]:
            lines.append(f"  → <i>{d.get('suggestion', '?')}</i>")
        lines.append("")

    # === NICHE MATRIX ===
    if niche_scores:
        sorted_n = sorted(niche_scores.values(), key=lambda x: x["total"], reverse=True)
        lines.append(f"📊 <b>NICHES (renditur nga me te mire):</b>")
        grade_emoji = {"A": "🏆", "B": "🥈", "C": "🥉", "D": "⚠️", "F": "❌"}
        for ns in sorted_n:
            grade = ns['grade']
            emoji = grade_emoji.get(grade[0], "📌")
            name = ns['name'].replace('_', ' ').title()
            lines.append(f"  {emoji} <b>{name}</b> — {ns['total']}/100 ({grade})")
        lines.append("")

    lines.append("📎 <i>Raporti i plote eshte bashkangjitur.</i>")
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────


def generate_daily_report() -> str:
    log.info("Generating daily intelligence report...")
    today = datetime.now().strftime("%Y-%m-%d")

    intel = DropshipIntelligence()
    analysis = intel.run_full_analysis()

    report_lines = []
    report_lines.extend(section_header(today))
    report_lines.extend(section_sources(analysis["sources"]))
    report_lines.extend(section_cross_refs(analysis["cross_references"]))
    report_lines.extend(section_amazon(analysis["amazon"]))
    report_lines.extend(section_ebay(analysis.get("ebay", {})))
    report_lines.extend(section_demand(analysis.get("demand", {})))
    report_lines.extend(section_trends(analysis["trends"]))
    report_lines.extend(section_aliexpress(analysis["aliexpress"]))
    report_lines.extend(section_competitors(analysis["competitors"]))
    report_lines.extend(section_niche_matrix(analysis["niche_scores"]))
    report_lines.extend(section_actions(analysis))

    report_lines.append("─" * 60)
    report_lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("  Signal Pilot — Dropship Intelligence Engine v4")
    report_lines.append("  Cost model: source + shipping + platform 15% + ads 30%")
    report_lines.append("")

    full_report = "\n".join(report_lines)

    # ── Save plain text (for logs/terminal) ──
    report_file = REPORTS_DIR / f"daily_{today}.txt"
    with open(report_file, "w") as f:
        f.write(full_report)
    log.info(f"TXT report saved: {report_file}")

    # ── Generate bilingual HTML reports (EN + SQ) ──
    html_files = {}
    for lang, label in [("en", "English"), ("sq", "Shqip")]:
        html_content = generate_html_report(analysis, today, lang=lang)
        html_file = REPORTS_DIR / f"daily_{today}_{lang}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        html_files[lang] = html_file
        log.info(f"HTML report saved: {html_file} ({label})")

    # ── Save raw analysis JSON ──
    analysis_file = DATA_DIR / f"analysis_{today}.json"
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, indent=2, default=str)

    # ── Send to Telegram: summary + both HTML documents ──
    summary = telegram_summary(analysis, today)
    send_alert(summary, parse_mode="HTML")
    send_document(str(html_files["en"]), caption=f"📊 Intelligence Report {today} — ENGLISH — open in browser")
    send_document(str(html_files["sq"]), caption=f"📊 Raporti i Inteligjences {today} — SHQIP — hape ne browser")

    log.info("Reports sent to Telegram (EN + SQ)")
    return full_report


if __name__ == "__main__":
    report = generate_daily_report()
    print(report)
