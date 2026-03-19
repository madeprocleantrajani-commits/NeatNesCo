"""
Winner Analyzer v1
-------------------
Deep analysis of all candidates for long-term business viability.
Evaluates EVERY candidate across 6 dimensions:
  1. Repeat Purchase Potential — Will customers buy again?
  2. Bundle Potential — Can we sell complementary products?
  3. UGC Content Potential — Will it go viral on TikTok/IG?
  4. Early Trend Detection — Is this product about to explode?
  5. Ad Intelligence — Are competitors advertising this?
  6. Cross-Source Validation — How many sources confirm demand?

Sends TOP WINNERS to Telegram with full reasoning.
Outputs: data/winners_YYYY-MM-DD.json
"""
import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR, SEED_KEYWORDS, get_logger, is_major_brand
from alert_bot import send_alert, send_document

log = get_logger("winner_analyzer")

# Memory system (SQLite) — optional, degrades gracefully
try:
    from memory_system import BotMemory
    mem = BotMemory()
except Exception:
    mem = None


# ── Keyword Dictionaries ──────────────────────────────

REPEAT_KEYWORDS = [
    "filter", "refill", "replacement", "pack", "supply", "wipe",
    "bag", "sheet", "tablet", "cartridge", "pod", "strip",
    "battery", "bulb", "brush head", "pad", "liner", "roll",
    "treats", "food", "supplement", "vitamin", "serum", "cream",
    "toothbrush", "floss", "sponge", "cloth", "detergent",
    "soap", "shampoo", "conditioner", "lotion", "moisturizer",
    "capsule", "powder", "spray", "gel", "tape", "bandage",
    "litter", "pellet", "grain", "seed", "fertilizer",
]

BUNDLE_KEYWORDS = [
    "set", "kit", "pack", "combo", "bundle", "collection",
    "organizer", "system", "multi", "accessory", "accessories",
    "tool", "band", "mat", "roller", "bottle", "light",
    "holder", "rack", "stand", "case", "cover", "pouch",
    "starter", "complete", "all-in-one", "deluxe", "premium",
    "with", "includes", "piece", "count",
]

UGC_KEYWORDS = [
    "before after", "transformation", "satisfying", "oddly",
    "unboxing", "review", "demo", "how to", "tutorial",
    "fitness", "workout", "beauty", "skin", "hair", "glow",
    "clean", "organize", "makeover", "hack", "diy",
    "kitchen", "cooking", "gadget", "cool", "smart",
    "pet", "dog", "cat", "baby", "kid",
    "shower", "light", "led", "spray", "roller",
    "massager", "scrub", "foam", "bubble", "color",
    "aroma", "scent", "candle", "diffuser",
    "magnetic", "portable", "mini", "compact",
    "reusable", "eco", "bamboo", "organic",
]

UGC_CATEGORIES = ["beauty", "fitness", "kitchen", "pet", "home", "baby", "eco"]

# ── Product DNA Keywords ──────────────────────────────

WOW_FACTOR_KEYWORDS = [
    "unique", "innovative", "patented", "first", "only", "new",
    "revolutionary", "never seen", "game changer", "amazing",
    "genius", "brilliant", "clever", "smart", "automatic",
    "magnetic", "self-cleaning", "rechargeable", "wireless",
    "2-in-1", "3-in-1", "all-in-one", "multi-function",
    "foldable", "collapsible", "telescopic", "adjustable",
    "360", "waterproof", "shockproof", "unbreakable",
    "glow", "color changing", "rgb", "led", "laser",
]

PROBLEM_SOLVING_KEYWORDS = [
    "finally", "life saver", "game changer", "must have",
    "essential", "never without", "can't live without",
    "problem solved", "no more", "stop", "prevent",
    "fix", "solution", "relief", "pain", "comfort",
    "protect", "save time", "easy", "effortless", "instant",
    "quick", "fast", "simple", "one touch", "one click",
    "hands free", "mess free", "hassle free", "odor free",
    "anti", "non-slip", "no spill", "stain resistant",
    "noise cancelling", "temperature control",
]

