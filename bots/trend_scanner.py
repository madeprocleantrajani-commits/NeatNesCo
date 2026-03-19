"""
Google Trends Scanner v3
-------------------------
v3: Linear regression trend detection, seasonality awareness,
    "emerging" product detection, rate limit handling, keyword discovery.

Outputs: data/trends_YYYY-MM-DD.json
"""
import json
import time
import random
from datetime import datetime
from pytrends.request import TrendReq

from config import (
    SEED_KEYWORDS, TRENDS_GEO, TRENDS_TIMEFRAME,
    DATA_DIR, PROXY_URL, get_logger,
)
from alert_bot import send_alert

log = get_logger("trend_scanner")


def _calc_slope_inline(vals: list) -> float:
    """Quick slope calculation for acceleration comparison."""
    n = len(vals)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(vals) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(vals))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den else 0.0


def _linear_trend(values: list) -> dict:
    """
    Calculate trend using linear regression slope.
    Returns: slope, direction, acceleration (2nd derivative).
    """
    if not values or len(values) < 4:
        return {"slope": 0, "direction": "unknown", "acceleration": 0}

    n = len(values)
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n

    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator else 0

    # Acceleration: compare slope of first half vs second half (slope-based, not avg-based)
    mid = n // 2
    first_half = values[:mid]
    second_half = values[mid:]

    if len(first_half) >= 2 and len(second_half) >= 2:
        slope_first = _calc_slope_inline(first_half)
        slope_second = _calc_slope_inline(second_half)
        acceleration = slope_second - slope_first  # Positive = accelerating
    else:
        acceleration = 0

    if slope > 0.5 and acceleration > 0:
        direction = "rising_fast"
    elif slope > 0.2:
        direction = "rising"
    elif slope < -0.5:
        direction = "falling_fast"
    elif slope < -0.2:
        direction = "falling"
    else:
        direction = "stable"

    return {
        "slope": round(slope, 3),
        "direction": direction,
        "acceleration": round(acceleration, 1),
    }


def _calc_slope(values: list) -> float:
    """Calculate linear regression slope for a list of values."""
    if not values or len(values) < 2:
        return 0.0
    n = len(values)
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den else 0.0


def scan_interest_over_time(pytrends, keywords: list[str]) -> dict:
    """Get interest over time with regression-based trend detection."""
    try:
        pytrends.build_payload(keywords, cat=0, timeframe=TRENDS_TIMEFRAME, geo=TRENDS_GEO)
        df = pytrends.interest_over_time()
        if df.empty:
            return {}

        results = {}
        for kw in keywords:
            if kw in df.columns:
                values = df[kw].tolist()
                trend_info = _linear_trend(values)

                current = values[-1] if values else 0
                avg = round(sum(values) / len(values), 1) if values else 0

                # Multi-timeframe momentum analysis (7d / 14d / 30d)
                slope_7d = round(_calc_slope(values[-7:]), 3) if len(values) >= 7 else 0
                slope_14d = round(_calc_slope(values[-14:]), 3) if len(values) >= 14 else 0
                slope_30d = round(_calc_slope(values[-30:]), 3) if len(values) >= 30 else 0

                # Momentum status based on slope comparison
                if slope_7d > slope_14d > slope_30d and slope_7d > 0.2:
                    momentum_status = "accelerating"
                elif slope_7d > 0 and slope_14d > 0 and slope_30d > 0:
                    momentum_status = "steady_up"
                elif slope_7d < slope_14d < slope_30d and slope_7d < -0.2:
                    momentum_status = "decelerating"
                elif slope_7d < 0 and slope_14d < 0:
                    momentum_status = "declining"
                elif slope_7d > 0.3 and slope_30d < 0:
                    momentum_status = "reversal_up"
                elif slope_7d < -0.3 and slope_30d > 0:
                    momentum_status = "reversal_down"
                else:
                    momentum_status = "flat"

                # Momentum score (0-100): how strong is the acceleration
                momentum_score = 0
                if momentum_status == "accelerating":
                    momentum_score = max(0, min(100, int(slope_7d * 50 + 40)))
                elif momentum_status == "steady_up":
                    momentum_score = max(0, min(70, int(slope_7d * 40 + 20)))
                elif momentum_status == "reversal_up":
                    momentum_score = max(0, min(80, int(slope_7d * 45 + 30)))
                elif momentum_status == "flat":
                    momentum_score = 10
                elif momentum_status in ("declining", "decelerating"):
                    momentum_score = 0

                results[kw] = {
                    "current": current,
                    "avg": avg,
                    "max": max(values) if values else 0,
                    "min": min(values) if values else 0,
                    "trend": trend_info["direction"],
                    "slope": trend_info["slope"],
                    "acceleration": trend_info["acceleration"],
                    "momentum": round(current - avg, 1),
                    "last_7": values[-7:] if len(values) >= 7 else values,
                    # New: Multi-timeframe momentum
                    "slope_7d": slope_7d,
                    "slope_14d": slope_14d,
                    "slope_30d": slope_30d,
                    "momentum_status": momentum_status,
                    "momentum_score": momentum_score,
                }

                # Emerging product detection: low absolute interest but steep upward slope
                if current < 40 and trend_info["slope"] > 0.5 and trend_info["acceleration"] > 5:
                    results[kw]["emerging"] = True

                # New: Breakout detection — sudden acceleration in last 7 days
                if slope_7d > 1.0 and slope_30d < 0.5 and current > 20:
                    results[kw]["breakout"] = True

        return results
    except Exception as e:
        log.error(f"Interest over time failed for {keywords}: {e}")
        return {}


