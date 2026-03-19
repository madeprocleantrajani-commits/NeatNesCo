"""
Shopify Product Importer v4
──────────────────────────────
Connects intelligence → business action.

Reads winner analysis data, selects the TOP products each day,
and creates them as DRAFT products in the Shopify store.

v4 changes (rebuilt):
  - Reads from winner_analyzer.py output (no AI API needed)
  - Smart Top-N selector (multi-factor ranking)
  - SEO-friendly title & description generation
  - Retail pricing with proper margins (2.5x-3x)
  - Creates as DRAFT (user reviews before publishing)
  - Duplicate detection (title hash + Shopify existing)
  - Telegram notification with import summary
  - Niche diversification (max 2 per niche)

Outputs: data/imports_YYYY-MM-DD.json
Run: daily after winner_analyzer (cron 11:00 AM)
"""

import json
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path

import requests

from config import DATA_DIR, SHOPIFY_STORE, SHOPIFY_TOKEN, get_logger
from alert_bot import send_alert

log = get_logger("shopify_importer")

# ── Constants ──────────────────────────────────────────────

MAX_IMPORTS_PER_DAY = 5          # Don't flood the store
MIN_VIABILITY_SCORE = 25         # Minimum viability to consider
MARKUP_FACTOR = 2.5              # Default retail markup
PREMIUM_MARKUP = 3.0             # For high-demand products

# Shopify API
SHOPIFY_API_VERSION = "2024-10"

# Import history file (prevents duplicates across days)
IMPORT_HISTORY_FILE = DATA_DIR / "shopify_import_history.json"

# Product type mapping for Shopify
NICHE_TO_TYPE = {
    "home_gadgets":     "Home & Kitchen",
    "fitness":          "Sports & Fitness",
    "pet_products":     "Pet Supplies",
    "tech_accessories": "Electronics & Tech",
    "beauty_health":    "Beauty & Health",
    "outdoor":          "Outdoor & Garden",
    "eco_friendly":     "Eco-Friendly",
    "home_office":      "Home Office",
    "car_accessories":  "Car Accessories",
    "kitchen_gadgets":  "Kitchen & Dining",
}


# ── Shopify API Helpers ────────────────────────────────────

def shopify_request(method: str, endpoint: str, payload: dict = None,
                    _retry: int = 0) -> dict | None:
    """Make a Shopify Admin API request with rate limit retry (max 3)."""
    if not SHOPIFY_STORE or not SHOPIFY_TOKEN:
        log.error("SHOPIFY_STORE or SHOPIFY_TOKEN not set in .env")
        return None

    url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/{endpoint}"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Content-Type": "application/json",
    }

    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=15)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=payload, timeout=15)
        else:
            return None

        if r.status_code in (200, 201):
            return r.json()
        elif r.status_code == 429:
            if _retry >= 3:
                log.error("Shopify rate limit: max retries exhausted")
                return None
            wait = 2 * (_retry + 1)
            log.warning(f"Rate limited, waiting {wait}s (retry {_retry + 1}/3)")
            time.sleep(wait)
            return shopify_request(method, endpoint, payload, _retry + 1)
        else:
            log.error(f"Shopify API {r.status_code}: {r.text[:300]}")
            return None
    except requests.RequestException as e:
        log.error(f"Shopify request failed: {e}")
        return None


def _get_existing_titles() -> set:
    """Get existing product titles from Shopify to prevent duplicates."""
    titles = set()
    result = shopify_request("GET", "products.json?status=any&fields=title&limit=250")
    if result:
        for p in result.get("products", []):
            titles.add(p.get("title", "").lower().strip())
    return titles


# ── History Management ─────────────────────────────────────

def load_import_history() -> dict:
    if IMPORT_HISTORY_FILE.exists():
        try:
            with open(IMPORT_HISTORY_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"imported": {}, "total_imported": 0}


def save_import_history(history: dict):
    with open(IMPORT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)


def _product_hash(title: str) -> str:
    """Create a consistent hash from product title for dedup."""
    clean = re.sub(r'[^a-z0-9\s]', '', title.lower().strip())
    clean = re.sub(r'\s+', ' ', clean)
    return hashlib.md5(clean.encode()).hexdigest()[:12]


