export const getGlobalStyles = (darkMode) => `
  /* ─── CSS Variables / Design Tokens ─────────────────────────────────── */
  :root {
    --bg-primary: ${darkMode ? '#0a0a0a' : '#fafaf8'};
    --bg-secondary: ${darkMode ? '#111111' : '#f0ede6'};
    --bg-card: ${darkMode ? '#161616' : '#ffffff'};
    --bg-card-hover: ${darkMode ? '#1a1a1a' : '#ffffff'};
    --bg-elevated: ${darkMode ? 'rgba(22,22,22,0.9)' : 'rgba(250,250,248,0.88)'};
    --text-primary: ${darkMode ? '#f0f0f0' : '#1a1a1a'};
    --text-secondary: ${darkMode ? '#888' : '#777'};
    --text-tertiary: ${darkMode ? '#555' : '#999'};
    --text-muted: ${darkMode ? '#444' : '#bbb'};
    --border-subtle: ${darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'};
    --border-hover: ${darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)'};
    --green-primary: #2d6a4f;
    --green-secondary: #40916c;
    --green-glow: ${darkMode ? 'rgba(45,106,79,0.3)' : 'rgba(45,106,79,0.15)'};
    --shadow-sm: ${darkMode ? '0 2px 12px rgba(0,0,0,0.3)' : '0 2px 12px rgba(0,0,0,0.03)'};
    --shadow-md: ${darkMode ? '0 8px 32px rgba(0,0,0,0.4)' : '0 8px 32px rgba(0,0,0,0.06)'};
    --shadow-lg: ${darkMode ? '0 24px 64px rgba(0,0,0,0.5)' : '0 24px 64px rgba(0,0,0,0.12)'};
    --shadow-glow: ${darkMode ? '0 0 40px rgba(45,106,79,0.2)' : '0 0 40px rgba(45,106,79,0.1)'};
    --noise: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  }

  body {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    transition: background 0.5s ease, color 0.5s ease;
  }

  /* ─── Shimmer Headline ──────────────────────────────────────────────── */
  .shimmer-text {
    background: linear-gradient(
      110deg,
      var(--text-primary) 20%,
      #2d6a4f 40%,
      #52b788 50%,
      #2d6a4f 60%,
      var(--text-primary) 80%
    );
    background-size: 300% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 6s ease-in-out infinite;
  }
  @keyframes shimmer {
    0% { background-position: 200% center; }
    100% { background-position: -200% center; }
  }

  /* ─── Gradient Text ─────────────────────────────────────────────────── */
  .gradient-text {
    background: linear-gradient(135deg, #2d6a4f, #52b788, #40916c);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  /* ─── Pulsing Dot ───────────────────────────────────────────────────── */
  .pulse-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #2d6a4f; display: inline-block;
    animation: pulse 2s ease-in-out infinite;
    box-shadow: 0 0 12px rgba(45,106,79,0.4);
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 12px rgba(45,106,79,0.4); }
    50% { opacity: 0.4; transform: scale(0.8); box-shadow: 0 0 4px rgba(45,106,79,0.1); }
  }

  /* ─── Scroll Indicator ──────────────────────────────────────────────── */
  .scroll-dot {
    animation: scrollBounce 2s ease-in-out infinite;
  }
  @keyframes scrollBounce {
    0%, 100% { transform: translateY(0); opacity: 1; }
    50% { transform: translateY(10px); opacity: 0; }
  }

  /* ─── Decorative Blobs ──────────────────────────────────────────────── */
  .blob {
    position: absolute; border-radius: 50%;
    filter: blur(80px); opacity: ${darkMode ? '0.08' : '0.15'}; pointer-events: none;
  }
  .blob-1 {
    width: 600px; height: 600px; top: -150px; right: -150px;
    background: linear-gradient(135deg, #2d6a4f, #52b788);
    animation: blobFloat 20s ease-in-out infinite;
  }
  .blob-2 {
    width: 500px; height: 500px; bottom: -100px; left: -150px;
    background: linear-gradient(135deg, #457b9d, #1d3557);
    animation: blobFloat 25s ease-in-out infinite reverse;
  }
  .blob-3 {
    width: 350px; height: 350px; top: 40%; left: 60%;
    background: linear-gradient(135deg, #e76f51, #f4a261);
    animation: blobFloat 30s ease-in-out infinite;
  }
  @keyframes blobFloat {
    0%, 100% { transform: translate(0, 0) scale(1) rotate(0deg); }
    25% { transform: translate(30px, -40px) scale(1.1) rotate(5deg); }
    50% { transform: translate(-20px, 20px) scale(0.9) rotate(-3deg); }
    75% { transform: translate(15px, 30px) scale(1.05) rotate(2deg); }
  }

  /* ─── Card Spotlight Effect ─────────────────────────────────────────── */
  .card-spotlight {
    background: radial-gradient(
      400px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
      rgba(45, 106, 79, 0.12), transparent 60%
    );
  }

  /* ─── Animated Gradient Border ──────────────────────────────────────── */
  .gradient-border {
    position: relative;
    background: var(--bg-card);
    border-radius: 24px;
  }
  .gradient-border::before {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 25px;
    background: linear-gradient(
      var(--border-angle, 0deg),
      transparent 40%,
      rgba(45,106,79,0.5) 50%,
      transparent 60%
    );
    z-index: -1;
    animation: borderRotate 4s linear infinite;
  }
  @keyframes borderRotate {
    from { --border-angle: 0deg; }
    to { --border-angle: 360deg; }
  }
  @property --border-angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
  }

  /* ─── Shiny Button ──────────────────────────────────────────────────── */
  .shiny-btn {
    position: relative;
    overflow: hidden;
  }
  .shiny-btn::after {
    content: '';
    position: absolute; inset: 0;
    background: conic-gradient(
      from var(--shiny-angle, 0deg),
      transparent 0%, rgba(255,255,255,0.15) 5%, transparent 15%
    );
    animation: shinyRotate 3s linear infinite;
    border-radius: inherit;
  }
  @keyframes shinyRotate {
    from { --shiny-angle: 0deg; }
    to { --shiny-angle: 360deg; }
  }
  @property --shiny-angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
  }

  /* ─── Glass Card ────────────────────────────────────────────────────── */
  .glass-card {
    background: ${darkMode ? 'rgba(22,22,22,0.6)' : 'rgba(255,255,255,0.6)'};
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
    border: 1px solid ${darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.8)'};
    box-shadow: ${darkMode
      ? '0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)'
      : '0 8px 32px rgba(0,0,0,0.04), inset 0 1px 0 rgba(255,255,255,0.8)'};
  }

  /* ─── Noise Texture Overlay ─────────────────────────────────────────── */
  .noise-overlay::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: var(--noise);
    background-repeat: repeat;
    opacity: ${darkMode ? '0.03' : '0.02'};
    pointer-events: none;
    border-radius: inherit;
  }

  /* ─── Hero CTA Hover ────────────────────────────────────────────────── */
  .hero-cta-primary {
    position: relative;
    overflow: hidden;
  }
  .hero-cta-primary::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #2d6a4f, #52b788);
    opacity: 0;
    transition: opacity 0.4s;
  }
  .hero-cta-primary:hover::before { opacity: 1; }
  .hero-cta-primary:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(45,106,79,0.4) !important;
  }
  .hero-cta-secondary:hover {
    border-color: #2d6a4f !important;
    color: #2d6a4f !important;
    background: rgba(45,106,79,0.04) !important;
    transform: translateY(-2px);
  }

  /* ─── Nav Link Hover ────────────────────────────────────────────────── */
  .nav-link {
    position: relative;
  }
  .nav-link::after {
    content: '';
    position: absolute; bottom: -4px; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #2d6a4f, #52b788);
    border-radius: 1px;
    transform: scaleX(0); transition: transform 0.3s;
    transform-origin: center;
  }
  .nav-link:hover::after { transform: scaleX(1); }
  .nav-link:hover { color: #2d6a4f !important; }

  /* ─── Subscribe Button ──────────────────────────────────────────────── */
  .subscribe-btn:hover {
    background: #40916c !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(45,106,79,0.4);
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
  @keyframes splashFade {
    0% { opacity: 1; }
    80% { opacity: 1; }
    100% { opacity: 0; pointer-events: none; }
  }
  @keyframes splashLogo {
    0% { transform: scale(0.5) rotate(-10deg); opacity: 0; }
    40% { transform: scale(1.1) rotate(2deg); opacity: 1; }
    60% { transform: scale(1) rotate(0deg); opacity: 1; }
    100% { transform: scale(1) rotate(0deg); opacity: 1; }
  }
  @keyframes splashLine {
    0% { width: 0; }
    60% { width: 120px; }
    100% { width: 120px; }
  }
  @keyframes splashText {
    0%, 30% { opacity: 0; transform: translateY(10px); }
    60% { opacity: 1; transform: translateY(0); }
    100% { opacity: 1; transform: translateY(0); }
  }

  /* ─── Back to Top ───────────────────────────────────────────────────── */
  @keyframes floatUp {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
  }

  /* ─── Fade Animations ───────────────────────────────────────────────── */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
  }
  @keyframes fadeInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
  }
  @keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
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

  /* ─── Countdown Flip ────────────────────────────────────────────────── */
  .countdown-digit {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 52px;
    height: 52px;
    background: ${darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)'};
    border-radius: 12px;
    font-size: 1.4rem;
    font-weight: 800;
    font-family: 'Inter', monospace;
    color: var(--text-primary);
    position: relative;
    overflow: hidden;
  }
  .countdown-digit::after {
    content: '';
    position: absolute;
    left: 0; right: 0;
    height: 1px;
    top: 50%;
    background: ${darkMode ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'};
  }

  /* ─── Product Card Hover ────────────────────────────────────────────── */
  .product-card {
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
  }
  .product-card:hover {
    border-color: var(--border-hover) !important;
  }

  /* ─── Responsive ────────────────────────────────────────────────────── */
  @media (max-width: 768px) {
    .nav-links-desktop { display: none !important; }
    .mobile-menu-btn { display: flex !important; flex-direction: column; gap: 0; }
    .blob { display: none; }
    .hero-stats { gap: 1.5rem !important; }
    .features-grid { grid-template-columns: 1fr !important; }
    .faq-container { padding: 0 !important; }
    .story-timeline { padding-left: 1.5rem !important; }
    .countdown-digit { min-width: 40px; height: 40px; font-size: 1.1rem; }
  }
  @media (min-width: 769px) {
    .mobile-menu-btn { display: none !important; }
  }

  /* ─── Custom Scrollbar ──────────────────────────────────────────────── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb {
    background: ${darkMode ? 'rgba(255,255,255,0.15)' : '#ccc'};
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: ${darkMode ? 'rgba(255,255,255,0.25)' : '#999'};
  }

  /* ─── Selection ─────────────────────────────────────────────────────── */
  ::selection {
    background: rgba(45,106,79,0.2);
    color: var(--text-primary);
  }

  /* ─── Reduced Motion ────────────────────────────────────────────────── */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }

  /* ─── Star rating ───────────────────────────────────────────────────── */
  .star-rating {
    background: linear-gradient(135deg, #f4a261, #e76f51);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  /* ─── Wishlist Heart ────────────────────────────────────────────────── */
  @keyframes heartBeat {
    0% { transform: scale(1); }
    25% { transform: scale(1.3); }
    50% { transform: scale(1); }
    75% { transform: scale(1.15); }
    100% { transform: scale(1); }
  }

  /* ─── Modal Overlay ─────────────────────────────────────────────────── */
  @keyframes modalOverlayIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  @keyframes modalContentIn {
    from { opacity: 0; transform: scale(0.9) translateY(20px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
  }

  /* ─── Section Divider ───────────────────────────────────────────────── */
  .section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-subtle), transparent);
    margin: 0 auto;
    max-width: 80%;
  }

  /* ─── Tag / Pill ────────────────────────────────────────────────────── */
  .section-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(45,106,79,0.06);
    border: 1px solid rgba(45,106,79,0.1);
    color: #2d6a4f;
    padding: 0.45rem 1.2rem;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
  }
`