def scan_rising_queries(pytrends, keyword: str) -> list[dict]:
    """Find rising related queries."""
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=TRENDS_TIMEFRAME, geo=TRENDS_GEO)
        related = pytrends.related_queries()
        rising = related.get(keyword, {}).get("rising")
        if rising is not None and not rising.empty:
            return rising.head(15).to_dict("records")
        return []
    except Exception as e:
        log.error(f"Rising queries failed for {keyword}: {e}")
        return []


def scan_top_queries(pytrends, keyword: str) -> list[dict]:
    """Find top related queries."""
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=TRENDS_TIMEFRAME, geo=TRENDS_GEO)
        related = pytrends.related_queries()
        top = related.get(keyword, {}).get("top")
        if top is not None and not top.empty:
            return top.head(10).to_dict("records")
        return []
    except Exception as e:
        log.error(f"Top queries failed for {keyword}: {e}")
        return []


def scan_regional_interest(pytrends, keyword: str) -> list[dict]:
    """See which US states search this product most."""
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=TRENDS_TIMEFRAME, geo=TRENDS_GEO)
        df = pytrends.interest_by_region(resolution="REGION", inc_low_vol=False)
        if df.empty:
            return []
        df = df.sort_values(by=keyword, ascending=False)
        top_regions = df.head(10)
        return [
            {"region": idx, "interest": int(row[keyword])}
            for idx, row in top_regions.iterrows()
        ]
    except Exception as e:
        log.error(f"Regional interest failed for {keyword}: {e}")
        return []