# Products with high return risk (avoid these categories)
HIGH_RETURN_CATEGORIES = [
    "clothing", "shoes", "apparel", "dress", "shirt", "pants",
    "jeans", "jacket", "coat", "sweater", "underwear", "bra",
    "swimwear", "bikini",
]

# Small/light products = cheap shipping = better margins
SHIPPING_FRIENDLY_KEYWORDS = [
    "mini", "compact", "portable", "lightweight", "small",
    "pocket", "travel", "foldable", "slim", "thin", "tiny",
    "micro", "clip", "keychain", "pen", "card",
]

# Heavy/bulky products = expensive shipping = lower margins
SHIPPING_UNFRIENDLY_KEYWORDS = [
    "large", "heavy", "oversized", "jumbo", "king size",
    "full size", "professional grade", "industrial",
    "furniture", "mattress", "chair", "table", "shelf",
    "cabinet", "rack", "tower", "stand",
]

SEASONAL_KEYWORDS = {
    "summer": ["fan", "cooling", "ice", "beach", "pool", "outdoor", "camping",
               "sunscreen", "sun", "water bottle", "portable"],
    "winter": ["heater", "blanket", "warm", "thermal", "heated", "cozy",
               "humidifier", "tea", "soup"],
    "holiday": ["gift", "christmas", "holiday", "stocking", "present",
                "party", "decoration", "ornament"],
    "school": ["backpack", "pencil", "notebook", "desk", "study",
               "organizer", "planner", "lamp"],
}


def score_wow_factor(title: str) -> tuple[int, list]:
    """Score how 'wow' / unique the product is (0-100)."""
    t = title.lower()
    hits = [kw for kw in WOW_FACTOR_KEYWORDS if kw in t]
    score = min(len(hits) * 18, 100)
    return score, hits


def score_problem_solving(title: str) -> tuple[int, list]:
    """Score how strongly the product solves a real problem (0-100)."""
    t = title.lower()
    hits = [kw for kw in PROBLEM_SOLVING_KEYWORDS if kw in t]
    score = min(len(hits) * 20, 100)
    return score, hits


def score_shipping(title: str) -> tuple[int, list]:
    """Score shipping feasibility (0-100). Higher = easier to ship."""
    t = title.lower()
    friendly = [kw for kw in SHIPPING_FRIENDLY_KEYWORDS if kw in t]
    unfriendly = [kw for kw in SHIPPING_UNFRIENDLY_KEYWORDS if kw in t]

    score = 50  # neutral baseline
    score += len(friendly) * 15
    score -= len(unfriendly) * 20
    score = max(0, min(100, score))
    reasons = friendly + [f"HEAVY:{kw}" for kw in unfriendly]
    return score, reasons


def score_return_risk(title: str, category: str = "") -> tuple[int, list]:
    """Score return risk (0-100). Higher = MORE risky."""
    t = (title + " " + category).lower()
    hits = [kw for kw in HIGH_RETURN_CATEGORIES if kw in t]
    score = min(len(hits) * 30, 100)
    return score, hits


def calculate_dna_score(wow: int, problem: int, shipping: int,
                        return_risk: int) -> int:
    """
    Product DNA Score — how well does this product fit the dropship model?

    Formula:
      DNA = wow_factor * 0.30 + problem_solving * 0.30 +
            shipping_feasibility * 0.25 + (100 - return_risk) * 0.15
    """
    dna = (
        wow * 0.30 +
        problem * 0.30 +
        shipping * 0.25 +
        (100 - return_risk) * 0.15
    )
    return round(dna)