# ── Smart Product Selector ─────────────────────────────────

def select_top_products(max_count: int = MAX_IMPORTS_PER_DAY) -> list[dict]:
    """
    Select the absolute best products from today's winner analysis.

    Ranking factors:
      1. Winner classification (STRONG_BUY +30, BUY +15)
      2. Viability score (0-20)
      3. Signal count (0-15)
      4. Profit margin if AliExpress sourced (0-15)
      5. Repeat purchase potential (0-10)
      6. TikTok viral signal (0-5)
      7. Competitor validation (0-5)
      8. NOT already imported
    """
    history = load_import_history()
    imported_hashes = set(history.get("imported", {}).keys())

    today = datetime.now().strftime("%Y-%m-%d")
    winners_file = DATA_DIR / f"winners_{today}.json"
    analysis_file = DATA_DIR / f"analysis_{today}.json"

    if not winners_file.exists():
        log.warning("No winners data found for today")
        return []

    with open(winners_file) as f:
        winners_data = json.load(f)

    # Load cross-reference data for extra signals
    cross_refs = {}
    if analysis_file.exists():
        with open(analysis_file) as f:
            analysis = json.load(f)
        for cr in analysis.get("cross_references", []):
            cr_hash = _product_hash(cr.get("title", ""))
            cross_refs[cr_hash] = cr

    # Combine strong_buys + buys (winners file uses these keys)
    all_winners = []
    for w in winners_data.get("strong_buys", []):
        w["_class"] = "STRONG_BUY"
        all_winners.append(w)
    for w in winners_data.get("buys", []):
        w["_class"] = "BUY"
        all_winners.append(w)

    candidates = []
    for product in all_winners:
        classification = product.get("_class", product.get("recommendation", ""))
        title = product.get("title", "")
        phash = _product_hash(title)

        # Skip already imported
        if phash in imported_hashes:
            continue

        # Viability field name is "viability" in winner_analyzer output
        viability = product.get("viability", product.get("viability_score", 0))
        if viability < MIN_VIABILITY_SCORE:
            continue

        # Get cross-reference data
        cr = cross_refs.get(phash, {})

        # Calculate composite import score
        score = 0.0

        # Classification (0-30)
        score += 30 if classification == "STRONG_BUY" else 15

        # Viability (0-20)
        score += min(viability / 5, 20)

        # Signal count (0-15)
        sig_count = cr.get("signal_count", product.get("signal_count", 0))
        score += min(sig_count * 3, 15)

        # Profit margin (0-15)
        margin = cr.get("margin_pct", product.get("margin_pct", 0))
        if margin >= 60:
            score += 15
        elif margin >= 40:
            score += 10
        elif margin >= 20:
            score += 5

        # Repeat purchase (0-10)
        repeat = product.get("repeat_score", 0)
        score += min(repeat / 10, 10)

        # TikTok viral (0-5)
        prod_signals = cr.get("signals", product.get("signals", []))
        if "tiktok_viral" in prod_signals or product.get("is_tiktok"):
            score += 5

        # Competitor validated (0-5)
        if "competitor_sells" in prod_signals:
            score += 5

        candidates.append({
            "title": title,
            "hash": phash,
            "classification": classification,
            "viability": viability,
            "import_score": round(score, 1),
            "signals": prod_signals,
            "signal_count": sig_count,
            "amazon_price": cr.get("amazon_price_usd") or product.get("price"),
            "source_price": cr.get("source_price"),
            "margin_pct": margin,
            "profit_viable": cr.get("profit_viable", product.get("profit_viable", False)),
            "niche": cr.get("matched_niche") or product.get("category", ""),
            "amazon_category": cr.get("amazon_category", product.get("category", "")),
            "amazon_rating": cr.get("amazon_rating") or product.get("rating"),
            "review_count": cr.get("review_count") or product.get("reviews"),
            "scores": {
                "repeat": product.get("repeat_score", 0),
                "bundle": product.get("bundle_score", 0),
                "ugc": product.get("ugc_score", 0),
            },
        })

    # Sort by import score
    candidates.sort(key=lambda x: -x["import_score"])

    # Diversify: max 2 from same niche
    selected = []
    niche_counts = {}
    for c in candidates:
        niche = c.get("niche", "other") or "other"
        if niche_counts.get(niche, 0) >= 2:
            continue
        selected.append(c)
        niche_counts[niche] = niche_counts.get(niche, 0) + 1
        if len(selected) >= max_count:
            break

    return selected


