import { useState, useEffect, useRef, useCallback } from 'react'

// ─── Constants ───────────────────────────────────────────────────────────────

const PRODUCTS = [
  {
    id: 1,
    name: 'AuraLamp Pro',
    price: 49.99,
    originalPrice: 89.99,
    category: 'Home',
    badge: 'Best Seller',
    description: 'Smart ambient LED lamp with 16M colors and app control.',
    emoji: '💡',
    gradient: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
  },
  {
    id: 2,
    name: 'ZenBrew Portable',
    price: 34.99,
    originalPrice: 59.99,
    category: 'Kitchen',
    badge: 'Trending',
    description: 'USB-C rechargeable coffee maker. Brew anywhere in 3 minutes.',
    emoji: '☕',
    gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
  },
  {
    id: 3,
    name: 'CloudRest Pillow',
    price: 29.99,
    originalPrice: 54.99,
    category: 'Bedroom',
    badge: 'New',
    description: 'Memory foam cervical pillow with cooling gel technology.',
    emoji: '☁️',
    gradient: 'linear-gradient(135deg, #c3cfe2 0%, #f5f7fa 100%)',
  },
  {
    id: 4,
    name: 'SnapClean Mini',
    price: 24.99,
    originalPrice: 44.99,
    category: 'Tech',
    badge: 'Hot Deal',
    description: 'Portable UV-C sanitizer for phones, keys, and accessories.',
    emoji: '✨',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    id: 5,
    name: 'FlexDesk Stand',
    price: 39.99,
    originalPrice: 69.99,
    category: 'Office',
    badge: 'Popular',
    description: 'Adjustable aluminum laptop stand with built-in cable management.',
    emoji: '💻',
    gradient: 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
  },
  {
    id: 6,
    name: 'PureAir Go',
    price: 44.99,
    originalPrice: 79.99,
    category: 'Home',
    badge: 'Staff Pick',
    description: 'Compact HEPA air purifier for desks, cars, and small rooms.',
    emoji: '🌿',
    gradient: 'linear-gradient(135deg, #96e6a1 0%, #d4fc79 100%)',
  },
  {
    id: 7,
    name: 'GlowRing Light',
    price: 19.99,
    originalPrice: 39.99,
    category: 'Tech',
    badge: 'Flash Sale',
    description: '10" RGB ring light with tripod. Perfect for content creators.',
    emoji: '💫',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  },
  {
    id: 8,
    name: 'NeatBottle 2.0',
    price: 27.99,
    originalPrice: 45.99,
    category: 'Lifestyle',
    badge: 'Exclusive',
    description: 'Self-cleaning water bottle with UV purification and temp display.',
    emoji: '💧',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  },
]

const REVIEWS = [
  { name: 'Sarah M.', location: 'Los Angeles, CA', text: 'Obsessed with the AuraLamp! My room looks like a vibe now. Already ordered two more for friends.', rating: 5, avatar: 'S' },
  { name: 'Jake R.', location: 'Austin, TX', text: 'ZenBrew is a game-changer for road trips. Coffee snobs will love this thing.', rating: 5, avatar: 'J' },
  { name: 'Priya K.', location: 'Toronto, ON', text: 'Shipping was super fast. Everything came well-packaged. Legit impressed.', rating: 5, avatar: 'P' },
  { name: 'Marcus T.', location: 'London, UK', text: 'The CloudRest pillow fixed my neck pain. Not even kidding, I sleep like a baby now.', rating: 5, avatar: 'M' },
  { name: 'Emily L.', location: 'Sydney, AU', text: 'Love the curation. Every product feels premium but the prices are insane.', rating: 4, avatar: 'E' },
  { name: 'David W.', location: 'Chicago, IL', text: 'FlexDesk Stand is SOLID. Looks way more expensive than it is. 10/10.', rating: 5, avatar: 'D' },
  { name: 'Aisha B.', location: 'Dubai, UAE', text: 'NeatBottle is genius. The UV cleaning feature actually works. Future is now.', rating: 5, avatar: 'A' },
  { name: 'Chris N.', location: 'Berlin, DE', text: 'GlowRing leveled up my Zoom calls. Coworkers think I got a studio setup.', rating: 5, avatar: 'C' },
]

const FEATURES = [
  { icon: '🚀', title: 'Fast Global Shipping', desc: 'Most orders delivered in 5-12 business days worldwide. Tracked every step.' },
  { icon: '🔒', title: 'Secure Checkout', desc: 'SSL encrypted with Stripe. Apple Pay, Google Pay, and all major cards.' },
  { icon: '↩️', title: '30-Day Returns', desc: "Don't love it? Full refund, no questions asked. We cover return shipping." },
  { icon: '💎', title: 'Curated Quality', desc: 'Every product is tested by our team before it makes the cut.' },
]

const CATEGORIES = ['All', 'Home', 'Tech', 'Kitchen', 'Bedroom', 'Office', 'Lifestyle']

// ─── Hooks ───────────────────────────────────────────────────────────────────

function useInView(options = {}) {
  const ref = useRef(null)
  const [isVisible, setIsVisible] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true)
        observer.unobserve(el)
      }
    }, { threshold: 0.1, ...options })
    observer.observe(el)
    return () => observer.unobserve(el)
  }, [])
  return [ref, isVisible]
}

