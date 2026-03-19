"""
eBay Sold Listings Scanner v3
-------------------------------
v3: New-condition filter, date filtering (last 30 days), median price,
    seller count for competition analysis, retry with backoff, pagination.

Outputs: data/ebay_YYYY-MM-DD.json
"""

import json
import re
import time
import random
from datetime import datetime, timedelta
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from config import (
    DATA_DIR, SEED_KEYWORDS, PROXY_URL, get_logger,
    is_physical_product, parse_price, resilient_fetch, get_session,
)
from validators import validate_price
from alert_bot import send_alert

log = get_logger("ebay_scanner")

EBAY_SOLD_URL = (
    "https://www.ebay.com/sch/i.html"
    "?_nkw={query}"
    "&LH_Complete=1"
    "&LH_Sold=1"
    "&LH_ItemCondition=1000"  # NEW condition only
    "&_sop=13"
    "&_ipg=60"
)

# Import curl_cffi if available
try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
    log.info("Using curl_cffi for browser TLS fingerprint")
except ImportError:
    import requests as curl_requests
    HAS_CURL_CFFI = False
    log.info("curl_cffi not available, using standard requests")


def _get_ebay_page(url: str, timeout: int = 25) -> str | None:
    """Fetch an eBay page with browser-like fingerprinting."""
    try:
        kwargs = {"timeout": timeout}

        if HAS_CURL_CFFI:
            kwargs["impersonate"] = "chrome"
            if PROXY_URL:
                kwargs["proxies"] = {"http": PROXY_URL, "https": PROXY_URL}
            resp = curl_requests.get(url, **kwargs)
        else:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml",
            }
            kwargs["headers"] = headers
            if PROXY_URL:
                kwargs["proxies"] = {"http": PROXY_URL, "https": PROXY_URL}
            resp = curl_requests.get(url, **kwargs)

        if resp.status_code == 429:
            log.warning("eBay rate limited (429). Backing off...")
            return None

        if resp.status_code != 200:
            log.warning(f"eBay returned status {resp.status_code}")
            return None

        if "Pardon Our Interruption" in resp.text[:1000]:
            return None

        return resp.text

    except Exception as e:
        log.warning(f"eBay request failed: {e}")
        return None


def check_ebay_access() -> bool:
    """Quick connectivity check."""
    test_url = EBAY_SOLD_URL.format(query="test")
    html = _get_ebay_page(test_url, timeout=20)
    if html is None:
        return False
    if "srp-results" in html or "s-item" in html:
        return True
    if len(html) > 50000:
        return True
    return False


def _parse_sold_date(date_text: str) -> datetime | None:
    """Parse eBay sold date in various formats."""
    try:
        cleaned = date_text.replace("Sold", "").replace("sold", "").replace("Ended:", "").strip()
        # Remove day-of-week prefix if present (e.g., "Mon, Mar 1, 2026")
        if "," in cleaned and len(cleaned.split(",")[0].strip()) <= 3:
            cleaned = cleaned.split(",", 1)[1].strip()
        for fmt in [
            "%b %d, %Y",    # Mar 1, 2026
            "%d %b %Y",     # 1 Mar 2026
            "%b %d %Y",     # Mar 1 2026
            "%B %d, %Y",    # March 1, 2026
            "%d %B %Y",     # 1 March 2026
            "%m/%d/%Y",     # 03/01/2026
            "%d/%m/%Y",     # 01/03/2026
            "%Y-%m-%d",     # 2026-03-01
        ]:
            try:
                return datetime.strptime(cleaned, fmt)
            except ValueError:
                continue
    except Exception:
        pass
    return None


