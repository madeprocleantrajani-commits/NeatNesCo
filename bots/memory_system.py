"""
NEATNESTCO — MEMORY SYSTEM
===========================
Sistemi qendror i kujtesës për të gjithë bot suite-in.
Çdo bot lexon dhe shkruan këtu — kështu nesër di çfarë ka bërë dje.

Përdorimi:
    from memory_system import BotMemory
    mem = BotMemory()

    # Në fillim të çdo bot:
    mem.bot_start("trend_scanner")

    # Ruaj produkt:
    mem.save_product(asin="B08XYZ", title="...", score=82, source="amazon")

    # Ruaj vendim:
    mem.log_decision("trend_scanner", "B08XYZ", "STRONG_BUY", reason="BSR rising 3 weeks")

    # Në fund të botit:
    mem.bot_end("trend_scanner", products_found=45, errors=0)

    # Winner Analyzer — merr historikun:
    history = mem.get_product_history("B08XYZ")
    already_imported = mem.was_imported("B08XYZ")
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(os.environ.get("MEMORY_DB_PATH", "/home/ubuntu/dropship-bots/memory.db"))


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Krijon të gjitha tabelat nëse nuk ekzistojnë."""
    with get_conn() as conn:
        conn.executescript("""

        -- 1. PRODUKTET — çdo produkt unik që sistemi ka parë ndonjëherë
        CREATE TABLE IF NOT EXISTS products (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            asin          TEXT,
            title         TEXT NOT NULL,
            source        TEXT NOT NULL,  -- amazon / aliexpress / tiktok / ebay
            first_seen    TEXT NOT NULL,
            last_seen     TEXT NOT NULL,
            times_seen    INTEGER DEFAULT 1,
            best_score    REAL DEFAULT 0,
            current_score REAL DEFAULT 0,
            status        TEXT DEFAULT 'tracking',
            -- statuset: tracking / candidate / imported / sold / rejected / paused
            notes         TEXT,
            UNIQUE(asin, source)
        );

        -- 2. SCORE HISTORY — çdo herë që një produkt merr score
        CREATE TABLE IF NOT EXISTS score_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL REFERENCES products(id),
            run_date    TEXT NOT NULL,
            score       REAL NOT NULL,
            demand_pts  REAL,
            financial_pts REAL,
            supply_pts  REAL,
            risk_pts    REAL,
            confidence  INTEGER,
            sources_confirmed TEXT  -- JSON list e burimeve
        );

        -- 3. VENDIMET — çdo vendim i marrë për një produkt
        CREATE TABLE IF NOT EXISTS decisions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL REFERENCES products(id),
            run_date    TEXT NOT NULL,
            bot_name    TEXT NOT NULL,
            decision    TEXT NOT NULL,  -- STRONG_BUY / BUY / WATCH / REJECT / IMPORT / SKIP
            reason      TEXT,
            confidence  REAL,
            overridden  INTEGER DEFAULT 0,  -- 1 nëse u anulua manualisht
            override_note TEXT
        );

        -- 4. IMPORTET — çdo produkt që ka shkuar në Shopify
        CREATE TABLE IF NOT EXISTS imports (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id      INTEGER NOT NULL REFERENCES products(id),
            shopify_id      TEXT,
            imported_at     TEXT NOT NULL,
            import_price    REAL,
            cost_price      REAL,
            margin_pct      REAL,
            status          TEXT DEFAULT 'draft',  -- draft / active / paused / removed
            views_7d        INTEGER DEFAULT 0,
            orders_total    INTEGER DEFAULT 0,
            revenue_total   REAL DEFAULT 0,
            last_updated    TEXT
        );

        -- 5. BOT RUNS — çdo ekzekutim i çdo boti
        CREATE TABLE IF NOT EXISTS bot_runs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_name        TEXT NOT NULL,
            started_at      TEXT NOT NULL,
            ended_at        TEXT,
            duration_sec    REAL,
            status          TEXT DEFAULT 'running',  -- running / success / failed / timeout
            products_found  INTEGER DEFAULT 0,
            products_new    INTEGER DEFAULT 0,
            errors          INTEGER DEFAULT 0,
            error_log       TEXT,  -- JSON list e erroreve
            data_size_kb    REAL,
            notes           TEXT
        );

        -- 6. MARKET SIGNALS — trendet dhe sinjalet e tregut me kohë
        CREATE TABLE IF NOT EXISTS market_signals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_date TEXT NOT NULL,
            source      TEXT NOT NULL,  -- google_trends / ebay / tiktok / amazon_bsr
            keyword     TEXT,
            product_id  INTEGER REFERENCES products(id),
            signal_type TEXT,  -- emerging / breakout / declining / stable
            value       REAL,
            raw_data    TEXT   -- JSON i plotë
        );

        -- 7. COMPETITOR EVENTS — çfarë kanë bërë konkurentët
        CREATE TABLE IF NOT EXISTS competitor_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date  TEXT NOT NULL,
            store_url   TEXT NOT NULL,
            event_type  TEXT NOT NULL,  -- new_product / price_change / removed / sale
            product_ref TEXT,
            old_value   TEXT,
            new_value   TEXT,
            notes       TEXT
        );

        -- 8. SYSTEM STATE — gjendja e përgjithshme e sistemit
        CREATE TABLE IF NOT EXISTS system_state (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        -- Indekset për queries të shpejta
        CREATE INDEX IF NOT EXISTS idx_products_asin    ON products(asin);
        CREATE INDEX IF NOT EXISTS idx_products_status  ON products(status);
        CREATE INDEX IF NOT EXISTS idx_products_score   ON products(current_score DESC);
        CREATE INDEX IF NOT EXISTS idx_score_product    ON score_history(product_id, run_date);
        CREATE INDEX IF NOT EXISTS idx_decisions_date   ON decisions(run_date, decision);
        CREATE INDEX IF NOT EXISTS idx_bot_runs_name    ON bot_runs(bot_name, started_at);
        CREATE INDEX IF NOT EXISTS idx_signals_date     ON market_signals(signal_date, source);
        """)
    print(f"[memory] Database initialized at {DB_PATH}")


