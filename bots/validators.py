"""
Data Validation Pipeline
-------------------------
Centralized validation for all data types across the bot suite.
Catches bad data before it poisons scoring and recommendations.
"""
import re


def validate_price(price, min_val: float = 0.50, max_val: float = 5000) -> float | None:
    """Validate a price value. Returns float or None if invalid."""
    if price is None:
        return None
    try:
        val = float(price)
        if min_val <= val <= max_val:
            return round(val, 2)
    except (ValueError, TypeError):
        pass
    return None


def validate_rating(rating) -> float | None:
    """Validate a product rating (0.0-5.0)."""
    if rating is None:
        return None
    try:
        val = float(rating)
        if 0.0 <= val <= 5.0:
            return round(val, 1)
    except (ValueError, TypeError):
        pass
    return None


def validate_review_count(count) -> int | None:
    """Validate review count. Returns integer or None."""
    if count is None:
        return None
    try:
        val = int(count)
        if val >= 0:
            return val
    except (ValueError, TypeError):
        pass
    return None


def validate_asin(asin: str) -> str | None:
    """Validate Amazon ASIN format (10 alphanumeric chars starting with B0)."""
    if not asin or not isinstance(asin, str):
        return None
    asin = asin.strip().upper()  # Normalize lowercase ASINs
    if re.match(r'^[A-Z0-9]{10}$', asin):
        return asin
    return None


def validate_url(url: str) -> str | None:
    """Basic URL validation."""
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    if url.startswith(("http://", "https://", "//")):
        return url
    return None


def sanitize_title(title: str) -> str:
    """Clean up product titles — remove spam, excessive symbols, normalize whitespace."""
    if not title:
        return ""
    # Remove common spam patterns
    cleaned = re.sub(r'[★☆✓✔✗✘⭐🔥💥🎁🎉]+', '', title)
    # Remove excessive exclamation/question marks
    cleaned = re.sub(r'[!?]{2,}', '!', cleaned)
    # Remove "SALE", "HOT", "NEW", "BEST" prefix spam
    cleaned = re.sub(r'^(SALE|HOT|NEW|BEST|TOP|LIMITED)\s*[-:|]?\s*', '', cleaned, flags=re.IGNORECASE)
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def parse_order_count(orders_str: str) -> int:
    """
    Parse order count from various formats:
    '1,234 sold', '10K+ sold', '500+ orders', '1.2K', etc.
    """
    if not orders_str:
        return 0
    try:
        cleaned = orders_str.lower().replace(",", "").replace("+", "").strip()
        cleaned = re.sub(r"[^\d.km]", "", cleaned)
        if "k" in cleaned:
            num = cleaned.replace("k", "")
            return int(float(num) * 1000) if num else 0
        if "m" in cleaned:
            num = cleaned.replace("m", "")
            return int(float(num) * 1_000_000) if num else 0
        match = re.search(r"(\d+)", cleaned)
        return int(match.group(1)) if match else 0
    except (ValueError, AttributeError):
        return 0


def validate_product(product: dict, required_fields: list[str] = None) -> dict:
    """
    Validate a product dict, returning cleaned version with skip_reasons.
    Adds 'valid' bool and 'skip_reasons' list.
    """
    if required_fields is None:
        required_fields = ["title"]

    result = dict(product)
    skip_reasons = []

    # Check required fields
    for field in required_fields:
        if not result.get(field):
            skip_reasons.append(f"missing_{field}")

    # Validate specific fields if present
    if "price_usd" in result:
        result["price_usd"] = validate_price(result["price_usd"])
    if "rating" in result:
        result["rating"] = validate_rating(result["rating"])
    if "review_count" in result:
        result["review_count"] = validate_review_count(result["review_count"])
    if "asin" in result:
        result["asin"] = validate_asin(result["asin"])
    if "title" in result and result["title"]:
        result["title"] = sanitize_title(result["title"])

    result["valid"] = len(skip_reasons) == 0
    result["skip_reasons"] = skip_reasons
    return result


def calculate_real_profit(source_price: float, retail_price: float,
                          shipping_cost: float = 0,
                          platform_fee_pct: float = 0.15,
                          ad_cost_pct: float = 0.30) -> dict:
    """
    Calculate REAL profit after ALL costs.
    No more fantasy 3x multipliers.

    Returns dict with breakdown:
      source_price, shipping, platform_fee, ad_cost, total_cost, profit, margin_pct
    """
    if not source_price or source_price <= 0 or not retail_price or retail_price <= 0:
        return {"profit": 0, "margin_pct": 0, "viable": False}

    platform_fee = retail_price * platform_fee_pct
    ad_cost = retail_price * ad_cost_pct
    total_cost = source_price + shipping_cost + platform_fee + ad_cost
    profit = retail_price - total_cost
    # Sanity check: profit cannot exceed retail price (impossible margin = data error)
    if profit > retail_price:
        profit = 0
    margin_pct = round((profit / retail_price) * 100, 1) if retail_price > 0 else 0

    return {
        "source_price": round(source_price, 2),
        "shipping_cost": round(shipping_cost, 2),
        "platform_fee": round(platform_fee, 2),
        "ad_cost": round(ad_cost, 2),
        "total_cost": round(total_cost, 2),
        "retail_price": round(retail_price, 2),
        "profit": round(profit, 2),
        "margin_pct": margin_pct,
        "viable": profit >= 5.0 and margin_pct >= 15,
    }