def scrape_sold_listings(keyword: str, max_pages: int = 2) -> dict:
    """Scrape eBay sold/completed listings for a keyword."""
    result = {
        "keyword": keyword,
        "sold_count": 0,
        "listings": [],
        "prices": [],
        "sellers": set(),
        "price_analysis": {},
    }

    cutoff_date = datetime.now() - timedelta(days=30)

    for page in range(1, max_pages + 1):
        page_param = f"&_pgn={page}" if page > 1 else ""
        url = EBAY_SOLD_URL.format(query=quote_plus(keyword)) + page_param

        html = _get_ebay_page(url)
        if html is None:
            if page == 1:
                log.warning(f"eBay blocked for '{keyword}'")
            break

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Total results count (only from page 1)
            if page == 1:
                count_el = soup.select_one(".srp-controls__count-heading span")
                if count_el:
                    count_text = count_el.get_text(strip=True).replace(",", "")
                    try:
                        result["sold_count"] = int(re.search(r"\d+", count_text).group())
                    except (ValueError, AttributeError):
                        pass

                if result["sold_count"] == 0:
                    for sel in [".srp-controls__count-heading", "h1.srp-controls__count-heading"]:
                        el = soup.select_one(sel)
                        if el:
                            text = el.get_text(strip=True).replace(",", "")
                            m = re.search(r"([\d,]+)\s+results", text)
                            if m:
                                result["sold_count"] = int(m.group(1).replace(",", ""))
                                break

            # Individual listings
            items = soup.select(".s-item")
            if not items:
                items = soup.select("[data-viewport]") or soup.select(".srp-river-answer li")

            for item in items:
                listing = {}

                # Title
                title_el = item.select_one(".s-item__title")
                if title_el:
                    title = title_el.get_text(strip=True)
                    if "shop on ebay" in title.lower():
                        continue
                    listing["title"] = title

                if not listing.get("title"):
                    continue

                if not is_physical_product(listing["title"]):
                    continue

                # Sold date — filter to last 30 days
                sold_el = item.select_one(".s-item__title--tagblock .POSITIVE, .s-item__endedDate")
                if sold_el:
                    date_text = sold_el.get_text(strip=True)
                    listing["sold_date"] = date_text
                    parsed_date = _parse_sold_date(date_text)
                    if parsed_date and parsed_date < cutoff_date:
                        continue  # Skip items sold more than 30 days ago

                # Sold price
                price_el = item.select_one(".s-item__price")
                if price_el:
                    price_text = price_el.get_text(strip=True)
                    listing["price_raw"] = price_text
                    prices_found = re.findall(r"\$?([\d,.]+)", price_text)
                    if prices_found:
                        try:
                            price_val = float(prices_found[0].replace(",", ""))
                            listing["price"] = validate_price(price_val)
                            if listing["price"]:
                                result["prices"].append(listing["price"])
                        except ValueError:
                            pass

                # Shipping
                ship_el = item.select_one(".s-item__shipping")
                if ship_el:
                    ship_text = ship_el.get_text(strip=True)
                    listing["shipping"] = ship_text
                    if "free" in ship_text.lower():
                        listing["shipping_cost"] = 0.0

                # Seller
                seller_el = item.select_one(".s-item__seller-info-text")
                if seller_el:
                    seller = seller_el.get_text(strip=True)
                    listing["seller"] = seller
                    result["sellers"].add(seller)

                # URL
                link_el = item.select_one(".s-item__link")
                if link_el:
                    listing["url"] = link_el.get("href", "")

                result["listings"].append(listing)

        except Exception as e:
            log.error(f"Parse error for '{keyword}' page {page}: {e}")

        time.sleep(random.uniform(3, 6))

    # Price analysis with proper median (using statistics module)
    if result["prices"]:
        from statistics import median as calc_median
        prices = sorted(result["prices"])
        median = calc_median(prices)

        result["price_analysis"] = {
            "min": round(min(prices), 2),
            "max": round(max(prices), 2),
            "avg": round(sum(prices) / len(prices), 2),
            "median": round(median, 2),
            "under_15": sum(1 for p in prices if p < 15),
            "15_to_30": sum(1 for p in prices if 15 <= p < 30),
            "30_to_50": sum(1 for p in prices if 30 <= p < 50),
            "over_50": sum(1 for p in prices if p >= 50),
            "sample_size": len(prices),
        }

    # Competition analysis
    result["unique_sellers"] = len(result["sellers"])
    result["competition_level"] = (
        "high" if result["unique_sellers"] > 20 else
        "medium" if result["unique_sellers"] > 5 else
        "low"
    )

    # Daily sales velocity
    if result["sold_count"] > 0:
        result["daily_velocity"] = round(result["sold_count"] / 30, 1)

    # Convert set to list for JSON
    result["sellers"] = list(result["sellers"])[:10]

    log.info(
        f"eBay '{keyword}': {result['sold_count']} sold, "
        f"{len(result['listings'])} scraped (new, 30d), "
        f"median ${result['price_analysis'].get('median', 0):.2f}, "
        f"{result['unique_sellers']} sellers ({result.get('competition_level', '?')})"
    )

    return result


