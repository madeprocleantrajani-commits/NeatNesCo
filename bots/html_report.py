"""
HTML Intelligence Report Generator (Bilingual: EN + SQ)
---------------------------------------------------------
Generates visually rich, dark-themed HTML reports for Telegram delivery.
Opens beautifully in any browser — phone or desktop.

Usage:
  generate_html_report(analysis, today, lang="en")  # English
  generate_html_report(analysis, today, lang="sq")  # Albanian

Called by report_generator.py → sends both as Telegram documents.
"""

from datetime import datetime
from validators import calculate_real_profit


# ── Translations ─────────────────────────────────────────────

T = {
    # Header
    "title":           {"en": "DROPSHIP INTELLIGENCE REPORT", "sq": "RAPORTI I INTELIGJENCES DROPSHIP"},
    "sources_label":   {"en": "Sources", "sq": "Burime"},
    "candidates_label":{"en": "Candidates", "sq": "Kandidate"},
    "active":          {"en": "active", "sq": "aktive"},

    # Sources
    "data_sources":    {"en": "Data Sources", "sq": "Burimet e te Dhenave"},
    "products":        {"en": "products", "sq": "produkte"},
    "suggestions":     {"en": "suggestions", "sq": "sugjerime"},
    "sold":            {"en": "sold", "sq": "te shitura"},
    "stores":          {"en": "stores", "sq": "dyqane"},
    "tracked":         {"en": "tracked", "sq": "gjurmuar"},
    "not_active":      {"en": "not active", "sq": "jo aktiv"},

    # Cross refs
    "multi_signal":    {"en": "Multi-Signal Matches", "sq": "Multi-Signal Matches"},
    "no_multi":        {"en": "No products found in 2+ sources.", "sq": "Asnje produkt nuk u gjet ne 2+ burime."},
    "product":         {"en": "Product", "sq": "Produkti"},
    "signals":         {"en": "Signals", "sq": "Sinjale"},
    "details":         {"en": "Details", "sq": "Detaje"},
    "profit_word":     {"en": "Profit", "sq": "Fitim"},

    # Amazon
    "amazon_bs":       {"en": "Amazon Best Sellers", "sq": "Amazon Best Sellers"},
    "no_data":         {"en": "No data.", "sq": "Ska te dhena."},
    "price_dist":      {"en": "Price Distribution (USD)", "sq": "Shperndarja e Cmimeve (USD)"},
    "range":           {"en": "Range", "sq": "Gama"},
    "count":           {"en": "Count", "sq": "Sasia"},
    "chart":           {"en": "Chart", "sq": "Grafik"},
    "avg":             {"en": "Avg", "sq": "Mesatare"},
    "median":          {"en": "Median", "sq": "Mediane"},
    "price":           {"en": "Price", "sq": "Cmimi"},
    "reviews":         {"en": "Reviews", "sq": "Reviews"},
    "trend":           {"en": "Trend", "sq": "Trend"},
    "dropship_cand":   {"en": "Dropship Candidates", "sq": "Kandidate Dropship"},
    "found":           {"en": "found", "sq": "gjetur"},
    "filters":         {"en": "Filters: $15–$80 | ★4.0+ | Non-brand | Dropship-friendly price",
                        "sq": "Filtrat: $15–$80 | ★4.0+ | Jo brand | Cmim i mire per dropship"},
    "bsr_rising":      {"en": "BSR Rising", "sq": "BSR Rising"},
    "climbing":        {"en": "climbing", "sq": "ne rritje"},
    "change":          {"en": "Change", "sq": "Ndryshimi"},

    # eBay
    "ebay_sold":       {"en": "eBay Sold Listings (real demand validation)", "sq": "eBay Sold Listings (validim real i kerkeses)"},
    "ebay_no_data":    {"en": "No data. Add PROXY_URL to .env", "sq": "Ska te dhena. Shto PROXY_URL ne .env"},
    "total":           {"en": "Total", "sq": "Gjithsej"},
    "keywords_sales":  {"en": "Keywords with sales", "sq": "Keywords me shitje"},
    "most_sold":       {"en": "Most Sold (by keyword)", "sq": "Me te Shiturat (sipas keyword)"},
    "sales":           {"en": "Sales", "sq": "Shitjet"},
    "competition":     {"en": "Competition", "sq": "Konkurenca"},
    "vel":             {"en": "Vel", "sq": "Vel"},
    "validated_prices":{"en": "Validated Prices (avg ≥ $15)", "sq": "Cmime te Validuara (avg ≥ $15)"},

    # Demand
    "amazon_demand":   {"en": "Amazon Demand (what buyers search for)", "sq": "Amazon Demand (cfare kerkojne bleresit)"},
    "keywords":        {"en": "Keywords", "sq": "Keywords"},
    "discoveries":     {"en": "Discoveries", "sq": "Zbulime te reja"},
    "new_ideas":       {"en": "New Ideas", "sq": "Ide te Reja"},
    "suggestion":      {"en": "Suggestion", "sq": "Sugjerimi"},
    "source":          {"en": "Source", "sq": "Burimi"},

    # Trends
    "google_trends":   {"en": "Google Trends", "sq": "Google Trends"},
    "trends_no_data":  {"en": "No data. Add PROXY_URL to .env", "sq": "Ska te dhena. Shto PROXY_URL ne .env"},
    "hot":             {"en": "Hot", "sq": "Hot"},
    "rising":          {"en": "rising", "sq": "ne rritje"},
    "interest":        {"en": "Interest", "sq": "Interesi"},
    "direction":       {"en": "Direction", "sq": "Drejtimi"},
    "emerging":        {"en": "Emerging", "sq": "Emerging"},
    "emerging_desc":   {"en": "new with fast growth", "sq": "te reja me rritje te shpejte"},
    "breakout":        {"en": "Breakout Queries", "sq": "Breakout Queries"},
    "growth":          {"en": "Growth", "sq": "Rritje"},
    "from":            {"en": "From", "sq": "Nga"},

    # AliExpress
    "ali_sourcing":    {"en": "AliExpress Sourcing", "sq": "AliExpress Sourcing"},
    "ali_no_data":     {"en": "No data. Add PROXY_URL to .env", "sq": "Ska te dhena. Shto PROXY_URL ne .env"},
    "ali_blocked":     {"en": "0 products — blocked.", "sq": "0 produkte — i bllokuar."},
    "best_deals":      {"en": "Best Deals (real profit after ALL costs)", "sq": "Ofertat me te mira (fitim real pas GJITHE kostove)"},
    "retail":          {"en": "Retail", "sq": "Retail"},
    "margin":          {"en": "Margin", "sq": "Margin"},
    "orders":          {"en": "Orders", "sq": "Porosi"},
    "cost_model":      {"en": "Costs: source + shipping + platform 15% + ads 30%",
                        "sq": "Kostot: burim + transport + platforme 15% + reklama 30%"},

    # Competitors
    "competitors":     {"en": "Competitors", "sq": "Konkurentet"},
    "comp_no_data":    {"en": "Configure COMPETITOR_STORES in config.py", "sq": "Konfiguro COMPETITOR_STORES ne config.py"},
    "found_via":       {"en": "Found via", "sq": "Gjetur nga"},

    # Niche matrix
    "niche_matrix":    {"en": "Niche Analysis Matrix", "sq": "Matrica e Nishave"},
    "niche":           {"en": "Niche", "sq": "Nisha"},
    "demand_col":      {"en": "Demand", "sq": "Kerkese"},
    "source_col":      {"en": "Source", "sq": "Burim"},
    "validation":      {"en": "Validation", "sq": "Validim"},
    "grade":           {"en": "Grade", "sq": "Nota"},
    "grades_legend":   {"en": "Grades: A(75+)=Strong | B(60+)=Good | C(40+)=Moderate | D(20+)=Weak | F=Poor",
                        "sq": "Notat: A(75+)=Forte | B(60+)=Mire | C(40+)=Mesatare | D(20+)=Dobet | F=Keq"},

    # Actions
    "actions":         {"en": "Next Actions", "sq": "Veprimet e Radhes"},
    "high_priority":   {"en": "High Priority", "sq": "Prioritet i Larte"},
    "monitor":         {"en": "Monitor", "sq": "Monitorim"},
    "fix":             {"en": "Fix", "sq": "Fikso"},
    "research_top":    {"en": "Research top candidate", "sq": "Kerko kandidatin kryesor"},
    "review_all":      {"en": "Review all", "sq": "Shqyrto te gjithe"},
    "act_viable":      {"en": "Act on", "sq": "Vepro per"},
    "multi_profit":    {"en": "MULTI-SIGNAL products with good profit", "sq": "produkte MULTI-SIGNAL me fitim te mire"},
    "deep_dive":       {"en": "Deep-dive", "sq": "Analizo thelle"},
    "multi_products":  {"en": "multi-signal products", "sq": "produkte multi-signal"},
    "validates":       {"en": "validates", "sq": "validon"},
    "sales_at_avg":    {"en": "sales, avg", "sq": "shitje, avg"},
    "explore_ideas":   {"en": "Explore", "sq": "Eksploro"},
    "new_ideas_from":  {"en": "new ideas from Amazon autocomplete", "sq": "ide te reja nga Amazon autocomplete"},
    "track_movers":    {"en": "Track", "sq": "Gjurmo"},
    "amazon_movers":   {"en": "Amazon movers", "sq": "Amazon movers"},
    "watch_rising":    {"en": "Watch", "sq": "Vezhgo"},
    "rising_bsr":      {"en": "products climbing BSR", "sq": "produkte ne rritje BSR"},
    "inactive_hint":   {"en": "not active —", "sq": "jo aktiv —"},
    "add_proxy":       {"en": "Add PROXY_URL to .env", "sq": "Shto PROXY_URL ne .env"},
    "run_cmd":         {"en": "Run", "sq": "Ekzekuto"},
    "add_stores":      {"en": "Add stores to COMPETITOR_STORES", "sq": "Shto dyqane ne COMPETITOR_STORES"},

    # TikTok
    "tiktok_title":    {"en": "TikTok Viral Products", "sq": "Produkte Virale TikTok"},
    "tiktok_no_data":  {"en": "No TikTok data. Run tiktok_scanner.py", "sq": "Ska te dhena TikTok. Nis tiktok_scanner.py"},
    "top_picks":       {"en": "Top Picks", "sq": "Zgjedhjet Top"},
    "tiktok_score":    {"en": "TikTok Score", "sq": "TikTok Score"},
    "trending_searches": {"en": "Trending TikTok Searches", "sq": "Kerkime Trending TikTok"},

    # Ad Spy
    "adspy_title":     {"en": "Ad Intelligence", "sq": "Inteligjence Reklamash"},
    "adspy_no_data":   {"en": "No ad data. Run ad_spy.py", "sq": "Ska te dhena reklamash. Nis ad_spy.py"},
    "advertised":      {"en": "Top Advertised Keywords", "sq": "Keywords me te Reklamuara"},
    "ad_signal":       {"en": "Ad Signal", "sq": "Sinjal Reklame"},
    "sponsored":       {"en": "Amazon Sponsored Products", "sq": "Produkte te Sponsorizuara Amazon"},

    # Winners
    "winners_title":   {"en": "Winner Analysis", "sq": "Analiza e Fituesve"},
    "winners_no_data": {"en": "No winner data. Run winner_analyzer.py", "sq": "Ska fitues. Nis winner_analyzer.py"},
    "strong_buy":      {"en": "STRONG BUY", "sq": "BLEJ FORT"},
    "buy":             {"en": "BUY", "sq": "BLEJ"},
    "repeat":          {"en": "Repeat", "sq": "Repeat"},
    "bundle":          {"en": "Bundle", "sq": "Bundle"},
    "ugc":             {"en": "UGC", "sq": "UGC"},
    "viability":       {"en": "Viability", "sq": "Viabilitet"},
    "product_type":    {"en": "Type", "sq": "Tipi"},

    # Footer
    "generated":       {"en": "Generated", "sq": "Gjeneruar"},
    "cost_footer":     {"en": "Cost model: source + shipping + platform 15% + ads 30%",
                        "sq": "Model kostosh: burim + transport + platforme 15% + reklama 30%"},
}


