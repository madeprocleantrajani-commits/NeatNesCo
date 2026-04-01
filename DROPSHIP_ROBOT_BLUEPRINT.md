# Seasonal Dropshipping Robot — Complete Blueprint

*AI-powered store automation: sourcing, listing, video ads, social scheduling, and seasonal intelligence*

---

## What This Robot Does

An AI-powered Python system that automatically manages a dropshipping store by:

1. **Detecting** upcoming seasons, holidays, and micro-trends 21 days ahead
2. **Sourcing** products from supplier APIs with AI quality scoring
3. **Creating** product listings, video ads, social content, and email campaigns
4. **Publishing** everything to Shopify and social media automatically
5. **Tracking** performance and learning from results for next season
6. **Archiving** expired seasonal products to keep the store fresh

The robot replaces 40+ hours of weekly manual work with a Monday morning cron job.

---

## System Architecture

```
CRON SCHEDULER (Weekly full scan + daily performance check)
  │
  ▼
CALENDAR ENGINE ──────────── TREND DETECTOR
(fixed holidays,              (Google Trends,
 regional dates,               TikTok trending,
 micro-seasons)                Amazon movers,
  │                            news events)
  └──────────┬────────────────┘
             ▼
        AI BRAIN (Claude API)
        Generates product briefs:
        themes, categories, keywords,
        price targets, urgency scores
             │
             ▼
        PRODUCT SCOUT
        Searches supplier APIs:
        CJ Dropshipping, AliExpress,
        Spocket, Zendrop
             │
             ▼
        QUALITY FILTER
        Scores products on:
        margin, shipping, reviews,
        wow factor, gift-ability,
        impulse potential
             │
             ▼
        CONTENT GENERATOR
        ├── Product listings (Claude)
        ├── Video scripts (Claude)
        ├── Video ads (Higgsfield AI)
        ├── Social content (Claude)
        └── Email campaigns (Claude)
             │
             ▼
        ┌────┴─────────────────┐
        │                      │
   STORE UPDATER          DISTRIBUTION
   (Shopify API)          ├── Social Scheduler
   • Create products      ├── Email Scheduler
   • Create collections   └── Ad Manager
   • Update navigation         (Facebook Ads)
   • Announcement bar
             │
             ▼
        PERFORMANCE TRACKER
        • Sales analytics
        • Creative performance
        • Seasonal postmortem
        • Learning loop → feeds AI Brain

```

---

## Calendar Engine — The Intelligence Layer

Not just "February = Valentine's." The robot understands context, timing, and sub-themes.

### Fixed Calendar (Global)

