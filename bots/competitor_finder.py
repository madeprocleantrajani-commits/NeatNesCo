"""
Competitor Store Finder v2
----------------------------
Automatically discovers Shopify stores selling products
similar to your seed keywords.

Discovery methods (in order):
  1. Google search (when accessible or proxy configured)
  2. Brute-force: generate common store name patterns + verify /products.json
  
Both methods verify stores via Shopify's /products.json API.

Outputs: data/competitors_discovered.json
Run: weekly
"""

import json
import time
import random
import re
from datetime import datetime
from urllib.parse import quote_plus, urlparse

from bs4 import BeautifulSoup

from config import (
    DATA_DIR, SEED_KEYWORDS, PROXY_URL, get_logger, get_session,
    is_physical_product, parse_price,
)
from alert_bot import send_alert

log = get_logger("competitor_finder")

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    import requests as curl_requests
    HAS_CURL_CFFI = False


def _web_get(url: str, timeout: int = 20) -> str | None:
    """Fetch a URL using curl_cffi with Chrome fingerprint."""
    try:
        kwargs = {"timeout": timeout}
        if HAS_CURL_CFFI:
            kwargs["impersonate"] = "chrome"
            if PROXY_URL:
                kwargs["proxies"] = {"http": PROXY_URL, "https": PROXY_URL}
        else:
            kwargs["headers"] = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
            }
            if PROXY_URL:
                kwargs["proxies"] = {"http": PROXY_URL, "https": PROXY_URL}
        resp = curl_requests.get(url, **kwargs)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception:
        return None


def _generate_store_names(keyword: str) -> list[str]:
    """Generate common Shopify store name patterns from a keyword."""
    slug = keyword.lower().replace(" ", "-")
    words = keyword.lower().split()
    names = set()

    # Direct patterns
    names.add(slug)
    names.add(f"the-{slug}")
    names.add(f"{slug}-store")
    names.add(f"{slug}-shop")
    names.add(f"my-{slug}")
    names.add(f"best-{slug}")
    names.add(f"get-{slug}")
    names.add(f"buy-{slug}")
    names.add(f"{slug}-co")
    names.add(f"{slug}-official")

    # Without hyphens
    joined = "".join(words)
    names.add(joined)
    names.add(f"the{joined}")
    names.add(f"get{joined}")

    # Word combos for multi-word keywords
    if len(words) > 1:
        names.add(words[0])
        names.add(words[-1])
        names.add(f"{words[0]}-{words[-1]}")
        names.add(f"{words[-1]}-{words[0]}")
        for i, w in enumerate(words):
            for j, w2 in enumerate(words):
                if i != j:
                    names.add(f"{w}{w2}")

    return list(names)


def search_stores_google(keyword: str, max_results: int = 10) -> list[str]:
    """Search Google for Shopify stores selling this product."""
    stores = set()

    queries = [
        f'site:myshopify.com "{keyword}"',
        f'"{keyword}" "powered by shopify"',
    ]

    for query in queries:
        url = f"https://www.google.com/search?q={quote_plus(query)}&num=20"
        html = _web_get(url)
        if not html:
            continue
        if "unusual traffic" in html.lower():
            continue

        # Extract myshopify URLs from HTML
        raw_urls = re.findall(r'https?://[\w.-]+\.myshopify\.com', html)
        for raw in raw_urls:
            parsed = urlparse(raw)
            domain = parsed.netloc.lower()
            store_name = domain.split(".myshopify.com")[0]
            stores.add(f"https://{store_name}.myshopify.com")

        # Also parse links
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/url?q=" in href:
                actual = href.split("/url?q=")[1].split("&")[0]
                if "myshopify.com" in actual:
                    parsed = urlparse(actual)
                    name = parsed.netloc.split(".myshopify.com")[0]
                    stores.add(f"https://{name}.myshopify.com")

        time.sleep(random.uniform(5, 10))

    return list(stores)[:max_results]


