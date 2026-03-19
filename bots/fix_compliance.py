"""
Legal Compliance Fix — Fix trademark violations, FDA claims, and misleading advertising
in all active Shopify products.
"""
import requests
import json
import time
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "8hendy-8i.myshopify.com")
TOKEN = os.getenv("SHOPIFY_TOKEN", "")
BASE = f"https://{SHOPIFY_STORE}/admin/api/2024-10/products"
HEADERS = {
    "X-Shopify-Access-Token": TOKEN,
    "Content-Type": "application/json"
}


def update_product(pid, title=None, body=None, tags=None):
    data = {"product": {"id": pid}}
    if title:
        data["product"]["title"] = title
    if body:
        data["product"]["body_html"] = body
    if tags:
        data["product"]["tags"] = tags
    r = requests.put(f"{BASE}/{pid}.json", headers=HEADERS, json=data)
    return r.status_code


fixes = []

# FIX 1: BlendJet → PowerBlend (trademark)
fixes.append({
    "id": 14972406923636,
    "issue": "BlendJet is a registered trademark",
    "title": "PowerBlend Portable Blender - USB Rechargeable Smoothie Maker",
    "tags": "fitness, kitchen, portable blender, smoothie maker, test, usb blender",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">Fresh Smoothies Anywhere in 30 Seconds</h2>'
        '<p>No more expensive smoothie shops or bulky kitchen blenders. This portable blender makes fresh smoothies, protein shakes, and baby food anywhere.</p>'
        '<ul>'
        '<li><strong>Powerful Motor:</strong> 6 stainless steel blades blend ice and frozen fruit in 30 seconds</li>'
        '<li><strong>USB Rechargeable:</strong> One charge makes 15+ smoothies</li>'
        '<li><strong>Self-Cleaning:</strong> Add water and soap, press blend</li>'
        '<li><strong>BPA-Free & Safe:</strong> Food-grade materials, magnetic safety switch</li>'
        '<li><strong>Perfect Size:</strong> 13.5 oz capacity fits in any bag or cup holder</li>'
        '</ul>'
        '<p><em>Perfect for fitness enthusiasts, busy professionals, and health-conscious families.</em></p>'
        '</div>'
})

# FIX 2: BrightSmile — remove medical claims
fixes.append({
    "id": 14972407546228,
    "issue": "Medical device claims (dentist-level, same LED technology dentists use)",
    "title": "BrightSmile LED Teeth Whitening Kit - Cosmetic Whitening at Home",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">A Brighter Smile From the Comfort of Home</h2>'
        '<p>Get a visibly brighter smile with our LED whitening kit. Easy to use, gentle on teeth, and designed for everyday people who want to feel more confident.</p>'
        '<ul>'
        '<li><strong>LED Light Technology:</strong> Blue light activates the whitening gel for enhanced results</li>'
        '<li><strong>Gentle Formula:</strong> Designed to minimize sensitivity while brightening your smile</li>'
        '<li><strong>Easy 10-Minute Sessions:</strong> Use while watching TV, reading, or relaxing</li>'
        '<li><strong>Complete Kit:</strong> LED mouthpiece, whitening gel syringes, shade guide, and case</li>'
        '<li><strong>Visible Results:</strong> Most users see a difference within the first week of use</li>'
        '</ul>'
        '<p style="font-size:12px;color:#666"><em>This is a cosmetic whitening product intended to improve the appearance of teeth. Not intended to diagnose, treat, cure, or prevent any disease. Results may vary. If you have dental concerns, consult your dentist before use.</em></p>'
        '</div>'
})

# FIX 3: Kojic Acid — remove VALITIC brand + drug claims
fixes.append({
    "id": 14987866505588,
    "issue": "Contains VALITIC brand name + 'Dark Spot Remover' is a drug claim",
    "title": "Kojic Acid Brightening Soap Bars with Vitamin C (2-Pack)",
    "tags": "beauty, brightening, kojic acid, skincare, soap",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">Reveal Your Natural Glow</h2>'
        '<p>These kojic acid soap bars help brighten and even out your skin tone with natural ingredients. Enriched with Vitamin C for a refreshed, radiant appearance.</p>'
        '<ul>'
        '<li><strong>Kojic Acid + Vitamin C:</strong> Natural brightening ingredients for a more even skin appearance</li>'
        '<li><strong>Gentle Daily Use:</strong> Suitable for face and body, all skin types</li>'
        '<li><strong>Plant-Based Formula:</strong> No harsh chemicals, parabens, or sulfates</li>'
        '<li><strong>2-Pack Value:</strong> Long-lasting bars that lather richly</li>'
        '</ul>'
        '<p style="font-size:12px;color:#666"><em>This is a cosmetic cleansing product. Not intended to diagnose, treat, cure, or prevent any disease or skin condition.</em></p>'
        '</div>'
})