```python
SEASONAL_CALENDAR = {
    "valentines": {
        "source_date": "Jan 15",        # Start sourcing products
        "list_date": "Jan 25",          # Products go live on store
        "peak": "Feb 10-14",            # Highest buying intent
        "archive_date": "Feb 16",       # Remove seasonal products
        "themes": [
            "gifts for her",
            "gifts for him",
            "couples items",
            "self-love / singles",       # Anti-Valentine's sells too
            "galentines (friend gifts)",
            "pet valentines",            # Niche but high conversion
        ],
        "price_sweet_spot": "$15-45",
        "urgency_copy": "Arrives before Valentine's Day!",
    },
    "mothers_day": {
        "source_date": "Apr 1",
        "list_date": "Apr 10",
        "peak": "May 5-11",
        "archive_date": "May 13",
        "themes": [
            "personalized gifts",
            "jewelry with meaning",
            "home spa / self-care",
            "garden accessories",
            "first-time mom",
            "grandma gifts",
        ],
    },
    "fathers_day": {
        "source_date": "May 1",
        "list_date": "May 10",
        "peak": "Jun 10-15",
        "themes": ["gadgets", "grilling", "personalized", "hobby-specific"],
    },
    "back_to_school": {
        "source_date": "Jul 1",
        "list_date": "Jul 15",
        "peak": "Aug 1-25",
        "themes": ["dorm room", "organization", "tech accessories", "study tools"],
    },
    "halloween": {
        "source_date": "Aug 15",
        "list_date": "Sep 1",
        "peak": "Oct 15-31",
        "themes": ["costumes", "decorations", "party supplies", "pet costumes"],
    },
    "black_friday": {
        "source_date": "Oct 1",
        "list_date": "Nov 1",
        "peak": "Nov 25-30",
        "themes": ["doorbuster deals", "gift bundles", "stocking stuffers"],
    },
    "christmas": {
        "source_date": "Oct 1",
        "list_date": "Nov 1",
        "peak": "Dec 1-23",
        "archive_date": "Dec 26",
        "themes": ["gifts under $25", "gifts under $50", "last-minute gifts",
                   "stocking stuffers", "white elephant", "matching family"],
    },
    "new_years": {
        "source_date": "Dec 1",
        "list_date": "Dec 15",
        "peak": "Dec 28-Jan 1",
        "themes": ["party supplies", "planners", "fitness", "self-improvement"],
    },
    "summer": {
        "source_date": "Apr 15",
        "list_date": "May 1",
        "peak": "Jun-Aug",
        "themes": ["outdoor", "beach", "travel accessories", "cooling gadgets"],
    },
    "spring_cleaning": {
        "source_date": "Feb 15",
        "list_date": "Mar 1",
        "themes": ["organization", "storage", "cleaning gadgets", "minimalism"],
    },

    # MICRO-SEASONS — The edge. Most stores miss these entirely.
    "super_bowl": {
        "source_date": "Jan 10",
        "peak": "Super Bowl Sunday",
        "themes": ["party supplies", "TV snack accessories", "game day fashion"],
    },
    "tax_refund_season": {
        "source_date": "Feb 15",
        "peak": "Mar-Apr",
        "themes": ["treat yourself", "home upgrade", "gadgets"],
        "note": "People have unexpected money and want to spend it",
    },
    "wedding_season": {
        "source_date": "Mar 1",
        "peak": "May-September",
        "themes": ["bridesmaid gifts", "groomsmen gifts",
                   "wedding guest outfits", "honeymoon accessories"],
    },
    "eclipse": {"dynamic": True},  # AI detects from news
    "viral_moments": {"dynamic": True},  # AI detects from TikTok trends
}
```

### Regional Awareness

```python
REGIONAL_CALENDAR = {
    "US": {
        "thanksgiving": "4th Thursday of November",
        "memorial_day": "Last Monday of May",
        "independence_day": "July 4",
    },
    "UK": {
        "boxing_day": "Dec 26",
        "bank_holidays": ["Easter Monday", "May Day", "Spring Bank Holiday"],
    },
    "EU": {
        "singles_day": "Nov 11",  # Growing in Europe
    },
    "AU": {
        "christmas": "Summer themed! Beach Christmas products",
        "fathers_day": "First Sunday of September",  # Different from US!
    },
}
```

### Dynamic Event Detection

The AI Brain checks weekly for events no static calendar captures:

- **Google Trends**: sudden spikes (solar eclipse glasses, Stanley cups)
- **TikTok trending**: #TikTokMadeMeBuyIt products with velocity
- **News API**: upcoming events (Olympics, elections, royal events, movie releases)
- **Amazon Movers & Shakers**: category momentum shifts

---

## Product Scout — Supplier Integration

```python
class ProductScout:
    """Search multiple supplier APIs based on AI-generated product briefs."""

    def search_products(self, brief: ProductBrief) -> list[RawProduct]:
        """
        A ProductBrief contains:
          - keywords: ["LED rose", "eternal rose", "rose gold jewelry"]
          - categories: ["gifts", "jewelry", "home-decor"]
          - price_range: (5.00, 15.00)  # supplier cost, not retail
          - shipping_max_days: 14
          - exclude: ["real flowers", "perishable", "fragile glass"]
        """
        results = []

        # Search each supplier API in parallel
        results += self.search_cj_dropshipping(brief)
        results += self.search_aliexpress(brief)
        results += self.search_spocket(brief)
        results += self.search_zendrop(brief)

        # Deduplicate (same product listed on multiple platforms)
        results = self.deduplicate_by_image_hash(results)

        # AI ranks by relevance to the brief
        results = self.ai_rank_relevance(results, brief)

        return results[:50]  # Top 50 candidates per brief
```