def run_ebay_scan(keywords: list[str] = None) -> dict:
    """Scan eBay sold listings."""
    log.info("Starting eBay sold listings scan...")

    has_access = check_ebay_access()
    if not has_access:
        log.warning("eBay BLOCKED — skipping scan")
        report = {
            "scan_date": datetime.now().isoformat(),
            "status": "blocked",
            "message": "eBay blocked this IP. Add residential proxy via PROXY_URL in .env",
            "keywords_scanned": 0, "results": {}, "top_sellers": [],
            "price_insights": [],
            "stats": {"total_sold_found": 0, "keywords_with_sales": 0, "avg_sold_price_all": 0},
        }
        today = datetime.now().strftime("%Y-%m-%d")
        output_file = DATA_DIR / f"ebay_{today}.json"
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        send_alert("📊 EBAY SCAN: BLOCKED\nShto PROXY_URL ne .env per akses te plote.")
        return report

    log.info("eBay accessible — running full scan")

    if not keywords:
        keywords = []
        for niche_kws in SEED_KEYWORDS.values():
            keywords.extend(niche_kws)

    report = {
        "scan_date": datetime.now().isoformat(),
        "status": "ok",
        "keywords_scanned": len(keywords),
        "results": {},
        "top_sellers": [],
        "price_insights": [],
    }

    for kw in keywords:
        log.info(f"Scanning: {kw}")
        data = scrape_sold_listings(kw, max_pages=2)
        report["results"][kw] = {
            "sold_count": data["sold_count"],
            "listings_scraped": len(data["listings"]),
            "price_analysis": data["price_analysis"],
            "unique_sellers": data.get("unique_sellers", 0),
            "competition_level": data.get("competition_level", "unknown"),
            "daily_velocity": data.get("daily_velocity", 0),
            "top_listings": data["listings"][:5],
        }
        time.sleep(random.uniform(3, 6))

    # Rank keywords by sold count
    ranked = sorted(
        report["results"].items(),
        key=lambda x: x[1]["sold_count"],
        reverse=True,
    )

    for kw, data in ranked[:15]:
        if data["sold_count"] > 0:
            report["top_sellers"].append({
                "keyword": kw,
                "sold_count": data["sold_count"],
                "avg_price": data["price_analysis"].get("avg", 0),
                "median_price": data["price_analysis"].get("median", 0),
                "daily_velocity": data.get("daily_velocity", 0),
                "competition": data.get("competition_level", "?"),
            })

    # Price insights — only products with real demand
    for kw, data in ranked:
        pa = data.get("price_analysis", {})
        if pa.get("median", 0) >= 15 and data["sold_count"] >= 10:
            report["price_insights"].append({
                "keyword": kw,
                "sold_count": data["sold_count"],
                "median_price": pa["median"],
                "avg_sold_price": pa["avg"],
                "price_range": f"${pa.get('min', 0):.2f}-${pa.get('max', 0):.2f}",
                "competition": data.get("competition_level", "?"),
            })

    # Stats
    report["stats"] = {
        "total_sold_found": sum(r["sold_count"] for r in report["results"].values()),
        "keywords_with_sales": sum(1 for r in report["results"].values() if r["sold_count"] > 0),
        "avg_sold_price_all": 0,
    }

    all_medians = [r["price_analysis"]["median"] for r in report["results"].values() if r["price_analysis"].get("median")]
    if all_medians:
        report["stats"]["avg_sold_price_all"] = round(sum(all_medians) / len(all_medians), 2)

    # Save
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = DATA_DIR / f"ebay_{today}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"eBay scan complete: {output_file}")

    # Telegram alert
    if report["top_sellers"]:
        msg = f"📊 <b>EBAY SOLD LISTINGS SCAN</b>\n📅 {today}\n\n"
        msg += f"🔍 Keywords: {len(keywords)} | Shitje totale: {report['stats']['total_sold_found']}\n\n"
        msg += f"🏆 <b>ME TE SHITURA (New, 30 dite):</b>\n"
        for ts in report["top_sellers"][:8]:
            comp_icon = "🔴" if ts["competition"] == "high" else "🟡" if ts["competition"] == "medium" else "🟢"
            msg += (
                f"  • <b>{ts['keyword']}</b> — {ts['sold_count']} shitje\n"
                f"    Median: ${ts['median_price']:.2f} | {ts['daily_velocity']}/dite | {comp_icon} {ts['competition']}\n"
            )
        msg += f"\n📁 <code>data/ebay_{today}.json</code>"
        send_alert(msg, parse_mode="HTML")

    return report


if __name__ == "__main__":
    run_ebay_scan()