# ── Title & Description Generators ─────────────────────────

def generate_shopify_title(title: str) -> str:
    """Create a clean Shopify-friendly title (max 70 chars for SEO)."""
    clean = re.sub(r'\s*[\[\(].*?[\]\)]', '', title)
    parts = clean.split(" - ")
    if len(parts) > 2:
        clean = " - ".join(parts[:2])
    if clean.count(",") > 2:
        clean = clean.split(",")[0]
    clean = re.sub(r'\s{2,}', ' ', clean).strip()
    if len(clean) > 70:
        clean = clean[:67] + "..."
    return clean


def generate_description(product: dict) -> str:
    """Generate an SEO-friendly product description."""
    title = product["title"]
    rating = product.get("amazon_rating")
    reviews = product.get("review_count")
    signals = product.get("signals", [])

    parts = []

    # Opening hook
    if "tiktok_viral" in signals:
        parts.append("<p>🔥 <strong>Trending on TikTok!</strong> This viral sensation is flying off the shelves.</p>")
    elif "google_trending" in signals:
        parts.append("<p>📈 <strong>Trending Now!</strong> This product is surging in popularity.</p>")
    elif product.get("classification") == "STRONG_BUY":
        parts.append("<p>⭐ <strong>Top Pick!</strong> Our data shows this product is in high demand.</p>")

    # Clean description
    desc = re.sub(r'\s*[\[\(].*?[\]\)]', '', title)
    desc = re.sub(r'\s{2,}', ' ', desc).strip()
    if len(desc) > 120:
        desc = desc[:117] + "..."
    parts.append(f"<p>{desc}</p>")

    # Social proof
    if rating and reviews:
        try:
            star_count = min(int(float(rating)), 5)
            stars = "⭐" * star_count
            parts.append(f"<p>{stars} Rated {rating}/5 by {int(reviews):,}+ customers</p>")
        except (ValueError, TypeError):
            pass

    # Trust signals
    trust = []
    if "amazon_bestseller" in signals:
        trust.append("Amazon Best Seller")
    if "ebay_validated" in signals:
        trust.append("Proven eBay demand")
    if "competitor_sells" in signals:
        trust.append("Sold by top competitors")
    if "search_demand" in signals:
        trust.append("High search demand")
    if "aliexpress_sourced" in signals:
        trust.append("Verified supplier available")

    if trust:
        parts.append("<p><strong>Why customers love it:</strong></p><ul>")
        for t in trust:
            parts.append(f"<li>✅ {t}</li>")
        parts.append("</ul>")

    # Standard footer
    parts.append(
        "<p>🚚 <strong>Fast & Free Shipping</strong> on all orders</p>"
        "<p>🔄 <strong>30-Day Money-Back Guarantee</strong></p>"
        "<p>📦 <strong>Secure Packaging</strong></p>"
    )

    return "\n".join(parts)


# ── Pricing Engine ─────────────────────────────────────────

def calculate_retail_price(product: dict) -> dict:
    """
    Calculate retail price with proper margins.

    Strategy:
      - If AliExpress source price: 2.5x-3x markup
      - If only Amazon price: match or slightly undercut
      - Psychological pricing (.99, .95)
    """
    source_price = product.get("source_price")
    amazon_price = product.get("amazon_price")

    if source_price and source_price > 0:
        factor = PREMIUM_MARKUP if product.get("classification") == "STRONG_BUY" else MARKUP_FACTOR
        raw_price = source_price * factor

        # Don't exceed Amazon price by much
        if amazon_price and raw_price > amazon_price * 1.1:
            raw_price = amazon_price * 0.95

        retail = _round_price(raw_price)
        compare_at = _round_price(raw_price * 1.3) if retail < 50 else _round_price(raw_price * 1.2)

        return {
            "price": f"{retail:.2f}",
            "compare_at_price": f"{compare_at:.2f}",
            "cost": f"{source_price:.2f}",
            "margin_pct": round(((retail - source_price) / retail) * 100, 1) if retail > 0 else 0,
        }

    elif amazon_price and amazon_price > 0:
        retail = _round_price(amazon_price * 0.90)
        compare_at = _round_price(amazon_price * 1.15)
        return {
            "price": f"{retail:.2f}",
            "compare_at_price": f"{compare_at:.2f}",
            "cost": None,
            "margin_pct": None,
        }

    return {
        "price": "29.99",
        "compare_at_price": "49.99",
        "cost": None,
        "margin_pct": None,
    }