---

## Quality Filter — The Margin Machine

```python
class QualityFilter:
    """Score and filter products. Only the best survive."""

    # Hard filters — instant reject if failed
    MIN_MARGIN = 0.40          # 40% margin after ALL costs
    MAX_SHIPPING_DAYS = 14     # 7 for urgent seasons
    MIN_SUPPLIER_RATING = 4.2
    MIN_ORDERS = 100           # Social proof on supplier side

    def calculate_true_margin(self, product: RawProduct) -> float:
        """
        Most dropshippers get margin wrong. They only compare
        supplier cost vs retail price. Include EVERYTHING:
        """
        supplier_cost = product.price
        shipping_cost = product.shipping_fee
        payment_processing = product.retail_price * 0.029 + 0.30  # Stripe fees
        platform_fee = product.retail_price * 0.02                 # Shopify tx
        ad_cost_estimate = product.retail_price * 0.15             # ~15% ROAS target
        refund_reserve = product.retail_price * 0.03               # 3% refund rate
        packaging_insert = 0.50                                     # Thank you card

        total_cost = (supplier_cost + shipping_cost + payment_processing
                     + platform_fee + ad_cost_estimate + refund_reserve
                     + packaging_insert)

        margin = (product.retail_price - total_cost) / product.retail_price
        return margin

    def ai_score_product(self, product: RawProduct, theme: str) -> dict:
        """Claude rates the product on dimensions that matter for dropshipping."""
        prompt = f"""
        Rate this product for a {theme} dropshipping store.
        Score each dimension 0-25 (total max 100):

        Product: {product.title}
        Price: ${product.price} supplier / ${product.retail_price} retail
        Images: {len(product.images)} photos
        Rating: {product.supplier_rating} stars ({product.order_count} orders)
        Shipping: {product.shipping_days} days

        Dimensions:
        1. WOW FACTOR (0-25): Would someone stop scrolling for this?
        2. GIFT-ABILITY (0-25): Easy to give as a gift? Nice unboxing?
        3. PERCEIVED VALUE (0-25): Looks more expensive than it costs?
        4. IMPULSE POTENTIAL (0-25): Would someone buy without overthinking?

        Also flag:
        - Any trademark/copyright concerns? (Disney, Nike, etc.)
        - Is this oversaturated? (everyone sells it already)
        - Is the product photo usable or does it need replacement?

        Return JSON:
        {{
          "wow": N, "gift": N, "value": N, "impulse": N, "total": N,
          "copyright_risk": true/false,
          "saturation": "low|medium|high",
          "photo_quality": "usable|needs_enhancement|unusable"
        }}
        """
        return claude_api.generate(prompt)
```

---

## Content Generator — AI Copywriting + Video Ads

### Product Listings (Claude)

```python
class ListingGenerator:
    """Generate Shopify-ready product listings."""

    def generate_listing(self, product: ScoredProduct, theme: Theme) -> Listing:
        prompt = f"""
        Create a Shopify product listing for a {theme.name} themed store.

        Product: {product.title}
        Supplier description: {product.raw_description}
        Key features: {product.features}
        Retail price: ${product.retail_price}
        Target buyer: {theme.target_demographic}

        Generate:
        1. TITLE: Catchy, SEO-friendly, max 70 chars. NO supplier Chinese-English.
        2. DESCRIPTION: 150-200 words. Lead with emotion, not specs.
           Include seasonal angle naturally.
           End with urgency ("Order by Feb 10 for Valentine's delivery!")
        3. BULLET_POINTS: 5 selling points. Emoji + benefit format.
        4. SEO_TITLE: Max 60 chars, includes main keyword
        5. SEO_DESCRIPTION: Max 155 chars, compelling summary
        6. TAGS: 5-8 tags for Shopify collections
        7. COMPARE_AT_PRICE: Suggested "was" price (ethical — based on market avg)

        TONE: Warm, premium-feeling, conversational.
        AVOID: "Buy now!!!", excessive caps, fake urgency, dropship-sounding copy.
        """
        return claude_api.generate(prompt)
```