// ─── Cursor Glow (like signalpilot constellation effect) ─────────────────────

function CursorGlow() {
  const glowRef = useRef(null)
  useEffect(() => {
    const handleMove = (e) => {
      if (glowRef.current) {
        glowRef.current.style.left = e.clientX + 'px'
        glowRef.current.style.top = e.clientY + 'px'
      }
    }
    window.addEventListener('mousemove', handleMove)
    return () => window.removeEventListener('mousemove', handleMove)
  }, [])

  return (
    <div ref={glowRef} style={{
      position: 'fixed', width: '600px', height: '600px',
      borderRadius: '50%', pointerEvents: 'none', zIndex: 0,
      background: 'radial-gradient(circle, rgba(45,106,79,0.04) 0%, transparent 70%)',
      transform: 'translate(-50%, -50%)',
      transition: 'left 0.15s ease-out, top 0.15s ease-out',
    }} />
  )
}

// ─── Floating Particles Background ───────────────────────────────────────────

function FloatingParticles() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animId
    let particles = []

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    for (let i = 0; i < 40; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2 + 0.5,
        speedX: (Math.random() - 0.5) * 0.3,
        speedY: (Math.random() - 0.5) * 0.3,
        opacity: Math.random() * 0.3 + 0.1,
      })
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      particles.forEach(p => {
        p.x += p.speedX
        p.y += p.speedY
        if (p.x < 0) p.x = canvas.width
        if (p.x > canvas.width) p.x = 0
        if (p.y < 0) p.y = canvas.height
        if (p.y > canvas.height) p.y = 0
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(45, 106, 79, ${p.opacity})`
        ctx.fill()
      })
      animId = requestAnimationFrame(animate)
    }
    animate()

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return <canvas ref={canvasRef} style={{
    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
    pointerEvents: 'none', zIndex: 0,
  }} />
}

// ─── Navbar ──────────────────────────────────────────────────────────────────

function Navbar({ cartCount }) {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [menuOpen])

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
      padding: '0 clamp(1rem, 4vw, 3rem)', height: '72px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      background: scrolled ? 'rgba(250,250,248,0.88)' : 'transparent',
      backdropFilter: scrolled ? 'blur(24px) saturate(1.4)' : 'none',
      WebkitBackdropFilter: scrolled ? 'blur(24px) saturate(1.4)' : 'none',
      borderBottom: scrolled ? '1px solid rgba(0,0,0,0.04)' : 'none',
      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    }}>
      <a href="#" style={{
        fontFamily: "'Playfair Display', serif", fontSize: '1.5rem', fontWeight: 700,
        color: '#1a1a1a', textDecoration: 'none', letterSpacing: '-0.03em',
        display: 'flex', alignItems: 'center', gap: '0.3rem',
      }}>
        <span style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          width: '32px', height: '32px', borderRadius: '8px',
          background: '#2d6a4f', color: '#fff', fontSize: '0.9rem', fontWeight: 800,
          fontFamily: "'Playfair Display', serif",
        }}>N</span>
        <span>eat<span style={{ color: '#2d6a4f' }}>Nes</span>Co</span>
      </a>

      <div style={{
        display: 'flex', gap: '2rem', alignItems: 'center',
      }} className="nav-links-desktop">
        {['Products', 'About', 'Reviews'].map(item => (
          <a key={item} href={`#${item.toLowerCase()}`} style={{
            color: '#555', textDecoration: 'none', fontSize: '0.92rem',
            fontWeight: 500, transition: 'color 0.2s', position: 'relative',
          }} className="nav-link">
            {item}
          </a>
        ))}
        <div style={{ position: 'relative' }}>
          <a href="#products" className="shiny-btn" style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            background: '#1a1a1a', color: '#fff', padding: '0.6rem 1.5rem',
            borderRadius: '100px', fontSize: '0.88rem', fontWeight: 600,
            textDecoration: 'none', transition: 'all 0.3s',
            position: 'relative', overflow: 'hidden',
          }}>
            <span style={{ position: 'relative', zIndex: 1 }}>Shop Now</span>
            {cartCount > 0 && (
              <span style={{
                background: '#e63946', color: '#fff', borderRadius: '50%',
                width: '18px', height: '18px', display: 'inline-flex',
                alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem',
                fontWeight: 800, position: 'relative', zIndex: 1,
              }}>{cartCount}</span>
            )}
          </a>
        </div>
      </div>

      <button onClick={() => setMenuOpen(!menuOpen)} className="mobile-menu-btn" style={{
        display: 'none', background: 'none', border: 'none', cursor: 'pointer',
        fontSize: '1.5rem', color: '#1a1a1a', padding: '0.5rem',
        position: 'relative', zIndex: 1001,
      }}>
        <div style={{
          width: '24px', height: '2px', background: '#1a1a1a',
          transition: 'all 0.3s',
          transform: menuOpen ? 'rotate(45deg) translateY(0)' : 'none',
          marginBottom: menuOpen ? 0 : '6px',
        }} />
        <div style={{
          width: '24px', height: '2px', background: '#1a1a1a',
          transition: 'all 0.3s',
          opacity: menuOpen ? 0 : 1,
          marginBottom: menuOpen ? 0 : '6px',
        }} />
        <div style={{
          width: '24px', height: '2px', background: '#1a1a1a',
          transition: 'all 0.3s',
          transform: menuOpen ? 'rotate(-45deg) translateY(0)' : 'none',
        }} />
      </button>

      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0,
        width: '100%', maxWidth: '320px',
        background: 'rgba(250,250,248,0.98)', backdropFilter: 'blur(30px)',
        transform: menuOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex', flexDirection: 'column', padding: '6rem 2rem 2rem',
        gap: '0.5rem', zIndex: 999, boxShadow: menuOpen ? '-20px 0 60px rgba(0,0,0,0.1)' : 'none',
      }}>
        {['Products', 'About', 'Reviews'].map((item, i) => (
          <a key={item} href={`#${item.toLowerCase()}`}
             onClick={() => setMenuOpen(false)}
             style={{
               color: '#1a1a1a', textDecoration: 'none', fontSize: '1.5rem', fontWeight: 600,
               padding: '1rem 0', borderBottom: '1px solid rgba(0,0,0,0.06)',
               opacity: menuOpen ? 1 : 0, transform: menuOpen ? 'translateX(0)' : 'translateX(20px)',
               transition: `all 0.3s ${i * 0.08 + 0.15}s cubic-bezier(0.4, 0, 0.2, 1)`,
             }}>
            {item}
          </a>
        ))}
        <a href="#products" onClick={() => setMenuOpen(false)} style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          background: '#1a1a1a', color: '#fff', padding: '1rem 2rem',
          borderRadius: '100px', fontSize: '1rem', fontWeight: 600,
          textDecoration: 'none', marginTop: '1rem',
          opacity: menuOpen ? 1 : 0, transform: menuOpen ? 'translateX(0)' : 'translateX(20px)',
          transition: 'all 0.3s 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>Shop Now</a>
      </div>

      {menuOpen && <div onClick={() => setMenuOpen(false)} style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.2)', zIndex: 998,
      }} />}
    </nav>
  )
}