def _round_price(price: float) -> float:
    """Psychological pricing (.99 endings)."""
    if price < 10:
        return max(round(price) - 0.01, 0.99)
    elif price < 50:
        return round(price) - 0.01
    elif price < 100:
        return (round(price / 5) * 5) - 0.05
    else:
        return (round(price / 10) * 10) - 0.01


# ── Create Draft Product ──────────────────────────────────

def create_draft_product(product: dict, pricing: dict, description: str) -> dict | None:
    """Create a DRAFT product in Shopify. Returns product data or None."""
    title = generate_shopify_title(product["title"])
    niche = product.get("niche", "")
    product_type = NICHE_TO_TYPE.get(niche, "General")

    # Tags
    tags = []
    if niche:
        tags.append(niche.replace("_", "-"))
    if product.get("classification") == "STRONG_BUY":
        tags.append("strong-buy")
    else:
        tags.append("buy-signal")

    for sig in product.get("signals", []):
        if sig == "tiktok_viral":
            tags.append("tiktok-trending")
        elif sig == "google_trending":
            tags.append("trending")
        elif sig == "amazon_bestseller":
            tags.append("bestseller")
        elif sig == "competitor_sells":
            tags.append("competitor-validated")

    tags.extend(["dropship-import", f"imported-{datetime.now().strftime('%Y-%m-%d')}"])

    payload = {
        "product": {
            "title": title,
            "body_html": description,
            "vendor": "Neatnestco",
            "product_type": product_type,
            "tags": ", ".join(tags),
            "status": "draft",
            "variants": [
                {
                    "price": pricing["price"],
                    "compare_at_price": pricing["compare_at_price"],
                    "inventory_management": None,
                    "fulfillment_service": "manual",
                    "requires_shipping": True,
                    "taxable": True,
                }
            ],
            "metafields": [
                {
                    "namespace": "intelligence",
                    "key": "import_score",
                    "value": str(product.get("import_score", 0)),
                    "type": "number_decimal",
                },
                {
                    "namespace": "intelligence",
                    "key": "classification",
                    "value": product.get("classification", ""),
                    "type": "single_line_text_field",
                },
                {
                    "namespace": "intelligence",
                    "key": "signals",
                    "value": ", ".join(product.get("signals", []))[:255],
                    "type": "single_line_text_field",
                },
            ],
        }
    }

    if pricing.get("cost"):
        payload["product"]["variants"][0]["cost"] = pricing["cost"]

    result = shopify_request("POST", "products.json", payload)
    if result and "product" in result:
        created = result["product"]
        log.info(f"✓ Created draft: {title} (ID: {created.get('id')})")
        return created
    return None


# ── Main Import Pipeline ───────────────────────────────────