### Video Scripts + Higgsfield Video Generation

```python
class VideoGenerator:
    """AI writes scripts, Higgsfield generates video ads."""

    def generate_video_package(self, product: ScoredProduct, theme: Theme) -> list[Video]:
        # Step 1: Claude writes 3 platform-specific scripts
        scripts = self.write_scripts(product, theme)

        # Step 2: Higgsfield generates videos from scripts
        videos = []
        for script in scripts:
            video = self.generate_video(product, script)
            videos.append(video)

        return videos

    def write_scripts(self, product: ScoredProduct, theme: Theme) -> list[VideoScript]:
        prompt = f"""
        Write 3 video ad scripts for this product.

        Product: {product.title} (${product.retail_price})
        Selling points: {product.bullet_points}
        Theme: {theme.name}
        Target audience: {theme.target_demographic}

        SCRIPT 1 — TikTok (15 seconds, 9:16 vertical)
        Structure:
          [0-2s] HOOK — stop the scroll (question, shock, or relatable pain point)
          [2-8s] REVEAL — show the product being used
          [8-12s] BENEFIT — one key reason they need it
          [12-15s] CTA — "Link in bio" or "Comment WANT"
        Include: text overlay instructions, trending audio style suggestion

        SCRIPT 2 — Instagram Reels (30 seconds, 9:16 vertical)
        Structure:
          [0-3s] SCENE — set the mood (bedroom, gift moment, lifestyle)
          [3-12s] PRODUCT — multiple angles, close-ups, tactile details
          [12-22s] LIFESTYLE — show it in real life context
          [22-28s] PROOF — "Thousands of happy customers" or review quote
          [28-30s] CTA — "Shop now, link in bio"
        Include: color mood, transition styles, music direction

        SCRIPT 3 — Facebook (30 seconds, 1:1 square, SILENT-FRIENDLY)
        Structure:
          [0-5s] TEXT: "Still looking for the perfect {theme.name} gift?"
          [5-15s] TEXT: "Meet the [product name]" + product visuals
          [15-25s] TEXT: benefit bullet points overlaid on product shots
          [25-30s] TEXT: "Only ${product.retail_price} — Free Shipping" + CTA
        Note: 80% of Facebook video is watched with sound OFF.
              Every frame must work without audio.

        Return as structured JSON with scene-by-scene breakdowns.
        """
        return claude_api.generate(prompt)

    def generate_video(self, product: ScoredProduct, script: VideoScript) -> Video:
        """Use Higgsfield API to generate video from script."""

        # Convert script scenes to Higgsfield prompt
        scene_descriptions = []
        for scene in script.scenes:
            scene_descriptions.append(
                f"[{scene.timestamp}] {scene.visual_description}. "
                f"Camera: {scene.camera_movement}. Mood: {script.overall_mood}."
            )

        higgsfield_prompt = f"""
        Create a {script.duration_seconds}-second product advertisement.
        Product: {product.title}
        Style: {script.overall_mood}
        Color palette: {script.color_palette}

        Scenes:
        {chr(10).join(scene_descriptions)}

        The product should look premium, well-lit, and desirable.
        """

        video = higgsfield_api.generate(
            prompt=higgsfield_prompt,
            aspect_ratio=script.aspect_ratio,
            duration=script.duration_seconds,
            reference_images=product.image_urls[:3],
        )

        # Post-processing
        video = self.add_text_overlays(video, script.text_overlays)
        video = self.add_logo_watermark(video)

        return video
```

### Social Media Package (Claude)

