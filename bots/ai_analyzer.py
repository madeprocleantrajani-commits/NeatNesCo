"""
AI Analyzer v3 — Claude-powered product intelligence
------------------------------------------------------
v3: Multi-source data feed (not just Amazon), batch analysis,
    JSON validation, real cost breakdown, confidence scoring.

Reads:  data/amazon_*.json + data/aliexpress_*.json + data/ebay_*.json + data/trends_*.json
Writes: data/ai_analysis_YYYY-MM-DD.json
"""
import json
import os
import re
import time
from datetime import datetime

import anthropic

from config import DATA_DIR, get_logger, ANTHROPIC_API_KEY
from validators import calculate_real_profit
from alert_bot import send_alert

log = get_logger("ai_analyzer")

# Model from ENV or default
AI_MODEL = os.getenv("AI_MODEL", "claude-haiku-4-5-20251001")
AI_RATE_LIMIT_DELAY = 1.5  # seconds between API calls


def _load_latest(prefix: str) -> dict | None:
    files = sorted(DATA_DIR.glob(f"{prefix}_*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _build_context() -> dict:
    """Load all available data sources for richer AI analysis."""
    context = {}

    # eBay sold data
    ebay = _load_latest("ebay")
    if ebay:
        context["ebay_top_sellers"] = ebay.get("top_sellers", [])[:10]

    # AliExpress data
    ali = _load_latest("aliexpress")
    if ali:
        context["aliexpress_deals"] = ali.get("best_deals", [])[:10]

    # Trends data
    trends = _load_latest("trends")
    if trends:
        context["hot_trends"] = trends.get("hot_products", [])[:10]
        context["emerging"] = trends.get("emerging_products", [])[:5]

    return context


def _extract_json(text: str) -> dict | None:
    """Extract valid JSON from Claude's response, handling markdown and extra text."""
    # Strip markdown code blocks
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    continue

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find first {...} block using regex
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def analyze_product(client: anthropic.Anthropic, product: dict, context: dict) -> dict:
    """Ask Claude to analyze a single product with multi-source context."""
    title = product.get("title", "Unknown")
    price = product.get("price_usd")
    rating = product.get("rating")
    reviews = product.get("review_count", 0)
    rank = product.get("rank")
    category = product.get("category", "")

    # Build context summary
    context_text = ""
    if context.get("ebay_top_sellers"):
        top_ebay = [s for s in context["ebay_top_sellers"]
                     if any(w in title.lower() for w in s.get("keyword", "").lower().split())]
        if top_ebay:
            eb = top_ebay[0]
            context_text += f"\neBay Validation: '{eb['keyword']}' has {eb.get('sold_count', 0)} sold items, avg ${eb.get('median_price', 0):.2f}"

    if context.get("hot_trends"):
        trending = [t for t in context["hot_trends"]
                    if any(w in title.lower() for w in t.get("keyword", "").lower().split())]
        if trending:
            tr = trending[0]
            context_text += f"\nGoogle Trends: '{tr['keyword']}' interest {tr.get('current_interest', 0)}/100 (slope: {tr.get('slope', 0)})"

    if context.get("aliexpress_deals"):
        ali_match = [d for d in context["aliexpress_deals"]
                     if any(w in title.lower() for w in d.get("keyword", "").lower().split())]
        if ali_match:
            al = ali_match[0]
            context_text += f"\nAliExpress Source: ${al.get('source_price', 'N/A')} | Orders: {al.get('orders', 'N/A')}"

    prompt = f"""You are an expert dropshipping analyst. Analyze this product and respond ONLY with valid JSON.

Product:
- Title: {title}
- Amazon Price: ${price}
- Rating: {rating}/5 ({reviews or 'unknown'} reviews)
- Amazon Rank: #{rank} in {category}
{context_text}

IMPORTANT: Calculate real profit = retail_price - source_cost - shipping($3) - platform_fee(15% of retail) - ad_cost(30% of retail).

Respond with ONLY this JSON (no markdown, no explanation):
{{
  "dropship_score": <0-100>,
  "score_reason": "<one sentence>",
  "suggested_retail_price": <float>,
  "estimated_aliexpress_price": <float>,
  "estimated_shipping": 3.0,
  "estimated_profit": <float after ALL costs>,
  "profit_margin_pct": <integer>,
  "shopify_title": "<SEO title, max 60 chars>",
  "shopify_description": "<2 paragraph HTML for Shopify, benefit-focused>",
  "tiktok_hook": "<punchy TikTok opener, max 15 words>",
  "target_audience": "<who buys this>",
  "red_flags": "<concerns or 'None'>",
  "verdict": "BUY" or "WATCH" or "SKIP"
}}"""

    try:
        message = client.messages.create(
            model=AI_MODEL,
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        result = _extract_json(raw)
        if result is None:
            raise json.JSONDecodeError("No valid JSON found", raw, 0)
        result["title"] = title
        result["amazon_price"] = price

        # Validate profit calculation
        source = result.get("estimated_aliexpress_price", 0)
        retail = result.get("suggested_retail_price", 0)
        if source and retail:
            real_margin = calculate_real_profit(source, retail, result.get("estimated_shipping", 3))
            result["verified_profit"] = real_margin

        return result

    except json.JSONDecodeError as e:
        log.warning(f"JSON parse failed for '{title}', retrying with prefill...")
        try:
            time.sleep(AI_RATE_LIMIT_DELAY)
            message2 = client.messages.create(
                model=AI_MODEL,
                max_tokens=700,
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": '{"dropship_score":'},
                ]
            )
            raw2 = '{"dropship_score":' + message2.content[0].text.strip()
            result2 = _extract_json(raw2)
            if result2:
                result2["title"] = title
                result2["amazon_price"] = price
                return result2
            return {"title": title, "dropship_score": 0, "verdict": "SKIP", "error": "JSON retry failed"}
        except Exception:
            return {"title": title, "dropship_score": 0, "verdict": "SKIP", "error": str(e)}

    except anthropic.RateLimitError:
        log.warning(f"Rate limited, waiting 30s before retry...")
        time.sleep(30)
        try:
            message = client.messages.create(
                model=AI_MODEL,
                max_tokens=700,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = message.content[0].text.strip()
            result = _extract_json(raw)
            if result:
                result["title"] = title
                result["amazon_price"] = price
                return result
        except Exception:
            pass
        return {"title": title, "dropship_score": 0, "verdict": "SKIP", "error": "Rate limited"}

    except Exception as e:
        log.error(f"Claude API error for '{title}': {e}")
        return {"title": title, "dropship_score": 0, "verdict": "SKIP", "error": str(e)}


def load_amazon_candidates() -> list[dict]:
    """Load top non-brand Amazon products from today's scan."""
    files = sorted(DATA_DIR.glob("amazon_*.json"), reverse=True)
    if not files:
        log.warning("No Amazon data found. Run amazon_tracker.py first.")
        return []

    with open(files[0]) as f:
        data = json.load(f)

    from config import DROPSHIP_PRICE_MIN, DROPSHIP_PRICE_MAX, DROPSHIP_MIN_RATING

    candidates = []
    for cat, products in data.get("best_sellers", {}).items():
        for p in products:
            if (
                not p.get("is_brand")
                and p.get("price_usd")
                and DROPSHIP_PRICE_MIN <= p["price_usd"] <= DROPSHIP_PRICE_MAX
                and p.get("rating", 0) >= DROPSHIP_MIN_RATING - 0.2
                and p.get("rank", 999) <= 50
            ):
                candidates.append(p)

    # Sort by rank, deduplicate by title, take top 15
    seen = set()
    unique = []
    for p in sorted(candidates, key=lambda x: x.get("rank", 999)):
        key = p["title"][:40]
        if key not in seen:
            seen.add(key)
            unique.append(p)
        if len(unique) >= 15:
            break

    log.info(f"Loaded {len(unique)} candidates for AI analysis")
    return unique


def run_ai_analysis() -> dict:
    """Run Claude analysis on today's Amazon candidates."""
    if not ANTHROPIC_API_KEY:
        log.error("ANTHROPIC_API_KEY not set in .env")
        return {}

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    candidates = load_amazon_candidates()
    context = _build_context()

    if not candidates:
        log.warning("No candidates to analyze.")
        return {}

    log.info(f"Analyzing {len(candidates)} products with Claude (with {len(context)} context sources)...")
    results = []

    for i, product in enumerate(candidates, 1):
        log.info(f"[{i}/{len(candidates)}] Analyzing: {product['title'][:50]}")
        analysis = analyze_product(client, product, context)
        results.append(analysis)
        time.sleep(AI_RATE_LIMIT_DELAY)  # Rate limit protection

    results.sort(key=lambda x: x.get("dropship_score", 0), reverse=True)

    winners = [r for r in results if r.get("verdict") == "BUY"]
    watch = [r for r in results if r.get("verdict") == "WATCH"]

    today = datetime.now().strftime("%Y-%m-%d")
    output = {
        "analysis_date": today,
        "total_analyzed": len(results),
        "context_sources": list(context.keys()),
        "winners": winners,
        "watch": watch,
        "all_results": results,
    }

    out_file = DATA_DIR / f"ai_analysis_{today}.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    log.info(f"AI analysis saved: {out_file}")

    # Telegram alert
    msg = f"🧠 <b>AI ANALYSIS COMPLETE</b>\n"
    msg += f"📅 {today}\n"
    msg += f"🔍 Analizova: <b>{len(results)}</b> produkte\n"
    msg += f"📊 Kontekst: {', '.join(context.keys()) if context else 'vetem Amazon'}\n\n"

    if winners:
        msg += f"🏆 <b>FITUESIT — BUY ({len(winners)}):</b>\n"
        for w in winners[:5]:
            score = w.get("dropship_score", 0)
            retail = w.get("suggested_retail_price", 0)
            profit = w.get("estimated_profit", 0)
            margin = w.get("profit_margin_pct", 0)
            verified = w.get("verified_profit", {})
            real_profit = verified.get("profit", profit)

            msg += f"\n  🟢 <b>{w['title'][:40]}</b>\n"
            msg += f"     Score: {score}/100 | Shitja: ${retail:.2f}\n"
            msg += f"     Fitimi REAL: <b>${real_profit:.2f}</b> ({margin}%)\n"
            msg += f"     💡 <i>{w.get('tiktok_hook', '')}</i>\n"

    if watch:
        msg += f"\n👀 <b>WATCH ({len(watch)}):</b>\n"
        for w in watch[:3]:
            msg += f"  • {w['title'][:40]} — {w.get('dropship_score', 0)}/100\n"

    msg += f"\n📎 <code>data/ai_analysis_{today}.json</code>"
    send_alert(msg, parse_mode="HTML")

    log.info(f"Winners: {len(winners)} | Watch: {len(watch)}")
    return output


if __name__ == "__main__":
    run_ai_analysis()