def run_full_scan():
    """Run a complete trend scan across all seed keywords."""
    log.info("Starting full trend scan...")
    req_args = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        },
    }
    if PROXY_URL:
        req_args["proxies"] = {"https": PROXY_URL, "http": PROXY_URL}
        log.info("Using proxy for Google Trends requests")

    pytrends = TrendReq(
        hl="en-US", tz=360, retries=3, backoff_factor=3.0,
        requests_args=req_args,
    )

    report = {
        "scan_date": datetime.now().isoformat(),
        "geo": TRENDS_GEO,
        "timeframe": TRENDS_TIMEFRAME,
        "niches": {},
        "hot_products": [],
        "emerging_products": [],
        "breakout_products": [],
        "accelerating_products": [],
        "discoveries": [],
        "new_keywords": [],  # Auto-discovered keywords for next run
    }

    for niche_name, keywords in SEED_KEYWORDS.items():
        log.info(f"Scanning niche: {niche_name} ({len(keywords)} keywords)")
        niche_data = {"keywords": {}}

        # Process in batches of 5 (Google Trends limit)
        for i in range(0, len(keywords), 5):
            batch = keywords[i:i+5]

            # Rate limit handling with retry
            for attempt in range(3):
                interest = scan_interest_over_time(pytrends, batch)
                if interest:
                    niche_data["keywords"].update(interest)
                    break
                else:
                    wait = (attempt + 1) * 15 + random.uniform(5, 10)
                    log.warning(f"Trends rate limited, waiting {wait:.0f}s (attempt {attempt + 1}/3)")
                    time.sleep(wait)

            time.sleep(random.uniform(12, 20))

        # Get rising/top queries for each keyword
        for kw in keywords:
            if kw in niche_data["keywords"]:
                rising = scan_rising_queries(pytrends, kw)
                top = scan_top_queries(pytrends, kw)
                niche_data["keywords"][kw]["rising_queries"] = rising
                niche_data["keywords"][kw]["top_queries"] = top

                kw_data = niche_data["keywords"][kw]

                # Hot products: rising trend with significant interest
                if kw_data["trend"] in ("rising", "rising_fast") and kw_data["current"] > 40:
                    report["hot_products"].append({
                        "keyword": kw,
                        "niche": niche_name,
                        "current_interest": kw_data["current"],
                        "avg_interest": kw_data["avg"],
                        "slope": kw_data["slope"],
                        "acceleration": kw_data["acceleration"],
                    })

                # Emerging products: low interest but growing fast
                if kw_data.get("emerging"):
                    report["emerging_products"].append({
                        "keyword": kw,
                        "niche": niche_name,
                        "current_interest": kw_data["current"],
                        "slope": kw_data["slope"],
                        "acceleration": kw_data["acceleration"],
                    })

                # Breakout products: sudden spike in last 7 days
                if kw_data.get("breakout"):
                    report["breakout_products"].append({
                        "keyword": kw,
                        "niche": niche_name,
                        "current_interest": kw_data["current"],
                        "slope_7d": kw_data.get("slope_7d", 0),
                        "slope_30d": kw_data.get("slope_30d", 0),
                        "momentum_score": kw_data.get("momentum_score", 0),
                    })

                # Accelerating products: 7d > 14d > 30d slope
                if kw_data.get("momentum_status") == "accelerating":
                    report["accelerating_products"].append({
                        "keyword": kw,
                        "niche": niche_name,
                        "current_interest": kw_data["current"],
                        "slope_7d": kw_data.get("slope_7d", 0),
                        "slope_14d": kw_data.get("slope_14d", 0),
                        "slope_30d": kw_data.get("slope_30d", 0),
                        "momentum_score": kw_data.get("momentum_score", 0),
                    })

                # Discoveries from rising queries → feed back as new keywords
                for rq in rising:
                    growth = rq.get("value", 0)
                    if growth > 200:  # Breakout threshold
                        report["discoveries"].append({
                            "query": rq["query"],
                            "growth": growth,
                            "source_keyword": kw,
                            "niche": niche_name,
                        })
                    # Auto-discover new keywords for next scan
                    if growth > 100:
                        report["new_keywords"].append(rq["query"])

                time.sleep(random.uniform(12, 18))

        report["niches"][niche_name] = niche_data

    # Deduplicate new keywords
    report["new_keywords"] = list(set(report["new_keywords"]))[:30]

    # Save report
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"trends_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Trend report saved: {output_file}")
    log.info(
        f"Hot: {len(report['hot_products'])} | Emerging: {len(report['emerging_products'])} | "
        f"Discoveries: {len(report['discoveries'])} | New keywords: {len(report['new_keywords'])}"
    )

    # Telegram alert
    has_data = (report["hot_products"] or report["discoveries"]
                or report["emerging_products"] or report["breakout_products"]
                or report["accelerating_products"])
    if has_data:
        msg = f"🔥 <b>TREND SCAN COMPLETE</b>\n📅 {today}\n\n"

        if report["breakout_products"]:
            msg += f"💥 <b>BREAKOUT</b> — {len(report['breakout_products'])} me shperthim te papritur:\n"
            for p in report["breakout_products"][:5]:
                msg += (
                    f"  • <b>{p['keyword']}</b> (7d:{p['slope_7d']} vs 30d:{p['slope_30d']})\n"
                    f"    Momentum: {p['momentum_score']}/100\n"
                )

        if report["accelerating_products"]:
            msg += f"\n🚀 <b>ACCELERATING</b> — {len(report['accelerating_products'])} 7d>14d>30d:\n"
            for p in report["accelerating_products"][:5]:
                msg += (
                    f"  • <b>{p['keyword']}</b>\n"
                    f"    7d:{p['slope_7d']} | 14d:{p['slope_14d']} | 30d:{p['slope_30d']}\n"
                )

        if report["hot_products"]:
            msg += f"\n🔥 <b>HOT PRODUCTS</b> — {len(report['hot_products'])} me kerkese ne rritje:\n"
            for p in report["hot_products"][:5]:
                interest = p['current_interest']
                bar_str = "█" * (interest // 10) + "░" * (10 - interest // 10)
                accel = "⬆️" if p.get("acceleration", 0) > 0 else "➡️"
                msg += f"  • <b>{p['keyword']}</b>\n"
                msg += f"    {bar_str} {interest}/100 | slope: {p['slope']} {accel}\n"

        if report["emerging_products"]:
            msg += f"\n🌱 <b>EMERGING</b> — {len(report['emerging_products'])} ne fillim te rritjes:\n"
            for p in report["emerging_products"][:5]:
                msg += f"  • <b>{p['keyword']}</b> ({p['current_interest']}/100, slope: {p['slope']})\n"

        if report["discoveries"]:
            msg += f"\n💡 <b>ZBULIME TE REJA</b> — {len(report['discoveries'])} query ne shperthim:\n"
            for d in report["discoveries"][:5]:
                msg += f"  ▲ <i>\"{d['query']}\"</i>  +{d['growth']}%\n"
                msg += f"    nga: <code>{d['source_keyword']}</code>\n"

        if report["new_keywords"]:
            msg += f"\n🔑 <b>{len(report['new_keywords'])}</b> keywords te reja per skanimin e ardhshem"

        msg += f"\n\n📁 <code>data/trends_{today}.json</code>"
        send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_full_scan()