```python
class SocialGenerator:
    """Generate platform-specific social media content."""

    def generate_social_package(self, product, theme, videos) -> SocialPackage:
        prompt = f"""
        Create a complete social media package for this product launch.

        Product: {product.title} (${product.retail_price})
        Theme: {theme.name}
        Videos available: TikTok 15s, Instagram 30s, Facebook 30s

        TIKTOK:
        - Caption (max 150 chars with hook)
        - 15 hashtags (mix: 5 trending + 5 niche + 5 branded)
        - Comment bait question to drive engagement
        - Reply template for "Where can I buy?" comments

        INSTAGRAM:
        - Caption (storytelling format with line breaks)
        - 30 hashtags (10 broad + 10 niche + 10 community)
        - Story sequence: 3-5 frames (teaser → reveal → swipe up)

        FACEBOOK:
        - Ad copy (primary text, headline, description)
        - Organic post copy (more personal tone)
        - Target audience suggestion (interests, age, behaviors)

        PINTEREST:
        - Pin title (SEO keyword-rich)
        - Pin description (500 chars, keyword-rich)
        - Board name suggestion
        """
        return claude_api.generate(prompt)
```

### Email Campaign (Claude)

```python
class EmailGenerator:
    """Generate 3-email seasonal launch sequence."""

    def generate_email_sequence(self, product, theme) -> list[Email]:
        prompt = f"""
        Create a 3-email launch sequence for this seasonal product.

        Product: {product.title} (${product.retail_price})
        Theme: {theme.name} (peak: {theme.peak})

        EMAIL 1 — TEASER (send 14 days before peak)
        Subject: 5 A/B variants
        Body: Short, curiosity. "Something special is coming..."
        CTA: "Get early access"

        EMAIL 2 — LAUNCH (send 10 days before peak)
        Subject: 5 A/B variants
        Body: Full reveal. Hero image. Benefits. Price.
        CTA: "Shop now — ships in time"
        Optional: Early bird 10% off code

        EMAIL 3 — LAST CHANCE (send 3 days before peak)
        Subject: 5 A/B variants (urgency)
        Body: "Last chance for {theme.name} delivery"
        CTA: "Order by [date] for guaranteed delivery"

        Return structured JSON with HTML body, plain text, and metadata.
        """
        return claude_api.generate(prompt)
```

---

## Store Updater — Shopify API

```python
class ShopifyUpdater:
    """Push everything to Shopify via Admin API."""

    def launch_seasonal_collection(self, theme: Theme, products: list[Listing]):
        """Full seasonal launch in one method."""

        # 1. Create themed collection
        collection_id = self.create_collection(
            title=f"{theme.name} {theme.year}",
            description=theme.collection_description,
            image=theme.banner_image_url,
        )

        # 2. Publish each product
        for listing in products:
            product_id = self.create_product(listing)
            self.add_to_collection(product_id, collection_id)

        # 3. Update store navigation
        self.add_to_navigation(collection_id, theme.nav_label)

        # 4. Update announcement bar
        self.update_announcement(
            f"{theme.announcement_emoji} {theme.name} Collection is Live! "
            f"Free Shipping on orders over $35 {theme.announcement_emoji}"
        )

    def archive_season(self, theme: Theme):
        """After the season ends, clean up automatically."""
        # Set all products in collection to draft (not delete — save for next year)
        products = self.get_collection_products(theme.collection_id)
        for product in products:
            self.set_product_status(product.id, "draft")

        # Remove collection from navigation
        self.remove_from_navigation(theme.collection_id)

        # Reset announcement bar
        self.update_announcement("")

        # Log for next year
        self.save_archived_products(theme, products)
```

---

## Social Scheduler — Automated Posting