# FIX 4: Mini Fan — remove Gaiatop brand
fixes.append({
    "id": 14987376886132,
    "issue": "Contains Gaiatop brand name in description",
    "title": "Mini Portable Clip-On Fan - Battery Operated for Stroller & Desk",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">Cool Breeze Anywhere You Clip It</h2>'
        '<p>This versatile mini fan clips onto strollers, desks, treadmills, and more. Battery operated with a detachable design for handheld use too.</p>'
        '<ul>'
        '<li><strong>Flexible Clip:</strong> Fits strollers, car seats, desks, cribs, and gym equipment</li>'
        '<li><strong>3 Speed Settings:</strong> Low, medium, and high for any situation</li>'
        '<li><strong>USB Rechargeable:</strong> 4-8 hours of runtime on a single charge</li>'
        '<li><strong>Whisper Quiet:</strong> Safe for sleeping babies and quiet offices</li>'
        '<li><strong>360 Degree Rotation:</strong> Adjust airflow in any direction</li>'
        '</ul>'
        '<p><em>A must-have for summer strolls, hot offices, and outdoor adventures.</em></p>'
        '</div>'
})

# FIX 5: Meat Shredder — remove SURETIVIAN brand
fixes.append({
    "id": 14975463981428,
    "issue": "Contains SURETIVIAN brand name in description",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">Shred a Whole Chicken in 30 Seconds</h2>'
        '<p>No more burning your fingers with forks. This twist-action shredder turns cooked chicken, pork, or beef into perfectly pulled meat with a simple twisting motion.</p>'
        '<ul>'
        '<li><strong>Twist & Shred:</strong> Shreds a full chicken breast in under 30 seconds</li>'
        '<li><strong>Works on Any Meat:</strong> Chicken, pork, beef, cooked or slow-cooked</li>'
        '<li><strong>BPA-Free Materials:</strong> Food-safe, heat-resistant up to 430 degrees F</li>'
        '<li><strong>Includes Cleaning Brush:</strong> Easy to clean after every use</li>'
        '<li><strong>Dishwasher Safe:</strong> Just toss it in for effortless cleanup</li>'
        '</ul>'
        '<p><em>Perfect for meal prep, BBQ pulled pork, tacos, and family dinners.</em></p>'
        '</div>'
})

# FIX 6: LED Headlamp — remove LHKNL brand
fixes.append({
    "id": 14975463817588,
    "issue": "Contains LHKNL brand name in description",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">See Everything, Hands Completely Free</h2>'
        '<p>Whether hiking, camping, fishing, or working in the garage, this ultra-bright rechargeable headlamp keeps both hands free while lighting your way.</p>'
        '<ul>'
        '<li><strong>Ultra-Bright LED:</strong> Wide-angle flood beam covers your full field of vision</li>'
        '<li><strong>USB Rechargeable:</strong> No more buying batteries, one charge lasts 6+ hours</li>'
        '<li><strong>Waterproof IPX4:</strong> Works in rain, snow, and humid conditions</li>'
        '<li><strong>Lightweight:</strong> Only 2.5 oz, forget you are wearing it</li>'
        '<li><strong>5 Modes:</strong> High, medium, low, strobe, and red light for night vision</li>'
        '</ul>'
        '<p><em>Essential gear for outdoor enthusiasts, runners, campers, and DIY projects.</em></p>'
        '</div>'
})

# FIX 7: Shower Head — remove Amazon claims + emoji spam
fixes.append({
    "id": 14986847617396,
    "issue": "Amazon Best Seller claims + emoji spam + misleading advertising",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">Transform Your Daily Shower Into a Spa Experience</h2>'
        '<p>This dual shower head system combines a luxurious rainfall head with a powerful handheld sprayer. Switch between them or use both simultaneously.</p>'
        '<ul>'
        '<li><strong>Dual System:</strong> 8 inch rain shower head + handheld spray with 5 settings</li>'
        '<li><strong>High Pressure Design:</strong> Built-in pressure booster works even with low water pressure</li>'
        '<li><strong>Easy Installation:</strong> No plumber needed, installs in 10 minutes with standard fittings</li>'
        '<li><strong>Anti-Clog Nozzles:</strong> Silicone jets prevent mineral buildup</li>'
        '<li><strong>60 inch Stainless Hose:</strong> Extra-long hose reaches every part of your shower</li>'
        '</ul>'
        '<p><em>Fits all standard US shower arms. No tools or plumbing modifications required.</em></p>'
        '</div>'
})

