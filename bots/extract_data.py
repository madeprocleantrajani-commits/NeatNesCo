import json
from pathlib import Path

files = sorted(Path("data").glob("analysis_*.json"), reverse=True)
with open(files[0]) as f:
    data = json.load(f)

print("=== SOURCES ===")
for name, info in data.get("sources", {}).items():
    status = "ACTIVE" if info.get("active") else "INACTIVE"
    print(f"  {name}: {status}")

print("\n=== TOP 20 CANDIDATES ===")
cands = data.get("amazon", {}).get("dropship_candidates", [])
for c in cands[:20]:
    title = c.get("title", "?")[:50]
    score = c.get("dropship_score", 0)
    price = c.get("price_usd", 0)
    rat = c.get("rating", 0)
    rev = c.get("review_count", 0)
    print(f"  Score:{score:>3} Price:{price:.2f} Rating:{rat:.1f} Rev:{rev} | {title}")

cross = data.get("cross_references", [])
print(f"\n=== CROSS-REFS ({len(cross)}) ===")
for ref in cross[:15]:
    sig = ", ".join(ref.get("signals", []))
    viable = "VIABLE" if ref.get("profit_viable") else "LOW"
    profit = ref.get("real_profit", 0)
    margin = ref.get("margin_pct", 0)
    title = ref.get("title", "?")[:45]
    sc = ref.get("signal_count", 1)
    print(f"  [{sc}sig] {viable} profit:{profit:.2f} margin:{margin:.1f}% | {title}")
    print(f"       -> {sig}")

print("\n=== NICHE SCORES ===")
niches = data.get("niche_scores", {})
for ns in sorted(niches.values(), key=lambda x: x["total"], reverse=True):
    name = ns["name"]
    total = ns["total"]
    grade = ns["grade"]
    print(f"  {name:>20} {total:>3}/100 Grade:{grade}")

print("\n=== ALIEXPRESS DEALS ===")
deals = data.get("aliexpress", {}).get("best_deals", [])
for d in deals[:10]:
    sp = d.get("source_price") or d.get("price_usd", 0)
    rp = d.get("retail_price") or d.get("potential_retail", 0)
    orders = d.get("orders", "N/A")
    title = d.get("title", "?")[:42]
    print(f"  Src:{sp:.2f} Ret:{rp:.2f} Ord:{orders} | {title}")

print("\n=== HOT TRENDS ===")
for p in data.get("trends", {}).get("hot_products", [])[:10]:
    interest = p.get("current_interest", 0)
    trend = p.get("trend", "?")
    kw = p["keyword"]
    print(f"  {interest:>3}/100 {trend:<12} | {kw}")

print("\n=== EMERGING ===")
for e in data.get("trends", {}).get("emerging_products", [])[:10]:
    slope = e.get("slope", 0)
    kw = e["keyword"]
    print(f"  slope:+{slope:.2f} | {kw}")

print("\n=== CATEGORIES ===")
for cn, cd in data.get("amazon", {}).get("categories", {}).items():
    total = cd.get("total", 0)
    avg = cd.get("avg_price", 0)
    print(f"  {cn}: {total} products avg {avg:.2f}")

print("\n=== BSR RISING ===")
for r in data.get("amazon", {}).get("rising_products", [])[:8]:
    rc = r.get("rank_change", 0)
    price = r.get("price_usd", 0)
    title = r.get("title", "?")[:45]
    print(f"  +{rc} ranks {price:.2f} | {title}")

print("\n=== PRICE DISTRIBUTION ===")
dist = data.get("amazon", {}).get("price_distribution", {})
for k, v in dist.items():
    print(f"  {k}: {v}")
