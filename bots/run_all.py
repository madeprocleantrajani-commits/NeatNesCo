"""
Master Runner v5
-----------------
Runs all bots with dependency graph, health checks, conditional execution.

v5: Fixed dependency logic (ANY dep fail = skip), added per-bot timeout (10min),
    improved summary reporting.

Usage:
  python run_all.py                    # Run everything
  python run_all.py amazon ebay        # Run specific bots
  python run_all.py report             # Just generate report
"""

import sys
import time
import signal
import threading
from datetime import datetime
from config import get_logger, ANTHROPIC_API_KEY, SHOPIFY_STORE, SHOPIFY_TOKEN
from alert_bot import send_alert

BOT_TIMEOUT = 600  # 10 minutes max per bot
BOT_TIMEOUTS = {"trends": 900, "competitors": 900}  # Slow bots get 15 min

log = get_logger("runner")

# Initialize memory system (SQLite)
try:
    from memory_system import BotMemory
    mem = BotMemory()
    log.info("[memory] SQLite memory system loaded")
except Exception as e:
    mem = None
    log.warning(f"[memory] Memory system unavailable: {e}")

BOTS = {
    "trends": ("trend_scanner", "run_full_scan"),
    "tiktok": ("tiktok_scanner", "run_tiktok_scan"),
    "amazon": ("amazon_tracker", "run_amazon_scan"),
    "demand": ("amazon_demand", "scan_demand"),
    "ebay": ("ebay_scanner", "run_ebay_scan"),
    "aliexpress": ("aliexpress_scanner", "run_aliexpress_scan"),
    "adspy": ("ad_spy", "run_ad_spy_scan"),
    "prices": ("price_monitor", "check_prices"),
    "competitors": ("competitor_tracker", "run_competitor_scan"),
    "discover": ("competitor_finder", "discover_competitors"),
    "saturation": ("saturation_detector", "run_saturation_scan"),
    "intelligence": ("intelligence", "DropshipIntelligence"),
    "winners": ("winner_analyzer", "run_winner_analysis"),
    "sentiment": ("sentiment_analyzer", "run_sentiment_analysis"),
    "council": ("ai_council", "run_ai_council"),
    "creatives": ("creative_lab", "run_creative_lab"),
    "ai": ("ai_analyzer", "run_ai_analysis"),
    "shopify": ("shopify_importer", "run_shopify_import"),
    "profit": ("profit_tracker", "run"),
    "inventory": ("inventory_checker", "run"),
    "learning": ("learning_db", "run_learning_report"),
    "metrics": ("metrics_tracker", "run_metrics_tracker"),
    "report": ("report_generator", "generate_daily_report"),
}

# Dependency graph — bot will be skipped if ANY of its required deps failed
DEPENDENCIES = {
    "aliexpress": ["trends"],       # Uses trending keywords
    "saturation": ["amazon"],       # Needs product data to check
    "intelligence": ["amazon"],      # Needs Amazon data at minimum
    "winners": ["intelligence"],     # Needs analysis data
    "sentiment": ["winners"],        # Analyzes winning product reviews
    "council": ["winners"],          # AI evaluates winners
    "creatives": ["winners"],        # Generates ads for winners
    "ai": ["amazon"],               # Analyzes Amazon candidates
    "shopify": ["winners"],          # Imports winner products
    "profit": ["shopify"],           # Tracks Shopify sales
    "inventory": ["shopify"],        # Checks stock for active products
    "learning": ["profit"],          # Generates learning report after profit data
    "metrics": ["winners"],           # Records snapshot after winners
    "report": ["amazon"],           # Needs at least Amazon data
}

# Default execution order — optimized for data flow
# Phase 1: Scraping → Phase 2: Analysis → Phase 3: AI → Phase 4: Action
DEFAULT_ORDER = [
    # Phase 1: Data Collection
    "trends", "tiktok", "amazon", "demand", "ebay",
    "aliexpress", "adspy", "prices", "competitors",
    # Phase 2: Analysis + Saturation
    "saturation", "intelligence", "winners",
    # Phase 3: AI Brain Layer
    "sentiment", "council", "creatives",
    # Phase 4: Metrics + Action + Reporting
    "metrics", "shopify", "profit", "inventory", "learning", "report",
]

# Bots that require specific config
REQUIRES_CONFIG = {
    "ai": lambda: bool(ANTHROPIC_API_KEY),
    "council": lambda: bool(ANTHROPIC_API_KEY),
    "creatives": lambda: bool(ANTHROPIC_API_KEY),
    "sentiment": lambda: bool(ANTHROPIC_API_KEY),
    "shopify": lambda: bool(SHOPIFY_STORE and SHOPIFY_TOKEN),
    "profit": lambda: bool(SHOPIFY_STORE and SHOPIFY_TOKEN),
    "inventory": lambda: bool(SHOPIFY_STORE and SHOPIFY_TOKEN),
}