```python
class SocialScheduler:
    """Schedule the full launch sequence across all platforms."""

    def schedule_launch(self, product, creative, theme):
        peak = theme.peak_date

        # PHASE 1: TEASER (14 days before)
        self.schedule(platform="instagram", type="story",
                     content=creative.teaser, date=peak - days(14))
        self.schedule(platform="tiktok", type="video",
                     content=creative.tiktok_teaser, date=peak - days(14))

        # PHASE 2: LAUNCH (10 days before)
        self.schedule(platform="tiktok", type="video",
                     content=creative.tiktok_video, date=peak - days(10))
        self.schedule(platform="instagram", type="reel",
                     content=creative.instagram_video, date=peak - days(10))
        self.schedule(platform="facebook", type="video",
                     content=creative.facebook_video, date=peak - days(10))
        self.schedule(platform="pinterest", type="pin",
                     content=creative.pinterest_pin, date=peak - days(10))

        # PHASE 3: SOCIAL PROOF (7 days before)
        self.schedule(platform="tiktok", type="video",
                     content=creative.social_proof_video, date=peak - days(7))

        # PHASE 4: URGENCY (3 days before)
        self.schedule(platform="all", type="story",
                     content=creative.urgency_content, date=peak - days(3))

        # PHASE 5: DAY-OF (peak date)
        self.schedule(platform="instagram", type="story",
                     content=creative.peak_day_content, date=peak)

        # Email sequence
        self.email_scheduler.schedule(creative.emails, peak)
```

---

## Performance Tracker — The Learning Loop

```python
class PerformanceTracker:
    """Track everything. Learn from everything. Feed back to AI Brain."""

    def daily_report(self):
        """Pull all analytics and generate AI-powered insights."""

        metrics = {
            "store": self.shopify_analytics(),        # Revenue, conversion, AOV
            "social": {
                "tiktok": self.tiktok_analytics(),    # Views, likes, shares
                "instagram": self.instagram_analytics(), # Reach, saves, shares
                "facebook": self.facebook_ad_analytics(), # CTR, CPC, ROAS
                "pinterest": self.pinterest_analytics(),  # Impressions, saves
            },
            "email": self.email_analytics(),          # Opens, clicks, revenue
            "per_product": self.product_analytics(),  # Per-product breakdown
        }

        # AI generates actionable insights
        insights = claude_api.generate(f"""
        Analyze this dropshipping performance data: {json.dumps(metrics)}

        Answer:
        1. Which 3 products should get more ad spend? Why?
        2. Which 3 products should be removed? Why?
        3. Which platform drives the most revenue per effort?
        4. Which video format (15s vs 30s) converts better?
        5. Which hook type gets highest CTR?
        6. What should we do differently tomorrow?
        """)

        return insights

    def seasonal_postmortem(self, theme: Theme):
        """End-of-season learning report. Stored for next year."""

        report = claude_api.generate(f"""
        Seasonal postmortem for {theme.name} {theme.year}:

        Products listed: {theme.products_listed}
        Revenue: ${theme.revenue}
        Ad spend: ${theme.ad_spend}
        ROAS: {theme.roas}
        Top products: {theme.top_3}
        Bottom products: {theme.bottom_3}

        Write a postmortem covering:
        1. What worked and why
        2. What failed and why
        3. Did we start sourcing early enough?
        4. What price point converted best?
        5. What creative format won?
        6. Specific recommendations for {theme.name} NEXT YEAR
        7. Products to pre-source for next year
        """)

        # Save for retrieval next year
        self.save_learning(theme.name, theme.year, report)
```

---

## Cron Schedule

```python
SCHEDULE = {
    "weekly_full_scan": {
        "cron": "0 9 * * MON",           # Monday 9 AM
        "action": "Full seasonal scan, source products, generate content, publish",
    },
    "daily_trend_check": {
        "cron": "0 10 * * *",            # Daily 10 AM
        "action": "Google Trends + TikTok trending. Alert on sudden spikes.",
    },
    "daily_performance": {
        "cron": "0 8 * * *",             # Daily 8 AM
        "action": "Pull analytics, generate daily report, auto-adjust ads.",
    },
    "daily_archive_check": {
        "cron": "0 6 * * *",             # Daily 6 AM
        "action": "Check if any seasonal collections need archiving.",
    },
    "weekly_email_sequence": {
        "cron": "0 11 * * TUE",          # Tuesday 11 AM
        "action": "Trigger next email in any active launch sequences.",
    },
}
```

---

## File Structure

