"""
Central configuration for all dropship bots.
Loads settings from .env file and provides shared utilities.

v3 — Rebuilt foundation:
  - Resilient HTTP with retries + backoff
  - 200+ brand word-boundary detection
  - USD-native pricing (Virginia VPS)
  - Expanded seed keywords (100+)
  - Centralized request utilities
"""
import os
import re
import time
import random
import logging
from pathlib import Path
from dotenv import load_dotenv

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# === Directories ===
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

for d in [DATA_DIR, LOGS_DIR, REPORTS_DIR]:
    d.mkdir(exist_ok=True)

# === Telegram Alerts ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# === Claude AI (Anthropic) ===
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# === Shopify ===
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "")   # your-store.myshopify.com
SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN", "")   # shpat_xxxxxxxxxxxx

# === Proxy ===
PROXY_URL = os.getenv("PROXY_URL", "")

# === Currency ===
# VPS is in Virginia (US) — Amazon returns USD natively.
DEFAULT_CURRENCY = "USD"

# === Google Trends ===
TRENDS_GEO = "US"
TRENDS_TIMEFRAME = "today 3-m"  # Last 3 months

# === Seed Keywords ===
# Physical products only — no digital, no subscriptions.
# 100+ keywords across 10 niches, focused on 2026 opportunity sub-niches.
SEED_KEYWORDS = {
    "home_gadgets": [
        "portable blender", "led strip lights", "smart plug",
        "air purifier", "electric lighter", "aroma diffuser",
        "motion sensor light", "portable projector", "smart doorbell",
        "robot vacuum cleaner",
    ],
    "fitness": [
        "posture corrector", "massage gun", "resistance bands",
        "ab roller", "yoga mat", "jump rope fitness",
        "foam roller", "grip strength trainer", "pull up bar",
        "wrist wraps",
    ],
    "pet_products": [
        "dog camera", "cat water fountain", "pet grooming glove",
        "dog car seat cover", "automatic pet feeder",
        "pet nail grinder", "dog anxiety vest", "cat tree tower",
        "dog poop bag dispenser", "pet hair remover",
    ],
    "tech_accessories": [
        "car phone mount", "wireless charger", "laptop stand",
        "ring light", "bluetooth tracker", "cable organizer",
        "portable monitor", "webcam cover", "usb hub",
        "phone tripod",
    ],
    "beauty_health": [
        "jade roller", "teeth whitening kit", "hair growth serum",
        "blackhead remover", "essential oil diffuser",
        "facial steamer", "derma roller", "lip plumper",
        "eyelash serum", "scalp massager",
    ],
    "outdoor": [
        "camping hammock", "solar power bank", "insulated water bottle",
        "tactical flashlight", "portable fan",
        "hiking backpack", "camping lantern", "survival bracelet",
        "portable water filter", "collapsible water bottle",
    ],
    "eco_friendly": [
        "reusable food wrap", "bamboo toothbrush", "solar garden lights",
        "reusable straw set", "beeswax wrap", "compost bin",
        "bamboo cutlery set", "reusable produce bags",
        "solar phone charger", "eco cleaning cloths",
    ],
    "home_office": [
        "desk organizer", "monitor light bar", "ergonomic mouse",
        "standing desk converter", "cable management box",
        "laptop cooling pad", "desk pad large", "blue light glasses",
        "noise cancelling earbuds", "whiteboard planner",
    ],
    "car_accessories": [
        "car vacuum cleaner", "dash cam", "seat gap filler",
        "trunk organizer", "car air freshener diffuser",
        "steering wheel cover", "car seat cushion", "phone mount magnetic",
        "car trash can", "back seat organizer",
    ],
    "kitchen_gadgets": [
        "air fryer accessories", "spice rack organizer", "vegetable chopper",
        "silicone baking mat", "egg cooker", "food scale digital",
        "can opener electric", "herb garden indoor", "ice cube tray silicone",
        "oil sprayer bottle",
    ],
}

# === Physical Product Filter ===
DIGITAL_KEYWORDS = [
    "subscription", "auto-renewal", "renewal", "monthly plan",
    "yearly plan", "annual plan", "digital download", "ebook",
    "e-book", "kindle edition", "gift card", "egift", "e-gift",
    "streaming", "membership", "warranty", "protection plan",
    "extended warranty", "service plan", "cloud storage",
    "software license", "app subscription", "prime membership",
    "audible", "kindle unlimited",
    "blink plus plan", "blink basic", "ring protect",
    "alexa together", "amazon music", "luna controller",
    "fire tv plan",
]

