#!/usr/bin/env python3
"""
Fix 14 safe generic products:
1. Search Amazon for product images
2. Add images to Shopify
3. Clean up titles (shorter, professional, NO brand names in title)
4. Set proper product types and tags
"""

import requests
import json
import re
import time
import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SHOP = os.getenv("SHOPIFY_STORE", "8hendy-8i.myshopify.com")
TOKEN = os.getenv("SHOPIFY_TOKEN", "")
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
API = "https://%s/admin/api/2024-01" % SHOP

img_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

PRODUCTS = [
    {
        "id": 14977660289396,
        "search": "instant read meat thermometer digital kitchen cooking",
        "clean_title": "Instant Read Digital Meat Thermometer - Fast & Accurate",
        "type": "Kitchen",
        "tags": "kitchen,cooking,thermometer,grilling,BBQ",
    },
    {
        "id": 14972661039476,
        "search": "PEVA shower liner clear waterproof curtain",
        "clean_title": "Premium Clear Shower Liner - Waterproof PEVA",
        "type": "Home & Bath",
        "tags": "home,bathroom,shower,curtain,waterproof",
    },
    {
        "id": 14975463883124,
        "search": "silicone spatula set 5 piece heat resistant kitchen",
        "clean_title": "5-Piece Heat Resistant Silicone Spatula Set",
        "type": "Kitchen",
        "tags": "kitchen,spatula,cooking,baking,silicone",
    },
    {
        "id": 14972661072244,
        "search": "kitchen sink sponge holder caddy organizer stainless",
        "clean_title": "Stainless Steel Kitchen Sink Caddy Organizer",
        "type": "Kitchen",
        "tags": "kitchen,organizer,sink,sponge holder,stainless",
    },
    {
        "id": 14987866407284,
        "search": "digital kitchen food scale grams ounces",
        "clean_title": "Digital Kitchen Food Scale - Precision Grams & Ounces",
        "type": "Kitchen",
        "tags": "kitchen,scale,food scale,digital,baking,meal prep",
    },
    {
        "id": 14987376886132,
        "search": "mini portable clip on fan stroller baby battery",
        "clean_title": "Mini Portable Clip-On Fan - Battery Operated",
        "type": "Baby & Outdoor",
        "tags": "baby,stroller,fan,portable,summer,clip on",
    },
    {
        "id": 14986847617396,
        "search": "high pressure rainfall shower head handheld combo dual",
        "clean_title": "Dual High Pressure Rain Shower Head with Handheld",
        "type": "Home & Bath",
        "tags": "home,bathroom,shower head,high pressure,rainfall",
    },
    {
        "id": 14975463620980,
        "search": "weighted jump rope tangle free speed ball bearing",
        "clean_title": "Tangle-Free Weighted Speed Jump Rope",
        "type": "Health & Fitness",
        "tags": "fitness,jump rope,exercise,cardio,workout",
    },
    {
        "id": 14975463817588,
        "search": "LED headlamp rechargeable bright waterproof",
        "clean_title": "Ultra-Bright Rechargeable LED Headlamp",
        "type": "Outdoor",
        "tags": "outdoor,headlamp,LED,flashlight,camping,hiking",
    },
    {
        "id": 14987376984436,
        "search": "under cabinet LED light bar rechargeable motion sensor",
        "clean_title": "Under Cabinet LED Light Bar with Motion Sensor (2-Pack)",
        "type": "Home & Lighting",
        "tags": "home,lighting,LED,cabinet,motion sensor,rechargeable",
    },
    {
        "id": 14975463981428,
        "search": "chicken shredder tool meat shredder twist",
        "clean_title": "Twist Chicken & Meat Shredder Tool",
        "type": "Kitchen",
        "tags": "kitchen,meat shredder,chicken,cooking,meal prep",
    },
    {
        "id": 14986847682932,
        "search": "glass olive oil sprayer bottle mister cooking",
        "clean_title": "Glass Olive Oil Sprayer Bottle for Cooking",
        "type": "Kitchen",
        "tags": "kitchen,olive oil sprayer,cooking,glass,healthy",
    },
    {
        "id": 14987866505588,
        "search": "kojic acid dark spot remover soap bar skin brightening",
        "clean_title": "Kojic Acid Dark Spot Remover Soap Bars (2-Pack)",
        "type": "Beauty & Skincare",
        "tags": "beauty,skincare,dark spots,soap,brightening,kojic acid",
    },
    {
        "id": 14986847584628,
        "search": "handheld milk frother electric wand coffee foam",
        "clean_title": "Electric Handheld Milk Frother Wand",
        "type": "Kitchen",
        "tags": "kitchen,milk frother,coffee,latte,foam maker",
    },
]