def run_bot(name: str, failed_bots: set) -> dict:
    """Run a single bot with dependency checking and timeout."""
    result = {"name": name, "status": "pending", "duration": 0, "error": None}

    if name not in BOTS:
        log.error(f"Unknown bot: {name}")
        result["status"] = "unknown"
        return result

    # Check dependencies — skip if ANY required dependency failed
    deps = DEPENDENCIES.get(name, [])
    if deps:
        failed_deps = [d for d in deps if d in failed_bots]
        if failed_deps:  # ANY dep failed = skip this bot
            log.warning(f"Skipping {name}: dependency failed ({', '.join(failed_deps)})")
            result["status"] = "skipped"
            result["error"] = f"Dependencies failed: {', '.join(failed_deps)}"
            return result

    # Check config requirements
    config_check = REQUIRES_CONFIG.get(name)
    if config_check and not config_check():
        log.warning(f"Skipping {name}: required config not set")
        result["status"] = "skipped"
        result["error"] = "Missing required configuration"
        return result

    module_name, func_name = BOTS[name]
    log.info(f"▶ Starting: {name}")
    start = time.time()

    # Register bot start in memory
    run_id = None
    if mem:
        try:
            run_id = mem.bot_start(name)
        except Exception:
            pass

    # Run bot in a thread with timeout
    bot_result = {"ok": False, "error": None}

    def _run():
        try:
            module = __import__(module_name)
            if name == "intelligence":
                intel = module.DropshipIntelligence()
                intel.run_full_analysis()
            else:
                func = getattr(module, func_name)
                func()
            bot_result["ok"] = True
        except Exception as e:
            bot_result["error"] = str(e)[:300]

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    timeout = BOT_TIMEOUTS.get(name, BOT_TIMEOUT)
    thread.join(timeout=timeout)

    elapsed = time.time() - start

    if thread.is_alive():
        # Bot timed out
        result["status"] = "failed"
        result["duration"] = round(elapsed, 1)
        result["error"] = f"TIMEOUT after {timeout}s"
        log.error(f"⏰ TIMEOUT: {name} exceeded {timeout}s limit")
        send_alert(f"⏰ BOT TIMEOUT: {name}\nExceeded {timeout}s limit")
        if mem and run_id:
            try: mem.bot_failed(run_id, f"TIMEOUT after {timeout}s")
            except Exception: pass
    elif bot_result["ok"]:
        result["status"] = "ok"
        result["duration"] = round(elapsed, 1)
        log.info(f"✓ Completed: {name} ({elapsed:.1f}s)")
        if mem and run_id:
            try: mem.bot_end(run_id)
            except Exception: pass
    else:
        result["status"] = "failed"
        result["duration"] = round(elapsed, 1)
        result["error"] = bot_result["error"]
        log.error(f"✗ FAILED: {name} — {bot_result['error']}")
        send_alert(f"⚠️ BOT FAILURE: {name}\nError: {bot_result['error'][:200]}")
        if mem and run_id:
            try: mem.bot_failed(run_id, bot_result["error"] or "unknown")
            except Exception: pass

    return result


def main():
    start_time = datetime.now()

    if len(sys.argv) > 1:
        bot_names = sys.argv[1:]
    else:
        bot_names = DEFAULT_ORDER

    log.info(f"{'=' * 60}")
    log.info(f"DROPSHIP BOT SUITE v4 — {start_time.strftime('%Y-%m-%d %H:%M')}")
    log.info(f"Running: {', '.join(bot_names)}")
    log.info(f"{'=' * 60}")

    results = []
    failed_bots = set()

    for name in bot_names:
        result = run_bot(name, failed_bots)
        results.append(result)

        if result["status"] == "failed":
            failed_bots.add(name)

        time.sleep(2)

    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    ok_count = sum(1 for r in results if r["status"] == "ok")
    fail_count = sum(1 for r in results if r["status"] == "failed")
    skip_count = sum(1 for r in results if r["status"] == "skipped")

    log.info(f"\n{'=' * 60}")
    log.info(f"COMPLETE in {elapsed:.0f}s — OK: {ok_count} | Failed: {fail_count} | Skipped: {skip_count}")
    log.info(f"{'=' * 60}")

    for r in results:
        status_icon = {"ok": "✓", "failed": "✗", "skipped": "⊘"}.get(r["status"], "?")
        duration = f"{r['duration']:.0f}s" if r["duration"] else ""
        error = f" — {r['error'][:80]}" if r.get("error") else ""
        log.info(f"  {status_icon} {r['name']:<15} {r['status']:<8} {duration:>5}{error}")

    # Telegram summary
    if fail_count > 0 or ok_count > 0:
        msg = f"🤖 <b>BOT RUN COMPLETE</b>\n"
        msg += f"⏱ {elapsed:.0f}s | ✓ {ok_count} | ✗ {fail_count} | ⊘ {skip_count}\n\n"
        for r in results:
            icon = {"ok": "✅", "failed": "❌", "skipped": "⏭"}.get(r["status"], "❓")
            msg += f"{icon} {r['name']}"
            if r.get("error"):
                msg += f" — <i>{r['error'][:60]}</i>"
            msg += "\n"
        send_alert(msg, parse_mode="HTML")


if __name__ == "__main__":
    main()
