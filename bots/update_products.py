#!/usr/bin/env python3
"""Update all 5 Shopify draft products with professional images, descriptions, and pricing."""
import requests, json, time, os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SHOP = os.getenv("SHOPIFY_STORE", "8hendy-8i.myshopify.com")
TOKEN = os.getenv("SHOPIFY_TOKEN", "")
HEADERS = {'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'}

# Load scraped images
with open('data/product_images.json') as f:
    img_data = json.load(f)

PRODUCTS = {
    'YARRAMATE': {
        'images_key': 'YARRAMATE Oil Sprayer',
        'our_price': '12.99',
        'compare_price': '24.99',
        'product_type': 'Kitchen Accessories',
        'tags': 'kitchen, oil-sprayer, cooking, air-fryer, bestseller, strong-buy, trending',
        'seo_title': 'YARRAMATE Glass Oil Sprayer 16oz - Perfect Kitchen Mist Sprayer',
        'seo_desc': 'Premium 16oz glass olive oil sprayer for cooking. Even mist, BPA-free, leak-proof. Rated 4.4/5 by 39,600+ customers. Free shipping.',
        'body_html': """<div class="product-description">
<h3>Premium Glass Oil Sprayer - The Kitchen Essential You Didn't Know You Needed</h3>
<p><strong>Say goodbye to over-oiling your food.</strong> This elegant 16oz glass olive oil sprayer gives you perfect, even coverage every time - whether you're air frying, grilling, or making salads.</p>
<h4>Why 39,600+ Customers Love It:</h4>
<ul>
<li><strong>Even Mist Spray</strong> - Ultra-fine nozzle distributes oil evenly, cutting oil usage by up to 80%</li>
<li><strong>Premium Glass Design</strong> - BPA-free borosilicate glass, no plastic taste, easy to clean</li>
<li><strong>Versatile Use</strong> - Perfect for olive oil, avocado oil, vinegar, lemon juice, soy sauce</li>
<li><strong>Large 16oz Capacity</strong> - Fill less often, cook more</li>
<li><strong>Leak-Proof Seal</strong> - No drips, no mess, no waste</li>
</ul>
<h4>Perfect For:</h4>
<p>Air fryer cooking | Grilling | Salad dressing | BBQ | Baking | Meal prep</p>
<p><strong>Free Shipping</strong> | <strong>30-Day Money-Back Guarantee</strong> | <strong>Rated 4.4/5 Stars</strong></p>
</div>"""
    },
    'HydroJug': {
        'images_key': 'HydroJug Traveler',
        'our_price': '34.99',
        'compare_price': '49.99',
        'product_type': 'Water Bottles',
        'tags': 'water-bottle, hydration, fitness, gym, travel, strong-buy, trending',
        'seo_title': 'HydroJug Traveler 32oz Water Bottle with Handle & Flip Straw',
        'seo_desc': 'HydroJug Traveler 32oz water bottle with handle and flip straw. Cup holder friendly, leak-proof. Rated 4.5/5.',
        'body_html': """<div class="product-description">
<h3>HydroJug Traveler - The Water Bottle That Actually Makes You Drink More Water</h3>
<p><strong>Stop dehydrating yourself.</strong> The HydroJug Traveler holds a full 32oz and fits in your car cup holder - no more excuses.</p>
<h4>Why 18,000+ Customers Are Obsessed:</h4>
<ul>
<li><strong>Dual-Function Lid</strong> - Flip straw for quick sips + wide mouth for ice and fruit</li>
<li><strong>Ergonomic Handle</strong> - Carry it everywhere with zero effort</li>
<li><strong>Cup Holder Friendly</strong> - Actually fits in your car, unlike most 32oz bottles</li>
<li><strong>Leak-Proof Design</strong> - Throw it in your bag without worrying</li>
<li><strong>BPA-Free &amp; Dishwasher Safe</strong> - Easy to clean, safe to use daily</li>
</ul>
<h4>Perfect For:</h4>
<p>Gym workouts | Office desk | Road trips | Hiking | Daily hydration goals</p>
<p><strong>Free Shipping</strong> | <strong>30-Day Money-Back Guarantee</strong> | <strong>Rated 4.5/5 Stars</strong></p>
</div>"""
    },
    'Sheba': {
        'images_key': 'Sheba Cat Food',
        'our_price': '22.99',
        'compare_price': '32.99',
        'product_type': 'Pet Food',
        'tags': 'cat-food, pet-supplies, cat, pet-food, grain-free, strong-buy, trending',
        'seo_title': 'Sheba Perfect Portions Wet Cat Food - Gourmet Cuts in Gravy',
        'seo_desc': 'Sheba Perfect Portions wet cat food with real meat in gravy. Grain-free, pre-portioned. Rated 4.7/5.',
        'body_html': """<div class="product-description">
<h3>Sheba Perfect Portions - The Gourmet Meal Your Cat Deserves</h3>
<p><strong>Your cat is tired of boring food.</strong> Sheba Perfect Portions delivers restaurant-quality cuts in savory gravy that cats go absolutely crazy for.</p>
<h4>Why 20,000+ Cat Parents Trust Sheba:</h4>
<ul>
<li><strong>Real Meat First</strong> - Premium cuts of real meat in rich, savory gravy</li>
<li><strong>Perfect Single Servings</strong> - Pre-portioned trays, no measuring, no waste</li>
<li><strong>Snap &amp; Peel Freshness</strong> - Each portion stays fresh until you open it</li>
<li><strong>Grain-Free Recipe</strong> - No corn, wheat, or soy - just pure nutrition</li>
<li><strong>Variety Pack</strong> - Multiple flavors to keep your cat excited at mealtime</li>
</ul>
<h4>Perfect For:</h4>
<p>Picky eaters | Senior cats | Multi-cat homes | Treat time | Meal toppers</p>
<p><strong>Free Shipping</strong> | <strong>30-Day Money-Back Guarantee</strong> | <strong>Rated 4.7/5 Stars</strong></p>
</div>"""
    },
    'Vegetable Chopper': {
        'images_key': 'Vegetable Chopper',
        'our_price': '19.99',
        'compare_price': '34.99',
        'product_type': 'Kitchen Tools',
        'tags': 'kitchen, vegetable-chopper, mandoline, meal-prep, cooking, strong-buy, trending',
        'seo_title': '8-Blade Vegetable Chopper Mandoline Slicer with Container',
        'seo_desc': 'All-in-1 vegetable chopper with 8 blades and container. Dice, slice, julienne in seconds. Rated 4.4/5.',
        'body_html': """<div class="product-description">
<h3>8-Blade Vegetable Chopper - Cut Your Meal Prep Time in Half</h3>
<p><strong>Stop wasting 30 minutes chopping vegetables.</strong> This all-in-1 mandoline slicer with 8 interchangeable blades does in seconds what takes you minutes by hand.</p>
<h4>Why Smart Cooks Love This:</h4>
<ul>
<li><strong>8 Blade Options</strong> - Dice, slice, julienne, grate - one tool does it all</li>
<li><strong>Built-In Container</strong> - Chop directly into the 1.5L collection tray, zero mess</li>
<li><strong>Hand Guard Included</strong> - Protect your fingers while chopping at speed</li>
<li><strong>Easy to Clean</strong> - All parts are dishwasher safe</li>
<li><strong>Space Saver</strong> - Replaces 8 different kitchen gadgets in your drawer</li>
</ul>
<h4>Perfect For:</h4>
<p>Meal prep | Salads | Stir-fry | Soups | Smoothie ingredients | Party platters</p>
<p><strong>Free Shipping</strong> | <strong>30-Day Money-Back Guarantee</strong> | <strong>Rated 4.4/5 Stars</strong></p>
</div>"""
    },
    'La Roche': {
        'images_key': 'La Roche-Posay',
        'our_price': '24.99',
        'compare_price': '38.99',
        'product_type': 'Skincare',
        'tags': 'skincare, moisturizer, beauty, face-cream, sensitive-skin, strong-buy, trending',
        'seo_title': 'La Roche-Posay Toleriane Double Repair Face Moisturizer',
        'seo_desc': 'La Roche-Posay Toleriane moisturizer with ceramides and niacinamide. 48hr hydration, oil-free. Rated 4.6/5.',
        'body_html': """<div class="product-description">
<h3>La Roche-Posay Toleriane - The Moisturizer Dermatologists Actually Recommend</h3>
<p><strong>Your skin barrier is everything.</strong> This double repair moisturizer restores and protects your skin's natural barrier while providing 48-hour hydration.</p>
<h4>Why 47,000+ Skincare Lovers Swear By It:</h4>
<ul>
<li><strong>Double Repair Formula</strong> - Ceramide-3 + Niacinamide restore and protect skin barrier</li>
<li><strong>48-Hour Hydration</strong> - Prebiotic thermal water locks in moisture all day</li>
<li><strong>Oil-Free &amp; Non-Comedogenic</strong> - Won't clog pores or cause breakouts</li>
<li><strong>Fragrance-Free</strong> - Safe for sensitive, reactive, and allergy-prone skin</li>
<li><strong>Dermatologist Tested</strong> - Recommended by 90,000+ dermatologists worldwide</li>
</ul>
<h4>Perfect For:</h4>
<p>Sensitive skin | Dry skin | Post-treatment recovery | Daily moisturizer | All skin types</p>
<p><strong>Free Shipping</strong> | <strong>30-Day Money-Back Guarantee</strong> | <strong>Rated 4.6/5 Stars</strong></p>
</div>"""
    }
}

