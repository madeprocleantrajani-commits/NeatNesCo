export const getGlobalStyles = () => `
  /* ─── NeatNesCo Cinematic Design System ─────────────────────────────── */
  :root {
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f7;
    --bg-dark: #0a0a0a;
    --bg-dark-card: #141414;
    --bg-card: #ffffff;
    --bg-elevated: rgba(255,255,255,0.92);
    --text-primary: #1d1d1f;
    --text-secondary: #6e6e73;
    --text-tertiary: #86868b;
    --text-muted: #aeaeb2;
    --text-light: #f5f5f7;
    --border-subtle: rgba(0,0,0,0.06);
    --border-hover: rgba(0,0,0,0.12);
    --border-light: rgba(255,255,255,0.08);
    --accent: #1d1d1f;
    --accent-blue: #0071e3;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
    --shadow-lg: 0 12px 40px rgba(0,0,0,0.08);
    --shadow-glow: 0 0 60px rgba(255,255,255,0.05);
  }

  * { box-sizing: border-box; }

  body {
    background: #ffffff !important;
    color: #1d1d1f !important;
    transition: none;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* ─── Aurora / Mesh Animations ──────────────────────────────────────── */
  @keyframes meshRotate {
    0% { transform: rotate(0deg) scale(1); }
    50% { transform: rotate(180deg) scale(1.1); }
    100% { transform: rotate(360deg) scale(1); }
  }
  @keyframes auroraShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  @keyframes glowPulse {
    0%, 100% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
  }
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  /* ─── Gradient Text ─────────────────────────────────────────────────── */
  .gradient-text {
    background: linear-gradient(135deg, #1d1d1f 0%, #6e6e73 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .gradient-text-light {
    background: linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.6) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .shimmer-text {
    color: #1d1d1f;
    -webkit-text-fill-color: #1d1d1f;
  }

  /* ─── Scroll Indicator ──────────────────────────────────────────────── */
  .scroll-dot {
    animation: scrollBounce 2s ease-in-out infinite;
  }
  @keyframes scrollBounce {
    0%, 100% { transform: translateY(0); opacity: 1; }
    50% { transform: translateY(10px); opacity: 0; }
  }

  /* ─── Card Spotlight Effect ─────────────────────────────────────────── */
  .card-spotlight {
    background: radial-gradient(
      400px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
      rgba(0,0,0,0.02), transparent 60%
    );
  }

  /* ─── Glass Card ────────────────────────────────────────────────────── */
  .glass-card {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  }
  .glass-card:hover {
    border-color: rgba(0,0,0,0.1);
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    transform: translateY(-2px);
  }

  /* ─── Dark Glass Card ──────────────────────────────────────────────── */
  .glass-card-dark {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(20px);
    transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s;
  }
  .glass-card-dark:hover {
    border-color: rgba(255,255,255,0.12);
    box-shadow: 0 8px 30px rgba(255,255,255,0.04);
    transform: translateY(-2px);
  }

  /* ─── Bento Card ────────────────────────────────────────────────────── */
  .bento-card {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .bento-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    padding: 1px;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    -webkit-mask-composite: xor;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .bento-card:hover::before {
    opacity: 1;
  }
  .bento-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  }

  /* ─── Noise Texture — removed for Apple clean ─────────────────────── */
  .noise-overlay::after { display: none; }

  /* ─── Hero CTA ────────────────────────────────────────────────────── */
  .hero-cta-primary {
    position: relative;
    overflow: hidden;
  }
  .hero-cta-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3) !important;
  }
  .hero-cta-secondary:hover {
    background: rgba(255,255,255,0.1) !important;
    transform: translateY(-1px);
  }

  /* ─── Nav Link Hover ────────────────────────────────────────────────── */
  .nav-link {
    position: relative;
  }
  .nav-link::after {
    content: '';
    position: absolute; bottom: -4px; left: 0; right: 0;
    height: 1.5px;
    background: #1d1d1f;
    border-radius: 1px;
    transform: scaleX(0); transition: transform 0.3s;
    transform-origin: center;
  }
  .nav-link:hover::after { transform: scaleX(1); }
  .nav-link:hover { color: #1d1d1f !important; }

  /* ─── Subscribe Button ──────────────────────────────────────────────── */
  .subscribe-btn:hover {
    opacity: 0.85 !important;
    transform: translateY(-1px);
  }

  /* ─── Marquee Carousel ──────────────────────────────────────────────── */
  .marquee-container {
    overflow: hidden;
    mask-image: linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent);
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent);
  }
  .marquee-track {
    display: flex; gap: 1.5rem;
    animation: marquee 60s linear infinite;
    width: max-content;
  }
  .marquee-track:hover { animation-play-state: paused; }
  .marquee-track-reverse {
    display: flex; gap: 1.5rem;
    animation: marqueeReverse 50s linear infinite;
    width: max-content;
  }
  .marquee-track-reverse:hover { animation-play-state: paused; }
  @keyframes marquee {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
  }
  @keyframes marqueeReverse {
    from { transform: translateX(-50%); }
    to { transform: translateX(0); }
  }

  /* ─── Brands Marquee ────────────────────────────────────────────────── */
  .brands-track {
    display: flex; gap: 4rem; align-items: center;
    animation: marquee 30s linear infinite;
    width: max-content;
  }

  /* ─── Toast Animation ───────────────────────────────────────────────── */
  @keyframes toastSlideIn {
    from { transform: translateX(120%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes toastSlideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(120%); opacity: 0; }
  }

  /* ─── Social Proof Popup ────────────────────────────────────────────── */
  @keyframes socialProofIn {
    from { transform: translateY(120%) scale(0.8); opacity: 0; }
    to { transform: translateY(0) scale(1); opacity: 1; }
  }
  @keyframes socialProofOut {
    from { transform: translateY(0) scale(1); opacity: 1; }
    to { transform: translateY(120%) scale(0.8); opacity: 0; }
  }

  /* ─── Splash Screen ────────────────────────────────────────────────── */
  @keyframes splashLogo {
    0% { transform: scale(0.8); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
  }
  @keyframes splashLine {
    0% { width: 0; }
    100% { width: 120px; }
  }
  @keyframes splashText {
    0% { opacity: 0; transform: translateY(8px); }
    100% { opacity: 1; transform: translateY(0); }
  }

  /* ─── Back to Top ───────────────────────────────────────────────────── */
  @keyframes floatUp {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
  }

  /* ─── Fade Animations ───────────────────────────────────────────────── */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ─── Accordion ─────────────────────────────────────────────────────── */
  .faq-answer {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .faq-answer.open {
    grid-template-rows: 1fr;
  }
  .faq-answer-inner {
    overflow: hidden;
  }

  /* ─── Product Card ────────────────────────────────────────────────── */
  .product-card {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
  }
  .product-card:hover {
    border-color: rgba(0,0,0,0.1) !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.12) !important;
    transform: translateY(-8px) !important;
  }

  /* ─── Star Rating ───────────────────────────────────────────────────── */
  .star-rating {
    color: #ff9500;
  }

  /* ─── Wishlist Heart ────────────────────────────────────────────────── */
  @keyframes heartBeat {
    0% { transform: scale(1); }
    25% { transform: scale(1.3); }
    50% { transform: scale(1); }
    75% { transform: scale(1.15); }
    100% { transform: scale(1); }
  }

  /* ─── Modal ─────────────────────────────────────────────────── */
  @keyframes modalOverlayIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  @keyframes modalContentIn {
    from { opacity: 0; transform: scale(0.95) translateY(10px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
  }

  @keyframes stickyBarIn {
    from { opacity: 0; transform: translateY(100%); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ─── Section Divider ───────────────────────────────────────────────── */
  .section-divider {
    height: 1px;
    background: rgba(0,0,0,0.06);
    margin: 0 auto;
    max-width: 80%;
  }

  /* ─── Section Tag ────────────────────────────────────────────────────── */
  .section-tag {
    display: inline-block;
    color: #86868b;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
  }

  /* ─── Countdown ────────────────────────────────────────────────────── */
  .countdown-digit {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 44px;
    height: 44px;
    background: rgba(255,255,255,0.2);
    border-radius: 8px;
    font-size: 1.2rem;
    font-weight: 700;
    font-family: 'Inter', monospace;
    color: #fff;
  }

  /* ─── Shiny Button ──────────────────────────────────────────────────── */
  .shiny-btn {
    position: relative;
    overflow: hidden;
  }
  .shiny-btn::after {
    content: '';
    position: absolute;
    top: 0; left: -100%; width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    animation: shimmer 3s ease-in-out infinite;
  }

  /* ─── Responsive ────────────────────────────────────────────────────── */
  @media (max-width: 420px) {
    .products-grid { grid-template-columns: 1fr !important; }
  }
  @media (min-width: 421px) and (max-width: 768px) {
    .products-grid { grid-template-columns: repeat(2, 1fr) !important; }
  }
  @media (max-width: 768px) {
    .nav-links-desktop { display: none !important; }
    .mobile-menu-btn { display: flex !important; flex-direction: row; align-items: center; gap: 0.5rem; }
    .features-grid { grid-template-columns: 1fr !important; }
    .features-grid > * { grid-column: span 1 !important; }
    .faq-container { padding: 0 !important; }
    .story-timeline { padding-left: 1.5rem !important; }
    .countdown-digit { min-width: 36px; height: 36px; font-size: 1rem; }
    .bento-grid { grid-template-columns: 1fr !important; }
    .bento-grid > * { grid-column: span 1 !important; }
    .hero-products-showcase { flex-direction: column !important; align-items: center !important; }
    .hero-products-showcase > * { width: 100% !important; max-width: 280px !important; }
    .hero-stats-bar { flex-wrap: wrap !important; gap: 0.8rem !important; padding: 1rem !important; }
    .hero-stats-bar > div { flex: 1 1 40% !important; }
    .quick-add-btn { opacity: 1 !important; transform: scale(1) !important; }
    .quickview-grid { grid-template-columns: 1fr !important; }
    .quickview-image { min-height: 260px !important; border-radius: 20px 20px 0 0 !important; }
    .category-strip { -webkit-overflow-scrolling: touch; }
  }
  @media (min-width: 769px) {
    .mobile-menu-btn { display: none !important; }
  }

  /* ─── Micro-interactions ─────────────────────────────────────── */
  button:active, a.hero-cta-primary:active, .subscribe-btn:active {
    transform: scale(0.97) !important;
    transition: transform 0.1s !important;
  }
  .product-card {
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  .product-card:hover {
    box-shadow: 0 12px 40px rgba(0,0,0,0.1);
  }
  .cart-item {
    transition: background 0.2s ease;
    border-radius: 12px;
  }
  .cart-item:hover {
    background: #f5f5f7 !important;
  }

  /* ─── Scrollbar ──────────────────────────────────────────────── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb {
    background: rgba(0,0,0,0.15);
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(0,0,0,0.3);
  }

  /* ─── Selection ─────────────────────────────────────────────────────── */
  ::selection {
    background: rgba(0,113,227,0.15);
    color: #1d1d1f;
  }

  /* ─── Reduced Motion ────────────────────────────────────────────────── */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }

  /* ─── Pulse Dot ───────────────────────────────────────────────────── */
  .pulse-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #34c759; display: inline-block;
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
  }
`