def _load_latest_json(prefix: str) -> dict | None:
    """Load the most recent JSON data file with given prefix."""
    files = sorted(DATA_DIR.glob(f"{prefix}_*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def score_repeat(title: str) -> tuple[int, list]:
    """Score repeat purchase potential (0-100)."""
    t = title.lower()
    hits = sum(1 for kw in REPEAT_KEYWORDS if kw in t)
    score = min(hits * 25, 100)
    reasons = [kw for kw in REPEAT_KEYWORDS if kw in t]
    return score, reasons


def score_bundle(title: str) -> tuple[int, list]:
    """Score bundle/upsell potential (0-100)."""
    t = title.lower()
    hits = sum(1 for kw in BUNDLE_KEYWORDS if kw in t)
    score = min(hits * 20, 100)
    reasons = [kw for kw in BUNDLE_KEYWORDS if kw in t]
    return score, reasons


def score_ugc(title: str, category: str = "") -> tuple[int, list]:
    """Score UGC/viral content potential (0-100)."""
    t = (title + " " + category).lower()
    hits = sum(1 for kw in UGC_KEYWORDS if kw in t)
    cat_bonus = 15 if any(c in category.lower() for c in UGC_CATEGORIES) else 0
    score = min(hits * 12 + cat_bonus, 100)
    reasons = [kw for kw in UGC_KEYWORDS if kw in t]
    return score, reasons


def score_seasonal(title: str) -> tuple[str, int]:
    """Detect seasonal dependency and score risk."""
    t = title.lower()
    for season, keywords in SEASONAL_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in t)
        if matches >= 2:
            return season, matches * 20
    return "evergreen", 0


def check_trend_match(title: str, trends_data: dict | None) -> tuple[bool, str, float]:
    """Check if product matches any trending keyword."""
    if not trends_data:
        return False, "", 0

    t = title.lower()
    for h in trends_data.get("hot_products", []):
        kw = h.get("keyword", "")
        if any(word in t for word in kw.lower().split() if len(word) > 3):
            return True, kw, h.get("current_interest", 0)
    for e in trends_data.get("emerging_products", []):
        kw = e.get("keyword", "")
        if any(word in t for word in kw.lower().split() if len(word) > 3):
            return True, kw, e.get("current_interest", 0)
    return False, "", 0


def check_tiktok_match(title: str, tiktok_data: dict | None) -> tuple[bool, int]:
    """Check if product has TikTok viral validation."""
    if not tiktok_data:
        return False, 0

    t = title.lower()
    tiktok_score = 0

    # Check against TikTok viral products
    for p in tiktok_data.get("top_picks", []):
        p_title = p.get("title", "").lower()
        # Word overlap check
        title_words = set(w for w in t.split() if len(w) > 3)
        pick_words = set(w for w in p_title.split() if len(w) > 3)
        overlap = len(title_words & pick_words)
        if overlap >= 2:
            tiktok_score = max(tiktok_score, p.get("tiktok_score", 0))

    # Check against TikTok trend suggestions
    for s in tiktok_data.get("trend_suggestions", []):
        kw = s.get("product_keyword", "").lower()
        if kw and len(kw) > 3 and kw in t:
            tiktok_score = max(tiktok_score, 30)

    return tiktok_score > 0, tiktok_score


def check_ad_validation(title: str, adspy_data: dict | None) -> tuple[bool, int]:
    """Check if product has advertising validation (competitors are spending on ads)."""
    if not adspy_data:
        return False, 0

    t = title.lower()
    ad_score = 0

    # Check ad intelligence
    for intel in adspy_data.get("intelligence", []):
        kw = intel.get("keyword", "").lower()
        if kw and any(word in t for word in kw.split() if len(word) > 3):
            ad_score = max(ad_score, intel.get("ad_score", 0))

    # Check Amazon sponsored
    for sp in adspy_data.get("amazon_sponsored", []):
        sp_title = sp.get("title", "").lower()
        title_words = set(w for w in t.split() if len(w) > 3)
        sp_words = set(w for w in sp_title.split() if len(w) > 3)
        if len(title_words & sp_words) >= 2:
            ad_score = max(ad_score, 25)

    return ad_score > 0, ad_score


def run_winner_analysis() -> dict:
    """Run complete winner analysis across all data sources."""
    log.info("=" * 60)
    log.info("WINNER ANALYZER — Deep Product Analysis")
    log.info("=" * 60)

    # Load all available data
    analysis_data = _load_latest_json("analysis")
    trends_data = _load_latest_json("trends")
    tiktok_data = _load_latest_json("tiktok")
    adspy_data = _load_latest_json("adspy")
    demand_data = _load_latest_json("demand")
    saturation_data = _load_latest_json("saturation")

    if not analysis_data:
        log.error("No analysis data found! Run intelligence.py first.")
        return {"status": "no_data"}

    candidates = analysis_data.get("amazon", {}).get("dropship_candidates", [])
    cross_refs = analysis_data.get("cross_references", [])
    trends = analysis_data.get("trends", {})

    log.info(f"Analyzing: {len(candidates)} candidates, {len(cross_refs)} cross-refs")

    # Merge candidates with cross-refs for richer data
    all_products = {}
    for c in candidates:
        key = c.get("asin") or c.get("title", "")[:50]
        all_products[key] = c.copy()

    for cr in cross_refs:
        key = cr.get("title", "")[:50]
        if key not in all_products:
            all_products[key] = cr.copy()
        else:
            # Merge cross-ref signals into existing candidate
            all_products[key]["signal_count"] = cr.get("signal_count", 1)
            all_products[key]["signals"] = cr.get("signals", [])
            all_products[key]["profit_viable"] = cr.get("profit_viable", False)
            all_products[key]["real_profit"] = cr.get("real_profit", 0)
            all_products[key]["margin_pct"] = cr.get("margin_pct", 0)

    # Analyze ALL products — filter out brands and invalid data first
    winners = []
    skipped_brand = 0
    skipped_price = 0
    for key, product in all_products.items():
        title = product.get("title", "")
        cat = product.get("category", product.get("amazon_category", ""))
        price = product.get("price_usd", product.get("amazon_price_usd", 0)) or 0
        score = product.get("dropship_score", 0)
        rating = product.get("rating", product.get("amazon_rating", 0)) or 0
        reviews = product.get("review_count", 0) or 0
        signals = product.get("signals", [])
        signal_count = product.get("signal_count", 1)

        # FILTER: Skip branded products (trademark risk)
        if is_major_brand(title) or product.get("is_brand", False):
            skipped_brand += 1
            continue

        # FILTER: Skip products with no price or too cheap (bad data / no margin)
        if price < 15:
            skipped_price += 1
            continue

        # Score all dimensions
        rep_score, rep_reasons = score_repeat(title)
        bun_score, bun_reasons = score_bundle(title)
        ugc_score, ugc_reasons = score_ugc(title, cat)
        season, season_risk = score_seasonal(title)
        is_trend, trend_kw, trend_interest = check_trend_match(title, trends_data)
        is_tiktok, tiktok_score = check_tiktok_match(title, tiktok_data)
        is_ad_validated, ad_score = check_ad_validation(title, adspy_data)

        # Product DNA scoring
        wow_score, wow_reasons = score_wow_factor(title)
        problem_score, problem_reasons = score_problem_solving(title)
        ship_score, ship_reasons = score_shipping(title)
        return_risk, return_reasons = score_return_risk(title, cat)
        dna_score = calculate_dna_score(wow_score, problem_score, ship_score, return_risk)

        # Saturation check — penalize saturated products
        saturation_penalty = 0
        saturation_level = "unknown"
        if saturation_data:
            for kw, sat in saturation_data.get("results", {}).items():
                kw_words = set(w.lower() for w in kw.split() if len(w) > 3)
                title_words = set(w.lower() for w in title.split() if len(w) > 3)
                if len(kw_words & title_words) >= 2:
                    saturation_level = sat.get("level", "unknown")
                    if saturation_level == "SATURATED":
                        saturation_penalty = 25
                    elif saturation_level == "HIGH_COMPETITION":
                        saturation_penalty = 10
                    break

        # Momentum bonus from trend scanner
        momentum_bonus = 0
        momentum_status = "unknown"
        if trends_data:
            for niche_data in trends_data.get("niches", {}).values():
                for kw, kw_data in niche_data.get("keywords", {}).items():
                    if any(w in title.lower() for w in kw.lower().split() if len(w) > 3):
                        momentum_status = kw_data.get("momentum_status", "unknown")
                        m_score = kw_data.get("momentum_score", 0)
                        if momentum_status == "accelerating":
                            momentum_bonus = min(m_score * 0.15, 12)
                        elif momentum_status == "steady_up":
                            momentum_bonus = min(m_score * 0.08, 6)
                        break

        # Combined VIABILITY score (weighted) — now includes DNA + saturation + momentum
        viability = (
            score * 0.15 +               # dropship score (Amazon BSR + multi-source)
            rep_score * 0.10 +            # repeat purchase potential
            bun_score * 0.05 +            # bundle/upsell potential
            ugc_score * 0.12 +            # UGC/viral content potential
            (30 if is_trend else 0) * 0.08 +  # Google Trends match
            tiktok_score * 0.12 +         # TikTok viral validation
            ad_score * 0.08 +             # Ad spend validation
            dna_score * 0.15 +            # Product DNA (wow + problem + shipping)
            (signal_count * 8) * 0.05 +   # Multi-source confirmation bonus
            momentum_bonus                # Trend acceleration bonus
        )

        # Penalties
        viability -= saturation_penalty

        # Season penalty for seasonal products
        if season != "evergreen":
            viability *= 0.85  # 15% penalty for seasonal

        # Return risk penalty
        if return_risk >= 60:
            viability *= 0.90  # 10% penalty for high return risk

        # Product type classification
        product_type = []
        if rep_score >= 25:
            product_type.append("REPEAT")
        if bun_score >= 20:
            product_type.append("BUNDLE")
        if ugc_score >= 25:
            product_type.append("UGC")
        if is_trend:
            product_type.append("TREND")
        if is_tiktok:
            product_type.append("TIKTOK")
        if is_ad_validated:
            product_type.append("AD_PROVEN")
        if not product_type:
            product_type.append("SHORT-TERM")

        # Count REAL signals (not just keyword matches — actual multi-platform validation)
        real_signals = 0
        if is_trend:
            real_signals += 1
        if is_tiktok:
            real_signals += 1
        if is_ad_validated:
            real_signals += 1
        if signal_count >= 2:
            real_signals += 1  # Cross-referenced across sources
        if product.get("profit_viable"):
            real_signals += 1

        # Business model recommendation — stricter thresholds
        # STRONG_BUY: 3+ types, 2+ real signals, viability 40+, price $15+
        if (len(product_type) >= 3 and "SHORT-TERM" not in product_type
                and real_signals >= 2 and viability >= 40 and price >= 15):
            recommendation = "STRONG_BUY"
        elif (len(product_type) >= 2 and "SHORT-TERM" not in product_type
              and real_signals >= 1 and viability >= 25 and price >= 15):
            recommendation = "BUY"
        elif viability >= 15:
            recommendation = "WATCH"
        else:
            recommendation = "SKIP"

        winners.append({
            "title": title[:80],
            "price": price,
            "score": score,
            "rating": rating,
            "reviews": reviews,
            "category": cat,
            "asin": product.get("asin", ""),
            "url": product.get("url", ""),
            # Dimension scores
            "repeat_score": rep_score,
            "bundle_score": bun_score,
            "ugc_score": ugc_score,
            "tiktok_score": tiktok_score,
            "ad_score": ad_score,
            # Product DNA
            "dna_score": dna_score,
            "wow_factor": wow_score,
            "problem_solving": problem_score,
            "shipping_score": ship_score,
            "return_risk": return_risk,
            # Saturation
            "saturation_level": saturation_level,
            "saturation_penalty": saturation_penalty,
            # Momentum
            "momentum_status": momentum_status,
            "momentum_bonus": round(momentum_bonus, 1),
            # Trend data
            "is_trend": is_trend,
            "trend_keyword": trend_kw,
            "is_tiktok": is_tiktok,
            "is_ad_validated": is_ad_validated,
            "real_signals": real_signals,
            # Season
            "season": season,
            "season_risk": season_risk,
            # Multi-source
            "signal_count": signal_count,
            "signals": signals,
            "profit_viable": product.get("profit_viable", False),
            "real_profit": product.get("real_profit", 0),
            "margin_pct": product.get("margin_pct", 0),
            # Final scores
            "viability": round(max(0, viability), 1),
            "type": " + ".join(product_type),
            "recommendation": recommendation,
            # Reasons
            "rep_reasons": rep_reasons,
            "bun_reasons": bun_reasons,
            "ugc_reasons": ugc_reasons,
            "wow_reasons": wow_reasons,
            "problem_reasons": problem_reasons,
            "ship_reasons": ship_reasons,
        })

    log.info(f"Filtered out: {skipped_brand} branded, {skipped_price} no-price")

    # Deduplicate — keep highest viability per product title
    seen_titles = {}
    unique_winners = []
    for w in winners:
        # Normalize title for dedup (first 40 chars, lowercase)
        norm_title = w["title"][:40].lower().strip()
        if norm_title in seen_titles:
            # Keep the one with higher viability
            if w["viability"] > seen_titles[norm_title]["viability"]:
                unique_winners.remove(seen_titles[norm_title])
                unique_winners.append(w)
                seen_titles[norm_title] = w
        else:
            seen_titles[norm_title] = w
            unique_winners.append(w)

    deduped = len(winners) - len(unique_winners)
    if deduped:
        log.info(f"Deduplicated: {deduped} duplicate products removed")
    winners = unique_winners

    # Sort by viability
    winners.sort(key=lambda x: x["viability"], reverse=True)

    # Save to SQLite memory — decisions + scores for every BUY/STRONG_BUY
    if mem:
        mem_saved = 0
        for w in winners:
            if w["recommendation"] in ("STRONG_BUY", "BUY", "WATCH"):
                try:
                    pid = mem.save_product(
                        title=w["title"],
                        source="winner_analyzer",
                        asin=w.get("asin", ""),
                        score=w["viability"],
                    )
                    mem.log_decision(
                        "winner_analyzer", pid, w["recommendation"],
                        reason=f"V:{w['viability']:.0f} | {w['type']} | Sig:{w.get('real_signals',0)}",
                        confidence=w.get("real_signals", 0),
                    )
                    mem.log_score(
                        pid, w["viability"],
                        demand_pts=w.get("tiktok_score", 0) + (10 if w.get("is_trend") else 0),
                        financial_pts=w.get("margin_pct", 0),
                        supply_pts=w.get("signal_count", 0) * 10,
                        risk_pts=-w.get("saturation_penalty", 0),
                        confidence=w.get("real_signals", 0),
                        sources=w.get("signals", []),
                    )
                    mem_saved += 1
                except Exception:
                    pass
        log.info(f"[memory] Saved {mem_saved} products to SQLite")

    # Build report
    strong_buys = [w for w in winners if w["recommendation"] == "STRONG_BUY"]
    buys = [w for w in winners if w["recommendation"] == "BUY"]
    watches = [w for w in winners if w["recommendation"] == "WATCH"]

    report = {
        "scan_date": datetime.now().isoformat(),
        "total_analyzed": len(winners),
        "strong_buys": strong_buys,
        "buys": buys,
        "watches": watches[:30],
        "all_winners": winners,
        "stats": {
            "total_products": len(winners),
            "strong_buy_count": len(strong_buys),
            "buy_count": len(buys),
            "watch_count": len(watches),
            "repeat_champions": len([w for w in winners if w["repeat_score"] >= 25]),
            "bundle_candidates": len([w for w in winners if w["bundle_score"] >= 20]),
            "ugc_superstars": len([w for w in winners if w["ugc_score"] >= 25]),
            "tiktok_validated": len([w for w in winners if w["is_tiktok"]]),
            "ad_proven": len([w for w in winners if w["is_ad_validated"]]),
            "trend_matches": len([w for w in winners if w["is_trend"]]),
            "evergreen": len([w for w in winners if w["season"] == "evergreen"]),
            "avg_viability": round(
                sum(w["viability"] for w in winners) / max(1, len(winners)), 1
            ),
        },
        "type_distribution": {},
    }

    # Type distribution
    types = {}
    for w in winners:
        for t in w["type"].split(" + "):
            types[t] = types.get(t, 0) + 1
    report["type_distribution"] = dict(sorted(types.items(), key=lambda x: -x[1]))

    # Save report
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"winners_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Winner report saved: {output_file}")
    log.info(
        f"STRONG_BUY: {len(strong_buys)} | BUY: {len(buys)} | "
        f"WATCH: {len(watches)} | Total: {len(winners)}"
    )

    # ── Send Results to Telegram ──────────────────────
    _send_telegram_report(report, today)

    # ── Record metrics for tracking development ──────
    try:
        from metrics_tracker import record_daily_snapshot, update_product_history
        record_daily_snapshot()
        update_product_history()
        log.info("Metrics snapshot recorded")
    except Exception as e:
        log.warning(f"Metrics recording failed (non-critical): {e}")

    return report


