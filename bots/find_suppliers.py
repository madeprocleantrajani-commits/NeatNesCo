#!/usr/bin/env python3
"""Find supplier costs from AliExpress and calculate real margins."""
import requests, json, time, re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
})

products = [
    {'name': 'YARRAMATE Oil Sprayer', 'search': 'glass olive oil sprayer 16oz cooking', 'our_price': 12.99, 'asin': 'B0CP4XY9QC'},
    {'name': 'HydroJug Traveler', 'search': '32oz water bottle handle flip straw', 'our_price': 34.99, 'asin': 'B0D6C6GS58'},
    {'name': 'Sheba Cat Food', 'search': 'wet cat food portions gravy variety pack', 'our_price': 22.99, 'asin': 'B072DTFZHL'},
    {'name': 'Vegetable Chopper', 'search': '8 blade vegetable chopper mandoline slicer container', 'our_price': 19.99, 'asin': 'B0FLXY2CBC'},
    {'name': 'La Roche-Posay', 'search': 'face moisturizer ceramide niacinamide double repair', 'our_price': 24.99, 'asin': 'B01N9SPQHQ'},
]

# Also get Amazon prices for reference
print("=== AMAZON PRICES (competitor reference) ===")
for p in products:
    try:
        url = f"https://www.amazon.com/dp/{p['asin']}"
        r = session.get(url, timeout=15)
        prices = re.findall(r'\$(\d+\.\d{2})', r.text[:8000])
        prices = [float(x) for x in prices if 1 < float(x) < 200]
        if prices:
            amazon_price = prices[0]
            p['amazon_price'] = amazon_price
            print(f"  {p['name']}: ${amazon_price:.2f} on Amazon")
        else:
            print(f"  {p['name']}: price not found")
    except Exception as e:
        print(f"  {p['name']}: error {e}")
    time.sleep(1.5)

print("\n=== ALIEXPRESS SUPPLIER SEARCH ===")
results = []
for p in products:
    query = p['search'].replace(' ', '+')
    try:
        url = f"https://www.aliexpress.com/wholesale?SearchText={query}"
        r = session.get(url, timeout=15)

        # Multiple price patterns
        prices = []
        # Pattern: US $X.XX
        for m in re.findall(r'US\s*\$\s*(\d+\.?\d*)', r.text):
            val = float(m)
            if 0.5 < val < 50:
                prices.append(val)
        # Pattern: "minPrice":"X.XX"
        for m in re.findall(r'"minPrice"\s*:\s*"?(\d+\.?\d*)"?', r.text):
            val = float(m)
            if 0.5 < val < 50:
                prices.append(val)

        prices = list(set(prices))[:15]

        if prices:
            min_cost = min(prices)
            avg_cost = sum(prices) / len(prices)
            amazon_price = p.get('amazon_price', p['our_price'] * 1.5)

            result = {
                'name': p['name'],
                'our_price': p['our_price'],
                'amazon_price': amazon_price,
                'supplier_min': round(min_cost, 2),
                'supplier_avg': round(avg_cost, 2),
                'margin_pct': round(((p['our_price'] - min_cost) / p['our_price']) * 100, 1),
                'profit_per_sale': round(p['our_price'] - min_cost, 2),
                'prices_found': len(prices)
            }
        else:
            # Estimate based on typical dropship margins (product cost ~30% of retail)
            est_cost = round(p['our_price'] * 0.25, 2)
            result = {
                'name': p['name'],
                'our_price': p['our_price'],
                'amazon_price': p.get('amazon_price', 0),
                'supplier_min': est_cost,
                'supplier_avg': est_cost,
                'margin_pct': 75.0,
                'profit_per_sale': round(p['our_price'] - est_cost, 2),
                'estimated': True
            }

        results.append(result)
        print(f"\n  {result['name']}:")
        print(f"    Our price: ${result['our_price']}")
        print(f"    Amazon:    ${result.get('amazon_price', '?')}")
        print(f"    Supplier:  ${result['supplier_min']:.2f} (min) / ${result['supplier_avg']:.2f} (avg)")
        print(f"    Margin:    {result['margin_pct']:.0f}%")
        print(f"    Profit:    ${result['profit_per_sale']:.2f}/sale")
        if result.get('estimated'):
            print(f"    NOTE: Estimated (AliExpress blocked)")
    except Exception as e:
        print(f"  {p['name']}: Error - {e}")
        results.append({
            'name': p['name'],
            'our_price': p['our_price'],
            'supplier_min': round(p['our_price'] * 0.25, 2),
            'estimated': True,
            'error': str(e)
        })
    time.sleep(2)

# Summary
print("\n\n=== PROFIT SUMMARY ===")
print(f"{'Product':<30} {'Our $':>8} {'Cost $':>8} {'Profit':>8} {'Margin':>8}")
print("-" * 70)
total_profit = 0
for r in results:
    profit = r.get('profit_per_sale', 0)
    total_profit += profit
    est = ' *' if r.get('estimated') else ''
    print(f"{r['name']:<30} ${r['our_price']:>6.2f} ${r['supplier_min']:>6.2f} ${profit:>6.2f} {r.get('margin_pct', 0):>6.1f}%{est}")

avg_profit = total_profit / len(results)
print(f"\nAvg profit per sale: ${avg_profit:.2f}")
print(f"To reach $3,000/month profit: need {3000/avg_profit:.0f} sales/month = {3000/avg_profit/30:.1f}/day")

with open('data/supplier_costs.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to data/supplier_costs.json")
