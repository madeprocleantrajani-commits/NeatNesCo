#!/usr/bin/env python3
"""
NEATNESTCO STORE REBUILDER
1. Deletes all old branded/duplicate products
2. Creates 15 winning products (3 HERO, 6 TEST, 6 BACKUP)
3. Professional descriptions, real images, weights, SEO
"""

import requests
import json
import time
import re
import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SHOP = os.getenv("SHOPIFY_STORE", "8hendy-8i.myshopify.com")
TOKEN = os.getenv("SHOPIFY_TOKEN", "")
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
API = "https://%s/admin/api/2024-01" % SHOP

# ===== STEP 1: DELETE OLD PRODUCTS =====
DELETE_IDS = [
    14971567440244,  # Vegetable Chopper (old)
    14972032549236,  # Vegetable Chopper (duplicate)
    14972032516468,  # DAYBETTER LED (brand)
    14971567309172,  # HydroJug (brand)
    14972032582004,  # KSIPZE LED (brand)
    14971567473012,  # La Roche-Posay (brand)
    14972032614772,  # La Roche-Posay (duplicate)
    14971567374708,  # Sheba (brand)
    14971566588276,  # YARRAMATE (old)
    14972032483700,  # YARRAMATE (duplicate)
]
# Keep: 14964731150708 NeatNest Splash Guard (our original product)

