"""
Comment Sentiment Analyzer v1
------------------------------
Analyzes Amazon reviews and TikTok-style comments for:
  1. Purchase intent ("where can I buy", "link please", "need this")
  2. Product objections ("looks cheap", "hard to clean", "too small")
  3. Feature requests ("wish it had", "would be better if")
  4. Competitor mentions ("better than X", "prefer Y")

Uses Claude Haiku for sentiment classification.
Feeds insights back to Creative Lab for smarter ad copy.

Outputs: data/sentiment_YYYY-MM-DD.json
"""
import json
import re
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from config import (
    DATA_DIR, ANTHROPIC_API_KEY, get_logger,
    get_session, resilient_fetch,
)
from alert_bot import send_alert

log = get_logger("sentiment_analyzer")

HAIKU = "claude-haiku-4-5-20251001"

# Purchase intent keywords (scored without AI)
PURCHASE_INTENT_KEYWORDS = [
    "where can i buy", "where to buy", "link please", "link?",
    "need this", "i need this", "take my money", "shut up and take",
    "how much", "how do i get", "where do i get", "drop the link",
    "link in bio", "want this", "i want this", "buying this",
    "just ordered", "just bought", "ordered mine", "got mine",
    "adding to cart", "in my cart",
]

# Objection keywords
OBJECTION_KEYWORDS = [
    "looks cheap", "looks fake", "too expensive", "not worth",
    "broke after", "stopped working", "doesn't work", "scam",
    "waste of money", "returned", "returning", "refund",
    "too small", "too big", "wrong size", "misleading",
    "bad quality", "poor quality", "flimsy", "fragile",
    "hard to clean", "hard to use", "complicated",
]