# === Brand Filter ===
# Major brands that are brand-gated, impossible to source cheap, or IP-protected.
# Word-boundary matching prevents false positives ("apple" won't match "pineapple").
MAJOR_BRANDS = [
    # Tech
    "apple", "samsung", "sony", "google", "amazon basics", "amazonbasics",
    "microsoft", "dell", "hp", "lenovo", "lg", "asus", "acer",
    "intel", "nvidia", "huawei", "oneplus", "oppo", "xiaomi",
    # Audio
    "bose", "jbl", "beats", "sennheiser", "harman kardon", "bang olufsen",
    "sonos", "marshall",
    # Gaming
    "nintendo", "playstation", "xbox", "razer", "steelseries", "corsair",
    "hyperx",
    # Camera/Action
    "canon", "nikon", "gopro", "dji", "fujifilm",
    # Wearables/GPS
    "garmin", "fitbit", "polar", "suunto",
    # Peripherals
    "anker", "logitech", "belkin",
    # Home appliances
    "dyson", "philips", "kitchenaid", "instant pot", "ninja", "keurig",
    "cuisinart", "whirlpool", "roomba", "irobot", "shark", "vitamix",
    "breville", "nespresso",
    # Outdoor
    "yeti", "hydro flask", "stanley", "thermos", "coleman",
    # Sports/Fashion
    "nike", "adidas", "under armour", "puma", "reebok", "new balance",
    "north face", "patagonia", "columbia",
    # Beauty/Health
    "olay", "neutrogena", "cerave", "the ordinary", "drunk elephant",
    "tatcha", "clinique", "estee lauder",
    # Pet
    "purina", "blue buffalo", "hills science", "royal canin", "iams",
    # Cleaning
    "swiffer", "clorox", "lysol", "method", "mrs meyers",
    # Baby
    "pampers", "huggies", "graco", "chicco",
    # Known brands user identified
    "owala", "dr elsey", "arm & hammer", "arm and hammer",
    "eos", "medicube",
    # Brands found leaking through winner pipeline
    "sheba", "hydrojug", "daybetter", "ksipze", "blendjet",
    "gaiatop", "valitic", "suretivian", "lhknl",
    "mrs meyer", "oxo", "lodge", "tervis", "contigo",
    "scotch brite", "dawn", "crest", "oral-b", "oral b",
    "colgate", "dove", "pantene", "head shoulders",
    "tide", "downy", "bounty", "charmin", "glad",
    "ziploc", "hefty", "rubbermaid", "tupperware",
    "black decker", "black+decker", "dewalt", "makita",
    "milwaukee", "bosch", "dremel", "craftsman",
    "ring", "blink", "eufy", "wyze", "arlo",
    "nutribullet", "magic bullet", "nutri ninja",
    "crocs", "birkenstock", "skechers", "ugg",
    # Round 2 — found leaking 2026-03-18
    "waterwipes", "rain-x", "rain x", "mcgor", "fullstar",
    "reynolds", "3m", "gorilla",
    "brita", "zero water", "zerowater", "berkey",
    "weber", "traeger", "blackstone",
    "simplehuman", "joseph joseph",
    "dr bronner", "seventh generation",
    "grove", "blueland",
    # Round 3 — branded products in BUY results
    "astroai", "cerakote", "biodance", "jeto", "tessan",
    "aquatabs", "eltamd", "bedlore",
    "ge xwfe", "ge rpwfe",
    "whirlpool", "maytag", "frigidaire", "samsung",
    "honeywell", "ecobee", "nest", "ring",
    "ruggable", "bissell", "hoover",
    "owala", "stanley", "hydro flask",
    "clorox", "lysol", "pledge", "windex",
    "zippo", "leatherman", "gerber",
    # Round 4 — more branded products caught
    "noco", "rawlings", "la roche-posay", "la roche posay",
    "lifestraw", "bella", "oster", "hamilton beach",
    "black+decker", "mr coffee", "cuisinart",
    "vitamix", "kitchenaid", "instant pot",
    "yeti", "hydro flask", "nalgene",
    "champion", "fila", "hanes", "fruit of the loom",
    "levi", "wrangler", "carhartt",
    "revlon", "maybelline", "l'oreal", "loreal", "nyx",
    "almay", "covergirl", "garnier",
    "old spice", "gillette", "schick",
    "arm & hammer", "arm and hammer",
    "energizer", "duracell",
    # Round 5 — caught from 2026-03-18 winner scan
    "zulay", "zulay kitchen", "filterbuy", "clean skin club",
    "eqqualberry", "noco", "bedlore",
]

# Compile brand regex once for performance (word boundary matching)
_BRAND_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(b) for b in MAJOR_BRANDS) + r')\b',
    re.IGNORECASE
)

# === Amazon Tracking ===
AMAZON_CATEGORIES = {
    "electronics": "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/",
    "home-kitchen": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/",
    "sports": "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/",
    "beauty": "https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/",
    "pet-supplies": "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/",
    "tools": "https://www.amazon.com/Best-Sellers-Tools/zgbs/hi/",
    "kitchen": "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/",
    "health": "https://www.amazon.com/Best-Sellers-Health/zgbs/hpc/",
    "baby": "https://www.amazon.com/Best-Sellers-Baby/zgbs/baby-products/",
    "automotive": "https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/",
}