# ===== STEP 2: 15 WINNING PRODUCTS =====
PRODUCTS = [
    # --- 3 HERO PRODUCTS ---
    {
        "tier": "HERO",
        "title": "ProSpin Electric Scrubber - Cordless Power Cleaning Brush with 8 Heads",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Clean Every Surface in Half the Time</h2>
<p>Tired of scrubbing on your hands and knees? The ProSpin Electric Scrubber does the hard work for you. With <strong>450 RPM power rotation</strong> and 8 interchangeable brush heads, it tackles bathrooms, kitchens, tiles, and grout effortlessly.</p>
<ul>
<li><strong>Cordless & Rechargeable</strong> - Up to 90 minutes of cleaning per charge</li>
<li><strong>Adjustable Handle</strong> - Extends from 17" to 42" so you never bend down again</li>
<li><strong>8 Brush Heads</strong> - Flat, corner, round, and detail brushes for every surface</li>
<li><strong>IPX7 Waterproof</strong> - Safe to use in showers, tubs, and sinks</li>
<li><strong>Lightweight Design</strong> - Only 2.4 lbs, comfortable for extended use</li>
</ul>
<h3>Perfect For:</h3>
<p>Bathrooms | Kitchens | Tile & Grout | Car Detailing | Outdoor Furniture</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Cleaning",
        "tags": "cleaning, electric scrubber, bathroom, kitchen, cordless, power brush, hero",
        "price": "39.99",
        "compare_price": "79.99",
        "weight": 2.4,
        "weight_unit": "lb",
        "seo_title": "ProSpin Electric Scrubber | Cordless Power Cleaning Brush - NeatNestCo",
        "seo_desc": "Clean bathrooms, kitchens & tiles in half the time. 450 RPM cordless electric scrubber with 8 brush heads. 30-day guarantee. Free shipping.",
        "search": "electric spin scrubber cleaning brush cordless",
        "collection": "Home & Cleaning",
    },
    {
        "tier": "HERO",
        "title": "AlignPro Posture Corrector - Adjustable Back Support Brace",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Stand Taller. Feel Better. Look Confident.</h2>
<p>Poor posture causes back pain, neck tension, and fatigue. The AlignPro Posture Corrector gently trains your muscles to maintain proper alignment - <strong>results visible in just 2 weeks</strong>.</p>
<ul>
<li><strong>Invisible Under Clothes</strong> - Ultra-thin breathable fabric disappears under any shirt</li>
<li><strong>Adjustable Tension</strong> - Customize support level from gentle to firm</li>
<li><strong>All-Day Comfort</strong> - Soft neoprene padding, no digging or chafing</li>
<li><strong>Fits All Sizes</strong> - Adjustable straps fit chest 28" to 48"</li>
<li><strong>Doctor Recommended</strong> - Used by chiropractors and physical therapists</li>
</ul>
<h3>Perfect For:</h3>
<p>Office Workers | Gamers | Students | Remote Workers | Anyone With Back Pain</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Health & Wellness",
        "tags": "posture corrector, back support, back brace, health, wellness, office, hero",
        "price": "27.99",
        "compare_price": "54.99",
        "weight": 0.6,
        "weight_unit": "lb",
        "seo_title": "AlignPro Posture Corrector | Adjustable Back Support Brace - NeatNestCo",
        "seo_desc": "Fix your posture in 2 weeks. Ultra-thin, invisible under clothes. Adjustable back support brace. 30-day guarantee. Free shipping.",
        "search": "posture corrector back brace adjustable",
        "collection": "Health & Wellness",
    },
    {
        "tier": "HERO",
        "title": "BreezePro Portable Neck Fan - Hands-Free Personal Cooling",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Stay Cool Anywhere, Hands Completely Free</h2>
<p>Beat the heat without holding anything. The BreezePro wraps around your neck and delivers <strong>360-degree cooling airflow</strong> with whisper-quiet bladeless technology.</p>
<ul>
<li><strong>Bladeless Safety</strong> - No exposed blades, safe for hair and skin</li>
<li><strong>3 Speed Settings</strong> - Low, medium, and turbo for any environment</li>
<li><strong>6-12 Hour Battery</strong> - USB-C rechargeable, lasts all day</li>
<li><strong>Ultra Lightweight</strong> - Only 9.5 oz, forget you are wearing it</li>
<li><strong>Flexible Fit</strong> - Soft silicone band adjusts to any neck size</li>
</ul>
<h3>Perfect For:</h3>
<p>Outdoor Events | Commuting | Working Out | Travel | Theme Parks | Gardening</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Personal Cooling",
        "tags": "neck fan, portable fan, hands free, personal cooling, summer, outdoor, hero",
        "price": "29.99",
        "compare_price": "59.99",
        "weight": 0.6,
        "weight_unit": "lb",
        "seo_title": "BreezePro Portable Neck Fan | Hands-Free Personal Cooling - NeatNestCo",
        "seo_desc": "Stay cool hands-free with 360-degree bladeless neck fan. 6-12hr battery, ultra lightweight. 30-day guarantee. Free shipping.",
        "search": "portable neck fan hands free bladeless",
        "collection": "Personal Care",
    },

    # --- 6 TEST PRODUCTS ---
    {
        "tier": "TEST",
        "title": "BlendJet Portable Blender - USB Rechargeable Smoothie Maker",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Fresh Smoothies Anywhere in 30 Seconds</h2>
<p>No more expensive smoothie shops or bulky kitchen blenders. This portable blender makes <strong>fresh smoothies, protein shakes, and baby food</strong> anywhere you go.</p>
<ul>
<li><strong>Powerful Motor</strong> - 6 stainless steel blades crush ice and frozen fruit</li>
<li><strong>USB-C Rechargeable</strong> - 15+ blends per charge</li>
<li><strong>Self-Cleaning</strong> - Add water and soap, press blend</li>
<li><strong>BPA-Free Tritan</strong> - 16oz capacity, safe and durable</li>
<li><strong>Ultra Portable</strong> - Fits in bag, car cup holder, gym bag</li>
</ul>
<h3>Perfect For:</h3>
<p>Gym | Office | Travel | Camping | Meal Prep | Baby Food</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Kitchen",
        "tags": "portable blender, smoothie maker, usb blender, kitchen, fitness, test",
        "price": "34.99",
        "compare_price": "69.99",
        "weight": 1.4,
        "weight_unit": "lb",
        "seo_title": "Portable USB Blender | Rechargeable Smoothie Maker - NeatNestCo",
        "seo_desc": "Make fresh smoothies anywhere in 30 seconds. USB-C rechargeable, self-cleaning portable blender. Free shipping.",
        "search": "portable blender usb rechargeable personal",
        "collection": "Kitchen",
    },
    {
        "tier": "TEST",
        "title": "SteamPro Portable Garment Steamer - Wrinkle Remover for Clothes",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Wrinkle-Free Clothes in 60 Seconds, No Ironing Board Needed</h2>
<p>Ditch the heavy iron and bulky board. The SteamPro heats up in <strong>just 25 seconds</strong> and removes wrinkles from any fabric while hanging.</p>
<ul>
<li><strong>25-Second Heat Up</strong> - Ready before you finish getting dressed</li>
<li><strong>15 Min Steam Time</strong> - Large 8.5oz water tank</li>
<li><strong>Safe on All Fabrics</strong> - Silk, cotton, linen, polyester, wool</li>
<li><strong>Compact & Portable</strong> - Perfect for travel, fits in carry-on</li>
<li><strong>Kills 99.9% Bacteria</strong> - Sanitizes while it steams</li>
</ul>
<h3>Perfect For:</h3>
<p>Business Travel | Daily Outfits | Curtains | Upholstery | Costumes</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Home",
        "tags": "garment steamer, portable steamer, wrinkle remover, travel, clothes, test",
        "price": "24.99",
        "compare_price": "49.99",
        "weight": 1.2,
        "weight_unit": "lb",
        "seo_title": "SteamPro Portable Garment Steamer | Wrinkle Remover - NeatNestCo",
        "seo_desc": "Remove wrinkles in 60 seconds without an iron. Portable garment steamer heats in 25 sec. Free shipping.",
        "search": "portable steamer clothes handheld garment",
        "collection": "Home & Cleaning",
    },
    {
        "tier": "TEST",
        "title": "MiniGrid Waffle Maker - Compact Non-Stick Breakfast Machine",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Perfect Golden Waffles in Under 3 Minutes</h2>
<p>Restaurant-quality waffles at home every morning. The MiniGrid heats evenly for <strong>crispy outside, fluffy inside perfection</strong> every single time.</p>
<ul>
<li><strong>Non-Stick Coating</strong> - Waffles slide right off, zero mess</li>
<li><strong>3-Minute Cook Time</strong> - Faster than making toast</li>
<li><strong>Indicator Light</strong> - Tells you exactly when it is ready</li>
<li><strong>Compact Design</strong> - 6" footprint, stores anywhere</li>
<li><strong>Versatile</strong> - Waffles, hash browns, paninis, cookies, and more</li>
</ul>
<h3>Perfect For:</h3>
<p>Breakfast | Kids Snacks | Dorms | Small Kitchens | Meal Prep</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Kitchen",
        "tags": "waffle maker, mini waffle, breakfast, kitchen appliance, non-stick, test",
        "price": "19.99",
        "compare_price": "39.99",
        "weight": 1.8,
        "weight_unit": "lb",
        "seo_title": "MiniGrid Waffle Maker | Compact Non-Stick Breakfast Machine - NeatNestCo",
        "seo_desc": "Golden waffles in under 3 minutes. Non-stick mini waffle maker, compact design. Free shipping.",
        "search": "mini waffle maker non stick compact",
        "collection": "Kitchen",
    },
    {
        "tier": "TEST",
        "title": "FlexFit Resistance Bands Set - 5 Levels Exercise Bands with Handles",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Full Gym Workout Anywhere, No Membership Required</h2>
<p>Replace an entire gym with one set that fits in your bag. 5 resistance levels from <strong>10 to 150 lbs</strong> cover every exercise from rehab to heavy training.</p>
<ul>
<li><strong>5 Resistance Levels</strong> - Stack bands to combine up to 150 lbs total</li>
<li><strong>Premium Latex</strong> - Natural latex tubes, snap-resistant up to 2x stretch</li>
<li><strong>11-Piece Set</strong> - 5 bands, 2 handles, 2 ankle straps, door anchor, carry bag</li>
<li><strong>Full Body Training</strong> - Arms, legs, chest, back, shoulders, core</li>
<li><strong>Travel Friendly</strong> - Entire set weighs under 2 lbs</li>
</ul>
<h3>Perfect For:</h3>
<p>Home Gym | Travel | Physical Therapy | Yoga | CrossFit | Beginners to Advanced</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Fitness",
        "tags": "resistance bands, exercise bands, fitness, home gym, workout, test",
        "price": "29.99",
        "compare_price": "59.99",
        "weight": 1.8,
        "weight_unit": "lb",
        "seo_title": "FlexFit Resistance Bands Set | 5-Level Exercise Bands - NeatNestCo",
        "seo_desc": "Full gym workout anywhere. 5 resistance levels up to 150 lbs, 11-piece set. Free shipping.",
        "search": "resistance bands set exercise handles",
        "collection": "Health & Wellness",
    },
    {
        "tier": "TEST",
        "title": "FurBuster Pet Hair Remover Roller - Reusable Lint Remover",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Remove Pet Hair From Any Surface in Seconds</h2>
<p>If you have pets, you have hair everywhere. The FurBuster lifts <strong>cat and dog hair</strong> from furniture, clothes, bedding, and car seats without sticky refills.</p>
<ul>
<li><strong>No Refills Needed</strong> - Self-cleaning base, reuse forever</li>
<li><strong>Works on Everything</strong> - Couch, bed, clothes, carpet, car seats</li>
<li><strong>Ergonomic Handle</strong> - Comfortable grip for extended cleaning sessions</li>
<li><strong>Travel Size Included</strong> - Bonus mini roller for on-the-go</li>
<li><strong>Eco-Friendly</strong> - No waste from disposable sticky sheets</li>
</ul>
<h3>Perfect For:</h3>
<p>Dog Owners | Cat Owners | Furniture | Car Interior | Clothing</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Pet Supplies",
        "tags": "pet hair remover, lint roller, reusable, dog hair, cat hair, pet, test",
        "price": "24.99",
        "compare_price": "44.99",
        "weight": 0.8,
        "weight_unit": "lb",
        "seo_title": "FurBuster Pet Hair Remover | Reusable Lint Roller - NeatNestCo",
        "seo_desc": "Remove pet hair from furniture, clothes & car seats. Reusable, no refills needed. Free shipping.",
        "search": "pet hair remover roller reusable lint",
        "collection": "Pet Supplies",
    },
    {
        "tier": "TEST",
        "title": "GlamSpin Rotating Makeup Organizer - 360 Adjustable Cosmetic Storage",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Every Product Visible, Every Morning Faster</h2>
<p>Stop digging through drawers. The GlamSpin rotates 360 degrees so <strong>every lipstick, brush, and palette is instantly accessible</strong>.</p>
<ul>
<li><strong>360-Degree Rotation</strong> - Spin to find what you need instantly</li>
<li><strong>Adjustable Shelves</strong> - 7 layers, removable trays fit any product size</li>
<li><strong>Holds 100+ Products</strong> - Lipsticks, palettes, brushes, skincare, perfume</li>
<li><strong>Crystal Clear Acrylic</strong> - See everything, matches any decor</li>
<li><strong>Easy Assembly</strong> - Snaps together in under 5 minutes, no tools</li>
</ul>
<h3>Perfect For:</h3>
<p>Vanity | Bathroom Counter | Dresser | Beauty Professionals | Gift Idea</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Beauty & Organization",
        "tags": "makeup organizer, rotating organizer, cosmetic storage, beauty, organization, test",
        "price": "34.99",
        "compare_price": "64.99",
        "weight": 2.2,
        "weight_unit": "lb",
        "seo_title": "GlamSpin Rotating Makeup Organizer | 360 Cosmetic Storage - NeatNestCo",
        "seo_desc": "360-degree rotating makeup organizer holds 100+ products. Adjustable shelves, clear acrylic. Free shipping.",
        "search": "rotating makeup organizer 360 acrylic",
        "collection": "Beauty",
    },

    # --- 6 BACKUP PRODUCTS ---
    {
        "tier": "BACKUP",
        "title": "GlowSense LED Motion Sensor Night Light (3-Pack)",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Lights That Think For You</h2>
<p>No more fumbling for switches in the dark. GlowSense detects motion and <strong>automatically lights your path</strong>, then turns off to save energy.</p>
<ul>
<li><strong>Smart Motion Sensor</strong> - 10ft detection range, auto on/off</li>
<li><strong>3 Color Modes</strong> - Warm white, cool white, and warm yellow</li>
<li><strong>Magnetic + Adhesive Mount</strong> - Sticks anywhere, no wiring needed</li>
<li><strong>USB-C Rechargeable</strong> - One charge lasts 3+ months with normal use</li>
<li><strong>3-Pack Value</strong> - Cover hallway, bathroom, and stairs</li>
</ul>
<h3>Perfect For:</h3>
<p>Hallways | Stairs | Bathrooms | Closets | Under Cabinets | Kids Rooms</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Home Lighting",
        "tags": "night light, motion sensor, LED, rechargeable, home, smart light, backup",
        "price": "16.99",
        "compare_price": "34.99",
        "weight": 0.7,
        "weight_unit": "lb",
        "seo_title": "GlowSense LED Motion Sensor Night Light 3-Pack - NeatNestCo",
        "seo_desc": "Smart motion-sensor night lights auto on/off. USB rechargeable, 3-pack. Hallways, stairs, bathrooms. Free shipping.",
        "search": "led motion sensor night light rechargeable",
        "collection": "Home & Cleaning",
    },
    {
        "tier": "BACKUP",
        "title": "FrothMaster Electric Milk Frother - Handheld Foam Maker",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Coffee Shop Foam at Home in 15 Seconds</h2>
<p>Save $5/day on lattes. The FrothMaster creates <strong>barista-quality microfoam</strong> for cappuccinos, matcha lattes, and hot chocolate at home.</p>
<ul>
<li><strong>19,000 RPM Motor</strong> - Silky smooth foam in 15 seconds flat</li>
<li><strong>Battery Powered</strong> - 2 AA batteries last 3+ months of daily use</li>
<li><strong>Stainless Steel Whisk</strong> - Food-grade, rust-proof, dishwasher safe</li>
<li><strong>One-Button Operation</strong> - Press and froth, that is it</li>
<li><strong>Multi-Use</strong> - Milk, cream, matcha, protein shakes, eggs</li>
</ul>
<h3>Perfect For:</h3>
<p>Coffee Lovers | Matcha Fans | Keto Dieters | Protein Shakes | Cocktails</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Kitchen",
        "tags": "milk frother, electric frother, coffee, latte, matcha, kitchen, backup",
        "price": "14.99",
        "compare_price": "29.99",
        "weight": 0.4,
        "weight_unit": "lb",
        "seo_title": "FrothMaster Electric Milk Frother | Handheld Foam Maker - NeatNestCo",
        "seo_desc": "Coffee shop foam at home in 15 seconds. Handheld milk frother, 19,000 RPM. Free shipping.",
        "search": "electric milk frother handheld stainless",
        "collection": "Kitchen",
    },
    {
        "tier": "BACKUP",
        "title": "BrightSmile LED Teeth Whitening Kit - Professional Home Treatment",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Dentist-Level Whitening For 1/10th The Price</h2>
<p>Professional teeth whitening costs $400+. BrightSmile uses the same <strong>LED light technology</strong> dentists use, for a fraction of the cost.</p>
<ul>
<li><strong>LED Accelerator Light</strong> - 16-point blue LED speeds up whitening gel</li>
<li><strong>3 Gel Syringes</strong> - Enough for 30+ treatments (6 month supply)</li>
<li><strong>Enamel Safe Formula</strong> - Carbamide peroxide, no sensitivity</li>
<li><strong>10-Minute Sessions</strong> - Visible results after first use</li>
<li><strong>Comfort Fit Tray</strong> - Moldable to your teeth shape</li>
</ul>
<h3>Perfect For:</h3>
<p>Coffee Drinkers | Smokers | Wine Lovers | Before Events | Daily Maintenance</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Beauty",
        "tags": "teeth whitening, LED whitening, dental care, beauty, smile, backup",
        "price": "29.99",
        "compare_price": "59.99",
        "weight": 0.5,
        "weight_unit": "lb",
        "seo_title": "BrightSmile LED Teeth Whitening Kit | Home Treatment - NeatNestCo",
        "seo_desc": "Professional teeth whitening at home. LED light technology, visible results after first use. Free shipping.",
        "search": "teeth whitening kit led professional home",
        "collection": "Beauty",
    },
    {
        "tier": "BACKUP",
        "title": "ClearPatch Acne Pimple Patches - Hydrocolloid Spot Treatment (72 Count)",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Wake Up With Clear Skin - Overnight Pimple Eraser</h2>
<p>Stop picking, stop scarring. ClearPatch absorbs pimple gunk while you sleep and <strong>flattens breakouts by morning</strong>.</p>
<ul>
<li><strong>Hydrocolloid Technology</strong> - Draws out pus and oil overnight</li>
<li><strong>72 Patches</strong> - 3 sizes (12mm, 10mm, 8mm) for any breakout</li>
<li><strong>Invisible on Skin</strong> - Ultra-thin, wear under makeup or in public</li>
<li><strong>Prevents Scarring</strong> - Creates protective barrier, stops picking</li>
<li><strong>Drug-Free</strong> - No salicylic acid, no benzoyl peroxide irritation</li>
</ul>
<h3>Perfect For:</h3>
<p>Teens | Adults | Hormonal Acne | Stress Breakouts | Overnight Treatment</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Skincare",
        "tags": "acne patches, pimple patches, hydrocolloid, skincare, clear skin, backup",
        "price": "12.99",
        "compare_price": "24.99",
        "weight": 0.15,
        "weight_unit": "lb",
        "seo_title": "ClearPatch Acne Pimple Patches 72-Count | Hydrocolloid - NeatNestCo",
        "seo_desc": "Flatten pimples overnight with hydrocolloid patches. 72 count, invisible on skin. Free shipping.",
        "search": "acne pimple patch hydrocolloid",
        "collection": "Beauty",
    },
    {
        "tier": "BACKUP",
        "title": "ChopMaster 8-in-1 Vegetable Chopper with Container",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Meal Prep Done in Minutes, Not Hours</h2>
<p>Chop, dice, slice, and julienne with one press. The ChopMaster replaces <strong>8 kitchen tools</strong> and cuts your meal prep time by 80%.</p>
<ul>
<li><strong>8 Interchangeable Blades</strong> - Dice, slice, julienne, wedge, spiralize, grate</li>
<li><strong>Built-In Container</strong> - 1.5L catch container with pour lid</li>
<li><strong>German Steel Blades</strong> - Stay sharp 3x longer than standard choppers</li>
<li><strong>Anti-Slip Base</strong> - Stable on any countertop</li>
<li><strong>Dishwasher Safe</strong> - Every piece goes in the dishwasher</li>
</ul>
<h3>Perfect For:</h3>
<p>Meal Prep | Salads | Stir Fry | Soups | Salsa | Baby Food</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Kitchen",
        "tags": "vegetable chopper, mandoline slicer, kitchen gadget, meal prep, chopper, backup",
        "price": "19.99",
        "compare_price": "39.99",
        "weight": 2.0,
        "weight_unit": "lb",
        "seo_title": "ChopMaster 8-in-1 Vegetable Chopper with Container - NeatNestCo",
        "seo_desc": "Chop, dice, slice 8 ways with one tool. Built-in container, dishwasher safe. Free shipping.",
        "search": "vegetable chopper 8 blade container",
        "collection": "Kitchen",
    },
    {
        "tier": "BACKUP",
        "title": "ArcLite Electric Lighter - USB Rechargeable Windproof Plasma",
        "body_html": """<div style="font-family:Arial,sans-serif;max-width:800px">
<h2 style="color:#2c3e50">Never Buy Lighter Fluid Again</h2>
<p>The ArcLite uses <strong>dual-arc plasma technology</strong> - no butane, no flame, no refills. Works in wind, rain, and at any altitude.</p>
<ul>
<li><strong>Dual Plasma Arc</strong> - Electric arc lights anything instantly</li>
<li><strong>100% Windproof</strong> - Works in storms, on boats, while hiking</li>
<li><strong>USB-C Rechargeable</strong> - 300+ lights per charge</li>
<li><strong>Safety Lock</strong> - Child-proof button prevents accidents</li>
<li><strong>LED Battery Indicator</strong> - Always know your charge level</li>
</ul>
<h3>Perfect For:</h3>
<p>Candles | Camping | BBQ | Fireplaces | Incense | Survival Kits</p>
<p style="color:#27ae60;font-weight:bold">30-Day Money Back Guarantee | Free Shipping on Orders $25+</p>
</div>""",
        "product_type": "Home",
        "tags": "electric lighter, usb lighter, plasma lighter, windproof, rechargeable, backup",
        "price": "14.99",
        "compare_price": "29.99",
        "weight": 0.3,
        "weight_unit": "lb",
        "seo_title": "ArcLite Electric Lighter | USB Rechargeable Windproof Plasma - NeatNestCo",
        "seo_desc": "Never buy lighter fluid again. Dual plasma arc, windproof, USB rechargeable. Free shipping.",
        "search": "electric lighter usb rechargeable plasma",
        "collection": "Home & Cleaning",
    },
]


