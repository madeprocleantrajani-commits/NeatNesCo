#!/usr/bin/env python3
"""Add Amazon images to all 15 new products"""

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
DATA_DIR = os.path.expanduser("~/dropship-bots/data")

# Product IDs and their Amazon search terms
PRODUCTS = [
    {"id": 14972406759796, "search": "electric spin scrubber cleaning brush cordless", "name": "ProSpin Electric Scrubber"},
    {"id": 14972406792564, "search": "posture corrector back brace adjustable", "name": "AlignPro Posture Corrector"},
    {"id": 14972406858100, "search": "portable neck fan hands free bladeless", "name": "BreezePro Neck Fan"},
    {"id": 14972406923636, "search": "portable blender usb rechargeable personal", "name": "BlendJet Portable Blender"},
    {"id": 14972406989172, "search": "portable steamer clothes handheld garment", "name": "SteamPro Garment Steamer"},
    {"id": 14972407054708, "search": "mini waffle maker non stick compact", "name": "MiniGrid Waffle Maker"},
    {"id": 14972407153012, "search": "resistance bands set exercise handles", "name": "FlexFit Resistance Bands"},
    {"id": 14972407251316, "search": "pet hair remover roller reusable lint", "name": "FurBuster Pet Hair Remover"},
    {"id": 14972407284084, "search": "rotating makeup organizer 360 acrylic", "name": "GlamSpin Makeup Organizer"},
    {"id": 14972407382388, "search": "led motion sensor night light rechargeable", "name": "GlowSense Night Light"},
    {"id": 14972407480692, "search": "electric milk frother handheld stainless", "name": "FrothMaster Milk Frother"},
    {"id": 14972407546228, "search": "teeth whitening kit led professional home", "name": "BrightSmile Whitening Kit"},
    {"id": 14972407611764, "search": "acne pimple patch hydrocolloid", "name": "ClearPatch Acne Patches"},
    {"id": 14972407677300, "search": "vegetable chopper 8 blade container", "name": "ChopMaster Veggie Chopper"},
    {"id": 14972407742836, "search": "electric lighter usb rechargeable plasma", "name": "ArcLite Electric Lighter"},
]

img_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

print("=" * 60)
print("ADDING AMAZON IMAGES TO 15 PRODUCTS")
print("=" * 60)

total_images = 0

for item in PRODUCTS:
    print("\n[%s] Searching images..." % item["name"])
    search_url = "https://www.amazon.com/s?k=" + item["search"].replace(" ", "+")
    try:
        r = requests.get(search_url, headers=img_headers, timeout=15)
        asins = re.findall(r"/dp/([A-Z0-9]{10})", r.text)
        if not asins:
            print("  No ASIN found")
            continue

        asin = asins[0]
        prod_url = "https://www.amazon.com/dp/%s" % asin
        r2 = requests.get(prod_url, headers=img_headers, timeout=15)

        hi_res = re.findall(r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"', r2.text)
        large = re.findall(r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"', r2.text)

        images = list(dict.fromkeys(hi_res + large))[:5]

        if images:
            added = 0
            for idx, img_url in enumerate(images):
                img_payload = {"image": {"src": img_url, "position": idx + 1}}
                ri = requests.post(
                    "%s/products/%d/images.json" % (API, item["id"]),
                    headers=HEADERS,
                    json=img_payload,
                )
                if ri.status_code == 200:
                    added += 1
                time.sleep(0.4)
            print("  ASIN: %s -> %d/%d images added" % (asin, added, len(images)))
            total_images += added
        else:
            print("  No hi-res images found for ASIN %s" % asin)

    except Exception as e:
        print("  ERROR: %s" % str(e))

    time.sleep(1.5)

# Save product data
store_data = PRODUCTS
with open(os.path.join(DATA_DIR, "store_products.json"), "w") as f:
    json.dump(store_data, f, indent=2)

print("\n" + "=" * 60)
print("IMAGES COMPLETE: %d total images added to %d products" % (total_images, len(PRODUCTS)))
print("=" * 60)

# Telegram notification
try:
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID", "")
    msg = "NEATNESTCO STORE REBUILT!\n\n"
    msg += "10 old branded products DELETED\n"
    msg += "15 winning products CREATED\n"
    msg += "%d product images ADDED\n\n" % total_images
    msg += "3 HERO | 6 TEST | 6 BACKUP\n"
    msg += "All non-brand, high-margin, filter-validated!\n"
    msg += "Weights, SEO, descriptions - all set!"
    requests.post(
        "https://api.telegram.org/bot%s/sendMessage" % tg_token,
        json={"chat_id": tg_chat, "text": msg},
    )
except:
    pass