# === Dropship price range (USD) ===
DROPSHIP_PRICE_MIN = 15.0
DROPSHIP_PRICE_MAX = 80.0
DROPSHIP_MIN_RATING = 4.0

# === AliExpress ===
ALIEXPRESS_SEARCH_URL = "https://www.aliexpress.com/wholesale"

# === Price Monitor ===
TRACKED_PRODUCTS = [
    # {"name": "Product Name", "url": "https://...", "target_price": 5.99}
]

# === Competitor Tracking ===
COMPETITOR_STORES = [
    # ── Verified Shopify stores with public /products.json API ──
    # All tested 2026-03-09, confirmed working
    "https://www.homesick.com",         # home candles/aromatics (31+ products)
    "https://gizmodern.com",            # smart gadgets & tech (250+ products)
    "https://shopneatnest.com",         # home organization (dropship competitor!)
    "https://www.ridgewallet.com",      # EDC / accessories (250+ products)
    "https://www.colourpop.com",        # beauty / cosmetics (250+ products)
    "https://www.nativecos.com",        # beauty / personal care (88+ products)
    "https://www.allbirds.com",         # eco-friendly shoes/apparel (250+ products)
    "https://www.pela.earth",           # eco-friendly phone cases (31+ products)
    "https://ugmonk.com",              # desk/office/lifestyle (180+ products)
    "https://thewoobles.com",          # crafts/hobby (250+ products)
]

# === Scraping Settings ===
REQUEST_TIMEOUT = 15
REQUEST_DELAY = 2
MAX_RETRIES = 3
BACKOFF_FACTOR = 2  # exponential: 2s, 4s, 8s

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

BOT_DETECTION_PATTERNS = [
    "pardon our interruption",
    "please verify you are a human",
    "access denied",
    "automated access",
    "robot or human",
    "captcha",
    "unusual traffic",
]

USER_AGENT = random.choice(USER_AGENTS)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def get_session(use_proxy: bool = True, max_retries: int = MAX_RETRIES) -> requests.Session:
    """
    Create a resilient requests session with:
      - Random user agent rotation
      - Automatic retries with exponential backoff
      - Proxy support
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    if use_proxy and PROXY_URL:
        session.proxies = {
            "http": PROXY_URL,
            "https": PROXY_URL,
        }
    return session


def resilient_fetch(url: str, session: requests.Session = None,
                    timeout: int = REQUEST_TIMEOUT,
                    max_retries: int = MAX_RETRIES) -> requests.Response | None:
    """
    Fetch a URL with retry logic, bot-detection checking, and error handling.
    Returns Response object or None if all attempts fail.
    """
    if session is None:
        session = get_session()

    for attempt in range(1, max_retries + 1):
        try:
            session.headers["User-Agent"] = random.choice(USER_AGENTS)
            response = session.get(url, timeout=timeout)

            if response.status_code == 429:
                wait = BACKOFF_FACTOR ** attempt + random.uniform(1, 3)
                time.sleep(wait)
                continue

            if response.status_code != 200:
                if attempt < max_retries:
                    time.sleep(BACKOFF_FACTOR ** attempt)
                    continue
                return None

            content_lower = response.text[:2000].lower()
            if any(pattern in content_lower for pattern in BOT_DETECTION_PATTERNS):
                if attempt < max_retries:
                    time.sleep(BACKOFF_FACTOR ** attempt + random.uniform(2, 5))
                    continue
                return None

            return response

        except requests.RequestException:
            if attempt < max_retries:
                time.sleep(BACKOFF_FACTOR ** attempt)
                continue
            return None

    return None


def is_physical_product(title: str) -> bool:
    """Return True if the product appears to be a physical, shippable item."""
    title_lower = title.lower()
    for kw in DIGITAL_KEYWORDS:
        if kw in title_lower:
            return False
    return True


def is_major_brand(title: str) -> bool:
    """Return True if the product is from a major brand. Uses word-boundary regex."""
    # Strip trademark symbols and special chars that break word boundaries
    cleaned = re.sub(r'[®™©]', '', title)
    return bool(_BRAND_PATTERN.search(cleaned))


def parse_price(price_str: str) -> float | None:
    """Parse price from any format: '$29.99', 'EUR 10.15', etc."""
    if not price_str:
        return None
    try:
        cleaned = re.sub(r"[€$£¥]|EUR|USD|GBP|\xa0", "", str(price_str)).strip()
        if "," in cleaned and "." not in cleaned:
            cleaned = cleaned.replace(",", ".")
        elif "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(",", "")
        match = re.search(r"[\d.]+", cleaned)
        if match:
            val = round(float(match.group()), 2)
            if 0.01 <= val <= 9999:
                return val
    except (ValueError, AttributeError):
        pass
    return None


def to_usd(price: float | None) -> float | None:
    """Identity function — VPS is in Virginia, prices are already USD."""
    return price


# === Logging ===


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(LOGS_DIR / f"{name}.log")
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