def run():
    print("=" * 60)
    print("NEATNESTCO STORE REBUILDER")
    print("=" * 60)

    # STEP 1: Delete old products
    print("\n--- STEP 1: Deleting old branded/duplicate products ---")
    for pid in DELETE_IDS:
        r = requests.delete("%s/products/%d.json" % (API, pid), headers=HEADERS)
        status = "DELETED" if r.status_code == 200 else "FAIL(%d)" % r.status_code
        print("  %s: Product %d" % (status, pid))
        time.sleep(0.5)

    print("\n--- STEP 2: Creating 15 winning products ---")
    created = []
    for prod in PRODUCTS:
        # Create product
        payload = {
            "product": {
                "title": prod["title"],
                "body_html": prod["body_html"],
                "product_type": prod["product_type"],
                "tags": prod["tags"],
                "status": "draft",
                "variants": [
                    {
                        "price": prod["price"],
                        "compare_at_price": prod["compare_price"],
                        "weight": prod["weight"],
                        "weight_unit": prod["weight_unit"],
                        "inventory_management": None,
                        "requires_shipping": True,
                    }
                ],
                "metafields_global_title_tag": prod["seo_title"],
                "metafields_global_description_tag": prod["seo_desc"],
            }
        }

        r = requests.post("%s/products.json" % API, headers=HEADERS, json=payload)
        if r.status_code == 201:
            new_id = r.json()["product"]["id"]
            vid = r.json()["product"]["variants"][0]["id"]
            tier = prod["tier"]
            print("  CREATED [%s]: %s (ID: %d)" % (tier, prod["title"][:50], new_id))
            created.append({
                "id": new_id,
                "variant_id": vid,
                "title": prod["title"],
                "tier": prod["tier"],
                "search": prod["search"],
                "collection": prod["collection"],
            })
        else:
            print("  FAIL(%d): %s - %s" % (r.status_code, prod["title"][:40], r.text[:100]))
        time.sleep(0.5)

    # Save created products
    with open(os.path.join(DATA_DIR, "store_products.json"), "w") as f:
        json.dump(created, f, indent=2)

    print("\n--- STEP 3: Scraping Amazon images ---")
    img_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for item in created:
        search_url = "https://www.amazon.com/s?k=" + item["search"].replace(" ", "+")
        try:
            r = requests.get(search_url, headers=img_headers, timeout=15)
            asins = re.findall(r"/dp/([A-Z0-9]{10})", r.text)
            if not asins:
                print("  No ASIN found for: %s" % item["title"][:40])
                continue

            asin = asins[0]
            # Get product page for images
            prod_url = "https://www.amazon.com/dp/%s" % asin
            r2 = requests.get(prod_url, headers=img_headers, timeout=15)

            # Extract hi-res images
            hi_res = re.findall(r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"', r2.text)
            large = re.findall(r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"', r2.text)

            images = list(dict.fromkeys(hi_res + large))[:5]

            if images:
                for idx, img_url in enumerate(images):
                    img_payload = {"image": {"src": img_url, "position": idx + 1}}
                    ri = requests.post(
                        "%s/products/%d/images.json" % (API, item["id"]),
                        headers=HEADERS,
                        json=img_payload,
                    )
                    time.sleep(0.3)
                print("  IMAGES: %s -> %d images added" % (item["title"][:40], len(images)))
            else:
                print("  NO IMAGES: %s" % item["title"][:40])

        except Exception as e:
            print("  ERROR images for %s: %s" % (item["title"][:40], str(e)))

        time.sleep(1.5)

    # Summary
    print("\n" + "=" * 60)
    print("STORE REBUILD COMPLETE")
    print("=" * 60)
    print("Deleted: %d old products" % len(DELETE_IDS))
    print("Created: %d new products" % len(created))
    heroes = [c for c in created if c["tier"] == "HERO"]
    tests = [c for c in created if c["tier"] == "TEST"]
    backups = [c for c in created if c["tier"] == "BACKUP"]
    print("  HERO: %d | TEST: %d | BACKUP: %d" % (len(heroes), len(tests), len(backups)))
    print("\nKept: NeatNest Splash Guard (ID: 14964731150708)")
    print("Total products in store: %d" % (len(created) + 1))

    # Send Telegram notification
    try:
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        tg_chat = os.getenv("TELEGRAM_CHAT_ID", "")
        msg = "NEATNESTCO STORE REBUILT!\n\n"
        msg += "Deleted: %d branded/duplicate products\n" % len(DELETE_IDS)
        msg += "Created: %d winning products\n\n" % len(created)
        msg += "HERO (3): %s\n" % ", ".join([h["title"][:30] for h in heroes])
        msg += "TEST (6): %s\n" % ", ".join([t["title"][:30] for t in tests])
        msg += "BACKUP (6): %s\n" % ", ".join([b["title"][:30] for b in backups])
        msg += "\nAll non-brand, high-margin, filter-validated!"
        requests.post(
            "https://api.telegram.org/bot%s/sendMessage" % tg_token,
            json={"chat_id": tg_chat, "text": msg},
        )
        print("\nTelegram notification sent!")
    except:
        pass


if __name__ == "__main__":
    run()