// ─── Hero ────────────────────────────────────────────────────────────────────

function Hero() {
  const [ref, visible] = useInView()
  const [count, setCount] = useState({ customers: 0, products: 0, countries: 0 })

  useEffect(() => {
    if (!visible) return
    const targets = { customers: 2847, products: 150, countries: 45 }
    const duration = 2000
    const steps = 60
    const interval = duration / steps
    let step = 0
    const timer = setInterval(() => {
      step++
      const progress = Math.min(step / steps, 1)
      const ease = 1 - Math.pow(1 - progress, 3)
      setCount({
        customers: Math.round(targets.customers * ease),
        products: Math.round(targets.products * ease),
        countries: Math.round(targets.countries * ease),
      })
      if (step >= steps) clearInterval(timer)
    }, interval)
    return () => clearInterval(timer)
  }, [visible])

  return (
    <section ref={ref} style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', textAlign: 'center',
      padding: '8rem 2rem 4rem', position: 'relative', overflow: 'hidden',
      background: 'linear-gradient(180deg, #f0ede6 0%, #fafaf8 50%, #fafaf8 100%)',
    }}>
      {/* Animated grid */}
      <div style={{
        position: 'absolute', inset: 0, opacity: 0.025,
        backgroundImage: 'linear-gradient(#1a1a1a 1px, transparent 1px), linear-gradient(90deg, #1a1a1a 1px, transparent 1px)',
        backgroundSize: '60px 60px',
      }} />

      {/* Decorative blobs */}
      <div className="blob blob-1" />
      <div className="blob blob-2" />

      <div style={{
        maxWidth: '880px', position: 'relative', zIndex: 1,
      }}>
        <div style={{
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.6rem',
            background: 'rgba(45,106,79,0.08)', border: '1px solid rgba(45,106,79,0.12)',
            padding: '0.5rem 1.2rem', borderRadius: '100px', marginBottom: '2rem',
          }}>
            <span className="pulse-dot" />
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#2d6a4f', letterSpacing: '0.04em' }}>
              New drops every week
            </span>
          </div>
        </div>

        <h1 style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: 'clamp(3rem, 7vw, 5.5rem)',
          fontWeight: 700, lineHeight: 1.05, letterSpacing: '-0.03em',
          marginBottom: '1.8rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s 0.1s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          <span className="shimmer-text">
            Neat Finds,
          </span>
          <br />
          <span style={{ color: '#2d6a4f' }}>Neatly Delivered</span>
        </h1>

        <p style={{
          fontSize: 'clamp(1.05rem, 2vw, 1.3rem)', color: '#777', lineHeight: 1.7,
          maxWidth: '560px', margin: '0 auto 2.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          We scour the internet for trending, high-quality products so you don't have to.
          Fresh drops every week — delivered straight to your door.
        </p>

        <div style={{
          display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          <a href="#products" className="hero-cta-primary" style={{
            background: '#1a1a1a', color: '#fff', padding: '1.1rem 2.8rem',
            borderRadius: '100px', fontSize: '1.05rem', fontWeight: 600,
            textDecoration: 'none', position: 'relative', overflow: 'hidden',
            boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          }}>
            <span style={{ position: 'relative', zIndex: 1 }}>Browse Products</span>
          </a>
          <a href="#about" style={{
            background: 'transparent', color: '#1a1a1a',
            padding: '1.1rem 2.8rem', borderRadius: '100px', fontSize: '1.05rem',
            fontWeight: 600, textDecoration: 'none', border: '2px solid rgba(0,0,0,0.1)',
            transition: 'all 0.3s',
          }} className="hero-cta-secondary">
            Our Story
          </a>
        </div>

        {/* Stats counter */}
        <div style={{
          display: 'flex', gap: 'clamp(1.5rem, 4vw, 3rem)', justifyContent: 'center',
          marginTop: '4rem', flexWrap: 'wrap',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          {[
            { value: count.customers.toLocaleString() + '+', label: 'Happy Customers' },
            { value: count.products + '+', label: 'Products Curated' },
            { value: count.countries + '+', label: 'Countries Shipped' },
          ].map((stat, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: 'clamp(1.5rem, 3vw, 2.2rem)', fontWeight: 800,
                color: '#1a1a1a', fontFamily: "'Inter', sans-serif",
              }}>{stat.value}</div>
              <div style={{ fontSize: '0.8rem', color: '#999', fontWeight: 500, marginTop: '0.2rem' }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="scroll-indicator" style={{
        position: 'absolute', bottom: '2rem', left: '50%', transform: 'translateX(-50%)',
        opacity: visible ? 0.4 : 0, transition: 'opacity 1s 1s',
      }}>
        <div style={{
          width: '24px', height: '40px', borderRadius: '12px',
          border: '2px solid #999', display: 'flex', justifyContent: 'center',
          paddingTop: '8px',
        }}>
          <div className="scroll-dot" style={{
            width: '3px', height: '8px', borderRadius: '3px', background: '#999',
          }} />
        </div>
      </div>
    </section>
  )
}

// ─── Product Card ────────────────────────────────────────────────────────────

function ProductCard({ product, delay, onAddToCart }) {
  const [ref, visible] = useInView()
  const cardRef = useRef(null)
  const [hovered, setHovered] = useState(false)
  const [added, setAdded] = useState(false)

  const discount = Math.round((1 - product.price / product.originalPrice) * 100)

  const handleMouseMove = (e) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    cardRef.current.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
    cardRef.current.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
  }

  const handleAdd = () => {
    setAdded(true)
    onAddToCart(product)
    setTimeout(() => setAdded(false), 1500)
  }

  return (
    <div
      ref={el => { ref.current = el; cardRef.current = el }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="product-card"
      style={{
        position: 'relative', borderRadius: '24px', overflow: 'hidden',
        background: '#fff', border: '1px solid rgba(0,0,0,0.05)',
        transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        transform: visible
          ? (hovered ? 'translateY(-8px) scale(1.01)' : 'translateY(0) scale(1)')
          : 'translateY(50px) scale(0.95)',
        opacity: visible ? 1 : 0,
        transitionDelay: visible ? `${delay * 0.08}s` : '0s',
        boxShadow: hovered
          ? '0 24px 64px rgba(0,0,0,0.12), 0 0 0 1px rgba(45,106,79,0.08)'
          : '0 2px 20px rgba(0,0,0,0.03)',
        cursor: 'pointer',
      }}
    >
      {/* Spotlight overlay */}
      <div className="card-spotlight" style={{
        position: 'absolute', inset: 0, borderRadius: '24px',
        opacity: hovered ? 1 : 0, transition: 'opacity 0.4s', pointerEvents: 'none', zIndex: 2,
      }} />

      {/* Product visual */}
      <div style={{
        height: '220px', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: product.gradient, position: 'relative', overflow: 'hidden',
      }}>
        <span style={{
          fontSize: '5rem', filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.1))',
          transition: 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
          transform: hovered ? 'scale(1.2) rotate(-5deg)' : 'scale(1) rotate(0)',
        }}>
          {product.emoji}
        </span>

        {/* Badge */}
        {product.badge && (
          <span style={{
            position: 'absolute', top: '1rem', left: '1rem',
            background: product.badge === 'Best Seller' ? '#2d6a4f' :
                        product.badge === 'Trending' ? '#e76f51' :
                        product.badge === 'New' ? '#264653' :
                        product.badge === 'Hot Deal' ? '#e63946' :
                        product.badge === 'Flash Sale' ? '#9b59b6' :
                        product.badge === 'Exclusive' ? '#1a1a1a' :
                        product.badge === 'Popular' ? '#457b9d' : '#6c757d',
            color: '#fff', padding: '0.35rem 0.9rem', borderRadius: '100px',
            fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.04em',
            textTransform: 'uppercase', backdropFilter: 'blur(8px)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          }}>
            {product.badge}
          </span>
        )}

        {/* Discount badge */}
        <span style={{
          position: 'absolute', top: '1rem', right: '1rem',
          background: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(8px)',
          color: '#e63946', padding: '0.3rem 0.7rem', borderRadius: '100px',
          fontSize: '0.75rem', fontWeight: 800,
        }}>
          -{discount}%
        </span>
      </div>

      {/* Product info */}
      <div style={{ padding: '1.5rem' }}>
        <div style={{
          fontSize: '0.7rem', color: '#2d6a4f', textTransform: 'uppercase',
          letterSpacing: '0.1em', fontWeight: 700, marginBottom: '0.5rem',
          display: 'flex', alignItems: 'center', gap: '0.4rem',
        }}>
          <span style={{ width: '12px', height: '1px', background: '#2d6a4f' }} />
          {product.category}
        </div>
        <h3 style={{
          fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.4rem',
          color: '#1a1a1a', letterSpacing: '-0.01em',
        }}>
          {product.name}
        </h3>
        <p style={{ fontSize: '0.88rem', color: '#999', lineHeight: 1.55, marginBottom: '1.2rem' }}>
          {product.description}
        </p>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
            <span style={{
              fontSize: '1.4rem', fontWeight: 800, color: '#1a1a1a',
              fontFamily: "'Inter', sans-serif",
            }}>
              ${product.price}
            </span>
            <span style={{
              fontSize: '0.88rem', color: '#ccc', textDecoration: 'line-through',
            }}>
              ${product.originalPrice}
            </span>
          </div>
          <button onClick={handleAdd} style={{
            background: added ? '#2d6a4f' : (hovered ? '#2d6a4f' : '#1a1a1a'),
            color: '#fff', border: 'none',
            padding: '0.6rem 1.4rem', borderRadius: '100px', fontSize: '0.82rem',
            fontWeight: 600, cursor: 'pointer',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            transform: added ? 'scale(0.95)' : 'scale(1)',
          }}>
            {added ? 'Added!' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Products Section ────────────────────────────────────────────────────────

function Products({ onAddToCart }) {
  const [ref, visible] = useInView()
  const [activeCategory, setActiveCategory] = useState('All')

  const filtered = activeCategory === 'All'
    ? PRODUCTS
    : PRODUCTS.filter(p => p.category === activeCategory)

  return (
    <section id="products" style={{
      padding: '6rem 2rem 4rem', position: 'relative', zIndex: 1,
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '2.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s',
        }}>
          <span style={{
            display: 'inline-block', background: 'rgba(45,106,79,0.06)',
            border: '1px solid rgba(45,106,79,0.1)',
            color: '#2d6a4f', padding: '0.4rem 1.2rem', borderRadius: '100px',
            fontSize: '0.78rem', fontWeight: 600, letterSpacing: '0.08em',
            textTransform: 'uppercase', marginBottom: '1rem',
          }}>
            This Week's Drops
          </span>
          <h2 style={{
            fontFamily: "'Playfair Display', serif", fontSize: 'clamp(2rem, 4vw, 3.2rem)',
            fontWeight: 700, color: '#1a1a1a', marginBottom: '0.5rem',
            letterSpacing: '-0.02em',
          }}>
            Trending Products
          </h2>
          <p style={{ color: '#999', fontSize: '1.05rem', maxWidth: '480px', margin: '0 auto' }}>
            Hand-picked finds that are actually worth your money.
          </p>
        </div>

        {/* Category filters */}
        <div style={{
          display: 'flex', gap: '0.5rem', justifyContent: 'center',
          marginBottom: '2.5rem', flexWrap: 'wrap',
          opacity: visible ? 1 : 0, transition: 'opacity 0.6s 0.2s',
        }}>
          {CATEGORIES.map(cat => (
            <button key={cat} onClick={() => setActiveCategory(cat)} style={{
              background: activeCategory === cat ? '#1a1a1a' : 'rgba(0,0,0,0.04)',
              color: activeCategory === cat ? '#fff' : '#777',
              border: 'none', padding: '0.5rem 1.2rem', borderRadius: '100px',
              fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            }}>
              {cat}
            </button>
          ))}
        </div>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem',
        }}>
          {filtered.map((product, i) => (
            <ProductCard key={product.id} product={product} delay={i} onAddToCart={onAddToCart} />
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Features / About ────────────────────────────────────────────────────────

function Features() {
  const [ref, visible] = useInView()

  return (
    <section id="about" style={{
      padding: '6rem 2rem',
      background: 'linear-gradient(180deg, #fafaf8 0%, #f0ede6 50%, #fafaf8 100%)',
      position: 'relative', zIndex: 1,
    }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '3.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s',
        }}>
          <span style={{
            display: 'inline-block', background: 'rgba(45,106,79,0.06)',
            border: '1px solid rgba(45,106,79,0.1)',
            color: '#2d6a4f', padding: '0.4rem 1.2rem', borderRadius: '100px',
            fontSize: '0.78rem', fontWeight: 600, letterSpacing: '0.08em',
            textTransform: 'uppercase', marginBottom: '1rem',
          }}>
            Why NeatNesCo
          </span>
          <h2 style={{
            fontFamily: "'Playfair Display', serif", fontSize: 'clamp(2rem, 4vw, 3.2rem)',
            fontWeight: 700, color: '#1a1a1a', letterSpacing: '-0.02em',
          }}>
            Built Different
          </h2>
          <p style={{ color: '#999', fontSize: '1.05rem', maxWidth: '500px', margin: '0.5rem auto 0' }}>
            We're not your average dropshipping store. Here's why.
          </p>
        </div>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
          gap: '1.5rem',
        }}>
          {FEATURES.map((feat, i) => {
            const [cardRef, cardVisible] = useInView()
            const [hovered, setHovered] = useState(false)
            return (
              <div key={i} ref={cardRef}
                onMouseEnter={() => setHovered(true)}
                onMouseLeave={() => setHovered(false)}
                style={{
                  background: '#fff', borderRadius: '20px', padding: '2rem',
                  border: '1px solid rgba(0,0,0,0.04)',
                  opacity: cardVisible ? 1 : 0,
                  transform: cardVisible
                    ? (hovered ? 'translateY(-4px)' : 'translateY(0)')
                    : 'translateY(30px)',
                  transition: `all 0.5s cubic-bezier(0.4, 0, 0.2, 1) ${i * 0.1}s`,
                  boxShadow: hovered ? '0 16px 48px rgba(0,0,0,0.08)' : '0 2px 12px rgba(0,0,0,0.02)',
              }}>
                <div style={{
                  width: '52px', height: '52px', borderRadius: '14px',
                  background: 'rgba(45,106,79,0.08)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.5rem', marginBottom: '1.2rem',
                  transition: 'transform 0.3s',
                  transform: hovered ? 'scale(1.1)' : 'scale(1)',
                }}>{feat.icon}</div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: '#1a1a1a' }}>
                  {feat.title}
                </h3>
                <p style={{ fontSize: '0.9rem', color: '#999', lineHeight: 1.6 }}>{feat.desc}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

// ─── Reviews ─────────────────────────────────────────────────────────────────

function Reviews() {
  const [ref, visible] = useInView()

  return (
    <section id="reviews" style={{
      padding: '6rem 2rem', overflow: 'hidden', position: 'relative', zIndex: 1,
    }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '3rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s',
        }}>
          <span style={{
            display: 'inline-block', background: 'rgba(45,106,79,0.06)',
            border: '1px solid rgba(45,106,79,0.1)',
            color: '#2d6a4f', padding: '0.4rem 1.2rem', borderRadius: '100px',
            fontSize: '0.78rem', fontWeight: 600, letterSpacing: '0.08em',
            textTransform: 'uppercase', marginBottom: '1rem',
          }}>
            Social Proof
          </span>
          <h2 style={{
            fontFamily: "'Playfair Display', serif", fontSize: 'clamp(2rem, 4vw, 3.2rem)',
            fontWeight: 700, color: '#1a1a1a', letterSpacing: '-0.02em',
          }}>
            What People Are Saying
          </h2>
        </div>

        <div className="marquee-container">
          <div className="marquee-track">
            {[...REVIEWS, ...REVIEWS].map((review, i) => (
              <div key={i} style={{
                minWidth: '340px', maxWidth: '340px', background: '#fff',
                borderRadius: '20px', padding: '1.8rem',
                border: '1px solid rgba(0,0,0,0.04)', flexShrink: 0,
                boxShadow: '0 2px 12px rgba(0,0,0,0.02)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1rem' }}>
                  <div style={{
                    width: '40px', height: '40px', borderRadius: '50%',
                    background: 'linear-gradient(135deg, #2d6a4f, #40916c)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: '#fff', fontWeight: 700, fontSize: '0.9rem',
                  }}>{review.avatar}</div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#1a1a1a' }}>{review.name}</div>
                    <div style={{ fontSize: '0.75rem', color: '#bbb' }}>{review.location}</div>
                  </div>
                </div>
                <div style={{ color: '#f4a261', marginBottom: '0.75rem', fontSize: '0.85rem', letterSpacing: '2px' }}>
                  {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
                </div>
                <p style={{
                  fontSize: '0.92rem', color: '#666', lineHeight: 1.6,
                  fontStyle: 'italic',
                }}>
                  "{review.text}"
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── Newsletter ──────────────────────────────────────────────────────────────

function Newsletter() {
  const [ref, visible] = useInView()
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (email) setSubmitted(true)
  }

  return (
    <section style={{
      padding: '6rem 2rem', position: 'relative', overflow: 'hidden', zIndex: 1,
      background: 'linear-gradient(135deg, #1a1a1a 0%, #1e3a2b 50%, #1a1a1a 100%)',
    }}>
      {/* Decorative circles */}
      <div style={{
        position: 'absolute', top: '-100px', right: '-100px',
        width: '400px', height: '400px', borderRadius: '50%',
        border: '1px solid rgba(45,106,79,0.15)',
      }} />
      <div style={{
        position: 'absolute', bottom: '-150px', left: '-150px',
        width: '500px', height: '500px', borderRadius: '50%',
        border: '1px solid rgba(45,106,79,0.1)',
      }} />

      <div ref={ref} style={{
        maxWidth: '600px', margin: '0 auto', textAlign: 'center',
        position: 'relative', zIndex: 1,
        opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.6s',
      }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📬</div>
        <h2 style={{
          fontFamily: "'Playfair Display', serif", fontSize: 'clamp(1.8rem, 4vw, 2.8rem)',
          fontWeight: 700, color: '#fff', marginBottom: '0.8rem', letterSpacing: '-0.02em',
        }}>
          Don't Miss a Drop
        </h2>
        <p style={{
          color: 'rgba(255,255,255,0.5)', marginBottom: '2.5rem',
          fontSize: '1.05rem', lineHeight: 1.6,
        }}>
          First access to new products, exclusive deals, and weekly curated drops. No spam, ever.
        </p>
        {submitted ? (
          <div style={{
            background: 'rgba(45,106,79,0.2)', border: '1px solid rgba(45,106,79,0.3)',
            borderRadius: '16px', padding: '1.5rem', color: '#a8dabc',
            fontSize: '1rem', fontWeight: 600,
            animation: 'fadeIn 0.5s ease-out',
          }}>
            You're in! Check your inbox for a welcome surprise.
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{
            display: 'flex', gap: '0.75rem', maxWidth: '480px', margin: '0 auto',
            flexWrap: 'wrap', justifyContent: 'center',
          }}>
            <input
              type="email" placeholder="your@email.com" value={email}
              onChange={e => setEmail(e.target.value)} required
              style={{
                flex: 1, minWidth: '240px', padding: '1rem 1.5rem', borderRadius: '100px',
                border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.06)',
                color: '#fff', fontSize: '1rem', outline: 'none',
                transition: 'all 0.3s', fontFamily: "'Inter', sans-serif",
              }}
              onFocus={e => {
                e.target.style.borderColor = 'rgba(45,106,79,0.5)'
                e.target.style.background = 'rgba(255,255,255,0.1)'
              }}
              onBlur={e => {
                e.target.style.borderColor = 'rgba(255,255,255,0.1)'
                e.target.style.background = 'rgba(255,255,255,0.06)'
              }}
            />
            <button type="submit" className="subscribe-btn" style={{
              background: '#2d6a4f', color: '#fff', padding: '1rem 2rem',
              borderRadius: '100px', border: 'none', fontSize: '1rem',
              fontWeight: 600, cursor: 'pointer', transition: 'all 0.3s',
              fontFamily: "'Inter', sans-serif",
            }}>
              Subscribe
            </button>
          </form>
        )}
        <p style={{
          color: 'rgba(255,255,255,0.25)', fontSize: '0.78rem', marginTop: '1.2rem',
        }}>
          Join 2,800+ others. Unsubscribe anytime.
        </p>
      </div>
    </section>
  )
}

// ─── Footer ──────────────────────────────────────────────────────────────────

function Footer() {
  return (
    <footer style={{
      background: '#0d0d0d', color: 'rgba(255,255,255,0.4)', padding: '4rem 2rem 2rem',
      position: 'relative', zIndex: 1,
    }}>
      <div style={{
        maxWidth: '1100px', margin: '0 auto',
        display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '2.5rem', marginBottom: '3rem',
      }}>
        <div>
          <h3 style={{
            fontFamily: "'Playfair Display', serif", fontSize: '1.3rem',
            fontWeight: 700, color: '#fff', marginBottom: '0.8rem',
            display: 'flex', alignItems: 'center', gap: '0.3rem',
          }}>
            <span style={{
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              width: '28px', height: '28px', borderRadius: '7px',
              background: '#2d6a4f', color: '#fff', fontSize: '0.75rem', fontWeight: 800,
            }}>N</span>
            eat<span style={{ color: '#2d6a4f' }}>Nes</span>Co
          </h3>
          <p style={{ fontSize: '0.85rem', lineHeight: 1.7 }}>
            Curating the internet's best trending products. Neat finds, neatly delivered — since 2024.
          </p>
          <div style={{ display: 'flex', gap: '0.6rem', marginTop: '1rem' }}>
            {['IG', 'TT', 'X', 'YT'].map(social => (
              <a key={social} href="#" style={{
                width: '34px', height: '34px', borderRadius: '8px',
                background: 'rgba(255,255,255,0.06)', display: 'flex',
                alignItems: 'center', justifyContent: 'center',
                color: 'rgba(255,255,255,0.4)', textDecoration: 'none',
                fontSize: '0.7rem', fontWeight: 700, transition: 'all 0.2s',
              }} onMouseEnter={e => { e.target.style.background = '#2d6a4f'; e.target.style.color = '#fff' }}
                 onMouseLeave={e => { e.target.style.background = 'rgba(255,255,255,0.06)'; e.target.style.color = 'rgba(255,255,255,0.4)' }}>
                {social}
              </a>
            ))}
          </div>
        </div>
        <div>
          <h4 style={{
            color: 'rgba(255,255,255,0.6)', fontSize: '0.78rem', fontWeight: 700,
            marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.1em',
          }}>Shop</h4>
          {['New Arrivals', 'Best Sellers', 'On Sale', 'All Products'].map(item => (
            <a key={item} href="#products" style={{
              display: 'block', color: 'rgba(255,255,255,0.4)', textDecoration: 'none',
              fontSize: '0.88rem', marginBottom: '0.7rem', transition: 'color 0.2s',
            }} onMouseEnter={e => e.target.style.color = '#fff'}
               onMouseLeave={e => e.target.style.color = 'rgba(255,255,255,0.4)'}>
              {item}
            </a>
          ))}
        </div>
        <div>
          <h4 style={{
            color: 'rgba(255,255,255,0.6)', fontSize: '0.78rem', fontWeight: 700,
            marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.1em',
          }}>Company</h4>
          {['About Us', 'Contact', 'FAQ', 'Shipping & Returns'].map(item => (
            <a key={item} href="#about" style={{
              display: 'block', color: 'rgba(255,255,255,0.4)', textDecoration: 'none',
              fontSize: '0.88rem', marginBottom: '0.7rem', transition: 'color 0.2s',
            }} onMouseEnter={e => e.target.style.color = '#fff'}
               onMouseLeave={e => e.target.style.color = 'rgba(255,255,255,0.4)'}>
              {item}
            </a>
          ))}
        </div>
        <div>
          <h4 style={{
            color: 'rgba(255,255,255,0.6)', fontSize: '0.78rem', fontWeight: 700,
            marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.1em',
          }}>Legal</h4>
          {['Privacy Policy', 'Terms of Service', 'Refund Policy', 'Cookie Policy'].map(item => (
            <a key={item} href="#" style={{
              display: 'block', color: 'rgba(255,255,255,0.4)', textDecoration: 'none',
              fontSize: '0.88rem', marginBottom: '0.7rem', transition: 'color 0.2s',
            }} onMouseEnter={e => e.target.style.color = '#fff'}
               onMouseLeave={e => e.target.style.color = 'rgba(255,255,255,0.4)'}>
              {item}
            </a>
          ))}
        </div>
      </div>

      <div style={{
        borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '1.5rem',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        flexWrap: 'wrap', gap: '1rem', fontSize: '0.78rem',
      }}>
        <span>&copy; 2024 NeatNesCo. All rights reserved.</span>
        <span style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>Powered with care</span>
          <span style={{ color: '#2d6a4f' }}>●</span>
          <span>Neat finds, neatly delivered</span>
        </span>
      </div>
    </footer>
  )
}

// ─── Main App ────────────────────────────────────────────────────────────────

export default function App() {
  const [cart, setCart] = useState([])

  const handleAddToCart = useCallback((product) => {
    setCart(prev => [...prev, product])
  }, [])

  return (
    <>
      <style>{`
        /* Shimmer headline animation (signalpilot-inspired) */
        .shimmer-text {
          background: linear-gradient(
            110deg, #1a1a1a 30%, #2d6a4f 45%, #40916c 50%, #2d6a4f 55%, #1a1a1a 70%
          );
          background-size: 300% 100%;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: shimmer 8s ease-in-out infinite;
        }
        @keyframes shimmer {
          0% { background-position: 200% center; }
          100% { background-position: -200% center; }
        }

        /* Pulsing dot */
        .pulse-dot {
          width: 8px; height: 8px; border-radius: 50%;
          background: #2d6a4f; display: inline-block;
          animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.8); }
        }

        /* Scroll indicator */
        .scroll-dot {
          animation: scrollBounce 2s ease-in-out infinite;
        }
        @keyframes scrollBounce {
          0%, 100% { transform: translateY(0); opacity: 1; }
          50% { transform: translateY(10px); opacity: 0; }
        }

        /* Decorative blobs */
        .blob {
          position: absolute; border-radius: 50%;
          filter: blur(80px); opacity: 0.15; pointer-events: none;
        }
        .blob-1 {
          width: 500px; height: 500px; top: -100px; right: -100px;
          background: #2d6a4f;
          animation: blobFloat 20s ease-in-out infinite;
        }
        .blob-2 {
          width: 400px; height: 400px; bottom: -50px; left: -100px;
          background: #457b9d;
          animation: blobFloat 25s ease-in-out infinite reverse;
        }
        @keyframes blobFloat {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -30px) scale(1.05); }
          66% { transform: translate(-20px, 20px) scale(0.95); }
        }

        /* Spotlight card effect (signalpilot-inspired) */
        .card-spotlight {
          background: radial-gradient(
            350px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
            rgba(45, 106, 79, 0.08), transparent 60%
          );
        }

        /* Shiny button (signalpilot-inspired) */
        .shiny-btn::after {
          content: '';
          position: absolute; inset: 0;
          background: conic-gradient(
            from var(--shiny-angle, 0deg),
            transparent 0%, rgba(255,255,255,0.1) 10%, transparent 20%
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

        /* Hero CTA hover */
        .hero-cta-primary:hover {
          background: #2d6a4f !important;
          transform: translateY(-3px) !important;
          box-shadow: 0 12px 40px rgba(45,106,79,0.35) !important;
        }
        .hero-cta-secondary:hover {
          border-color: #2d6a4f !important;
          color: #2d6a4f !important;
          transform: translateY(-2px);
        }

        /* Nav link hover underline */
        .nav-link::after {
          content: '';
          position: absolute; bottom: -4px; left: 0; right: 0;
          height: 2px; background: #2d6a4f; border-radius: 1px;
          transform: scaleX(0); transition: transform 0.3s;
          transform-origin: center;
        }
        .nav-link:hover::after { transform: scaleX(1); }
        .nav-link:hover { color: #2d6a4f !important; }

        /* Subscribe button */
        .subscribe-btn:hover {
          background: #40916c !important;
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(45,106,79,0.3);
        }

        /* Infinite marquee carousel */
        .marquee-container {
          overflow: hidden;
          mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
          -webkit-mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
        }
        .marquee-track {
          display: flex; gap: 1.5rem;
          animation: marquee 50s linear infinite;
          width: max-content;
        }
        .marquee-track:hover {
          animation-play-state: paused;
        }
        @keyframes marquee {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }

        /* Fade in animation */
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
          .nav-links-desktop { display: none !important; }
          .mobile-menu-btn { display: flex !important; flex-direction: column; gap: 0; }
          .blob { display: none; }
        }
        @media (min-width: 769px) {
          .mobile-menu-btn { display: none !important; }
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #999; }

        /* Selection color */
        ::selection { background: rgba(45,106,79,0.15); color: #1a1a1a; }

        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
      <FloatingParticles />
      <CursorGlow />
      <Navbar cartCount={cart.length} />
      <Hero />
      <Products onAddToCart={handleAddToCart} />
      <Features />
      <Reviews />
      <Newsletter />
      <Footer />
    </>
  )
}