```
dropship-robot/
├── main.py                      # Entry point, cron dispatcher
├── config.py                    # API keys, store config, thresholds
├── requirements.txt             # Python dependencies
│
├── intelligence/
│   ├── calendar_engine.py       # Seasonal calendar + dynamic events
│   ├── trend_detector.py        # Google Trends, TikTok, Amazon APIs
│   └── ai_brain.py              # Claude API wrapper for all AI decisions
│
├── sourcing/
│   ├── product_scout.py         # Multi-supplier search orchestrator
│   ├── quality_filter.py        # Margin calc, AI scoring, filtering
│   └── suppliers/
│       ├── cj_dropshipping.py   # CJ Dropshipping API client
│       ├── aliexpress.py        # AliExpress API client
│       ├── spocket.py           # Spocket API client
│       └── zendrop.py           # Zendrop API client
│
├── content/
│   ├── listing_generator.py     # Product title, description, SEO
│   ├── video_generator.py       # Higgsfield API video creation
│   ├── script_writer.py         # Claude writes video scripts
│   ├── social_generator.py      # Platform-specific social content
│   └── email_generator.py       # Email campaign sequences
│
├── distribution/
│   ├── store_updater.py         # Shopify Admin API integration
│   ├── social_scheduler.py      # Buffer/Later API for post scheduling
│   ├── email_scheduler.py       # Klaviyo/Mailchimp API
│   └── ad_manager.py            # Facebook Ads API for paid campaigns
│
├── analytics/
│   ├── performance_tracker.py   # Sales, conversion, creative metrics
│   ├── creative_analyzer.py     # Which video/hook/platform converts
│   └── seasonal_postmortem.py   # End-of-season learning reports
│
├── data/
│   ├── seasonal_calendar.json   # Fixed holiday calendar
│   ├── regional_calendar.json   # Regional date variations
│   ├── product_history.jsonl    # Every product ever listed
│   ├── seasonal_learnings.json  # Postmortem insights per season
│   ├── creative_performance.jsonl # Which creative converts best
│   ├── trend_cache.json         # Cached trend detection data
│   └── supplier_ratings.json    # Track supplier reliability over time
│
└── templates/
    ├── prompts/
    │   ├── product_listing.txt  # Claude prompt template for listings
    │   ├── video_script.txt     # Claude prompt template for scripts
    │   ├── social_package.txt   # Claude prompt template for social
    │   ├── email_sequence.txt   # Claude prompt template for emails
    │   ├── quality_score.txt    # Claude prompt template for scoring
    │   └── postmortem.txt       # Claude prompt template for review
    └── email_html/
        ├── teaser.html          # Email HTML template — teaser
        ├── launch.html          # Email HTML template — launch
        └── urgency.html         # Email HTML template — last chance
```

---

## API Keys Required

```bash
# AI Intelligence
ANTHROPIC_API_KEY=               # Claude API — the brain
HIGGSFIELD_API_KEY=              # Video ad generation

# Store Platform
SHOPIFY_API_KEY=                 # Shopify Admin API
SHOPIFY_API_SECRET=              # Shopify Admin API
SHOPIFY_STORE_URL=               # yourstore.myshopify.com

# Suppliers
CJ_API_KEY=                      # CJ Dropshipping
ALIEXPRESS_APP_KEY=              # AliExpress
SPOCKET_API_KEY=                 # Spocket
ZENDROP_API_KEY=                 # Zendrop

# Trends & Data
SERPAPI_KEY=                      # Google Trends via SerpAPI
NEWS_API_KEY=                    # NewsAPI for event detection

# Distribution
BUFFER_API_KEY=                  # Social media scheduling
KLAVIYO_API_KEY=                 # Email marketing
FACEBOOK_ADS_TOKEN=              # Paid ad management
TIKTOK_ADS_TOKEN=                # TikTok ad management (optional)

# Optional Enhancements
CANVA_API_KEY=                   # Static image enhancement
CLOUDINARY_API_KEY=              # Image CDN and optimization
```

---