# FIX 8: ClearPatch — change "Spot Treatment" to "Spot Care"
fixes.append({
    "id": 14972407611764,
    "issue": "'Spot Treatment' is a drug claim — change to 'Spot Care'",
    "title": "ClearPatch Acne Pimple Patches - Hydrocolloid Spot Care (72 Count)",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">Wake Up With Clearer-Looking Skin</h2>'
        '<p>Stop picking, stop scarring. ClearPatch uses hydrocolloid technology to absorb impurities while you sleep, helping to flatten and conceal blemishes by morning.</p>'
        '<ul>'
        '<li><strong>Hydrocolloid Technology:</strong> Absorbs impurities and protects the spot from touching</li>'
        '<li><strong>Invisible on Skin:</strong> Ultra-thin, matte finish blends with all skin tones</li>'
        '<li><strong>72 Patches:</strong> 3 sizes (12mm, 10mm, 8mm) for any blemish size</li>'
        '<li><strong>Drug-Free:</strong> No salicylic acid, no benzoyl peroxide, just hydrocolloid</li>'
        '<li><strong>Works Overnight:</strong> Apply before bed, see results in the morning</li>'
        '</ul>'
        '<p style="font-size:12px;color:#666"><em>This is a cosmetic patch product. It does not treat, cure, or prevent acne. For persistent skin concerns, consult a dermatologist.</em></p>'
        '</div>'
})

# FIX 9: AlignPro — add wellness disclaimer
fixes.append({
    "id": 14972406792564,
    "issue": "Posture corrector could be seen as medical device — add disclaimer",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">Stand Taller. Feel Better. Look Confident.</h2>'
        '<p>Poor posture from desk work and phone use can leave you feeling stiff and tired. The AlignPro gently trains your muscles to maintain better posture throughout the day.</p>'
        '<ul>'
        '<li><strong>Gentle Reminder:</strong> Lightweight design gently pulls shoulders back without restricting movement</li>'
        '<li><strong>Adjustable Fit:</strong> Fits chest sizes 28 to 48 inches, men and women</li>'
        '<li><strong>Breathable Mesh:</strong> Wear comfortably under clothes all day</li>'
        '<li><strong>Easy On/Off:</strong> Velcro straps adjust in seconds</li>'
        '<li><strong>Gradual Training:</strong> Start with 30 minutes daily, build up as your muscles adapt</li>'
        '</ul>'
        '<p style="font-size:12px;color:#666"><em>This is a wellness and comfort product. It is not a medical device and is not intended to diagnose, treat, cure, or prevent any medical condition. If you have back pain or spinal issues, consult a healthcare professional before use.</em></p>'
        '</div>'
})

# FIX 10: ArcLite Lighter — add 18+ disclaimer
fixes.append({
    "id": 14972407742836,
    "issue": "Lighter needs age restriction disclaimer",
    "body": '<div style="font-family:Arial,sans-serif;max-width:800px">'
        '<h2 style="color:#2c3e50">Never Buy Lighter Fluid Again</h2>'
        '<p>The ArcLite uses dual-arc plasma technology with no butane, no flame, and no refills. Works in wind, rain, and at any altitude. Just charge via USB and you are set.</p>'
        '<ul>'
        '<li><strong>Dual-Arc Plasma:</strong> Electric arc lights anything a traditional lighter can</li>'
        '<li><strong>Windproof:</strong> Works perfectly in wind, rain, and cold weather</li>'
        '<li><strong>USB Rechargeable:</strong> One charge provides 300+ lights</li>'
        '<li><strong>Safety Lock:</strong> Push-button safety prevents accidental ignition</li>'
        '<li><strong>Eco-Friendly:</strong> No butane, no fluid waste, no flint to replace</li>'
        '</ul>'
        '<p style="font-size:12px;color:#666"><em>You must be 18 years or older to purchase this product. By purchasing, you confirm you are of legal age. Keep out of reach of children.</em></p>'
        '</div>'
})

# ============================================================
# EXECUTE ALL FIXES
# ============================================================
print("=" * 60)
print("LEGAL COMPLIANCE FIX — 10 PRODUCTS")
print("=" * 60)

success = 0
for i, fix in enumerate(fixes, 1):
    pid = fix["id"]
    status = update_product(
        pid,
        title=fix.get("title"),
        body=fix.get("body"),
        tags=fix.get("tags")
    )
    ok = "OK" if status == 200 else f"FAIL ({status})"
    if status == 200:
        success += 1
    print(f"  [{i}/10] {ok} — {fix['issue'][:60]}")
    time.sleep(0.5)

print(f"\nDone: {success}/10 fixes applied successfully")
