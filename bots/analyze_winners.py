"""
Deep Winner Analysis — Repeat / Bundle / UGC / Early Trend Potential
Evaluates every candidate for long-term business viability.
"""
import json
from pathlib import Path

data_files = sorted(Path("data").glob("analysis_*.json"), reverse=True)
with open(data_files[0]) as f:
    data = json.load(f)

candidates = data.get("amazon", {}).get("dropship_candidates", [])
cross_refs = data.get("cross_references", [])
trends = data.get("trends", {})
hot = trends.get("hot_products", [])
emerging = trends.get("emerging_products", [])

# Keywords that indicate repeat purchase potential
REPEAT_KEYWORDS = [
    "filter", "refill", "replacement", "pack", "supply", "wipe",
    "bag", "sheet", "tablet", "cartridge", "pod", "strip",
    "battery", "bulb", "brush head", "pad", "liner", "roll",
    "treats", "food", "supplement", "vitamin", "serum", "cream",
]

# Keywords that indicate bundle potential
BUNDLE_KEYWORDS = [
    "set", "kit", "pack", "combo", "bundle", "collection",
    "organizer", "system", "multi", "accessory", "accessories",
    "tool", "band", "mat", "roller", "bottle", "light",
]

# Keywords that indicate UGC/viral content potential
UGC_KEYWORDS = [
    "before after", "transformation", "satisfying", "oddly",
    "unboxing", "review", "demo", "how to", "tutorial",
    "fitness", "workout", "beauty", "skin", "hair", "glow",
    "clean", "organize", "makeover", "hack", "diy",
    "kitchen", "cooking", "gadget", "cool", "smart",
    "pet", "dog", "cat", "baby", "kid",
    "shower", "light", "led", "spray", "roller",
]

# Categories with high UGC potential
UGC_CATEGORIES = ["beauty", "fitness", "kitchen", "pet", "home", "baby"]

def score_repeat(title):
    t = title.lower()
    hits = sum(1 for kw in REPEAT_KEYWORDS if kw in t)
    # Products bought regularly score higher
    score = min(hits * 30, 100)
    reasons = [kw for kw in REPEAT_KEYWORDS if kw in t]
    return score, reasons

def score_bundle(title):
    t = title.lower()
    hits = sum(1 for kw in BUNDLE_KEYWORDS if kw in t)
    score = min(hits * 25, 100)
    reasons = [kw for kw in BUNDLE_KEYWORDS if kw in t]
    return score, reasons

def score_ugc(title, category=""):
    t = (title + " " + category).lower()
    hits = sum(1 for kw in UGC_KEYWORDS if kw in t)
    cat_bonus = 20 if any(c in category.lower() for c in UGC_CATEGORIES) else 0
    score = min(hits * 15 + cat_bonus, 100)
    reasons = [kw for kw in UGC_KEYWORDS if kw in t]
    return score, reasons

def is_early_trend(title):
    t = title.lower()
    # Check if product matches any hot/emerging trend
    for h in hot:
        if any(word in t for word in h["keyword"].lower().split() if len(word) > 3):
            return True, h["keyword"], h.get("current_interest", 0)
    for e in emerging:
        if any(word in t for word in e["keyword"].lower().split() if len(word) > 3):
            return True, e["keyword"], e.get("current_interest", 0)
    return False, "", 0


print("=" * 90)
print("  DEEP WINNER ANALYSIS — Repeat / Bundle / UGC / Early Trend")
print("  Candidates:", len(candidates), "| Cross-refs:", len(cross_refs))
print("=" * 90)