def search_stores_bruteforce(keyword: str) -> list[str]:
    """Discover Shopify stores by trying common name patterns."""
    names = _generate_store_names(keyword)
    found = []
    session = get_session(use_proxy=False)  # Direct, no proxy needed

    for name in names:
        url = f"https://{name}.myshopify.com/products.json?limit=1"
        try:
            resp = session.get(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("products"):
                    found.append(f"https://{name}.myshopify.com")
                    log.info(f"    Brute-force hit: {name}.myshopify.com")
        except Exception:
            pass
        time.sleep(0.3)

    return found


def verify_shopify_store(store_url: str) -> dict | None:
    """Verify a URL is a Shopify store and get basic stats."""
    session = get_session(use_proxy=False)  # Shopify API works from any IP
    products_url = f"{store_url.rstrip('/')}/products.json?limit=250"

    try:
        resp = session.get(products_url, timeout=10)
        if resp.status_code != 200:
            return None

        data = resp.json()
        products = data.get("products", [])
        if not products:
            return None

        prices = []
        product_types = set()
        titles = []

        for p in products:
            titles.append(p.get("title", ""))
            ptype = p.get("product_type", "")
            if ptype:
                product_types.add(ptype)
            for v in p.get("variants", []):
                price = parse_price(v.get("price", ""))
                if price and price > 0:
                    prices.append(price)

        store_info = {
            "url": store_url,
            "product_count": len(products),
            "product_types": list(product_types)[:10],
            "sample_titles": [t for t in titles[:5] if t],
        }

        if prices:
            store_info["avg_price"] = round(sum(prices) / len(prices), 2)
            store_info["min_price"] = min(prices)
            store_info["max_price"] = max(prices)
            store_info["price_range"] = f"${min(prices):.2f}-${max(prices):.2f}"

        return store_info

    except Exception:
        return None


def discover_competitors() -> dict:
    """Discover competitor Shopify stores for all seed keywords."""
    log.info("Starting competitor discovery...")

    # Check if Google search works
    test_html = _web_get("https://www.google.com/search?q=test", timeout=15)
    google_works = bool(test_html and "unusual traffic" not in test_html.lower())

    if google_works:
        log.info("Google search available — using search + brute-force")
    else:
        log.info("Google blocked — using brute-force discovery only")

    all_stores = {}
    keyword_stores = {}

    for niche, keywords in SEED_KEYWORDS.items():
        log.info(f"Searching niche: {niche}")

        for kw in keywords:
            log.info(f"  Searching: {kw}")

            # Method 1: Google search (if available)
            found_urls = []
            if google_works:
                found_urls = search_stores_google(kw, max_results=10)

            # Method 2: Brute-force (always runs)
            brute_urls = search_stores_bruteforce(kw)
            for bu in brute_urls:
                if bu not in found_urls:
                    found_urls.append(bu)

            # Verify each store
            verified = []
            for url in found_urls:
                domain = urlparse(url).netloc
                if domain in all_stores:
                    verified.append(domain)
                    continue

                info = verify_shopify_store(url)
                if info:
                    all_stores[domain] = info
                    all_stores[domain]["found_via"] = kw
                    all_stores[domain]["niche"] = niche
                    verified.append(domain)
                    log.info(
                        f"    FOUND: {domain}: {info['product_count']} products, "
                        f"avg ${info.get('avg_price', 0):.2f}"
                    )

                time.sleep(random.uniform(0.5, 1.5))

            keyword_stores[kw] = verified
            time.sleep(random.uniform(1, 3))

    # Build report
    report = {
        "scan_date": datetime.now().isoformat(),
        "method": "google+bruteforce" if google_works else "bruteforce_only",
        "stores_found": len(all_stores),
        "stores": all_stores,
        "keyword_coverage": {
            kw: len(stores) for kw, stores in keyword_stores.items()
        },
        "store_urls": list(info["url"] for info in all_stores.values()),
    }

    # Save
    output_file = DATA_DIR / "competitors_discovered.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    log.info(f"Discovery complete: {len(all_stores)} stores found")

    # Telegram alert
    if all_stores:
        msg = f"COMPETITOR DISCOVERY\n"
        msg += f"Method: {report['method']}\n"
        msg += f"Stores found: {len(all_stores)}\n\n"
        for domain, info in list(all_stores.items())[:8]:
            msg += (
                f"  {domain}\n"
                f"    {info['product_count']} products | "
                f"Avg ${info.get('avg_price', 0):.2f} | "
                f"Via: {info.get('found_via', '?')}\n"
            )
        send_alert(msg)
    else:
        send_alert(
            f"COMPETITOR DISCOVERY\n"
            f"Method: {report['method']}\n"
            f"0 stores found. Add PROXY_URL for better discovery."
        )

    return report


if __name__ == "__main__":
    discover_competitors()