# Get current products
r = requests.get(f'https://{SHOP}/admin/api/2024-01/products.json?limit=50', headers=HEADERS)
shopify_products = r.json()['products']
print(f'Found {len(shopify_products)} products in store\n')

# Match IDs
for p in shopify_products:
    title = p['title'].lower()
    for key in PRODUCTS:
        if key.lower() in title and PRODUCTS[key].get('id') is None:
            PRODUCTS[key]['id'] = p['id']
            break

# Update each product
for name, data in PRODUCTS.items():
    pid = data.get('id')
    if not pid:
        print(f'SKIP {name}: no matching product found')
        continue

    print(f'=== Updating {name} (ID: {pid}) ===')

    # 1. Update product details
    update = {
        'product': {
            'id': pid,
            'body_html': data['body_html'],
            'tags': data['tags'],
            'product_type': data['product_type'],
            'metafields_global_title_tag': data['seo_title'],
            'metafields_global_description_tag': data['seo_desc'],
        }
    }

    r = requests.put(f'https://{SHOP}/admin/api/2024-01/products/{pid}.json',
                     headers=HEADERS, json=update)
    if r.status_code == 200:
        print(f'  Description + Tags + SEO: OK')
        prod_data = r.json().get('product', {})
    else:
        print(f'  Update FAIL: {r.status_code} - {r.text[:150]}')
        continue

    # 2. Update variant price
    variants = prod_data.get('variants', [])
    if variants:
        vid = variants[0]['id']
        var_update = {
            'variant': {
                'id': vid,
                'price': data['our_price'],
                'compare_at_price': data['compare_price']
            }
        }
        rv = requests.put(f'https://{SHOP}/admin/api/2024-01/variants/{vid}.json',
                         headers=HEADERS, json=var_update)
        if rv.status_code == 200:
            print(f'  Price: ${data["our_price"]} (compare: ${data["compare_price"]})')
        else:
            print(f'  Price FAIL: {rv.status_code}')

    # 3. Add images
    images = img_data.get(data['images_key'], {}).get('images', [])
    for i, img_url in enumerate(images[:5]):
        img_payload = {
            'image': {
                'src': img_url,
                'position': i + 1
            }
        }
        ri = requests.post(f'https://{SHOP}/admin/api/2024-01/products/{pid}/images.json',
                          headers=HEADERS, json=img_payload)
        if ri.status_code == 200:
            print(f'  Image {i+1}/5: OK')
        else:
            print(f'  Image {i+1}/5: FAIL ({ri.status_code} - {ri.text[:80]})')
        time.sleep(0.5)

    print()
    time.sleep(0.5)

print('=== ALL PRODUCTS UPDATED! ===')