# Analyze ALL candidates
winners = []
for c in candidates:
    title = c.get("title", "")
    cat = c.get("category", "")
    price = c.get("price_usd", 0)
    score = c.get("dropship_score", 0)
    rating = c.get("rating", 0)
    reviews = c.get("review_count", 0)

    rep_score, rep_reasons = score_repeat(title)
    bun_score, bun_reasons = score_bundle(title)
    ugc_score, ugc_reasons = score_ugc(title, cat)
    is_trend, trend_kw, trend_interest = is_early_trend(title)

    # Combined viability score
    viability = (
        score * 0.3 +           # dropship score
        rep_score * 0.25 +      # repeat purchase
        bun_score * 0.15 +      # bundle potential
        ugc_score * 0.2 +       # UGC/viral potential
        (30 if is_trend else 0) * 0.1  # trend bonus
    )

    product_type = []
    if rep_score >= 30:
        product_type.append("REPEAT")
    if bun_score >= 25:
        product_type.append("BUNDLE")
    if ugc_score >= 30:
        product_type.append("UGC")
    if is_trend:
        product_type.append("TREND")
    if not product_type:
        product_type.append("SHORT-TERM")

    winners.append({
        "title": title[:50],
        "price": price,
        "score": score,
        "rating": rating,
        "reviews": reviews,
        "category": cat,
        "repeat_score": rep_score,
        "bundle_score": bun_score,
        "ugc_score": ugc_score,
        "is_trend": is_trend,
        "trend_keyword": trend_kw,
        "viability": round(viability, 1),
        "type": " + ".join(product_type),
        "rep_reasons": rep_reasons,
        "bun_reasons": bun_reasons,
        "ugc_reasons": ugc_reasons,
    })

# Sort by viability
winners.sort(key=lambda x: x["viability"], reverse=True)

# Print top winners
print("\n--- TOP 25 LONG-TERM WINNERS (sorted by viability) ---\n")
for i, w in enumerate(winners[:25], 1):
    print(f"#{i:>2} VIABILITY:{w['viability']:>5.1f} | TYPE: {w['type']}")
    print(f"    {w['title']}")
    print(f"    ${w['price']:.2f} | Score:{w['score']} | R:{w['rating']:.1f} | Rev:{w['reviews']:,} | Cat:{w['category']}")
    if w['rep_reasons']:
        print(f"    REPEAT: {', '.join(w['rep_reasons'])}")
    if w['bun_reasons']:
        print(f"    BUNDLE: {', '.join(w['bun_reasons'])}")
    if w['ugc_reasons']:
        print(f"    UGC: {', '.join(w['ugc_reasons'])}")
    if w['is_trend']:
        print(f"    TREND: matches '{w['trend_keyword']}'")
    print()

# Summary stats
types = {}
for w in winners:
    for t in w["type"].split(" + "):
        types[t] = types.get(t, 0) + 1

print("--- TYPE DISTRIBUTION ---")
for t, count in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {t}: {count} products")

# Repeat purchase champions
repeat_champs = [w for w in winners if w["repeat_score"] >= 30]
print(f"\n--- REPEAT PURCHASE CHAMPIONS ({len(repeat_champs)}) ---")
for w in repeat_champs[:10]:
    print(f"  ${w['price']:.2f} | Rep:{w['repeat_score']} | {w['title']}")
    print(f"         Reasons: {', '.join(w['rep_reasons'])}")

# Bundle candidates
bundle_cands = [w for w in winners if w["bundle_score"] >= 25]
print(f"\n--- BUNDLE CANDIDATES ({len(bundle_cands)}) ---")
for w in bundle_cands[:10]:
    print(f"  ${w['price']:.2f} | Bun:{w['bundle_score']} | {w['title']}")
    print(f"         Reasons: {', '.join(w['bun_reasons'])}")

# UGC superstars
ugc_stars = [w for w in winners if w["ugc_score"] >= 30]
print(f"\n--- UGC SUPERSTARS ({len(ugc_stars)}) ---")
for w in ugc_stars[:10]:
    print(f"  ${w['price']:.2f} | UGC:{w['ugc_score']} | {w['title']}")
    print(f"         Reasons: {', '.join(w['ugc_reasons'])}")

# Early trend matches
trend_matches = [w for w in winners if w["is_trend"]]
print(f"\n--- EARLY TREND MATCHES ({len(trend_matches)}) ---")
for w in trend_matches[:10]:
    print(f"  ${w['price']:.2f} | Trend:'{w['trend_keyword']}' | {w['title']}")

# ULTIMATE PICKS: products with 3+ type tags
ultimate = [w for w in winners if len(w["type"].split(" + ")) >= 2 and "SHORT-TERM" not in w["type"]]
print(f"\n{'='*90}")
print(f"  ULTIMATE PICKS — Products with 2+ winning traits ({len(ultimate)})")
print(f"{'='*90}")
for i, w in enumerate(ultimate[:15], 1):
    print(f"  #{i} [{w['type']}]")
    print(f"     {w['title']}")
    print(f"     ${w['price']:.2f} | Viability:{w['viability']:.1f} | Score:{w['score']}")
    print()
