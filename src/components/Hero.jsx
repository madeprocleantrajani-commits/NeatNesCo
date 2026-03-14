import { useState, useEffect } from 'react'
import { useInView } from '../hooks'

export default function Hero({ darkMode }) {
  const [ref, visible] = useInView()
  const [count, setCount] = useState({ customers: 0, products: 0, countries: 0, rating: 0 })

  useEffect(() => {
    if (!visible) return
    const targets = { customers: 50847, products: 150, countries: 45, rating: 4.9 }
    const duration = 2500
    const steps = 80
    const interval = duration / steps
    let step = 0
    const timer = setInterval(() => {
      step++
      const progress = Math.min(step / steps, 1)
      const ease = 1 - Math.pow(1 - progress, 4)
      setCount({
        customers: Math.round(targets.customers * ease),
        products: Math.round(targets.products * ease),
        countries: Math.round(targets.countries * ease),
        rating: Math.round(targets.rating * ease * 10) / 10,
      })
      if (step >= steps) clearInterval(timer)
    }, interval)
    return () => clearInterval(timer)
  }, [visible])

  return (
    <section ref={ref} style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', textAlign: 'center',
      padding: '10rem 2rem 4rem', position: 'relative', overflow: 'hidden',
      background: darkMode
        ? 'linear-gradient(180deg, #0d1a12 0%, #0a0a0a 50%, #0a0a0a 100%)'
        : 'linear-gradient(180deg, #f0ede6 0%, #fafaf8 50%, #fafaf8 100%)',
    }}>
      {/* Animated grid */}
      <div style={{
        position: 'absolute', inset: 0, opacity: darkMode ? 0.04 : 0.025,
        backgroundImage: `linear-gradient(${darkMode ? 'rgba(255,255,255,0.4)' : '#1a1a1a'} 1px, transparent 1px), linear-gradient(90deg, ${darkMode ? 'rgba(255,255,255,0.4)' : '#1a1a1a'} 1px, transparent 1px)`,
        backgroundSize: '60px 60px',
      }} />

      {/* Decorative blobs */}
      <div className="blob blob-1" />
      <div className="blob blob-2" />
      <div className="blob blob-3" />

      {/* Radial glow */}
      <div style={{
        position: 'absolute', top: '20%', left: '50%', transform: 'translateX(-50%)',
        width: '800px', height: '600px',
        background: darkMode
          ? 'radial-gradient(ellipse, rgba(45,106,79,0.15) 0%, transparent 70%)'
          : 'radial-gradient(ellipse, rgba(45,106,79,0.06) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      <div style={{ maxWidth: '920px', position: 'relative', zIndex: 1 }}>
        {/* Badge */}
        <div style={{
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.6rem',
            background: darkMode ? 'rgba(45,106,79,0.15)' : 'rgba(45,106,79,0.08)',
            border: '1px solid rgba(45,106,79,0.15)',
            padding: '0.5rem 1.2rem', borderRadius: '100px', marginBottom: '2rem',
            backdropFilter: 'blur(8px)',
          }}>
            <span className="pulse-dot" />
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#2d6a4f', letterSpacing: '0.04em' }}>
              New drops every week
            </span>
          </div>
        </div>

        {/* Headline */}
        <h1 style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: 'clamp(3rem, 8vw, 6rem)',
          fontWeight: 700, lineHeight: 1.02, letterSpacing: '-0.04em',
          marginBottom: '2rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s 0.1s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          <span className="shimmer-text">Neat Finds,</span>
          <br />
          <span className="gradient-text">Neatly Delivered</span>
        </h1>

        {/* Subheadline */}
        <p style={{
          fontSize: 'clamp(1.05rem, 2vw, 1.3rem)',
          color: 'var(--text-secondary)', lineHeight: 1.7,
          maxWidth: '580px', margin: '0 auto 3rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          We scour the internet for the most trending, high-quality products so you don't have to.
          <br />
          <span style={{ color: 'var(--text-tertiary)' }}>Fresh drops every week — delivered worldwide.</span>
        </p>

        {/* CTAs */}
        <div style={{
          display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          marginBottom: '4rem',
        }}>
          <a href="#products" className="hero-cta-primary" style={{
            background: darkMode ? '#fff' : '#1a1a1a',
            color: darkMode ? '#1a1a1a' : '#fff',
            padding: '1.15rem 3rem',
            borderRadius: '100px', fontSize: '1.05rem', fontWeight: 600,
            textDecoration: 'none', position: 'relative', overflow: 'hidden',
            boxShadow: '0 4px 24px rgba(0,0,0,0.2)',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            display: 'flex', alignItems: 'center', gap: '0.6rem',
          }}>
            <span style={{ position: 'relative', zIndex: 1 }}>Browse Products</span>
            <span style={{ position: 'relative', zIndex: 1, fontSize: '1.2rem' }}>→</span>
          </a>
          <a href="#story" className="hero-cta-secondary" style={{
            background: 'transparent', color: 'var(--text-primary)',
            padding: '1.15rem 3rem', borderRadius: '100px', fontSize: '1.05rem',
            fontWeight: 600, textDecoration: 'none',
            border: `2px solid ${darkMode ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.1)'}`,
            transition: 'all 0.3s',
          }}>
            Our Story
          </a>
        </div>

        {/* Stats */}
        <div className="hero-stats" style={{
          display: 'flex', gap: 'clamp(2rem, 5vw, 4rem)', justifyContent: 'center',
          flexWrap: 'wrap',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(40px)',
          transition: 'all 1s 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          {[
            { value: count.customers.toLocaleString() + '+', label: 'Happy Customers', icon: '👥' },
            { value: count.products + '+', label: 'Products Curated', icon: '📦' },
            { value: count.countries + '+', label: 'Countries', icon: '🌍' },
            { value: count.rating + ' ★', label: 'Avg Rating', icon: '⭐' },
          ].map((stat, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: 'clamp(1.5rem, 3vw, 2.4rem)', fontWeight: 800,
                color: 'var(--text-primary)', fontFamily: "'Inter', sans-serif",
                marginBottom: '0.2rem',
              }}>{stat.value}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', fontWeight: 500 }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div style={{
        position: 'absolute', bottom: '2rem', left: '50%', transform: 'translateX(-50%)',
        opacity: visible ? 0.4 : 0, transition: 'opacity 1s 1.5s',
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem',
      }}>
        <div style={{
          width: '24px', height: '40px', borderRadius: '12px',
          border: `2px solid var(--text-tertiary)`, display: 'flex', justifyContent: 'center',
          paddingTop: '8px',
        }}>
          <div className="scroll-dot" style={{
            width: '3px', height: '8px', borderRadius: '3px', background: 'var(--text-tertiary)',
          }} />
        </div>
        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
          Scroll
        </span>
      </div>
    </section>
  )
}