class BotMemory:
    """
    Ndërfaqja kryesore — çdo bot e përdor këtë klasë.
    
    Shembull i plotë i përdorimit në trend_scanner.py:
    
        mem = BotMemory()
        run_id = mem.bot_start("trend_scanner")
        
        for product in found_products:
            pid = mem.save_product(
                asin=product['asin'],
                title=product['title'],
                source='amazon',
                score=product['score']
            )
            mem.log_decision("trend_scanner", pid, "STRONG_BUY",
                           reason=f"BSR #{product['bsr']}, rising 3 weeks")
        
        mem.bot_end(run_id, products_found=len(found_products), errors=0)
    """

    def __init__(self):
        init_db()

    # ─── BOT LIFECYCLE ────────────────────────────────────────────

    def bot_start(self, bot_name: str) -> int:
        """Regjistro fillimin e botit. Kthe run_id."""
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO bot_runs (bot_name, started_at, status) VALUES (?,?,?)",
                (bot_name, _now(), "running")
            )
            run_id = cur.lastrowid
        self._set_state(f"bot.{bot_name}.last_run_id", str(run_id))
        self._set_state(f"bot.{bot_name}.last_run_start", _now())
        self._set_state(f"bot.{bot_name}.status", "running")
        print(f"[memory] {bot_name} started — run_id={run_id}")
        return run_id

    def bot_end(self, run_id: int, products_found: int = 0,
                products_new: int = 0, errors: int = 0,
                error_log: list = None, data_size_kb: float = 0,
                notes: str = None):
        """Regjistro përfundimin e botit."""
        with get_conn() as conn:
            row = conn.execute(
                "SELECT started_at, bot_name FROM bot_runs WHERE id=?", (run_id,)
            ).fetchone()
            if not row:
                return
            started = datetime.fromisoformat(row["started_at"])
            duration = (datetime.now() - started).total_seconds()
            status = "failed" if errors > 0 else "success"
            conn.execute("""
                UPDATE bot_runs SET
                    ended_at=?, duration_sec=?, status=?,
                    products_found=?, products_new=?, errors=?,
                    error_log=?, data_size_kb=?, notes=?
                WHERE id=?
            """, (
                _now(), round(duration, 1), status,
                products_found, products_new, errors,
                json.dumps(error_log or []), data_size_kb, notes,
                run_id
            ))
            bot_name = row["bot_name"]
        self._set_state(f"bot.{bot_name}.status", status)
        self._set_state(f"bot.{bot_name}.last_run_end", _now())
        self._set_state(f"bot.{bot_name}.last_products_found", str(products_found))
        print(f"[memory] {bot_name} ended — {status}, {products_found} products, {round(duration,1)}s")

    def bot_failed(self, run_id: int, error: str):
        """Shëno bot si dështuar me error message."""
        with get_conn() as conn:
            row = conn.execute(
                "SELECT started_at, bot_name FROM bot_runs WHERE id=?", (run_id,)
            ).fetchone()
            if not row:
                return
            duration = (datetime.now() - datetime.fromisoformat(row["started_at"])).total_seconds()
            conn.execute("""
                UPDATE bot_runs SET ended_at=?, duration_sec=?, status='failed',
                    errors=1, error_log=?
                WHERE id=?
            """, (_now(), round(duration, 1), json.dumps([error]), run_id))

    # ─── PRODUKTET ────────────────────────────────────────────────

    def save_product(self, title: str, source: str, asin: str = None,
                     score: float = 0, notes: str = None) -> int:
        """
        Ruaj ose përditëso një produkt. Kthe product_id.
        Nëse produkti ekziston (sipas asin+source), përditëso — mos dublikato.
        """
        now = _now()
        with get_conn() as conn:
            if asin:
                row = conn.execute(
                    "SELECT id, times_seen, best_score FROM products WHERE asin=? AND source=?",
                    (asin, source)
                ).fetchone()
                if row:
                    best = max(row["best_score"], score)
                    conn.execute("""
                        UPDATE products SET
                            last_seen=?, times_seen=times_seen+1,
                            current_score=?, best_score=?, notes=?
                        WHERE id=?
                    """, (now, score, best, notes, row["id"]))
                    return row["id"]

            cur = conn.execute("""
                INSERT INTO products (asin, title, source, first_seen, last_seen, current_score, best_score, notes)
                VALUES (?,?,?,?,?,?,?,?)
            """, (asin, title, source, now, now, score, score, notes))
            return cur.lastrowid

    def update_product_status(self, product_id: int, status: str, notes: str = None):
        """
        Ndryshon statusin e produktit.
        Statuset: tracking / candidate / imported / sold / rejected / paused
        """
        with get_conn() as conn:
            conn.execute(
                "UPDATE products SET status=?, notes=COALESCE(?,notes) WHERE id=?",
                (status, notes, product_id)
            )

    def get_product_history(self, asin: str) -> dict:
        """
        Kthe historikun e plotë të një produkti:
        - sa herë është parë
        - score-t e kaluara
        - vendimet e marra
        - a është importuar
        """
        with get_conn() as conn:
            product = conn.execute(
                "SELECT * FROM products WHERE asin=? ORDER BY best_score DESC LIMIT 1",
                (asin,)
            ).fetchone()
            if not product:
                return {}

            pid = product["id"]
            scores = conn.execute("""
                SELECT run_date, score, demand_pts, financial_pts, supply_pts, risk_pts
                FROM score_history WHERE product_id=? ORDER BY run_date DESC LIMIT 30
            """, (pid,)).fetchall()

            decisions = conn.execute("""
                SELECT run_date, bot_name, decision, reason
                FROM decisions WHERE product_id=? ORDER BY run_date DESC LIMIT 20
            """, (pid,)).fetchall()

            imp = conn.execute(
                "SELECT * FROM imports WHERE product_id=? LIMIT 1", (pid,)
            ).fetchone()

            return {
                "product": dict(product),
                "score_trend": [dict(s) for s in scores],
                "decisions": [dict(d) for d in decisions],
                "import": dict(imp) if imp else None,
                "was_imported": imp is not None,
                "was_rejected": any(d["decision"] == "REJECT" for d in decisions),
                "times_seen": product["times_seen"],
                "best_score": product["best_score"],
            }

    def was_imported(self, asin: str) -> bool:
        """Kontrollo nëse ky ASIN është importuar tashmë në Shopify."""
        with get_conn() as conn:
            row = conn.execute("""
                SELECT i.id FROM imports i
                JOIN products p ON p.id = i.product_id
                WHERE p.asin=?
            """, (asin,)).fetchone()
            return row is not None

    def was_rejected(self, asin: str) -> bool:
        """Kontrollo nëse ky ASIN është refuzuar tashmë."""
        with get_conn() as conn:
            row = conn.execute("""
                SELECT d.id FROM decisions d
                JOIN products p ON p.id = d.product_id
                WHERE p.asin=? AND d.decision='REJECT'
            """, (asin,)).fetchone()
            return row is not None

    # ─── VENDIMET ─────────────────────────────────────────────────

    def log_decision(self, bot_name: str, product_id: int,
                     decision: str, reason: str = None, confidence: float = None):
        """
        Regjistro çdo vendim të marrë për një produkt.
        Decision: STRONG_BUY / BUY / WATCH / REJECT / IMPORT / SKIP
        """
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO decisions (product_id, run_date, bot_name, decision, reason, confidence)
                VALUES (?,?,?,?,?,?)
            """, (product_id, _now(), bot_name, decision, reason, confidence))

    def log_score(self, product_id: int, score: float,
                  demand_pts: float = None, financial_pts: float = None,
                  supply_pts: float = None, risk_pts: float = None,
                  confidence: int = None, sources: list = None):
        """Ruaj score-in e plotë me breakdown."""
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO score_history
                    (product_id, run_date, score, demand_pts, financial_pts,
                     supply_pts, risk_pts, confidence, sources_confirmed)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                product_id, _now(), score, demand_pts, financial_pts,
                supply_pts, risk_pts, confidence,
                json.dumps(sources or [])
            ))

    # ─── IMPORTET ─────────────────────────────────────────────────

    def log_import(self, product_id: int, shopify_id: str,
                   import_price: float, cost_price: float) -> int:
        """Regjistro importimin e produktit në Shopify."""
        margin = round((import_price - cost_price) / import_price * 100, 1) if import_price > 0 else 0
        with get_conn() as conn:
            cur = conn.execute("""
                INSERT INTO imports (product_id, shopify_id, imported_at,
                    import_price, cost_price, margin_pct, last_updated)
                VALUES (?,?,?,?,?,?,?)
            """, (product_id, shopify_id, _now(), import_price, cost_price, margin, _now()))
            imp_id = cur.lastrowid
        self.update_product_status(product_id, "imported")
        return imp_id

    def update_import_performance(self, shopify_id: str,
                                   views_7d: int = None, orders: int = None,
                                   revenue: float = None):
        """Përditëso performancën e produktit pas shitjeve."""
        with get_conn() as conn:
            conn.execute("""
                UPDATE imports SET
                    views_7d   = COALESCE(?, views_7d),
                    orders_total = COALESCE(?, orders_total),
                    revenue_total = COALESCE(?, revenue_total),
                    last_updated = ?
                WHERE shopify_id=?
            """, (views_7d, orders, revenue, _now(), shopify_id))

    # ─── SINJALET E TREGUT ────────────────────────────────────────

    def log_signal(self, source: str, signal_type: str,
                   keyword: str = None, product_id: int = None,
                   value: float = None, raw_data: dict = None):
        """Ruaj sinjalin e tregut (trend, breakout, declining...)."""
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO market_signals
                    (signal_date, source, keyword, product_id, signal_type, value, raw_data)
                VALUES (?,?,?,?,?,?,?)
            """, (_now(), source, keyword, product_id, signal_type, value,
                  json.dumps(raw_data or {})))

    def log_competitor_event(self, store_url: str, event_type: str,
                              product_ref: str = None,
                              old_value: str = None, new_value: str = None,
                              notes: str = None):
        """Regjistro çdo ndryshim te konkurentët."""
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO competitor_events
                    (event_date, store_url, event_type, product_ref, old_value, new_value, notes)
                VALUES (?,?,?,?,?,?,?)
            """, (_now(), store_url, event_type, product_ref, old_value, new_value, notes))

    # ─── QUERIES PËR INTELLIGENCE ENGINE ─────────────────────────

    def get_candidates(self, min_score: float = 70,
                       max_results: int = 20,
                       exclude_imported: bool = True) -> list:
        """
        Kthe produktet kandidatë për importim.
        Filtruar sipas score, pa ata të importuar tashmë.
        """
        exclude_clause = "AND p.status NOT IN ('imported','rejected')" if exclude_imported else ""
        with get_conn() as conn:
            rows = conn.execute(f"""
                SELECT p.*, COUNT(d.id) as decision_count,
                       MAX(CASE WHEN d.decision='STRONG_BUY' THEN 1 ELSE 0 END) as has_strong_buy
                FROM products p
                LEFT JOIN decisions d ON d.product_id = p.id
                    AND d.run_date >= datetime('now', '-3 days')
                WHERE p.current_score >= ?
                {exclude_clause}
                GROUP BY p.id
                HAVING decision_count >= 1
                ORDER BY p.current_score DESC
                LIMIT ?
            """, (min_score, max_results)).fetchall()
            return [dict(r) for r in rows]

    def get_winners_today(self) -> dict:
        """
        Kthe summary të winners të sotëm.
        Kjo zëvendëson "128 STRONG_BUY" me kontekst real.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        with get_conn() as conn:
            strong_buy = conn.execute("""
                SELECT COUNT(DISTINCT product_id) as cnt FROM decisions
                WHERE decision='STRONG_BUY' AND run_date LIKE ?
            """, (f"{today}%",)).fetchone()["cnt"]

            buy = conn.execute("""
                SELECT COUNT(DISTINCT product_id) as cnt FROM decisions
                WHERE decision='BUY' AND run_date LIKE ?
            """, (f"{today}%",)).fetchone()["cnt"]

            new_today = conn.execute("""
                SELECT COUNT(*) as cnt FROM products WHERE first_seen LIKE ?
            """, (f"{today}%",)).fetchone()["cnt"]

            already_imported = conn.execute(
                "SELECT COUNT(*) as cnt FROM imports"
            ).fetchone()["cnt"]

            return {
                "date": today,
                "strong_buy": strong_buy,
                "buy": buy,
                "new_products_seen": new_today,
                "total_imported": already_imported,
            }

    def get_bot_status_summary(self) -> list:
        """
        Kthe gjendjen e të gjithë botave — për raport.
        """
        with get_conn() as conn:
            rows = conn.execute("""
                SELECT bot_name,
                       MAX(started_at) as last_run,
                       status,
                       products_found,
                       duration_sec,
                       errors
                FROM bot_runs
                WHERE started_at >= datetime('now', '-1 day')
                GROUP BY bot_name
                ORDER BY last_run DESC
            """).fetchall()
            return [dict(r) for r in rows]

    def get_product_trend(self, asin: str, days: int = 14) -> list:
        """Kthe trendin e score-it të një produkti gjatë X ditëve."""
        with get_conn() as conn:
            rows = conn.execute("""
                SELECT sh.run_date, sh.score, sh.demand_pts, sh.risk_pts
                FROM score_history sh
                JOIN products p ON p.id = sh.product_id
                WHERE p.asin=? AND sh.run_date >= datetime('now', ?)
                ORDER BY sh.run_date ASC
            """, (asin, f"-{days} days")).fetchall()
            return [dict(r) for r in rows]

    def get_rejected_asins(self) -> set:
        """Kthe set-in e të gjithë ASIN-ve të refuzuara — për filtrим të shpejtë."""
        with get_conn() as conn:
            rows = conn.execute("""
                SELECT DISTINCT p.asin FROM decisions d
                JOIN products p ON p.id = d.product_id
                WHERE d.decision = 'REJECT' AND p.asin IS NOT NULL
            """).fetchall()
            return {r["asin"] for r in rows}

    def get_imported_asins(self) -> set:
        """Kthe set-in e të gjithë ASIN-ve të importuara."""
        with get_conn() as conn:
            rows = conn.execute("""
                SELECT DISTINCT p.asin FROM imports i
                JOIN products p ON p.id = i.product_id
                WHERE p.asin IS NOT NULL
            """).fetchall()
            return {r["asin"] for r in rows}

    # ─── SYSTEM STATE ─────────────────────────────────────────────

    def _set_state(self, key: str, value: str):
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO system_state (key, value, updated_at) VALUES (?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """, (key, value, _now()))

    def get_state(self, key: str, default: str = None) -> str:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT value FROM system_state WHERE key=?", (key,)
            ).fetchone()
            return row["value"] if row else default

    def get_full_context(self) -> dict:
        """
        Kthe kontekstin e plotë të sistemit — run_all.py e përdor këtë
        për të ditur gjendjen para se të fillojë.
        """
        with get_conn() as conn:
            total_products = conn.execute(
                "SELECT COUNT(*) as c FROM products"
            ).fetchone()["c"]

            total_imported = conn.execute(
                "SELECT COUNT(*) as c FROM imports"
            ).fetchone()["c"]

            top5 = conn.execute("""
                SELECT title, current_score, status, asin
                FROM products ORDER BY current_score DESC LIMIT 5
            """).fetchall()

            last_run = conn.execute("""
                SELECT bot_name, started_at, status, products_found
                FROM bot_runs ORDER BY started_at DESC LIMIT 10
            """).fetchall()

            return {
                "total_products_seen_ever": total_products,
                "total_imported": total_imported,
                "winners_today": self.get_winners_today(),
                "top5_products": [dict(r) for r in top5],
                "last_10_bot_runs": [dict(r) for r in last_run],
                "bot_statuses": self.get_bot_status_summary(),
            }

    # ─── CLEANUP ──────────────────────────────────────────────────

    def cleanup_old_data(self, keep_days: int = 90):
        """
        Pastro të dhënat e vjetra — mbaj vetëm X ditët e fundit
        për market_signals dhe competitor_events.
        Produktet dhe importet NËVER fshihen.
        """
        cutoff = (datetime.now() - timedelta(days=keep_days)).isoformat()
        with get_conn() as conn:
            c1 = conn.execute(
                "DELETE FROM market_signals WHERE signal_date < ?", (cutoff,)
            ).rowcount
            c2 = conn.execute(
                "DELETE FROM competitor_events WHERE event_date < ?", (cutoff,)
            ).rowcount
        print(f"[memory] Cleanup: {c1} signals, {c2} competitor events removed (>{keep_days}d old)")


# ─── HELPER ───────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ─── CLI — testo direkt nga terminal ──────────────────────────────

if __name__ == "__main__":
    import sys

    mem = BotMemory()

    if len(sys.argv) < 2 or sys.argv[1] == "status":
        ctx = mem.get_full_context()
        print("\n=== NEATNESTCO MEMORY STATUS ===")
        print(f"Produkte të parë gjithsej : {ctx['total_products_seen_ever']}")
        print(f"Importuar në Shopify      : {ctx['total_imported']}")
        w = ctx["winners_today"]
        print(f"\nSot ({w['date']}):")
        print(f"  STRONG_BUY : {w['strong_buy']}")
        print(f"  BUY        : {w['buy']}")
        print(f"  Produkte të reja : {w['new_products_seen']}")
        print(f"\nTop 5 produktet:")
        for p in ctx["top5_products"]:
            print(f"  [{p['current_score']:5.1f}] {p['title'][:50]} ({p['status']})")
        print(f"\nRuns e fundit:")
        for r in ctx["last_10_bot_runs"]:
            print(f"  {r['bot_name']:<25} {r['status']:<10} {r['started_at'][:16]}  {r['products_found']} products")

    elif sys.argv[1] == "test":
        print("\n--- Duke testuar memory system ---")
        run_id = mem.bot_start("test_bot")
        pid = mem.save_product(
            asin="B0TEST001",
            title="Test Product — Kitchen Gadget",
            source="amazon",
            score=78.5
        )
        mem.log_score(pid, 78.5, demand_pts=28, financial_pts=22, supply_pts=15, risk_pts=-5,
                      confidence=4, sources=["amazon", "google_trends", "tiktok", "aliexpress"])
        mem.log_decision("test_bot", pid, "STRONG_BUY",
                         reason="BSR #142 rising, 4 sources confirmed, margin 38%")
        mem.bot_end(run_id, products_found=1, products_new=1)
        print("[OK] Test i kryer. Ekzekuto 'python memory_system.py status' për të parë.")

    elif sys.argv[1] == "product" and len(sys.argv) > 2:
        asin = sys.argv[2]
        h = mem.get_product_history(asin)
        if not h:
            print(f"Produkti {asin} nuk gjendet.")
        else:
            p = h["product"]
            print(f"\n=== {p['title'][:60]} ===")
            print(f"ASIN: {asin} | Score: {p['current_score']} | Status: {p['status']}")
            print(f"Parë: {p['times_seen']} herë | Importuar: {h['was_imported']}")
            print(f"\nVendimet e fundit:")
            for d in h["decisions"][:5]:
                print(f"  {d['run_date'][:16]}  {d['decision']:<12}  {d['reason']}")

    elif sys.argv[1] == "cleanup":
        mem.cleanup_old_data(keep_days=90)

    else:
        print("Përdorimi: python memory_system.py [status|test|product ASIN|cleanup]")
