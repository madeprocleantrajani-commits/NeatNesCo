"""
AI Product Council v1
----------------------
6 AI analysts evaluate each product, then a Meta-AI makes the final decision.

Analysts:
  1. Demand Analyst — search growth, review velocity, category demand
  2. Virality Analyst — social media potential, UGC, engagement
  3. Competition Analyst — saturation, ad density, store count
  4. Supply Chain Analyst — shipping, supplier reliability, margin stability
  5. Profit Analyst — CPA estimate, margin, logistics cost
  6. Risk Analyst — return risk, brand issues, seasonal dependency

Meta-AI (Portfolio Manager):
  Final Score = Demand*0.25 + Virality*0.20 + Profit*0.20 +
                Competition*0.15 + Supply*0.10 + Risk*0.10

Uses Haiku for individual analysts, Sonnet for Meta-AI (top products only).
Cost: ~$0.02-0.05 per product with Haiku.

Outputs: data/council_YYYY-MM-DD.json
"""
import json
import time
from datetime import datetime

from config import DATA_DIR, ANTHROPIC_API_KEY, get_logger
from alert_bot import send_alert

log = get_logger("ai_council")

HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-4-6"


def _load_latest_json(prefix: str) -> dict | None:
    files = sorted(DATA_DIR.glob(f"{prefix}_*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _call_claude(prompt: str, model: str = HAIKU, max_tokens: int = 500) -> str:
    """Call Claude API."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        log.error(f"Claude API error: {e}")
        return ""


def _parse_analyst_response(text: str) -> dict:
    """Parse analyst JSON response."""
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return {"score": 50, "confidence": "low", "reasoning": text[:200]}


def _build_product_context(product: dict) -> str:
    """Build a rich context string for analysts."""
    return (
        f"Product: {product.get('title', 'Unknown')}\n"
        f"Price: ${product.get('price', 0):.2f}\n"
        f"Category: {product.get('category', 'Unknown')}\n"
        f"Rating: {product.get('rating', 0)}/5 ({product.get('reviews', 0):,} reviews)\n"
        f"Amazon BSR Score: {product.get('score', 0)}/100\n"
        f"Viability Score: {product.get('viability', 0)}/100\n"
        f"Signals: {', '.join(product.get('signals', []))}\n"
        f"Signal Count: {product.get('signal_count', 0)}\n"
        f"Type: {product.get('type', 'Unknown')}\n"
        f"Season: {product.get('season', 'Unknown')}\n"
        f"Profit Viable: {product.get('profit_viable', False)}\n"
        f"Margin: {product.get('margin_pct', 0):.0f}%\n"
        f"TikTok Score: {product.get('tiktok_score', 0)}\n"
        f"Ad Score: {product.get('ad_score', 0)}\n"
        f"DNA Score: {product.get('dna_score', 0)}\n"
        f"Wow Factor: {product.get('wow_factor', 0)}\n"
        f"Problem Solving: {product.get('problem_solving', 0)}\n"
        f"Shipping Score: {product.get('shipping_score', 0)}\n"
        f"Saturation: {product.get('saturation_level', 'unknown')}\n"
        f"Momentum: {product.get('momentum_status', 'unknown')}\n"
    )


def analyst_demand(product: dict) -> dict:
    """AI Analyst 1: Demand Analysis."""
    context = _build_product_context(product)
    prompt = f"""You are a Demand Analyst for a dropshipping AI hedge fund.
Your job: evaluate market DEMAND for this product in the US market.

{context}

Analyze:
1. Search growth potential (is demand increasing?)
2. Review velocity (many reviews = established market, few = emerging)
3. Category demand (is this category growing in the US?)
4. Price point appeal (is ${{product.get('price', 0):.2f}} attractive for impulse buy?)

Return JSON: {{"score": 0-100, "confidence": "high/medium/low", "reasoning": "1-2 sentences"}}
ONLY return the JSON object."""

    return _parse_analyst_response(_call_claude(prompt))


def analyst_virality(product: dict) -> dict:
    """AI Analyst 2: Virality Analysis."""
    context = _build_product_context(product)
    prompt = f"""You are a Virality Analyst for a dropshipping AI hedge fund.
Your job: evaluate social media VIRAL POTENTIAL for this product.

{context}

Analyze:
1. TikTok viral potential (is this visually satisfying? "oddly satisfying"?)
2. UGC content potential (can regular people make compelling content?)
3. Shareability (would someone tag a friend? "You NEED this!")
4. Emotional trigger (surprise, delight, problem-solved, before/after)

Return JSON: {{"score": 0-100, "confidence": "high/medium/low", "reasoning": "1-2 sentences"}}
ONLY return the JSON object."""

    return _parse_analyst_response(_call_claude(prompt))


def analyst_competition(product: dict) -> dict:
    """AI Analyst 3: Competition Analysis."""
    context = _build_product_context(product)
    prompt = f"""You are a Competition Analyst for a dropshipping AI hedge fund.
Your job: evaluate market SATURATION and competition for this product.

{context}

Analyze:
1. Market saturation (saturated products fail even with good ads)
2. Ad density (how many competitors are running ads?)
3. Differentiation potential (can we stand out from competitors?)
4. Entry barrier (is it easy for new sellers to compete?)

HIGH score = LOW competition (good opportunity).
LOW score = HIGH competition (saturated, avoid).

Return JSON: {{"score": 0-100, "confidence": "high/medium/low", "reasoning": "1-2 sentences"}}
ONLY return the JSON object."""

    return _parse_analyst_response(_call_claude(prompt))


def analyst_supply_chain(product: dict) -> dict:
    """AI Analyst 4: Supply Chain Analysis."""
    context = _build_product_context(product)
    prompt = f"""You are a Supply Chain Analyst for a dropshipping AI hedge fund.
Your job: evaluate SUPPLY CHAIN reliability for this product.

{context}

Analyze:
1. Shipping feasibility (small/light = cheap shipping, heavy/bulky = expensive)
2. Supplier reliability (multiple sources vs single source risk)
3. Quality consistency (can suppliers maintain quality at scale?)
4. US warehouse availability potential (faster shipping = better reviews)

Return JSON: {{"score": 0-100, "confidence": "high/medium/low", "reasoning": "1-2 sentences"}}
ONLY return the JSON object."""

    return _parse_analyst_response(_call_claude(prompt))


def analyst_profit(product: dict) -> dict:
    """AI Analyst 5: Profit Analysis."""
    context = _build_product_context(product)
    price = product.get("price", 0)
    margin = product.get("margin_pct", 0)
    prompt = f"""You are a Profit Analyst for a dropshipping AI hedge fund.
Your job: evaluate PROFITABILITY of this product.

{context}

Consider the real economics:
- Product cost: ~{price * 0.35:.2f} (estimated 35% of retail)
- Shipping: ~$3-5
- Platform fees: ~15% of retail
- Ad cost: ~30% of retail (average CPA)
- Real margin: {margin:.0f}%

Analyze:
1. Is {margin:.0f}% margin enough after ads?
2. Can we achieve CPA under ${price * 0.30:.2f}?
3. Is the price sweet spot for impulse purchases? ($20-60 ideal)
4. Upsell/AOV potential (bundles, quantity discounts)?

Return JSON: {{"score": 0-100, "confidence": "high/medium/low", "reasoning": "1-2 sentences"}}
ONLY return the JSON object."""

    return _parse_analyst_response(_call_claude(prompt))


def analyst_risk(product: dict) -> dict:
    """AI Analyst 6: Risk Analysis."""
    context = _build_product_context(product)
    prompt = f"""You are a Risk Analyst for a dropshipping AI hedge fund.
Your job: evaluate RISKS of selling this product.

{context}

Analyze:
1. Return risk (clothing/sizing = high return rate, gadgets = low)
2. Brand/IP risk (is this too close to a patented product?)
3. Seasonal dependency (summer/holiday only = risky)
4. Customer complaint risk (fragile? complex? misleading?)
5. Platform policy risk (does it violate FB/TikTok ad policies?)

HIGH score = LOW risk (safe to sell).
LOW score = HIGH risk (avoid).

Return JSON: {{"score": 0-100, "confidence": "high/medium/low", "reasoning": "1-2 sentences"}}
ONLY return the JSON object."""

    return _parse_analyst_response(_call_claude(prompt))


def meta_ai_decision(product: dict, analyst_results: dict) -> dict:
    """Meta-AI Portfolio Manager — makes the final decision."""
    scores_text = "\n".join(
        f"  {name}: {data.get('score', 0)}/100 ({data.get('confidence', '?')}) — {data.get('reasoning', '')}"
        for name, data in analyst_results.items()
    )

    prompt = f"""You are the Portfolio Manager AI for a dropshipping hedge fund.
6 specialist analysts have evaluated this product. Make the FINAL decision.

Product: {product.get('title', 'Unknown')} (${product.get('price', 0):.2f})

ANALYST SCORES:
{scores_text}

WEIGHTED FORMULA:
Final = Demand*0.25 + Virality*0.20 + Profit*0.20 + Competition*0.15 + Supply*0.10 + Risk*0.10

Calculate the weighted score and make a decision:
- Score > 75: STRONG_TEST (allocate $200-500 test budget)
- Score 60-75: TEST (allocate $100-200 test budget)
- Score 45-60: WATCH (monitor, don't spend yet)
- Score < 45: REJECT (skip this product)

Return JSON:
{{"final_score": 0-100, "decision": "STRONG_TEST/TEST/WATCH/REJECT",
  "budget_recommendation": dollar_amount,
  "key_strength": "1 sentence",
  "key_risk": "1 sentence",
  "verdict": "2-3 sentence final verdict"}}
ONLY return the JSON object."""

    result = _call_claude(prompt, model=HAIKU, max_tokens=500)
    return _parse_analyst_response(result)


def evaluate_product(product: dict) -> dict:
    """Run all 6 analysts + Meta-AI on a single product."""
    title = product.get("title", "Unknown")
    log.info(f"Council evaluating: {title[:50]}")

    analysts = {}

    analysts["demand"] = analyst_demand(product)
    time.sleep(0.5)

    analysts["virality"] = analyst_virality(product)
    time.sleep(0.5)

    analysts["competition"] = analyst_competition(product)
    time.sleep(0.5)

    analysts["supply_chain"] = analyst_supply_chain(product)
    time.sleep(0.5)

    analysts["profit"] = analyst_profit(product)
    time.sleep(0.5)

    analysts["risk"] = analyst_risk(product)
    time.sleep(0.5)

    # Calculate weighted score locally as backup
    weighted = (
        analysts["demand"].get("score", 0) * 0.25 +
        analysts["virality"].get("score", 0) * 0.20 +
        analysts["profit"].get("score", 0) * 0.20 +
        analysts["competition"].get("score", 0) * 0.15 +
        analysts["supply_chain"].get("score", 0) * 0.10 +
        analysts["risk"].get("score", 0) * 0.10
    )

    # Meta-AI final decision
    meta = meta_ai_decision(product, analysts)
    time.sleep(0.5)

    return {
        "product": title,
        "price": product.get("price", 0),
        "analysts": analysts,
        "meta_decision": meta,
        "weighted_score": round(weighted, 1),
        "final_score": meta.get("final_score", round(weighted)),
        "decision": meta.get("decision", "WATCH"),
        "budget": meta.get("budget_recommendation", 0),
    }


def run_ai_council() -> dict:
    """Run AI Council on all winning products."""
    log.info("=" * 60)
    log.info("AI PRODUCT COUNCIL — Starting")
    log.info("=" * 60)

    if not ANTHROPIC_API_KEY:
        log.error("No ANTHROPIC_API_KEY set. Council requires Claude API.")
        return {"status": "no_api_key"}

    winners_data = _load_latest_json("winners")
    if not winners_data:
        log.error("No winners data. Run winner_analyzer first.")
        return {"status": "no_data"}

    # Only evaluate STRONG_BUY + top BUY products (cost control)
    products = (
        winners_data.get("strong_buys", []) +
        winners_data.get("buys", [])[:10]
    )

    if not products:
        log.info("No products to evaluate.")
        return {"status": "no_products"}

    log.info(f"Evaluating {len(products)} products through AI Council")

    report = {
        "scan_date": datetime.now().isoformat(),
        "model_analysts": HAIKU,
        "model_meta": HAIKU,
        "evaluations": [],
        "strong_test": [],
        "test": [],
        "watch": [],
        "reject": [],
        "stats": {},
    }

    for product in products:
        evaluation = evaluate_product(product)
        report["evaluations"].append(evaluation)

        decision = evaluation["decision"]
        if decision == "STRONG_TEST":
            report["strong_test"].append(evaluation)
        elif decision == "TEST":
            report["test"].append(evaluation)
        elif decision == "WATCH":
            report["watch"].append(evaluation)
        else:
            report["reject"].append(evaluation)

        log.info(
            f"  {decision}: {evaluation['product'][:40]} "
            f"(score: {evaluation['final_score']}, budget: ${evaluation['budget']})"
        )

    # Stats
    total_budget = sum(e["budget"] for e in report["evaluations"] if isinstance(e.get("budget"), (int, float)))
    report["stats"] = {
        "total_evaluated": len(report["evaluations"]),
        "strong_test": len(report["strong_test"]),
        "test": len(report["test"]),
        "watch": len(report["watch"]),
        "reject": len(report["reject"]),
        "total_recommended_budget": total_budget,
        "avg_score": round(
            sum(e["final_score"] for e in report["evaluations"]
                if isinstance(e.get("final_score"), (int, float)))
            / max(1, len(report["evaluations"])), 1
        ),
    }

    # Save
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"council_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Council report saved: {output_file}")

    # Telegram alert
    msg = f"🏛 <b>AI PRODUCT COUNCIL COMPLETE</b>\n📅 {today}\n\n"

    msg += (
        f"📊 Evaluated: {report['stats']['total_evaluated']} products\n"
        f"🟢 STRONG TEST: {report['stats']['strong_test']}\n"
        f"🟡 TEST: {report['stats']['test']}\n"
        f"🔵 WATCH: {report['stats']['watch']}\n"
        f"🔴 REJECT: {report['stats']['reject']}\n"
        f"💰 Total budget: ${report['stats']['total_recommended_budget']}\n\n"
    )

    for e in report["strong_test"][:3]:
        msg += (
            f"🟢 <b>{e['product'][:40]}</b>\n"
            f"  Score: {e['final_score']} | Budget: ${e['budget']}\n"
        )
        meta = e.get("meta_decision", {})
        if meta.get("verdict"):
            msg += f"  <i>{meta['verdict'][:80]}</i>\n\n"

    for e in report["test"][:3]:
        msg += (
            f"🟡 <b>{e['product'][:40]}</b>\n"
            f"  Score: {e['final_score']} | Budget: ${e['budget']}\n"
        )

    msg += f"\n📁 <code>data/council_{today}.json</code>"
    send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_ai_council()
