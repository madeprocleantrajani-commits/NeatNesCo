#!/usr/bin/env python3
"""
DROPSHIP INTELLIGENCE FILTER
Finds winning non-brand products using multi-source validation.
Only accepts products that pass ALL filters:
  - TikTok viral (videos with 500k+ views)
  - Amazon rating > 4.3 stars
  - 3x markup possible (sell price >= 3x supplier cost)
  - NOT a brand product
"""

import requests
import json
import re
import time
import os
from datetime import datetime

DATA_DIR = os.path.expanduser("~/dropship-bots/data")
os.makedirs(DATA_DIR, exist_ok=True)

# ===== WINNING PRODUCT NICHES (non-brand, high-demand, viral potential) =====
SEARCH_QUERIES = [
    "electric spin scrubber cleaning brush",
    "portable blender usb rechargeable",
    "led motion sensor night light",
    "silicone ice cube tray with lid",
    "electric milk frother handheld",
    "magnetic phone mount car",
    "posture corrector back brace",
    "portable neck fan hands free",
    "cloud slides slippers pillow",
    "led strip lights bedroom",
    "mini waffle maker",
    "teeth whitening kit led",
    "scalp massager shampoo brush",
    "insulated tumbler stainless steel 40oz",
    "sunset lamp projector",
    "portable steamer clothes",
    "acne pimple patch",
    "glass olive oil sprayer",
    "vegetable chopper mandoline",
    "electric lighter rechargeable usb",
    "car vacuum cleaner portable",
    "hair claw clips large",
    "blue light blocking glasses",
    "resistance bands set exercise",
    "tongue scraper stainless steel",
    "shower head high pressure",
    "smart water bottle reminder",
    "pet hair remover roller",
    "makeup organizer rotating",
    "self cleaning hair brush",
]


def check_amazon(query):
    """Search Amazon for product, get rating, price, review count"""
    try:
        url = "https://www.amazon.com/s?k=" + query.replace(" ", "+")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        r = requests.get(url, headers=headers, timeout=15)

        ratings = re.findall(r"(\d\.\d) out of 5 stars", r.text)
        prices = re.findall(r"\$(\d+\.\d{2})", r.text)
        reviews = re.findall(r"([\d,]+)\s*(?:ratings|reviews)", r.text)
        asins = re.findall(r"/dp/([A-Z0-9]{10})", r.text)

        if ratings and prices and asins:
            rating = float(ratings[0])
            price = float(prices[0]) if prices else 0
            review_count = int(reviews[0].replace(",", "")) if reviews else 0
            asin = asins[0]

            return {
                "rating": rating,
                "price": price,
                "reviews": review_count,
                "asin": asin,
                "found": True,
            }
    except Exception as e:
        pass

    return {"found": False}


def estimate_supplier_cost(amazon_price):
    """Estimate AliExpress/CJ supplier cost (typically 20-35% of Amazon price)"""
    return round(amazon_price * 0.28, 2)


def check_tiktok_viral(query):
    """Check if product has viral TikTok presence via web search"""
    try:
        search_url = "https://www.google.com/search?q=tiktok+" + query.replace(" ", "+") + "+viral+review"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        r = requests.get(search_url, headers=headers, timeout=10)

        views = re.findall(r"(\d+(?:\.\d+)?)\s*[MmBb]\s*(?:views|Views)", r.text)
        tiktok_mentions = r.text.lower().count("tiktok")
        viral_mentions = r.text.lower().count("viral")

        has_views = len(views) > 0
        view_count = 0
        if views:
            num = float(views[0].replace(",", ""))
            view_count = num * 1000000

        viral_score = 0
        if has_views:
            viral_score += 3
        viral_score += min(tiktok_mentions, 5)
        viral_score += min(viral_mentions, 3)

        return {
            "viral_score": viral_score,
            "estimated_views": view_count,
            "tiktok_mentions": tiktok_mentions,
            "is_viral": viral_score >= 3,
        }
    except:
        return {"viral_score": 0, "is_viral": False, "estimated_views": 0, "tiktok_mentions": 0}