def _load_latest_json(prefix: str) -> dict | None:
    files = sorted(DATA_DIR.glob(f"{prefix}_*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _call_claude(prompt: str, max_tokens: int = 600) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=HAIKU,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        log.error(f"Claude API error: {e}")
        return ""


def scrape_amazon_reviews(asin: str, session) -> list[str]:
    """Scrape top Amazon reviews for a product."""
    reviews = []
    url = f"https://www.amazon.com/product-reviews/{asin}?sortBy=recent"

    response = resilient_fetch(url, session=session, timeout=20)
    if not response:
        return reviews

    try:
        soup = BeautifulSoup(response.text, "lxml")

        # Review body selectors
        review_els = soup.select(
            'span[data-hook="review-body"] span, '
            '.review-text-content span'
        )
        for el in review_els:
            text = el.get_text(strip=True)
            if text and len(text) > 20:
                reviews.append(text[:500])

        # Review titles
        title_els = soup.select('a[data-hook="review-title"] span')
        for el in title_els:
            text = el.get_text(strip=True)
            if text and len(text) > 5:
                reviews.append(text)

    except Exception as e:
        log.debug(f"Review scraping error for {asin}: {e}")

    return reviews[:30]  # Max 30 reviews


def analyze_keyword_sentiment(reviews: list[str]) -> dict:
    """Fast keyword-based sentiment analysis (no API cost)."""
    purchase_intent = 0
    objections = 0
    intent_examples = []
    objection_examples = []

    for review in reviews:
        r_lower = review.lower()

        for kw in PURCHASE_INTENT_KEYWORDS:
            if kw in r_lower:
                purchase_intent += 1
                intent_examples.append(review[:100])
                break

        for kw in OBJECTION_KEYWORDS:
            if kw in r_lower:
                objections += 1
                objection_examples.append(review[:100])
                break

    total = max(1, len(reviews))
    return {
        "purchase_intent_count": purchase_intent,
        "purchase_intent_pct": round(purchase_intent / total * 100, 1),
        "objection_count": objections,
        "objection_pct": round(objections / total * 100, 1),
        "intent_examples": intent_examples[:5],
        "objection_examples": objection_examples[:5],
    }


def ai_deep_sentiment(reviews: list[str], product_name: str) -> dict:
    """Use Claude to extract deep insights from reviews."""
    if not ANTHROPIC_API_KEY or not reviews:
        return {}

    # Combine reviews into one block (limit tokens)
    reviews_text = "\n---\n".join(reviews[:15])

    prompt = f"""You are a consumer insights analyst. Analyze these reviews for "{product_name}".

REVIEWS:
{reviews_text}

Extract:
1. Top 3 things customers LOVE (positive patterns)
2. Top 3 OBJECTIONS/complaints (what makes people hesitate)
3. Top 2 FEATURE REQUESTS (what customers wish the product had)
4. Overall sentiment (positive/mixed/negative)
5. Ad creative insight: what angle would overcome the #1 objection?

Return JSON:
{{"loves": ["...","...","..."],
  "objections": ["...","...","..."],
  "feature_requests": ["...","..."],
  "sentiment": "positive/mixed/negative",
  "sentiment_score": 0-100,
  "ad_insight": "1 sentence: how to address the top objection in an ad"}}
ONLY return the JSON object."""

    result = _call_claude(prompt, max_tokens=600)
    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return {}


def run_sentiment_analysis() -> dict:
    """Run sentiment analysis on winning products."""
    log.info("=" * 60)
    log.info("SENTIMENT ANALYZER — Starting")
    log.info("=" * 60)

    session = get_session()

    winners_data = _load_latest_json("winners")
    if not winners_data:
        log.error("No winners data. Run winner_analyzer first.")
        return {"status": "no_data"}

    # Analyze STRONG_BUY + top BUY products
    products = (
        winners_data.get("strong_buys", []) +
        winners_data.get("buys", [])[:8]
    )

    # Filter to products with ASINs (needed for Amazon reviews)
    products_with_asin = [p for p in products if p.get("asin")]

    log.info(f"Analyzing sentiment for {len(products_with_asin)} products with ASINs")

    report = {
        "scan_date": datetime.now().isoformat(),
        "products": [],
        "stats": {},
    }

    for product in products_with_asin:
        asin = product["asin"]
        title = product.get("title", "Unknown")
        log.info(f"Analyzing: {title[:50]} ({asin})")

        # Scrape reviews
        reviews = scrape_amazon_reviews(asin, session)
        time.sleep(random.uniform(3, 6))

        if not reviews:
            log.info(f"  No reviews found for {asin}")
            continue

        # Keyword-based analysis (free)
        keyword_sentiment = analyze_keyword_sentiment(reviews)

        # AI deep analysis (uses API tokens)
        ai_sentiment = {}
        if ANTHROPIC_API_KEY:
            ai_sentiment = ai_deep_sentiment(reviews, title)
            time.sleep(1)

        result = {
            "product": title,
            "asin": asin,
            "price": product.get("price", 0),
            "reviews_analyzed": len(reviews),
            "keyword_analysis": keyword_sentiment,
            "ai_analysis": ai_sentiment,
            "purchase_intent_score": keyword_sentiment["purchase_intent_pct"],
            "objection_score": keyword_sentiment["objection_pct"],
        }

        report["products"].append(result)

        log.info(
            f"  Reviews: {len(reviews)} | "
            f"Intent: {keyword_sentiment['purchase_intent_pct']}% | "
            f"Objections: {keyword_sentiment['objection_pct']}%"
        )

    # Stats
    if report["products"]:
        avg_intent = sum(p["purchase_intent_score"] for p in report["products"]) / len(report["products"])
        avg_objection = sum(p["objection_score"] for p in report["products"]) / len(report["products"])
    else:
        avg_intent = avg_objection = 0

    report["stats"] = {
        "total_products": len(report["products"]),
        "total_reviews": sum(p["reviews_analyzed"] for p in report["products"]),
        "avg_purchase_intent": round(avg_intent, 1),
        "avg_objection_rate": round(avg_objection, 1),
        "high_intent_products": sum(
            1 for p in report["products"] if p["purchase_intent_score"] > 10
        ),
    }

    # Save
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"sentiment_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Sentiment report saved: {output_file}")

    # Telegram alert
    msg = f"💬 <b>SENTIMENT ANALYSIS COMPLETE</b>\n📅 {today}\n\n"

    msg += (
        f"📊 Products: {report['stats']['total_products']}\n"
        f"📝 Reviews analyzed: {report['stats']['total_reviews']}\n"
        f"🛒 Avg purchase intent: {report['stats']['avg_purchase_intent']}%\n"
        f"⚠️ Avg objection rate: {report['stats']['avg_objection_rate']}%\n\n"
    )

    for p in report["products"][:5]:
        msg += f"<b>{p['product'][:40]}</b>\n"
        msg += f"  🛒 Intent: {p['purchase_intent_score']}% | ⚠️ Objections: {p['objection_score']}%\n"

        ai = p.get("ai_analysis", {})
        if ai.get("loves"):
            msg += f"  ❤️ Love: {ai['loves'][0][:50]}\n"
        if ai.get("objections"):
            msg += f"  😤 Issue: {ai['objections'][0][:50]}\n"
        if ai.get("ad_insight"):
            msg += f"  💡 Ad tip: <i>{ai['ad_insight'][:60]}</i>\n"
        msg += "\n"

    msg += f"📁 <code>data/sentiment_{today}.json</code>"
    send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_sentiment_analysis()