def _t(key: str, lang: str) -> str:
    """Get translation for key in given language."""
    entry = T.get(key, {})
    return entry.get(lang, entry.get("en", key))


# ── Helpers ──────────────────────────────────────────────────


def _esc(text) -> str:
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fp(price, currency="$") -> str:
    if price is None:
        return "N/A"
    return f"{currency}{price:.2f}"


def _tr(text: str, length: int) -> str:
    if not text:
        return ""
    return text if len(text) <= length else text[: length - 1] + "…"


def _bar(value: float, max_val: float = 100, color: str = "#00b894") -> str:
    pct = min(100, (value / max_val * 100)) if max_val > 0 else 0
    return (
        f'<div class="bar-bg">'
        f'<div class="bar-fill" style="width:{pct:.0f}%;background:{color}"></div>'
        f'</div>'
    )


def _grade_bg(grade: str) -> str:
    g = grade[0] if grade else "F"
    return {"A": "#00b894", "B": "#74b9ff", "C": "#fdcb6e", "D": "#e17055"}.get(g, "#d63031")


def _dots(filled: int, total: int = 6) -> str:
    f = min(filled, total)
    return (
        '<span class="signal-dots">'
        + '<span class="dot-on">●</span>' * f
        + '<span class="dot-off">○</span>' * (total - f)
        + '</span>'
    )


# ── CSS ──────────────────────────────────────────────────────

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#0f0f1a;color:#e0e0e0;padding:20px;line-height:1.6}
.c{max-width:920px;margin:0 auto}

