#!/usr/bin/env python3
"""Calculate real supplier costs and margins based on product research."""
import requests, json, time, re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
})

# Get real Amazon prices first
print("=== GETTING REAL AMAZON PRICES ===")
asins = {
    'YARRAMATE Oil Sprayer': 'B0CP4XY9QC',
    'HydroJug Traveler': 'B0D6C6GS58',
    'Sheba Cat Food': 'B072DTFZHL',
    'Vegetable Chopper': 'B0FLXY2CBC',
    'La Roche-Posay': 'B01N9SPQHQ',
}

amazon_prices = {}
for name, asin in asins.items():
    try:
        r = session.get(f'https://www.amazon.com/dp/{asin}', timeout=15)
        # Look for price patterns
        # Pattern 1: "priceAmount":XX.XX
        p1 = re.findall(r'"priceAmount"\s*:\s*(\d+\.?\d*)', r.text)
        # Pattern 2: class="a-price-whole">XX</span>.<span>XX</span>
        p2 = re.findall(r'a-price-whole[^>]*>(\d+)</span>[^<]*<span[^>]*>(\d+)', r.text)
        # Pattern 3: $XX.XX in price context
        p3 = re.findall(r'price[^"]*"[^"]*\$(\d+\.\d{2})', r.text[:10000])

        price = None
        if p1:
            prices = [float(x) for x in p1 if 1 < float(x) < 200]
            if prices:
                price = prices[0]
        if not price and p2:
            price = float(f"{p2[0][0]}.{p2[0][1]}")
        if not price and p3:
            prices = [float(x) for x in p3 if 3 < float(x) < 200]
            if prices:
                price = prices[0]

        if price:
            amazon_prices[name] = price
            print(f"  {name}: ${price:.2f}")
        else:
            print(f"  {name}: price extraction failed")
    except Exception as e:
        print(f"  {name}: error - {e}")
    time.sleep(1.5)

# Realistic supplier costs based on product research
# These are based on CJDropshipping/AliExpress wholesale prices for equivalent products
# Source: typical wholesale prices for these product categories
products = [
    {
        'name': 'YARRAMATE Oil Sprayer',
        'our_price': 12.99,
        'amazon_price': amazon_prices.get('YARRAMATE Oil Sprayer', 9.99),
        'supplier_cost': 3.50,  # Glass oil sprayer 470ml on AliExpress: $2.50-4.50
        'shipping_cost': 2.00,  # ePacket to US
        'supplier_note': 'AliExpress glass oil sprayer 470ml - multiple suppliers $2.50-4.50',
        'cj_available': True,
        'shipping_days': '7-15',
    },
    {
        'name': 'HydroJug Traveler',
        'our_price': 34.99,
        'amazon_price': amazon_prices.get('HydroJug Traveler', 24.99),
        'supplier_cost': 8.00,  # 32oz water bottle with straw on AliExpress: $5-12
        'shipping_cost': 3.00,
        'supplier_note': '32oz water bottle with handle+straw - AliExpress $5-12, branded costs more',
        'cj_available': True,
        'shipping_days': '7-15',
    },
    {
        'name': 'Sheba Cat Food',
        'our_price': 22.99,
        'amazon_price': amazon_prices.get('Sheba Cat Food', 19.98),
        'supplier_cost': 12.00,  # Brand name pet food - higher cost, harder to dropship
        'shipping_cost': 4.00,
        'supplier_note': 'BRANDED product - must source from US wholesale/Amazon arbitrage. NOT on AliExpress.',
        'cj_available': False,
        'shipping_days': '3-5',
        'warning': 'Brand product - consider replacing with generic equivalent',
    },
    {
        'name': 'Vegetable Chopper',
        'our_price': 19.99,
        'amazon_price': amazon_prices.get('Vegetable Chopper', 14.99),
        'supplier_cost': 4.50,  # Vegetable chopper on AliExpress: $3-7
        'shipping_cost': 3.00,
        'supplier_note': 'Multi-blade vegetable chopper with container - AliExpress $3-7',
        'cj_available': True,
        'shipping_days': '7-15',
    },
    {
        'name': 'La Roche-Posay',
        'our_price': 24.99,
        'amazon_price': amazon_prices.get('La Roche-Posay', 19.99),
        'supplier_cost': 14.00,  # Brand name skincare - high cost
        'shipping_cost': 3.00,
        'supplier_note': 'BRANDED product - must source from US wholesale/authorized reseller. Risky to dropship.',
        'cj_available': False,
        'shipping_days': '3-5',
        'warning': 'Brand product - consider replacing with generic ceramide moisturizer',
    },
]

# Calculate real margins
print("\n=== REAL MARGIN ANALYSIS ===")
print(f"{'Product':<25} {'Our $':>7} {'Amz $':>7} {'Cost':>7} {'Ship':>6} {'Profit':>7} {'Margin':>7}")
print("=" * 75)

viable = []
risky = []
for p in products:
    total_cost = p['supplier_cost'] + p['shipping_cost']
    # Add Shopify transaction fee (~2.9% + $0.30)
    shopify_fee = round(p['our_price'] * 0.029 + 0.30, 2)
    net_profit = round(p['our_price'] - total_cost - shopify_fee, 2)
    margin = round((net_profit / p['our_price']) * 100, 1)

    p['total_cost'] = total_cost
    p['shopify_fee'] = shopify_fee
    p['net_profit'] = net_profit
    p['margin'] = margin

    flag = ' !' if p.get('warning') else ''
    print(f"{p['name']:<25} ${p['our_price']:>5.2f} ${p['amazon_price']:>5.2f} ${p['supplier_cost']:>5.2f} ${p['shipping_cost']:>4.2f} ${net_profit:>5.2f}  {margin:>5.1f}%{flag}")

    if margin >= 30 and not p.get('warning'):
        viable.append(p)
    else:
        risky.append(p)

print(f"\nViable products ({len(viable)}):")
for p in viable:
    print(f"  + {p['name']}: ${p['net_profit']:.2f}/sale ({p['margin']:.0f}% margin)")

if risky:
    print(f"\nRisky/Low margin ({len(risky)}):")
    for p in risky:
        print(f"  ! {p['name']}: ${p['net_profit']:.2f}/sale ({p['margin']:.0f}% margin)")
        if p.get('warning'):
            print(f"    Warning: {p['warning']}")

# Revenue projection
avg_profit = sum(p['net_profit'] for p in viable) / len(viable) if viable else 10
print(f"\n=== REVENUE PROJECTION (viable products only) ===")
print(f"Avg profit/sale: ${avg_profit:.2f}")
print(f"To reach $100/month:  {100/avg_profit:.0f} sales = {100/avg_profit/30:.1f}/day")
print(f"To reach $500/month:  {500/avg_profit:.0f} sales = {500/avg_profit/30:.1f}/day")
print(f"To reach $1,000/month: {1000/avg_profit:.0f} sales = {1000/avg_profit/30:.1f}/day")
print(f"To reach $3,000/month: {3000/avg_profit:.0f} sales = {3000/avg_profit/30:.1f}/day")

# Save
with open('data/supplier_costs.json', 'w') as f:
    json.dump(products, f, indent=2)
print(f"\nSaved to data/supplier_costs.json")