def _send_telegram_report(report: dict, today: str):
    """Send winner analysis results to Telegram with full detail."""
    stats = report["stats"]
    strong_buys = report["strong_buys"]
    buys = report["buys"]

    msg = (
        f"🏆 <b>WINNER ANALYSIS COMPLETE</b>\n"
        f"📅 {today}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    # Summary stats
    msg += (
        f"📊 <b>OVERVIEW</b>\n"
        f"  Products analyzed: {stats['total_products']}\n"
        f"  🔴 STRONG BUY: {stats['strong_buy_count']}\n"
        f"  🟡 BUY: {stats['buy_count']}\n"
        f"  🔵 WATCH: {stats['watch_count']}\n"
        f"  Avg viability: {stats['avg_viability']}\n\n"
    )

    # Type distribution
    msg += "📋 <b>TYPE DISTRIBUTION</b>\n"
    for t, count in report["type_distribution"].items():
        emoji = {
            "REPEAT": "🔄", "BUNDLE": "📦", "UGC": "📸",
            "TREND": "📈", "TIKTOK": "🎵", "AD_PROVEN": "💰",
            "SHORT-TERM": "⏳",
        }.get(t, "•")
        msg += f"  {emoji} {t}: {count}\n"

    msg += "\n"

    # STRONG BUY products
    if strong_buys:
        msg += f"🔴 <b>STRONG BUY — Top {min(8, len(strong_buys))} Winners</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, w in enumerate(strong_buys[:8], 1):
            msg += (
                f"\n<b>#{i} [{w['type']}]</b>\n"
                f"  {w['title'][:55]}\n"
                f"  💲{w['price']:.2f} | V:{w['viability']:.0f} | "
                f"⭐{w['rating']:.1f} | 📝{w['reviews']:,}\n"
            )
            details = []
            if w['repeat_score'] > 0:
                details.append(f"🔄Rep:{w['repeat_score']}")
            if w['bundle_score'] > 0:
                details.append(f"📦Bun:{w['bundle_score']}")
            if w['ugc_score'] > 0:
                details.append(f"📸UGC:{w['ugc_score']}")
            if w['is_tiktok']:
                details.append(f"🎵TT:{w['tiktok_score']}")
            if w['is_ad_validated']:
                details.append(f"💰Ad:{w['ad_score']}")
            if w['is_trend']:
                details.append(f"📈{w['trend_keyword'][:15]}")
            if details:
                msg += f"  {' | '.join(details)}\n"
            if w['profit_viable']:
                msg += f"  ✅ Profit: ${w['real_profit']:.2f} ({w['margin_pct']:.0f}%)\n"

    # BUY products (condensed)
    if buys:
        msg += f"\n🟡 <b>BUY — Top {min(8, len(buys))}</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, w in enumerate(buys[:8], 1):
            msg += (
                f"  {i}. <b>{w['title'][:45]}</b>\n"
                f"     ${w['price']:.2f} | V:{w['viability']:.0f} | [{w['type']}]\n"
            )

    # Key insights
    msg += "\n💡 <b>KEY INSIGHTS</b>\n"
    if stats["repeat_champions"] > 0:
        msg += f"  🔄 {stats['repeat_champions']} products with repeat purchase potential\n"
    if stats["tiktok_validated"] > 0:
        msg += f"  🎵 {stats['tiktok_validated']} TikTok-validated products\n"
    if stats["ad_proven"] > 0:
        msg += f"  💰 {stats['ad_proven']} products with active ad spend\n"
    if stats["trend_matches"] > 0:
        msg += f"  📈 {stats['trend_matches']} trending products detected\n"
    msg += f"  🌿 {stats['evergreen']} evergreen (non-seasonal) products\n"

    msg += f"\n📁 <code>data/winners_{today}.json</code>"

    send_alert(msg, parse_mode="HTML")
    log.info("Winner analysis sent to Telegram")


if __name__ == "__main__":
    run_winner_analysis()