def search_amazon_images(search_term):
    """Search Amazon and get product images"""
    search_url = "https://www.amazon.com/s?k=" + search_term.replace(" ", "+")
    try:
        r = requests.get(search_url, headers=img_headers, timeout=15)
        asins = re.findall(r"/dp/([A-Z0-9]{10})", r.text)
        if not asins:
            print("    No ASINs found in search results")
            return []

        unique_asins = list(dict.fromkeys(asins))
        for asin in unique_asins[:5]:
            prod_url = "https://www.amazon.com/dp/%s" % asin
            r2 = requests.get(prod_url, headers=img_headers, timeout=15)

            hi_res = re.findall(
                r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"', r2.text
            )
            large = re.findall(
                r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"', r2.text
            )

            images = list(dict.fromkeys(hi_res + large))[:5]
            if images:
                print("    Found %d images from ASIN %s" % (len(images), asin))
                return images
            time.sleep(1)

        return []
    except Exception as e:
        print("    Search error: %s" % str(e))
        return []


def add_images_to_product(product_id, images):
    """Add images to a Shopify product"""
    added = 0
    for idx, img_url in enumerate(images):
        payload = {"image": {"src": img_url, "position": idx + 1}}
        r = requests.post(
            "%s/products/%d/images.json" % (API, product_id),
            headers=HEADERS,
            json=payload,
        )
        if r.status_code == 200:
            added += 1
        else:
            print("    Image %d failed: HTTP %s" % (idx + 1, r.status_code))
        time.sleep(0.5)
    return added


def update_product(product_id, title, product_type, tags):
    """Update product title, type, and tags"""
    payload = {
        "product": {
            "id": product_id,
            "title": title,
            "product_type": product_type,
            "tags": tags,
        }
    }
    r = requests.put(
        "%s/products/%d.json" % (API, product_id),
        headers=HEADERS,
        json=payload,
    )
    return r.status_code == 200


# ── Main ──

print("=" * 60)
print("FIXING 14 SAFE PRODUCTS - Images + Titles + Types")
print("=" * 60)

total_images = 0
success = 0
failed = []

for i, item in enumerate(PRODUCTS):
    pid = item["id"]
    name = item["clean_title"]
    print("\n[%d/%d] %s (ID: %d)" % (i + 1, len(PRODUCTS), name, pid))

    # 1. Update title, type, tags
    if update_product(pid, item["clean_title"], item["type"], item["tags"]):
        print("  OK - Title/type/tags updated")
    else:
        print("  FAIL - Could not update product info")

    # 2. Search for images
    print("  Searching: %s" % item["search"])
    images = search_amazon_images(item["search"])

    if images:
        added = add_images_to_product(pid, images)
        print("  OK - %d/%d images added" % (added, len(images)))
        total_images += added
        if added > 0:
            success += 1
        else:
            failed.append(name)
    else:
        print("  FAIL - No images found")
        failed.append(name)

    time.sleep(2)

print("\n" + "=" * 60)
print("RESULTS:")
print("  Products fixed: %d/%d" % (success, len(PRODUCTS)))
print("  Total images added: %d" % total_images)
if failed:
    print("  Need manual fix (%d):" % len(failed))
    for f in failed:
        print("    - %s" % f)
else:
    print("  All products fixed successfully!")
print("=" * 60)

# Save results
results = {
    "success": success,
    "total": len(PRODUCTS),
    "images": total_images,
    "failed": failed,
}
with open(
    os.path.expanduser("~/dropship-bots/data/fix_results.json"), "w"
) as fout:
    json.dump(results, fout, indent=2)
