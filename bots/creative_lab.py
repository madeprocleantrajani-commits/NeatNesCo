"""
AI Creative Lab v1
-------------------
Generates ad creatives using Claude AI for winning products.

For each STRONG_BUY / BUY product, generates:
  - 5 hooks (attention-grabbing opening lines)
  - 3 angles (problem-solution, before-after, life-hack, luxury-feel)
  - 2 video script formats (15s and 30s)
  - 5 headlines for ads

Uses Haiku for cost efficiency (~$0.01 per product).

Outputs: data/creatives_YYYY-MM-DD.json
"""
import json
import time
from datetime import datetime

from config import DATA_DIR, ANTHROPIC_API_KEY, get_logger
from alert_bot import send_alert

log = get_logger("creative_lab")

MODEL = "claude-haiku-4-5-20251001"


def _load_latest_json(prefix: str) -> dict | None:
    files = sorted(DATA_DIR.glob(f"{prefix}_*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _call_claude(prompt: str, max_tokens: int = 1500) -> str:
    """Call Claude API with Haiku for cost efficiency."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        log.error(f"Claude API error: {e}")
        return ""


def generate_hooks(product_name: str, price: float, category: str) -> list[str]:
    """Generate 5 attention-grabbing hooks for ads."""
    prompt = f"""You are a top-performing Facebook/TikTok ad copywriter for US dropshipping.

Product: {product_name}
Price: ${price:.2f}
Category: {category}

Generate exactly 5 ad hooks. Each hook must:
- Be under 15 words
- Create urgency or curiosity
- Target US consumers
- Work for TikTok/Facebook/Instagram ads

Formats to use:
1. Price comparison hook: "Americans are switching from $X to this $Y tool"
2. Problem hook: "If you struggle with [problem], you need this"
3. Social proof hook: "Over X people bought this in [month]"
4. Curiosity hook: "This $X gadget is replacing [expensive thing]"
5. Urgency hook: "They don't want you to know about this $X [product]"

Return ONLY the 5 hooks, one per line, numbered 1-5. No explanations."""

    result = _call_claude(prompt, max_tokens=400)
    hooks = []
    for line in result.strip().split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            # Remove numbering
            hook = line.lstrip("0123456789.)-: ").strip()
            if hook:
                hooks.append(hook)
    return hooks[:5]


def generate_angles(product_name: str, price: float, category: str) -> list[dict]:
    """Generate 3 ad angles with descriptions."""
    prompt = f"""You are a dropshipping ad strategist for the US market.

Product: {product_name}
Price: ${price:.2f}
Category: {category}

Generate exactly 3 ad angles. For each, provide:
- Angle name (2-3 words)
- Target emotion
- Key message (1 sentence)
- Best platform (TikTok/Facebook/Instagram)

Angles to create:
1. Problem-Solution: Show the problem, then the product as the fix
2. Before-After: Dramatic transformation
3. Life Hack / Luxury Feel: Make cheap product feel premium

Return as JSON array with keys: name, emotion, message, platform
Return ONLY the JSON array, no other text."""

    result = _call_claude(prompt, max_tokens=500)
    try:
        # Extract JSON from response
        start = result.find("[")
        end = result.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def generate_video_script(product_name: str, price: float,
                           category: str, duration: int = 15) -> dict:
    """Generate a video script for TikTok/Reels."""
    prompt = f"""You are a viral TikTok ad script writer for US e-commerce.

Product: {product_name}
Price: ${price:.2f}
Category: {category}
Video duration: {duration} seconds

Write a {duration}-second video script with EXACT timestamps:

{"0-2s: HOOK (grab attention)" if duration == 15 else "0-3s: HOOK (grab attention)"}
{"2-6s: PROBLEM (show the pain point)" if duration == 15 else "3-8s: PROBLEM (show the pain point)"}
{"6-11s: SOLUTION (show product in action)" if duration == 15 else "8-20s: SOLUTION (demonstrate product)"}
{"11-15s: CTA (call to action)" if duration == 15 else "20-30s: CTA + OFFER (urgency + call to action)"}

Include:
- Voiceover text (what narrator says)
- Visual description (what viewer sees)
- Text overlay (on-screen text)

Return as JSON with keys: hook, problem, solution, cta
Each section has: time, voiceover, visual, text_overlay
Return ONLY the JSON object, no other text."""

    result = _call_claude(prompt, max_tokens=800)
    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return {}


def generate_headlines(product_name: str, price: float, category: str) -> list[str]:
    """Generate 5 ad headlines."""
    prompt = f"""You are a Facebook Ads headline specialist for US dropshipping.

Product: {product_name}
Price: ${price:.2f}
Category: {category}

Generate exactly 5 ad headlines for Facebook/Instagram ads.
Each headline must be under 10 words.

Types:
1. Benefit-focused: "Save time every morning with..."
2. Problem-focused: "Stop wasting money on..."
3. Curiosity: "This gadget fixes X instantly"
4. Social proof: "Join X+ happy customers"
5. Urgency: "Limited stock - X% off today"

Return ONLY 5 headlines, one per line, numbered 1-5."""

    result = _call_claude(prompt, max_tokens=300)
    headlines = []
    for line in result.strip().split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            hl = line.lstrip("0123456789.)-: ").strip()
            if hl:
                headlines.append(hl)
    return headlines[:5]


def run_creative_lab() -> dict:
    """Generate creatives for all winning products."""
    log.info("=" * 60)
    log.info("AI CREATIVE LAB — Starting")
    log.info("=" * 60)

    if not ANTHROPIC_API_KEY:
        log.error("No ANTHROPIC_API_KEY set. Creative Lab requires Claude API.")
        return {"status": "no_api_key"}

    winners_data = _load_latest_json("winners")
    if not winners_data:
        log.error("No winners data found. Run winner_analyzer first.")
        return {"status": "no_data"}

    # Only generate creatives for STRONG_BUY and top BUY products
    products = (
        winners_data.get("strong_buys", []) +
        winners_data.get("buys", [])[:5]
    )

    if not products:
        log.info("No winning products to generate creatives for.")
        return {"status": "no_winners"}

    log.info(f"Generating creatives for {len(products)} products")

    report = {
        "scan_date": datetime.now().isoformat(),
        "model": MODEL,
        "products": [],
        "stats": {"total_products": 0, "total_hooks": 0,
                  "total_scripts": 0, "total_headlines": 0},
    }

    for product in products:
        title = product.get("title", "")
        price = product.get("price", 0)
        cat = product.get("category", "")

        log.info(f"Generating creatives: {title[:50]}")

        creative = {
            "product": title,
            "price": price,
            "category": cat,
            "recommendation": product.get("recommendation", ""),
            "viability": product.get("viability", 0),
        }

        # Generate all creative elements
        creative["hooks"] = generate_hooks(title, price, cat)
        time.sleep(1)

        creative["angles"] = generate_angles(title, price, cat)
        time.sleep(1)

        creative["script_15s"] = generate_video_script(title, price, cat, 15)
        time.sleep(1)

        creative["script_30s"] = generate_video_script(title, price, cat, 30)
        time.sleep(1)

        creative["headlines"] = generate_headlines(title, price, cat)
        time.sleep(1)

        # Count combinations
        n_hooks = len(creative["hooks"])
        n_angles = len(creative["angles"])
        creative["total_combinations"] = n_hooks * n_angles * 2  # 2 script formats

        report["products"].append(creative)

        report["stats"]["total_hooks"] += n_hooks
        report["stats"]["total_scripts"] += 2
        report["stats"]["total_headlines"] += len(creative["headlines"])

    report["stats"]["total_products"] = len(report["products"])

    # Save
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"creatives_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Creative report saved: {output_file}")
    log.info(f"Generated creatives for {len(report['products'])} products")

    # Telegram alert
    msg = f"🎨 <b>AI CREATIVE LAB COMPLETE</b>\n📅 {today}\n\n"
    msg += (
        f"📊 Products: {report['stats']['total_products']}\n"
        f"🎣 Hooks: {report['stats']['total_hooks']}\n"
        f"🎬 Scripts: {report['stats']['total_scripts']}\n"
        f"📝 Headlines: {report['stats']['total_headlines']}\n\n"
    )

    for p in report["products"][:3]:
        msg += f"<b>{p['product'][:45]}</b> (${p['price']:.2f})\n"
        if p["hooks"]:
            msg += f"  🎣 Hook: <i>{p['hooks'][0][:60]}</i>\n"
        if p["headlines"]:
            msg += f"  📝 Headline: <i>{p['headlines'][0][:50]}</i>\n"
        msg += f"  🔢 {p['total_combinations']} creative combinations\n\n"

    msg += f"📁 <code>data/creatives_{today}.json</code>"
    send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_creative_lab()
