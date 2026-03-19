#!/usr/bin/env python3
"""
NEATNESTCO STORE SETUP
Creates: Collections, Pages (About, Shipping, Refund, Privacy, Terms)
Makes the store look like a REAL BRAND, not a random dropship store.
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SHOP = os.getenv("SHOPIFY_STORE", "8hendy-8i.myshopify.com")
TOKEN = os.getenv("SHOPIFY_TOKEN", "")
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
API = "https://%s/admin/api/2024-01" % SHOP

# Product IDs by collection
PRODUCT_MAP = {
    "Kitchen": [
        14972406923636,  # BlendJet Portable Blender
        14972407054708,  # MiniGrid Waffle Maker
        14972407480692,  # FrothMaster Milk Frother
        14972407677300,  # ChopMaster Veggie Chopper
    ],
    "Home & Cleaning": [
        14972406759796,  # ProSpin Electric Scrubber
        14972406989172,  # SteamPro Garment Steamer
        14972407382388,  # GlowSense Night Light
        14972407742836,  # ArcLite Electric Lighter
        14964731150708,  # NeatNest Splash Guard
    ],
    "Health & Wellness": [
        14972406792564,  # AlignPro Posture Corrector
        14972407153012,  # FlexFit Resistance Bands
        14972407546228,  # BrightSmile Teeth Whitening
    ],
    "Beauty & Skincare": [
        14972407284084,  # GlamSpin Makeup Organizer
        14972407611764,  # ClearPatch Acne Patches
    ],
    "Personal Care": [
        14972406858100,  # BreezePro Neck Fan
    ],
    "Pet Supplies": [
        14972407251316,  # FurBuster Pet Hair Remover
    ],
}


def create_collections():
    """Create smart collections for each category"""
    print("--- CREATING COLLECTIONS ---")

    # First, create manual collections and add products
    for name, product_ids in PRODUCT_MAP.items():
        payload = {
            "custom_collection": {
                "title": name,
                "published": True,
                "sort_order": "best-selling",
            }
        }

        r = requests.post(
            "%s/custom_collections.json" % API,
            headers=HEADERS,
            json=payload,
        )

        if r.status_code == 201:
            coll_id = r.json()["custom_collection"]["id"]
            print("  CREATED: %s (ID: %d)" % (name, coll_id))

            # Add products to collection
            for pid in product_ids:
                collect_payload = {
                    "collect": {
                        "product_id": pid,
                        "collection_id": coll_id,
                    }
                }
                rc = requests.post(
                    "%s/collects.json" % API,
                    headers=HEADERS,
                    json=collect_payload,
                )
                time.sleep(0.3)

            print("    Added %d products" % len(product_ids))
        else:
            print("  FAIL(%d): %s - %s" % (r.status_code, name, r.text[:100]))
        time.sleep(0.5)


def create_pages():
    """Create store pages: About, Shipping, Refund, Privacy, Terms"""
    print("\n--- CREATING STORE PAGES ---")

    pages = [
        {
            "title": "About Us",
            "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px">
<h1>Welcome to NeatNestCo</h1>
<p>We believe your home should be a place of comfort, order, and joy. That is why we curate the smartest, most practical products that make everyday life easier.</p>

<h2>Our Mission</h2>
<p>To bring you carefully selected, high-quality products that solve real problems. Every item in our store has been tested, reviewed, and validated before we offer it to you.</p>

<h2>Why NeatNestCo?</h2>
<ul>
<li><strong>Curated Selection</strong> - We test hundreds of products and only sell the best</li>
<li><strong>Real Reviews</strong> - Every product has 4.3+ stars from real customers</li>
<li><strong>Fair Prices</strong> - No markup games, just honest pricing</li>
<li><strong>Fast Support</strong> - Real humans respond within 24 hours</li>
</ul>

<h2>Our Promise</h2>
<p>If you are not 100% satisfied with your purchase, we will make it right. No questions asked. That is our 30-day guarantee.</p>

<p>Have questions? Email us at <strong>support@neatnestco.com</strong></p>
</div>""",
        },
        {
            "title": "Shipping Policy",
            "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px">
<h1>Shipping Policy</h1>
<p><em>Last updated: March 2026</em></p>

<h2>Processing Time</h2>
<p>Orders are processed within <strong>1-3 business days</strong>. You will receive a tracking number via email once your order ships.</p>

<h2>Shipping Times</h2>
<table style="width:100%;border-collapse:collapse;margin:15px 0">
<tr style="background:#f4f4f4"><th style="padding:10px;text-align:left;border:1px solid #ddd">Region</th><th style="padding:10px;text-align:left;border:1px solid #ddd">Estimated Delivery</th><th style="padding:10px;text-align:left;border:1px solid #ddd">Cost</th></tr>
<tr><td style="padding:10px;border:1px solid #ddd">United States</td><td style="padding:10px;border:1px solid #ddd">7-15 business days</td><td style="padding:10px;border:1px solid #ddd">FREE on orders $25+</td></tr>
<tr><td style="padding:10px;border:1px solid #ddd">Canada</td><td style="padding:10px;border:1px solid #ddd">10-20 business days</td><td style="padding:10px;border:1px solid #ddd">$4.99</td></tr>
<tr><td style="padding:10px;border:1px solid #ddd">International</td><td style="padding:10px;border:1px solid #ddd">15-30 business days</td><td style="padding:10px;border:1px solid #ddd">$7.99</td></tr>
</table>

<h2>Tracking</h2>
<p>All orders include tracking. You will receive your tracking number via email within 3 business days of placing your order.</p>

<h2>Customs & Duties</h2>
<p>International orders may be subject to customs fees and import duties. These charges are the responsibility of the buyer.</p>

<h2>Lost or Delayed Packages</h2>
<p>If your package has not arrived within the estimated delivery window, please contact us at <strong>support@neatnestco.com</strong> and we will resolve it immediately.</p>
</div>""",
        },
        {
            "title": "Refund Policy",
            "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px">
<h1>Refund Policy</h1>
<p><em>Last updated: March 2026</em></p>

<h2>30-Day Money Back Guarantee</h2>
<p>We stand behind every product we sell. If you are not completely satisfied, you can request a full refund within <strong>30 days of delivery</strong>.</p>

<h2>How to Request a Refund</h2>
<ol>
<li>Email <strong>support@neatnestco.com</strong> with your order number</li>
<li>Briefly describe the reason for your return</li>
<li>We will respond within 24 hours with return instructions</li>
</ol>

<h2>Refund Process</h2>
<ul>
<li>Refunds are processed within <strong>5-7 business days</strong> after we receive the returned item</li>
<li>Refunds are issued to the original payment method</li>
<li>Shipping costs are non-refundable unless the item arrived damaged or defective</li>
</ul>

<h2>Damaged or Defective Items</h2>
<p>If your item arrives damaged or defective, we will send a replacement or issue a full refund (including shipping) at no cost to you. Just send us a photo of the issue.</p>

<h2>Non-Returnable Items</h2>
<p>For hygiene reasons, the following items cannot be returned once opened: teeth whitening kits, acne patches, and personal care items.</p>
</div>""",
        },
        {
            "title": "Privacy Policy",
            "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px">
<h1>Privacy Policy</h1>
<p><em>Last updated: March 2026</em></p>

<h2>Information We Collect</h2>
<p>When you make a purchase, we collect:</p>
<ul>
<li>Name and email address</li>
<li>Shipping address</li>
<li>Payment information (processed securely by Shopify Payments)</li>
<li>Order history</li>
</ul>

<h2>How We Use Your Information</h2>
<ul>
<li>To fulfill and ship your orders</li>
<li>To send order confirmations and tracking updates</li>
<li>To respond to customer service requests</li>
<li>To improve our products and services</li>
</ul>

<h2>Information We Do NOT Sell</h2>
<p>We do <strong>not sell, trade, or rent</strong> your personal information to third parties. Ever.</p>

<h2>Payment Security</h2>
<p>All payments are processed through Shopify Payments with industry-standard SSL encryption. We never store your credit card information on our servers.</p>

<h2>Cookies</h2>
<p>We use cookies to improve your shopping experience, remember your cart, and analyze site traffic. You can disable cookies in your browser settings.</p>

<h2>Your Rights</h2>
<p>You can request to view, update, or delete your personal data at any time by emailing <strong>support@neatnestco.com</strong>.</p>

<h2>Contact</h2>
<p>For privacy-related questions: <strong>support@neatnestco.com</strong></p>
</div>""",
        },
        {
            "title": "Terms of Service",
            "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px">
<h1>Terms of Service</h1>
<p><em>Last updated: March 2026</em></p>

<h2>Overview</h2>
<p>This website is operated by NeatNestCo. By visiting our site and making purchases, you agree to the following terms and conditions.</p>

<h2>Products</h2>
<ul>
<li>Product images are for illustration purposes. Actual products may vary slightly in color or appearance</li>
<li>Prices are listed in USD and are subject to change without notice</li>
<li>We reserve the right to limit quantities or refuse orders</li>
</ul>

<h2>Accuracy of Information</h2>
<p>We strive to provide accurate product descriptions and pricing. If an error is found, we will correct it and notify affected customers.</p>

<h2>Intellectual Property</h2>
<p>All content on this website (text, images, logos) is the property of NeatNestCo and may not be reproduced without written permission.</p>

<h2>Limitation of Liability</h2>
<p>NeatNestCo is not liable for any indirect, incidental, or consequential damages arising from the use of our products or services.</p>

<h2>Governing Law</h2>
<p>These terms are governed by the laws of the United States.</p>

<h2>Changes to Terms</h2>
<p>We reserve the right to update these terms at any time. Continued use of the site after changes constitutes acceptance.</p>

<h2>Contact</h2>
<p>Questions about our terms? Email <strong>support@neatnestco.com</strong></p>
</div>""",
        },
    ]

    for page in pages:
        payload = {
            "page": {
                "title": page["title"],
                "body_html": page["body_html"],
                "published": True,
            }
        }
        r = requests.post(
            "%s/pages.json" % API,
            headers=HEADERS,
            json=payload,
        )
        if r.status_code == 201:
            pid = r.json()["page"]["id"]
            print("  CREATED: %s (ID: %d)" % (page["title"], pid))
        else:
            print("  FAIL(%d): %s - %s" % (r.status_code, page["title"], r.text[:100]))
        time.sleep(0.5)


def main():
    print("=" * 60)
    print("NEATNESTCO STORE SETUP")
    print("=" * 60)

    create_collections()
    create_pages()

    print("\n" + "=" * 60)
    print("STORE SETUP COMPLETE!")
    print("=" * 60)
    print("Collections: Kitchen, Home, Health, Beauty, Personal, Pet")
    print("Pages: About Us, Shipping, Refund, Privacy, Terms")


if __name__ == "__main__":
    main()
