from amazon_demand import scan_demand
result = scan_demand()
status = result.get("status", "?")
scanned = result.get("keywords_scanned", 0)
suggestions = result.get("total_suggestions", 0)
discoveries = result.get("new_discoveries", 0)
top = result.get("top_discoveries", [])

print("=== AMAZON DEMAND RESULTS ===")
print("Status:", status)
print("Keywords scanned:", scanned)
print("Total suggestions:", suggestions)
print("New discoveries:", discoveries)
print("Top discoveries:", len(top))
for d in top[:15]:
    sug = d.get("suggestion", "?")
    src = d.get("source_keyword", "?")
    print("  ->", sug, "(from:", src + ")")