.hdr{text-align:center;padding:32px 20px;background:linear-gradient(135deg,#1a1a3e,#0f3460);border-radius:14px;margin-bottom:20px;border:1px solid #2a2a5e}
.hdr h1{font-size:1.7em;color:#fff;letter-spacing:1px}
.hdr .dt{color:#74b9ff;font-size:1.05em;margin-top:4px}
.hdr .ver{color:#636e72;font-size:.82em;margin-top:6px}
.hdr .stat-row{display:flex;justify-content:center;gap:16px;margin-top:14px;flex-wrap:wrap}
.hdr .stat{background:rgba(255,255,255,.06);padding:6px 16px;border-radius:8px;font-size:.88em}
.hdr .stat b{color:#00b894}
.lang-tag{display:inline-block;background:#0f3460;color:#74b9ff;padding:2px 10px;border-radius:12px;font-size:.75em;font-weight:600;letter-spacing:1px;margin-top:8px}

.card{background:#1a1a2e;border-radius:10px;padding:20px;margin-bottom:16px;border:1px solid #2a2a4e}
.card h2{font-size:1.1em;color:#74b9ff;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #2a2a4e}
.card h3{font-size:.95em;color:#dfe6e9;margin:14px 0 8px}

.sg{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.si{background:#16213e;padding:10px 14px;border-radius:8px;display:flex;justify-content:space-between;align-items:center}
.si .nm{font-weight:600;font-size:.92em}
.si .dt{color:#b2bec3;font-size:.8em;margin-top:2px}
.si-on{border-left:3px solid #00b894}
.si-off{border-left:3px solid #e17055;opacity:.6}
.qb{font-size:.72em;padding:2px 8px;border-radius:10px;font-weight:600;white-space:nowrap}
.qe{background:#00b894;color:#fff}
.qg{background:#74b9ff;color:#000}
.qp{background:#fdcb6e;color:#000}
.qo{background:#636e72;color:#fff}

table{width:100%;border-collapse:collapse;margin:8px 0;font-size:.88em}
th{background:#16213e;color:#74b9ff;padding:8px 10px;text-align:left;font-weight:600;font-size:.82em;text-transform:uppercase;letter-spacing:.5px}
td{padding:7px 10px;border-bottom:1px solid #1e1e3e}
tr:nth-child(even) td{background:rgba(255,255,255,.02)}
tr:hover td{background:rgba(116,185,255,.06)}
.ar{text-align:right}
.ac{text-align:center}

.bar-bg{background:#2d3436;border-radius:3px;height:8px;width:80px;display:inline-block;vertical-align:middle}
.bar-fill{height:100%;border-radius:3px}

.bd{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.76em;font-weight:600}
.bg{background:rgba(0,184,148,.2);color:#00b894}
.br{background:rgba(225,112,85,.2);color:#e17055}
.by{background:rgba(253,203,110,.2);color:#fdcb6e}
.bb{background:rgba(116,185,255,.2);color:#74b9ff}
.bx{background:rgba(99,110,114,.2);color:#b2bec3}

.gr{display:inline-block;width:28px;height:28px;line-height:28px;text-align:center;border-radius:6px;font-weight:700;font-size:.88em;color:#fff}

.signal-dots{letter-spacing:2px;font-size:1.1em}
.dot-on{color:#00b894}
.dot-off{color:#636e72}

.act-h{border-left:3px solid #e17055;padding-left:12px;margin:6px 0;font-size:.92em}
.act-m{border-left:3px solid #fdcb6e;padding-left:12px;margin:6px 0;font-size:.92em}
.act-f{border-left:3px solid #636e72;padding-left:12px;margin:6px 0;font-size:.92em}

.cb{background:#16213e;border-radius:8px;padding:12px;margin:10px 0}
.ch{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.cn{font-weight:600;color:#dfe6e9}
.cs{color:#b2bec3;font-size:.84em}

.empty{color:#636e72;font-style:italic;padding:12px 0}

.footer{text-align:center;padding:20px;color:#636e72;font-size:.82em;border-top:1px solid #2a2a4e;margin-top:20px}

@media(max-width:600px){
  body{padding:10px}
  .sg{grid-template-columns:1fr}
  table{font-size:.78em}
  th,td{padding:5px 6px}
  .bar-bg{width:50px}
}
"""


# ── Quality helpers ──────────────────────────────────────────


def _quality_class(score: int) -> tuple:
    if score >= 80:
        return "qe", "excellent"
    elif score >= 60:
        return "qg", "good"
    elif score > 0:
        return "qp", "partial"
    return "qo", "offline"


def _calc_quality(name: str, info: dict) -> int:
    if not info.get("active"):
        return 0
    score = 50
    if name == "amazon":
        p = info.get("products", 0)
        score = 95 if p >= 100 else 80 if p >= 50 else 60 if p > 0 else 50
    elif name == "ebay":
        s = info.get("total_sold", 0)
        score = 95 if s >= 200 else 75 if s >= 50 else 55 if s > 0 else 50
    elif name == "trends":
        score = min(95, 50 + info.get("hot_products", 0) * 5)
    elif name == "aliexpress":
        p = info.get("products", 0)
        score = 90 if p >= 50 else 70 if p >= 20 else 55 if p > 0 else 50
    elif name == "competitors":
        score = min(90, 50 + info.get("stores", 0) * 10)
    elif name == "demand":
        score = min(90, 50 + info.get("suggestions", 0) // 5)
    elif name == "prices":
        score = min(90, 50 + info.get("tracked", 0) * 5)
    return score


# ── Sections ─────────────────────────────────────────────────


def _html_header(today: str, sources: dict, analysis: dict, lang: str) -> str:
    L = lang
    active = sum(1 for s in sources.values() if s.get("active"))
    total = len(sources)
    cross = len(analysis.get("cross_references", []))
    candidates = len(analysis.get("amazon", {}).get("dropship_candidates", []))
    lang_label = "ENGLISH" if L == "en" else "SHQIP"

    return f'''<div class="hdr">
<h1>{_t("title", L)}</h1>
<div class="dt">{_esc(today)}</div>
<div class="ver">Signal Pilot v4</div>
<div class="lang-tag">{lang_label}</div>
<div class="stat-row">
<div class="stat">{_t("sources_label", L)}: <b>{active}/{total}</b></div>
<div class="stat">{_t("candidates_label", L)}: <b>{candidates}</b></div>
<div class="stat">Multi-Signal: <b>{cross}</b></div>
</div>
</div>'''


def _html_sources(sources: dict, lang: str) -> str:
    L = lang
    active = sum(1 for s in sources.values() if s.get("active"))
    total = len(sources)

    defs = [
        ("amazon", "Amazon BSR", lambda s: f"{s.get('products',0)} {_t('products', L)}, {s.get('movers',0)} movers"),
        ("demand", "Amazon Demand", lambda s: f"{s.get('suggestions',0)} {_t('suggestions', L)}"),
        ("ebay", "eBay Sold", lambda s: f"{s.get('total_sold',0)} {_t('sold', L)}"),
        ("trends", "Google Trends", lambda s: f"{s.get('hot_products',0)} hot"),
        ("aliexpress", "AliExpress", lambda s: f"{s.get('products',0)} {_t('products', L)}"),
        ("competitors", "Competitors", lambda s: f"{s.get('stores',0)} {_t('stores', L)}"),
        ("prices", "Price Monitor", lambda s: f"{s.get('tracked',0)} {_t('tracked', L)}"),
    ]

    items = []
    for key, name, detail_fn in defs:
        info = sources.get(key, {})
        is_active = info.get("active", False)
        cls = "si-on" if is_active else "si-off"
        icon = "✓" if is_active else "✗"
        detail = detail_fn(info) if is_active else _t("not_active", L)
        q_score = _calc_quality(key, info)
        q_cls, q_label = _quality_class(q_score)

        items.append(
            f'<div class="si {cls}">'
            f'<div><div class="nm">{icon} {_esc(name)}</div>'
            f'<div class="dt">{_esc(detail)}</div></div>'
            f'<span class="qb {q_cls}">{_esc(q_label)}</span>'
            f'</div>'
        )

    return f'''<div class="card">
<h2>📡 {_t("data_sources", L)} ({active}/{total} {_t("active", L)})</h2>
<div class="sg">{"".join(items)}</div>
</div>'''


def _html_cross_refs(cross_refs: list, lang: str) -> str:
    L = lang
    if not cross_refs:
        return f'<div class="card"><h2>🔗 {_t("multi_signal", L)}</h2><p class="empty">{_t("no_multi", L)}</p></div>'

    rows = []
    for i, ref in enumerate(cross_refs[:15], 1):
        signals = _esc(" + ".join(ref.get("signals", [])))
        conf = ref.get("signal_count", 1)
        dots = _dots(conf)
        brand_tag = ' <span class="bd br">BRAND</span>' if ref.get("is_brand") else ""
        title = _esc(_tr(ref.get("title", "?"), 45))

        details = []
        if ref.get("amazon_rank"):
            details.append(f"Amazon #{ref['amazon_rank']} {_fp(ref.get('amazon_price_usd'))}")
        if ref.get("ebay_sold"):
            details.append(f"eBay: {ref['ebay_sold']} {_t('sold', L)}, avg {_fp(ref.get('ebay_avg_price'))}")
        if ref.get("source_price"):
            viable_cls = "bg" if ref.get("profit_viable") else "br"
            viable_txt = "VIABLE" if ref.get("profit_viable") else "LOW"
            details.append(
                f"Source: {_fp(ref['source_price'])} → {_t('profit_word', L)}: {_fp(ref.get('real_profit'))} "
                f"({ref.get('margin_pct', '?')}%) "
                f'<span class="bd {viable_cls}">{viable_txt}</span>'
            )
        if ref.get("trend_interest"):
            details.append(f"Trend: {ref['trend_interest']}/100")

        risks = []
        if ref.get("is_brand"):
            risks.append('<span class="bd br">BRAND-GATED</span>')
        if ref.get("review_count") and ref["review_count"] > 5000:
            risks.append('<span class="bd by">SATURATED</span>')
        if ref.get("margin_pct") and ref["margin_pct"] < 15:
            risks.append('<span class="bd br">LOW-MARGIN</span>')

        detail_html = "<br>".join(details)
        risk_html = " ".join(risks) if risks else ""

        rows.append(
            f'<tr><td class="ac">{i}</td>'
            f'<td>{dots}</td>'
            f'<td><b>{title}</b>{brand_tag}</td>'
            f'<td style="font-size:.82em">{signals}</td>'
            f'<td style="font-size:.82em">{detail_html}</td>'
            f'<td>{risk_html}</td></tr>'
        )

    return f'''<div class="card">
<h2>🔗 {_t("multi_signal", L)} ({len(cross_refs)} {_t("products", L)})</h2>
<table>
<tr><th>#</th><th>Conf</th><th>{_t("product", L)}</th><th>{_t("signals", L)}</th><th>{_t("details", L)}</th><th>Risk</th></tr>
{"".join(rows)}
</table>
</div>'''


def _html_amazon(amazon: dict, lang: str) -> str:
    L = lang
    if amazon.get("status") == "no_data":
        return f'<div class="card"><h2>🛒 Amazon</h2><p class="empty">{_t("no_data", L)}</p></div>'

    parts = ['<div class="card">', f'<h2>🛒 {_t("amazon_bs", L)}</h2>']

    # Price distribution
    dist = amazon.get("price_distribution", {})
    if dist:
        total = dist.get("total", 1)
        parts.append(f'<h3>{_t("price_dist", L)}</h3>')
        parts.append(f'<table><tr><th>{_t("range", L)}</th><th>{_t("count", L)}</th><th>{_t("chart", L)}</th><th class="ar">%</th></tr>')
        for label, key in [("<$10", "under_10"), ("$10–25", "10_to_25"),
                           ("$25–50", "25_to_50"), ("$50–100", "50_to_100"),
                           (">$100", "over_100")]:
            count = dist.get(key, 0)
            pct = round(count / total * 100) if total else 0
            color = "#00b894" if label in ("$25–50",) else "#74b9ff" if label in ("$10–25", "$50–100") else "#636e72"
            parts.append(
                f'<tr><td>{label}</td><td class="ac">{count}</td>'
                f'<td>{_bar(count, total, color)}</td>'
                f'<td class="ar">{pct}%</td></tr>'
            )
        parts.append('</table>')
        parts.append(
            f'<p style="color:#b2bec3;font-size:.85em;margin-top:6px">'
            f'{_t("avg", L)}: {_fp(dist.get("avg"))} &nbsp;|&nbsp; {_t("median", L)}: {_fp(dist.get("median"))}'
            f'</p>'
        )

    # Categories
    for cat_name, cat in amazon.get("categories", {}).items():
        display = _esc(cat_name.upper().replace("-", " & ").replace("_", " "))
        pr = cat.get("price_range", {})

        parts.append(f'<div class="cb">')
        parts.append(f'<div class="ch"><span class="cn">{display} ({cat["total"]} {_t("products", L)})</span>')
        parts.append(
            f'<span class="cs">'
            f'Avg: {_fp(cat.get("avg_price"))} | '
            f'Range: {_fp(pr.get("min"))}–{_fp(pr.get("max"))} | '
            f'Rating: {cat.get("avg_rating", 0):.1f}/5'
            f'</span>'
        )
        parts.append('</div>')

        parts.append(f'<table><tr><th>#</th><th>{_t("product", L)}</th><th class="ar">{_t("price", L)}</th><th class="ac">★</th><th class="ar">{_t("reviews", L)}</th><th>{_t("trend", L)}</th></tr>')
        for p in cat.get("top_5", []):
            rd = p.get("rank_direction", "")
            arrow = ""
            if rd == "up":
                arrow = f'<span style="color:#00b894">↑{p.get("rank_change","")}</span>'
            elif rd == "down":
                arrow = f'<span style="color:#e17055">↓{abs(p.get("rank_change",0))}</span>'
            elif rd == "new":
                arrow = '<span class="bd bg">NEW</span>'

            brand = ' <span class="bd br">B</span>' if p.get("is_brand") else ""
            rating = f'{p["rating"]:.1f}' if p.get("rating") else "—"
            reviews = f'{p["review_count"]:,}' if p.get("review_count") else "—"

            parts.append(
                f'<tr><td>#{p.get("rank","?")}</td>'
                f'<td>{_esc(_tr(p["title"], 40))}{brand}</td>'
                f'<td class="ar">{_fp(p.get("price_usd"))}</td>'
                f'<td class="ac">{rating}</td>'
                f'<td class="ar">{reviews}</td>'
                f'<td>{arrow}</td></tr>'
            )
        parts.append('</table></div>')

    # Dropship candidates
    candidates = amazon.get("dropship_candidates", [])
    if candidates:
        parts.append(f'<h3>🎯 {_t("dropship_cand", L)} ({len(candidates)} {_t("found", L)})</h3>')
        parts.append(f'<p style="color:#b2bec3;font-size:.82em;margin-bottom:8px">{_t("filters", L)}</p>')
        parts.append(
            f'<table><tr><th>Score</th><th>{_t("product", L)}</th>'
            f'<th class="ar">{_t("price", L)}</th><th class="ac">★</th>'
            f'<th class="ar">{_t("reviews", L)}</th><th>Risk</th></tr>'
        )
        for c in candidates[:20]:
            score = c.get("dropship_score", 0)
            s_color = "#00b894" if score >= 70 else "#fdcb6e" if score >= 50 else "#e17055"
            rating = f'{c["rating"]:.1f}' if c.get("rating") else "—"
            reviews = f'{c["review_count"]:,}' if c.get("review_count") else "—"
            risks = c.get("skip_reasons", [])
            risk_badges = " ".join(
                f'<span class="bd by">{_esc(r.replace("_"," "))}</span>' for r in risks
            ) if risks else '<span class="bd bg">OK</span>'

            parts.append(
                f'<tr><td><span style="color:{s_color};font-weight:700">{score}</span> '
                f'{_bar(score, 100, s_color)}</td>'
                f'<td>{_esc(_tr(c["title"], 38))}</td>'
                f'<td class="ar">{_fp(c.get("price_usd"))}</td>'
                f'<td class="ac">{rating}</td>'
                f'<td class="ar">{reviews}</td>'
                f'<td>{risk_badges}</td></tr>'
            )
        parts.append('</table>')

    # Rising
    rising = amazon.get("rising_products", [])
    if rising:
        parts.append(f'<h3>📈 {_t("bsr_rising", L)} ({len(rising)} {_t("climbing", L)})</h3>')
        parts.append(f'<table><tr><th>{_t("change", L)}</th><th>{_t("product", L)}</th><th class="ar">{_t("price", L)}</th></tr>')
        for p in rising[:10]:
            parts.append(
                f'<tr><td style="color:#00b894;font-weight:600">'
                f'↑{p.get("rank_change","?")} ranks</td>'
                f'<td>{_esc(_tr(p["title"], 45))}</td>'
                f'<td class="ar">{_fp(p.get("price_usd"))}</td></tr>'
            )
        parts.append('</table>')

    # Movers
    movers = amazon.get("movers", [])
    if movers:
        parts.append(f'<h3>🔥 Movers & Shakers ({len(movers)})</h3>')
        parts.append(f'<table><tr><th>Category</th><th>{_t("product", L)}</th><th class="ar">{_t("price", L)}</th></tr>')
        for m in movers[:15]:
            brand = ' <span class="bd br">B</span>' if m.get("is_brand") else ""
            cat = _esc(_tr(m.get("category", "?"), 14))
            parts.append(
                f'<tr><td><span class="bd bb">{cat}</span></td>'
                f'<td>{_esc(_tr(m["title"], 42))}{brand}</td>'
                f'<td class="ar">{_fp(m.get("price_usd"))}</td></tr>'
            )
        parts.append('</table>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_ebay(ebay: dict, lang: str) -> str:
    L = lang
    if ebay.get("status") == "no_data":
        return (
            f'<div class="card"><h2>🏷 eBay Sold</h2>'
            f'<p class="empty">{_t("ebay_no_data", L)}</p></div>'
        )

    parts = [
        '<div class="card">',
        f'<h2>🏷 {_t("ebay_sold", L)}</h2>',
        f'<p style="color:#b2bec3;font-size:.85em">'
        f'{_t("total", L)}: {ebay.get("total_sold",0)} {_t("sold", L)} | '
        f'{_t("keywords_sales", L)}: {ebay.get("keywords_with_sales",0)}/{ebay.get("keywords_scanned",0)}'
        f'</p>',
    ]

    top = ebay.get("top_sellers", [])
    if top:
        parts.append(f'<h3>{_t("most_sold", L)}</h3>')
        parts.append(
            f'<table><tr><th>Keyword</th><th class="ar">{_t("sales", L)}</th>'
            f'<th class="ar">Avg</th><th class="ar">{_t("median", L)}</th>'
            f'<th>{_t("competition", L)}</th><th class="ar">{_t("vel", L)}</th></tr>'
        )
        results = ebay.get("results", {})
        for ts in top[:12]:
            kw = ts.get("keyword", "")
            kw_data = results.get(kw, {})
            comp = kw_data.get("competition", "?")
            vel = kw_data.get("daily_velocity", 0)
            vel_str = f"{vel:.1f}/day" if vel else "—"
            comp_cls = "bg" if comp == "low" else "by" if comp == "moderate" else "br" if comp == "high" else "bx"

            parts.append(
                f'<tr><td>{_esc(_tr(kw, 26))}</td>'
                f'<td class="ar">{ts.get("sold_count",0)}</td>'
                f'<td class="ar">{_fp(ts.get("avg_price"))}</td>'
                f'<td class="ar">{_fp(ts.get("median_price"))}</td>'
                f'<td><span class="bd {comp_cls}">{_esc(comp)}</span></td>'
                f'<td class="ar">{vel_str}</td></tr>'
            )
        parts.append('</table>')

    insights = ebay.get("price_insights", [])
    if insights:
        parts.append(f'<h3>{_t("validated_prices", L)}</h3>')
        parts.append(
            f'<table><tr><th>Keyword</th><th class="ar">{_t("sales", L)}</th>'
            f'<th class="ar">Avg</th><th>Range</th></tr>'
        )
        for pi in insights[:8]:
            parts.append(
                f'<tr><td>{_esc(_tr(pi["keyword"], 28))}</td>'
                f'<td class="ar">{pi.get("sold_count",0)}</td>'
                f'<td class="ar">{_fp(pi.get("avg_sold_price"))}</td>'
                f'<td>{_esc(pi.get("price_range","N/A"))}</td></tr>'
            )
        parts.append('</table>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_demand(demand: dict, lang: str) -> str:
    L = lang
    if demand.get("status") == "no_data":
        return f'<div class="card"><h2>💡 Amazon Demand</h2><p class="empty">{_t("no_data", L)}</p></div>'

    parts = [
        '<div class="card">',
        f'<h2>💡 {_t("amazon_demand", L)}</h2>',
        f'<p style="color:#b2bec3;font-size:.85em">'
        f'{_t("keywords", L)}: {demand.get("keywords_scanned",0)} | '
        f'{_t("suggestions", L)}: {demand.get("total_suggestions",0)} | '
        f'{_t("discoveries", L)}: {demand.get("new_discoveries",0)}</p>',
    ]

    discoveries = demand.get("top_discoveries", [])
    if discoveries:
        parts.append(f'<h3>🆕 {_t("new_ideas", L)} ({len(discoveries)})</h3>')
        parts.append(f'<table><tr><th>{_t("suggestion", L)}</th><th>{_t("source", L)}</th></tr>')
        for d in discoveries[:15]:
            parts.append(
                f'<tr><td>{_esc(d.get("suggestion","?"))}</td>'
                f'<td><span class="bd bb">{_esc(d.get("source_keyword","?"))}</span></td></tr>'
            )
        parts.append('</table>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_trends(trends: dict, lang: str) -> str:
    L = lang
    if trends.get("status") == "no_data":
        return (
            f'<div class="card"><h2>📊 {_t("google_trends", L)}</h2>'
            f'<p class="empty">{_t("trends_no_data", L)}</p></div>'
        )

    parts = ['<div class="card">', f'<h2>📊 {_t("google_trends", L)}</h2>']

    hot = trends.get("hot_products", [])
    if hot:
        parts.append(f'<h3>🔥 {_t("hot", L)} ({len(hot)} {_t("rising", L)})</h3>')
        parts.append(f'<table><tr><th>Keyword</th><th>{_t("interest", L)}</th><th>{_t("chart", L)}</th><th>{_t("direction", L)}</th></tr>')
        for p in hot:
            td = p.get("trend", "unknown")
            icon = {"rising_fast": "⬆⬆", "rising": "⬆", "stable": "→",
                    "falling": "⬇", "falling_fast": "⬇⬇"}.get(td, "?")
            i_color = "#00b894" if "rising" in td else "#fdcb6e" if td == "stable" else "#e17055"
            interest = p.get("current_interest", 0)
            parts.append(
                f'<tr><td><b>{_esc(p["keyword"])}</b></td>'
                f'<td class="ac">{interest}/100</td>'
                f'<td>{_bar(interest, 100, i_color)}</td>'
                f'<td style="color:{i_color}">{icon}</td></tr>'
            )
        parts.append('</table>')

    emerging = trends.get("emerging_products", [])
    if emerging:
        parts.append(f'<h3>🌱 {_t("emerging", L)} ({len(emerging)} {_t("emerging_desc", L)})</h3>')
        parts.append(f'<table><tr><th>Keyword</th><th class="ac">{_t("interest", L)}</th><th class="ar">Slope</th><th class="ar">Accel</th></tr>')
        for e in emerging:
            parts.append(
                f'<tr><td>{_esc(e["keyword"])}</td>'
                f'<td class="ac">{e.get("current_interest",0)}/100</td>'
                f'<td class="ar" style="color:#00b894">+{e.get("slope",0):.2f}</td>'
                f'<td class="ar">{e.get("acceleration",0):.2f}</td></tr>'
            )
        parts.append('</table>')

    disc = trends.get("discoveries", [])
    if disc:
        parts.append(f'<h3>▲ {_t("breakout", L)} ({len(disc)})</h3>')
        parts.append(f'<table><tr><th>Query</th><th class="ar">{_t("growth", L)}</th><th>{_t("from", L)}</th></tr>')
        for d in disc:
            parts.append(
                f'<tr><td><b>{_esc(d["query"])}</b></td>'
                f'<td class="ar" style="color:#00b894">+{d.get("growth",0)}%</td>'
                f'<td><span class="bd bb">{_esc(d.get("source_keyword","?"))}</span></td></tr>'
            )
        parts.append('</table>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_aliexpress(aliexpress: dict, lang: str) -> str:
    L = lang
    if aliexpress.get("status") == "no_data":
        return (
            f'<div class="card"><h2>🏭 AliExpress</h2>'
            f'<p class="empty">{_t("ali_no_data", L)}</p></div>'
        )
    total = aliexpress.get("total_products", 0)
    if total == 0:
        return f'<div class="card"><h2>🏭 AliExpress</h2><p class="empty">{_t("ali_blocked", L)}</p></div>'

    parts = ['<div class="card">', f'<h2>🏭 {_t("ali_sourcing", L)}</h2>']

    deals = aliexpress.get("best_deals", [])
    if deals:
        parts.append(f'<h3>{_t("best_deals", L)}</h3>')
        parts.append(
            f'<table><tr><th>{_t("product", L)}</th><th class="ar">{_t("source", L)}</th>'
            f'<th class="ar">{_t("retail", L)}</th><th class="ar">{_t("profit_word", L)}</th>'
            f'<th class="ar">{_t("margin", L)}</th><th class="ar">{_t("orders", L)}</th></tr>'
        )
        for d in deals[:10]:
            source_p = d.get("source_price") or d.get("price_usd", 0)
            retail_p = d.get("retail_price") or d.get("potential_retail") or (source_p * 2.5 if source_p else 0)
            shipping = d.get("shipping_cost", 0)
            pi = calculate_real_profit(source_p, retail_p, shipping)
            profit = pi.get("profit", 0)
            margin = pi.get("margin_pct", 0)
            viable = pi.get("viable", False)
            v_cls = "bg" if viable else "br"
            v_txt = "✓" if viable else "✗"
            orders = d.get("orders", "N/A")

            parts.append(
                f'<tr><td>{_esc(_tr(d.get("title","?"), 35))}</td>'
                f'<td class="ar">{_fp(source_p)}</td>'
                f'<td class="ar">{_fp(retail_p)}</td>'
                f'<td class="ar"><span class="bd {v_cls}">{_fp(profit)} {v_txt}</span></td>'
                f'<td class="ar">{margin:.1f}%</td>'
                f'<td class="ar">{orders}</td></tr>'
            )
        parts.append('</table>')
        parts.append(f'<p style="color:#636e72;font-size:.8em;margin-top:6px">{_t("cost_model", L)}</p>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_competitors(competitors: dict, lang: str) -> str:
    L = lang
    if competitors.get("status") == "no_data":
        return (
            f'<div class="card"><h2>🔍 {_t("competitors", L)}</h2>'
            f'<p class="empty">{_t("comp_no_data", L)}</p></div>'
        )

    stores = competitors.get("stores", {})
    parts = [
        '<div class="card">',
        f'<h2>🔍 {_t("competitors", L)} ({len(stores)} {_t("stores", L)})</h2>',
    ]

    for domain, info in list(stores.items())[:10]:
        # Stats may be nested under "stats" key (from competitor_tracker.py)
        stats = info.get("stats", {})
        products = stats.get("total_products", info.get("product_count", info.get("total_products", 0)))
        avg = stats.get("avg_price", info.get("avg_price", 0))
        pr = stats.get("price_range", info.get("price_range", "N/A"))
        sweet = stats.get("sweet_spot_pct", 0)
        via = info.get("found_via", "")

        # Sweet spot color
        sw_cls = "bg" if sweet >= 50 else "by" if sweet >= 30 else "br"

        parts.append(f'<div class="cb">')
        parts.append(
            f'<div class="ch"><span class="cn">{_esc(domain)}</span>'
            f'<span class="cs">{products} {_t("products", L)} | Avg: {_fp(avg)} | {_esc(pr)}</span></div>'
        )
        if sweet:
            parts.append(f'<p style="font-size:.82em;color:#b2bec3">Sweet Spot: <span class="bd {sw_cls}">{sweet}%</span></p>')
        if via:
            parts.append(f'<p style="font-size:.82em;color:#b2bec3">{_t("found_via", L)}: "{_esc(via)}"</p>')

        # Show niche overlap if available
        overlap = info.get("niche_overlap", {})
        if overlap:
            niche_badges = " ".join(
                f'<span class="bd bb">{_esc(n)}</span>' for n in list(overlap.keys())[:5]
            )
            parts.append(f'<p style="font-size:.82em;margin-top:4px">Niches: {niche_badges}</p>')

        # Show top products as samples
        top_products = info.get("top_products", [])
        samples = info.get("sample_titles", [])
        if top_products:
            for tp in top_products[:3]:
                t = tp.get("title", "")
                p = tp.get("price")
                price_str = f" ({_fp(p)})" if p else ""
                parts.append(f'<p style="font-size:.84em;padding-left:10px">• {_esc(_tr(t, 50))}{price_str}</p>')
        elif samples:
            for s in samples[:3]:
                parts.append(f'<p style="font-size:.84em;padding-left:10px">• {_esc(_tr(s, 55))}</p>')
        parts.append('</div>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_tiktok(tiktok: dict, lang: str) -> str:
    L = lang
    if tiktok.get("status") == "no_data":
        return (
            f'<div class="card"><h2>🎵 {_t("tiktok_title", L)}</h2>'
            f'<p class="empty">{_t("tiktok_no_data", L)}</p></div>'
        )

    stats = tiktok.get("stats", {})
    top_picks = tiktok.get("top_picks", [])
    trends = tiktok.get("trend_suggestions", [])

    parts = [
        '<div class="card">',
        f'<h2>🎵 {_t("tiktok_title", L)}</h2>',
        f'<div class="sg">',
        f'<div class="si"><span class="sn">{_t("products", L)}</span><span class="sv">{stats.get("total_products_found", 0)}</span></div>',
        f'<div class="si"><span class="sn">{_t("top_picks", L)}</span><span class="sv">{stats.get("top_picks_count", 0)}</span></div>',
        f'<div class="si"><span class="sn">Avg Score</span><span class="sv">{stats.get("avg_tiktok_score", 0)}</span></div>',
        '</div>',
    ]

    if top_picks:
        parts.append(f'<h3>🔥 {_t("top_picks", L)} (Top 10)</h3>')
        parts.append('<table><tr><th>#</th><th>{}</th><th>{}</th><th>⭐</th><th>{}</th></tr>'.format(
            _t("product", L), _t("price", L), _t("tiktok_score", L)))
        for i, p in enumerate(top_picks[:10], 1):
            score = p.get("tiktok_score", 0)
            bar_w = min(score, 100)
            color = "#00b894" if score >= 50 else "#fdcb6e" if score >= 30 else "#e17055"
            parts.append(
                f'<tr><td>{i}</td><td>{_esc(_tr(p.get("title", ""), 50))}</td>'
                f'<td>{_fp(p.get("price_usd", 0))}</td>'
                f'<td>{p.get("rating", 0) or 0:.1f}</td>'
                f'<td><div class="bar-bg"><div class="bar-fill" style="width:{bar_w}%;background:{color}">{score}</div></div></td></tr>'
            )
        parts.append('</table>')

    if trends:
        parts.append(f'<h3>📈 {_t("trending_searches", L)} (Top 10)</h3>')
        parts.append('<div style="display:flex;flex-wrap:wrap;gap:6px">')
        seen = set()
        count = 0
        for t in trends:
            kw = t.get("product_keyword", "")
            if kw and kw not in seen and count < 10:
                seen.add(kw)
                parts.append(f'<span class="bd" style="background:#6c5ce7;color:#fff">{_esc(kw)}</span>')
                count += 1
        parts.append('</div>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_adspy(adspy: dict, lang: str) -> str:
    L = lang
    if adspy.get("status") == "no_data":
        return (
            f'<div class="card"><h2>🕵️ {_t("adspy_title", L)}</h2>'
            f'<p class="empty">{_t("adspy_no_data", L)}</p></div>'
        )

    stats = adspy.get("stats", {})
    intelligence = adspy.get("intelligence", [])
    fb_trending = adspy.get("fb_trending", [])

    parts = [
        '<div class="card">',
        f'<h2>🕵️ {_t("adspy_title", L)}</h2>',
        f'<div class="sg">',
        f'<div class="si"><span class="sn">Google Keywords</span><span class="sv">{stats.get("google_keywords_analyzed", 0)}</span></div>',
        f'<div class="si"><span class="sn">{_t("advertised", L)}</span><span class="sv">{stats.get("google_top_advertised", 0)}</span></div>',
        f'<div class="si"><span class="sn">{_t("sponsored", L)}</span><span class="sv">{stats.get("amazon_sponsored_found", 0)}</span></div>',
        '</div>',
    ]

    if intelligence:
        parts.append(f'<h3>💰 {_t("ad_signal", L)} (Top 10)</h3>')
        parts.append('<table><tr><th>Keyword</th><th>Score</th><th>Signals</th><th>Rec</th></tr>')
        for item in intelligence[:10]:
            rec = item.get("recommendation", "WATCH")
            rec_color = {"STRONG_BUY": "#00b894", "BUY": "#fdcb6e", "WATCH": "#74b9ff"}.get(rec, "#dfe6e9")
            signals = ", ".join(item.get("signals", []))
            parts.append(
                f'<tr><td><b>{_esc(item.get("keyword", ""))}</b></td>'
                f'<td>{item.get("ad_score", 0)}</td>'
                f'<td style="font-size:.82em">{_esc(signals)}</td>'
                f'<td><span class="bd" style="background:{rec_color};color:#222">{rec}</span></td></tr>'
            )
        parts.append('</table>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_winners(analysis: dict, lang: str) -> str:
    """Render winners section from winners data file if available."""
    L = lang
    import json, glob
    from pathlib import Path

    # Try to load latest winners data
    pattern = str(Path("data") / "winners_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        return (
            f'<div class="card"><h2>🏆 {_t("winners_title", L)}</h2>'
            f'<p class="empty">{_t("winners_no_data", L)}</p></div>'
        )

    try:
        with open(files[0]) as f:
            winners = json.load(f)
    except (json.JSONDecodeError, IOError):
        return (
            f'<div class="card"><h2>🏆 {_t("winners_title", L)}</h2>'
            f'<p class="empty">{_t("winners_no_data", L)}</p></div>'
        )

    stats = winners.get("stats", {})
    strong_buys = winners.get("strong_buys", [])
    buys = winners.get("buys", [])
    type_dist = winners.get("type_distribution", {})

    parts = [
        '<div class="card">',
        f'<h2>🏆 {_t("winners_title", L)}</h2>',
        f'<div class="sg">',
        f'<div class="si" style="border-left:3px solid #e74c3c"><span class="sn">🔴 {_t("strong_buy", L)}</span><span class="sv" style="color:#e74c3c;font-size:1.5em">{stats.get("strong_buy_count", 0)}</span></div>',
        f'<div class="si" style="border-left:3px solid #f39c12"><span class="sn">🟡 {_t("buy", L)}</span><span class="sv" style="color:#f39c12;font-size:1.5em">{stats.get("buy_count", 0)}</span></div>',
        f'<div class="si"><span class="sn">🔄 {_t("repeat", L)}</span><span class="sv">{stats.get("repeat_champions", 0)}</span></div>',
        f'<div class="si"><span class="sn">📦 {_t("bundle", L)}</span><span class="sv">{stats.get("bundle_candidates", 0)}</span></div>',
        f'<div class="si"><span class="sn">📸 {_t("ugc", L)}</span><span class="sv">{stats.get("ugc_superstars", 0)}</span></div>',
        f'<div class="si"><span class="sn">🎵 TikTok</span><span class="sv">{stats.get("tiktok_validated", 0)}</span></div>',
        f'<div class="si"><span class="sn">💰 Ad Proven</span><span class="sv">{stats.get("ad_proven", 0)}</span></div>',
        f'<div class="si"><span class="sn">🌿 Evergreen</span><span class="sv">{stats.get("evergreen", 0)}</span></div>',
        '</div>',
    ]

    # Type distribution badges
    if type_dist:
        parts.append('<div style="margin:12px 0;display:flex;flex-wrap:wrap;gap:6px">')
        type_colors = {
            "REPEAT": "#00b894", "BUNDLE": "#0984e3", "UGC": "#e17055",
            "TIKTOK": "#6c5ce7", "AD_PROVEN": "#fdcb6e", "TREND": "#00cec9",
            "SHORT-TERM": "#636e72",
        }
        for t, count in type_dist.items():
            color = type_colors.get(t, "#636e72")
            parts.append(f'<span class="bd" style="background:{color};color:#fff">{t}: {count}</span>')
        parts.append('</div>')

    # STRONG_BUY table
    if strong_buys:
        parts.append(f'<h3>🔴 {_t("strong_buy", L)} — Top 12</h3>')
        parts.append(f'<table><tr><th>#</th><th>{_t("product", L)}</th><th>{_t("price", L)}</th>'
                      f'<th>{_t("viability", L)}</th><th>{_t("product_type", L)}</th>'
                      f'<th>🔄</th><th>📦</th><th>📸</th><th>🎵</th></tr>')
        for i, w in enumerate(strong_buys[:12], 1):
            viab = w.get("viability", 0)
            bar_w = min(viab * 2, 100)
            parts.append(
                f'<tr><td>{i}</td>'
                f'<td style="max-width:250px">{_esc(_tr(w.get("title", ""), 50))}</td>'
                f'<td>{_fp(w.get("price", 0))}</td>'
                f'<td><div class="bar-bg"><div class="bar-fill" style="width:{bar_w}%;background:#00b894">{viab:.0f}</div></div></td>'
                f'<td style="font-size:.75em">{_esc(w.get("type", ""))}</td>'
                f'<td>{w.get("repeat_score", 0)}</td>'
                f'<td>{w.get("bundle_score", 0)}</td>'
                f'<td>{w.get("ugc_score", 0)}</td>'
                f'<td>{w.get("tiktok_score", 0)}</td></tr>'
            )
        parts.append('</table>')

    # BUY summary
    if buys:
        parts.append(f'<h3>🟡 {_t("buy", L)} — Top 8</h3>')
        parts.append('<table><tr><th>#</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>'.format(
            _t("product", L), _t("price", L), _t("viability", L), _t("product_type", L)))
        for i, w in enumerate(buys[:8], 1):
            parts.append(
                f'<tr><td>{i}</td>'
                f'<td>{_esc(_tr(w.get("title", ""), 45))}</td>'
                f'<td>{_fp(w.get("price", 0))}</td>'
                f'<td>{w.get("viability", 0):.0f}</td>'
                f'<td style="font-size:.75em">{_esc(w.get("type", ""))}</td></tr>'
            )
        parts.append('</table>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_niche_matrix(niche_scores: dict, lang: str) -> str:
    L = lang
    if not niche_scores:
        return ""

    sorted_n = sorted(niche_scores.values(), key=lambda x: x["total"], reverse=True)

    parts = [
        '<div class="card">',
        f'<h2>📐 {_t("niche_matrix", L)}</h2>',
        '<table>',
        f'<tr><th>{_t("niche", L)}</th><th class="ac">{_t("trend", L)}</th><th class="ac">{_t("demand_col", L)}</th>'
        f'<th class="ac">{_t("source_col", L)}</th><th class="ac">{_t("validation", L)}</th>'
        f'<th class="ac">Total</th><th class="ac">{_t("grade", L)}</th></tr>',
    ]

    for ns in sorted_n:
        name = _esc(ns["name"].replace("_", " ").title())
        grade = ns["grade"]
        g_bg = _grade_bg(grade)

        parts.append(
            f'<tr>'
            f'<td><b>{name}</b></td>'
            f'<td>{_bar(ns["trend_score"], 25, "#74b9ff")}</td>'
            f'<td>{_bar(ns["demand_score"], 25, "#00b894")}</td>'
            f'<td>{_bar(ns["source_score"], 25, "#fdcb6e")}</td>'
            f'<td>{_bar(ns["validation_score"], 25, "#e17055")}</td>'
            f'<td class="ac"><b>{ns["total"]}/100</b></td>'
            f'<td class="ac"><span class="gr" style="background:{g_bg}">{_esc(grade)}</span></td>'
            f'</tr>'
        )

    parts.append('</table>')
    parts.append(f'<p style="color:#636e72;font-size:.8em;margin-top:8px">{_t("grades_legend", L)}</p>')
    parts.append('</div>')
    return "\n".join(parts)


def _html_actions(analysis: dict, lang: str) -> str:
    L = lang
    sources = analysis.get("sources", {})
    amazon = analysis.get("amazon", {})
    ebay = analysis.get("ebay", {})
    demand = analysis.get("demand", {})
    cross_refs = analysis.get("cross_references", [])

    high, monitor, fix = [], [], []

    candidates = amazon.get("dropship_candidates", [])
    if candidates:
        top = candidates[0]
        high.append(
            f'{_t("research_top", L)}: "<b>{_esc(_tr(top["title"], 35))}</b>" '
            f'(Score: {top.get("dropship_score",0)}/100, {_fp(top.get("price_usd"))})'
        )
    if len(candidates) > 5:
        high.append(f'{_t("review_all", L)} {len(candidates)} {_t("candidates_label", L).lower()}')

    if cross_refs:
        viable = [r for r in cross_refs if r.get("profit_viable")]
        if viable:
            high.append(f'{_t("act_viable", L)} {len(viable)} {_t("multi_profit", L)}')
        else:
            high.append(f'{_t("deep_dive", L)} {len(cross_refs)} {_t("multi_products", L)}')

    if ebay.get("top_sellers"):
        ts = ebay["top_sellers"][0]
        high.append(
            f'eBay {_t("validates", L)} "<b>{_esc(ts["keyword"])}</b>" — '
            f'{ts.get("sold_count",0)} {_t("sales_at_avg", L)} {_fp(ts.get("avg_price"))}'
        )

    if demand.get("top_discoveries"):
        count = len(demand["top_discoveries"])
        high.append(f'{_t("explore_ideas", L)} {count} {_t("new_ideas_from", L)}')

    movers = amazon.get("movers", [])
    if movers:
        monitor.append(f'{_t("track_movers", L)} {len(movers)} {_t("amazon_movers", L)}')
    rising = amazon.get("rising_products", [])
    if rising:
        monitor.append(f'{_t("watch_rising", L)} {len(rising)} {_t("rising_bsr", L)}')

    fix_hints = {
        "trends":      ("Google Trends", _t("add_proxy", L)),
        "aliexpress":  ("AliExpress",    _t("add_proxy", L)),
        "demand":      ("Amazon Demand", f'{_t("run_cmd", L)}: python amazon_demand.py'),
        "ebay":        ("eBay Sold",     f'{_t("run_cmd", L)}: python ebay_scanner.py'),
        "competitors": ("Competitors",   _t("add_stores", L)),
    }
    for key, (name, hint) in fix_hints.items():
        if not sources.get(key, {}).get("active"):
            fix.append(f'{name} {_t("inactive_hint", L)} {hint}')

    parts = ['<div class="card">', f'<h2>⚡ {_t("actions", L)}</h2>']

    if high:
        parts.append(f'<h3 style="color:#e17055">🔴 {_t("high_priority", L)}</h3>')
        for i, a in enumerate(high, 1):
            parts.append(f'<div class="act-h">{i}. {a}</div>')

    if monitor:
        parts.append(f'<h3 style="color:#fdcb6e">🟡 {_t("monitor", L)}</h3>')
        for a in monitor:
            parts.append(f'<div class="act-m">• {a}</div>')

    if fix:
        parts.append(f'<h3 style="color:#636e72">⚠ {_t("fix", L)}</h3>')
        for a in fix:
            parts.append(f'<div class="act-f">⚠ {a}</div>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_footer(today: str, lang: str) -> str:
    L = lang
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f'''<div class="footer">
<p>{_t("generated", L)}: {now}</p>
<p>Signal Pilot — Dropship Intelligence Engine v4</p>
<p>{_t("cost_footer", L)}</p>
</div>'''


# ── Main ─────────────────────────────────────────────────────


def generate_html_report(analysis: dict, today: str, lang: str = "sq") -> str:
    """
    Generate a complete styled HTML intelligence report.

    Args:
        analysis: Full analysis dict from intelligence engine
        today: Date string (YYYY-MM-DD)
        lang: "en" for English, "sq" for Albanian (default)

    Returns:
        Complete HTML string
    """
    sources = analysis.get("sources", {})
    html_lang = "en" if lang == "en" else "sq"

    parts = [
        "<!DOCTYPE html>",
        f'<html lang="{html_lang}">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">',
        f"<title>Intelligence Report — {_esc(today)} ({html_lang.upper()})</title>",
        f"<style>{CSS}</style>",
        "</head>",
        "<body>",
        '<div class="c">',
        _html_header(today, sources, analysis, lang),
        _html_sources(sources, lang),
        _html_winners(analysis, lang),
        _html_cross_refs(analysis.get("cross_references", []), lang),
        _html_tiktok(analysis.get("tiktok", {}), lang),
        _html_adspy(analysis.get("adspy", {}), lang),
        _html_amazon(analysis.get("amazon", {}), lang),
        _html_ebay(analysis.get("ebay", {}), lang),
        _html_demand(analysis.get("demand", {}), lang),
        _html_trends(analysis.get("trends", {}), lang),
        _html_aliexpress(analysis.get("aliexpress", {}), lang),
        _html_competitors(analysis.get("competitors", {}), lang),
        _html_niche_matrix(analysis.get("niche_scores", {}), lang),
        _html_actions(analysis, lang),
        _html_footer(today, lang),
        "</div>",
        "</body>",
        "</html>",
    ]
    return "\n".join(parts)