def run_shopify_import():
    """
    Main pipeline:
      1. Test Shopify connection
      2. Select top products from winners
      3. Generate descriptions & pricing
      4. Create drafts in Shopify
      5. Update import history
      6. Send Telegram summary
    """
    log.info("=" * 60)
    log.info("SHOPIFY IMPORTER — Intelligence → Store Pipeline")
    log.info("=" * 60)

    if not SHOPIFY_STORE or not SHOPIFY_TOKEN:
        log.error("Shopify credentials not configured in .env")
        send_alert(
            "⚠️ <b>SHOPIFY IMPORTER</b>\n\n"
            "Credentials not set. Add SHOPIFY_STORE and SHOPIFY_TOKEN to .env",
            parse_mode="HTML",
        )
        return {"status": "error", "reason": "no_credentials"}

    # Test connection
    test = shopify_request("GET", "shop.json")
    if not test:
        log.error("Cannot connect to Shopify — check credentials")
        return {"status": "error", "reason": "connection_failed"}

    shop_name = test.get("shop", {}).get("name", SHOPIFY_STORE)
    log.info(f"Connected to Shopify: {shop_name}")

    # Get existing products for dedup
    existing_titles = _get_existing_titles()
    log.info(f"Found {len(existing_titles)} existing products in store")

    # Select top products
    log.info("Selecting top products from today's winners...")
    top_products = select_top_products(MAX_IMPORTS_PER_DAY)

    if not top_products:
        log.info("No new products to import today")
        send_alert(
            "📦 <b>SHOPIFY IMPORTER</b>\n\n"
            "No new products to import today.\n"
            "All winners already imported or below thresholds.",
            parse_mode="HTML",
        )
        return {"status": "ok", "imported": 0}

    log.info(f"Selected {len(top_products)} products for import:")
    for i, p in enumerate(top_products, 1):
        log.info(f"  #{i} [{p['classification']}] {p['title'][:50]} (score: {p['import_score']})")

    # Import loop
    history = load_import_history()
    imported = []
    failed = []

    for product in top_products:
        title_clean = generate_shopify_title(product["title"])

        # Extra dedup: check Shopify existing titles
        if title_clean.lower().strip() in existing_titles:
            log.info(f"⊘ Already in store: {title_clean[:50]}")
            continue

        pricing = calculate_retail_price(product)
        description = generate_description(product)

        log.info(f"Creating: {title_clean[:50]} @ ${pricing['price']}")
        created = create_draft_product(product, pricing, description)

        if created:
            record = {
                "shopify_id": created.get("id"),
                "title": created.get("title"),
                "original_title": product["title"],
                "price": pricing["price"],
                "compare_at": pricing["compare_at_price"],
                "cost": pricing.get("cost"),
                "margin_pct": pricing.get("margin_pct"),
                "classification": product["classification"],
                "import_score": product["import_score"],
                "signals": product["signals"],
                "niche": product.get("niche"),
                "imported_at": datetime.now().isoformat(),
            }
            imported.append(record)

            # Update history + existing set
            history["imported"][product["hash"]] = record
            history["total_imported"] = len(history["imported"])
            existing_titles.add(title_clean.lower().strip())
        else:
            failed.append(product["title"][:50])

        time.sleep(1)  # Rate limit courtesy

    save_import_history(history)

    # Save daily report
    today = datetime.now().strftime("%Y-%m-%d")
    report = {
        "date": today,
        "store": shop_name,
        "imported_count": len(imported),
        "failed_count": len(failed),
        "products": imported,
        "failed": failed,
        "total_history": history["total_imported"],
    }

    output_file = DATA_DIR / f"imports_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    log.info(f"Import report saved: {output_file}")

    # Telegram notification
    _send_import_alert(imported, failed, shop_name)

    log.info(f"Done: {len(imported)} imported, {len(failed)} failed")
    return report


def _send_import_alert(imported: list, failed: list, shop_name: str):
    """Send import summary to Telegram."""
    parts = [f"🏪 <b>SHOPIFY IMPORT — {shop_name}</b>\n"]

    if imported:
        parts.append(f"✅ <b>{len(imported)} produkte importuar si DRAFT</b>\n")
        for i, p in enumerate(imported, 1):
            margin_str = f" | margin {p['margin_pct']}%" if p.get("margin_pct") else ""
            sig_count = len(p.get("signals", []))
            parts.append(
                f"  {i}. <b>{p['title']}</b>\n"
                f"     💰 ${p['price']} (was ${p['compare_at']})"
                f"{margin_str} | {sig_count} signals"
            )

        parts.append(
            f"\n🔗 Shiko draftet: https://{SHOPIFY_STORE}/admin/products?status=draft"
        )

    if failed:
        parts.append(f"\n❌ {len(failed)} dështuan:")
        for f_title in failed:
            parts.append(f"  • {f_title}")

    parts.append("\n⚠️ <i>Të gjitha janë DRAFT — shiko dhe publiko vetë!</i>")
    send_alert("\n".join(parts), parse_mode="HTML")


if __name__ == "__main__":
    run_shopify_import()