## The Complete Robot Cycle — One Week Example

```
MONDAY 9 AM — WEEKLY SCAN
│
├── Calendar Engine checks: "Valentine's Day in 18 days. SOURCE NOW."
│
├── Trend Detector: "LED rose lamps +340% on TikTok this week"
│
├── AI Brain generates 5 product briefs:
│   1. LED Rose Lamp (primary — trending)
│   2. Personalized Name Necklace (proven seller)
│   3. Couple Matching Pajamas (seasonal)
│   4. Self-Care Spa Gift Set (singles angle)
│   5. Pet Valentine's Bandana (niche, high conversion)
│
├── Product Scout: Searches 4 supplier APIs → 200 raw candidates
│
├── Quality Filter: Scores all 200 → passes 15 (40%+ margin, <14 day ship)
│
├── Content Generator creates PER PRODUCT:
│   • Shopify listing (title, description, SEO, bullet points)
│   • 3 video scripts (TikTok, Instagram, Facebook)
│   • 3 AI-generated video ads via Higgsfield
│   • Social media package (captions, hashtags, targeting)
│   • 3-email campaign sequence
│
├── Store Updater:
│   • Creates "Valentine's Day 2026" collection on Shopify
│   • Publishes 15 products with AI content
│   • Updates announcement bar: "Valentine's Collection Now Live!"
│   • Adds collection to store navigation
│
├── Social Scheduler:
│   • Queues 4-phase launch across TikTok, IG, FB, Pinterest
│   • Spaces posts for optimal engagement times
│
├── Email Scheduler:
│   • Queues 3-email sequence in Klaviyo
│   • Email 1 (teaser) sends today
│   • Email 2 (launch) sends in 4 days
│   • Email 3 (urgency) sends in 11 days
│
└── Ad Manager:
    • Creates Facebook ad campaigns with video creative
    • Creates TikTok ad campaigns
    • Sets AI-recommended targeting
    • Budget: starts at $20/day, auto-scales winners

DAILY 8 AM — PERFORMANCE CHECK
│
├── Pulls yesterday's Shopify sales data
├── Pulls social media engagement metrics
├── Pulls ad performance (CTR, CPC, ROAS)
├── AI generates daily insight report
├── Auto-pauses underperforming ads (ROAS < 1.5x)
├── Auto-increases budget on winners (ROAS > 3x)
└── Alerts store owner if manual action needed

FEB 16 — POST-SEASON CLEANUP
│
├── Sets all Valentine's products to draft
├── Removes collection from navigation
├── Resets announcement bar
├── Generates seasonal postmortem report
├── Saves learnings: "LED roses outsold jewelry 3:1, price sweet spot $18-25"
└── Calendar Engine: "Next up: Mother's Day. Start sourcing Apr 1."
```

---

## What Makes This Robot Better Than Manual Dropshipping

| Manual Store Owner | Robot |
|---|---|
| Reacts to seasons last minute | Plans 21 days ahead |
| Sources 5-10 products by browsing | Scans 200+ across 4 suppliers |
| Calculates margin as cost vs price | Includes ads, refunds, processing, packaging |
| Uses supplier photos as-is | Generates video ads + enhanced listings |
| Posts manually on social media | 4-phase launch sequence auto-scheduled |
| Sends one email blast | 3-email nurture sequence with A/B testing |
| Forgets to remove old products | Auto-archives day after season ends |
| Repeats same mistakes next year | Seasonal postmortem + stored learnings |
| Spends 40+ hours/week on store | Runs on Monday morning cron job |

---

## Getting Started

1. Clone the repo
2. `pip install -r requirements.txt`
3. Fill in API keys in `config.py`
4. Run `python main.py --scan` for your first seasonal scan
5. Review AI recommendations before publishing
6. Enable cron schedule once comfortable

Start with ONE season (the nearest one). Let the robot source, score, and generate content. Review manually. Approve. Publish. Track. Learn. Then automate.

---

*Built with Claude API + Higgsfield AI + Shopify Admin API*
*The store that runs itself.*