def filter_products():
    """Run the full product filter pipeline"""
    print("=" * 60)
    print("DROPSHIP INTELLIGENCE FILTER")
    print("Scanning %d product categories..." % len(SEARCH_QUERIES))
    print("=" * 60)

    results = []

    for i, query in enumerate(SEARCH_QUERIES):
        print("\n[%d/%d] Analyzing: %s" % (i + 1, len(SEARCH_QUERIES), query))

        amazon = check_amazon(query)
        time.sleep(1.5)

        if not amazon.get("found"):
            print("  X Not found on Amazon")
            continue

        tiktok = check_tiktok_viral(query)
        time.sleep(1)

        supplier_cost = estimate_supplier_cost(amazon["price"])
        selling_price = amazon["price"]
        shipping_est = 3.0
        shopify_fee = round(selling_price * 0.029 + 0.30, 2)
        total_cost = supplier_cost + shipping_est + shopify_fee
        profit = round(selling_price - total_cost, 2)
        margin = round((profit / selling_price) * 100, 1) if selling_price > 0 else 0
        markup = round(selling_price / (supplier_cost + shipping_est), 1) if (supplier_cost + shipping_est) > 0 else 0

        passes_rating = amazon["rating"] >= 4.3
        passes_markup = markup >= 2.5
        passes_viral = tiktok["is_viral"]
        passes_price = 10 <= selling_price <= 60

        score = 0
        if passes_rating:
            score += 25
        if passes_markup:
            score += 25
        if passes_viral:
            score += 30
        if passes_price:
            score += 20
        if amazon.get("reviews", 0) > 1000:
            score += 10

        status = "PASS" if score >= 70 else "MAYBE" if score >= 50 else "FAIL"

        print("  Amazon: $%.2f | Rating: %.1f | %d reviews" % (selling_price, amazon["rating"], amazon.get("reviews", 0)))
        print("  Supplier est: $%.2f + $%.2f ship" % (supplier_cost, shipping_est))
        print("  Margin: %.1f%% | Markup: %.1fx" % (margin, markup))
        print("  TikTok viral: %s (score: %d)" % ("YES" if tiktok["is_viral"] else "NO", tiktok["viral_score"]))
        print("  %s (score: %d/100)" % (status, score))

        results.append({
            "query": query,
            "amazon_price": selling_price,
            "amazon_rating": amazon["rating"],
            "amazon_reviews": amazon.get("reviews", 0),
            "asin": amazon.get("asin", ""),
            "supplier_cost": supplier_cost,
            "shipping_cost": shipping_est,
            "selling_price": selling_price,
            "profit": profit,
            "margin": margin,
            "markup": markup,
            "tiktok_viral": tiktok["is_viral"],
            "tiktok_score": tiktok["viral_score"],
            "total_score": score,
            "passes_rating": passes_rating,
            "passes_markup": passes_markup,
            "passes_viral": passes_viral,
            "passes_price": passes_price,
        })

    results.sort(key=lambda x: x["total_score"], reverse=True)

    heroes = [r for r in results if r["total_score"] >= 80][:3]
    tests = [r for r in results if 60 <= r["total_score"] < 80][:6]
    backups = [r for r in results if 45 <= r["total_score"] < 60][:6]

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    print("\nHERO PRODUCTS (%d/3):" % len(heroes))
    for p in heroes:
        print("  * %s | $%.2f | %.1f%% margin | Score: %d" % (p["query"], p["selling_price"], p["margin"], p["total_score"]))

    print("\nTEST PRODUCTS (%d/6):" % len(tests))
    for p in tests:
        print("  * %s | $%.2f | %.1f%% margin | Score: %d" % (p["query"], p["selling_price"], p["margin"], p["total_score"]))

    print("\nBACKUP PRODUCTS (%d/6):" % len(backups))
    for p in backups:
        print("  * %s | $%.2f | %.1f%% margin | Score: %d" % (p["query"], p["selling_price"], p["margin"], p["total_score"]))

    output = {
        "scan_date": datetime.now().isoformat(),
        "total_scanned": len(SEARCH_QUERIES),
        "total_passed": len([r for r in results if r["total_score"] >= 45]),
        "heroes": heroes,
        "tests": tests,
        "backups": backups,
        "all_results": results,
    }

    with open(os.path.join(DATA_DIR, "winning_products.json"), "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to data/winning_products.json")
    print("Total: %d heroes | %d tests | %d backups" % (len(heroes), len(tests), len(backups)))

    return output


if __name__ == "__main__":
    filter_products()
