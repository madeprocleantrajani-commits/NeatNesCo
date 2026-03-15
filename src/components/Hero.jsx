import { useState, useEffect } from 'react'
import { useInView } from '../hooks'
import { PRODUCTS } from '../data'

const FEATURED_IDS = [1, 9, 8]

export default function Hero({ onQuickView }) {
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

  const featured = FEATURED_IDS.map(id => PRODUCTS.find(p => p.id === id)).filter(Boolean)

  return (
    <section ref={ref} style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', textAlign: 'center',
      padding: '9rem 2rem 5rem',
      background: '#ffffff',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ maxWidth: '900px', marginBottom: '2rem', position: 'relative', zIndex: 1 }}>
        {/* Badge */}
        <div style={{
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.4rem 1rem', borderRadius: '100px', marginBottom: '1.5rem',
            background: '#f5f5f7',
            border: '1px solid rgba(0,0,0,0.06)',
          }}>
            <span className="pulse-dot" />
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#1d1d1f' }}>
              New drops every week
            </span>
          </div>
        </div>

        {/* Headline */}
        <h1 style={{
          fontFamily: "'Inter', 'SF Pro Display', -apple-system, sans-serif",
          fontSize: 'clamp(3.2rem, 9vw, 6rem)',
          fontWeight: 700, lineHeight: 1.02, letterSpacing: '-0.04em',
          marginBottom: '1.5rem', color: '#1d1d1f',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.8s 0.1s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          Neat Finds,
          <br />
          <span style={{ color: '#86868b' }}>Neatly Delivered.</span>
        </h1>

        {/* Subheadline */}
        <p style={{
          fontSize: 'clamp(1.05rem, 2vw, 1.25rem)',
          color: '#6e6e73', lineHeight: 1.6,
          maxWidth: '560px', margin: '0 auto 2.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.8s 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          fontWeight: 400,
        }}>
          Trending products, curated weekly. Delivered worldwide.
        </p>

        {/* CTA */}
        <div style={{
          display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.8s 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          <a href="#products" className="hero-cta-primary shiny-btn" style={{
            background: '#1d1d1f', color: '#ffffff',
            padding: '1rem 2.5rem', borderRadius: '980px',
            fontSize: '1rem', fontWeight: 500, textDecoration: 'none',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            fontFamily: "'Inter', sans-serif",
          }}>
            Shop Now
          </a>
        </div>
      </div>

      {/* Featured Products Showcase */}
      <div className="hero-products-showcase" style={{
        display: 'flex', gap: '1.2rem', justifyContent: 'center',
        maxWidth: '900px', width: '100%',
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(30px)',
        transition: 'all 1s 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative', zIndex: 1,
        marginTop: '1rem',
      }}>
        {featured.map((product, i) => (
          <div
            key={product.id}
            onClick={() => onQuickView?.(product)}
            style={{
              flex: 1, cursor: 'pointer',
              borderRadius: '18px', overflow: 'hidden',
              background: '#f5f5f7',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.transform = 'translateY(-6px)'
              e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.1)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div style={{ height: '200px', overflow: 'hidden' }}>
              <img src={product.image} alt={product.name} loading="lazy" style={{
                width: '100%', height: '100%', objectFit: 'cover',
                transition: 'transform 0.5s ease',
              }} />
            </div>
            <div style={{ padding: '0.8rem 1rem' }}>
              <div style={{
                fontSize: '0.6rem', fontWeight: 600, color: '#86868b',
                textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.2rem',
              }}>{product.badge}</div>
              <div style={{
                fontSize: '0.92rem', fontWeight: 600, color: '#1d1d1f',
                fontFamily: "'Inter', sans-serif", marginBottom: '0.2rem',
              }}>{product.name}</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.3rem' }}>
                <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#1d1d1f' }}>
                  ${product.price}
                </span>
                <span style={{ fontSize: '0.7rem', color: '#aeaeb2', textDecoration: 'line-through' }}>
                  ${product.originalPrice}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Stats */}
      <div className="hero-stats-bar" style={{
        opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.8s 0.7s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex', justifyContent: 'center', alignItems: 'center',
        marginTop: '2.5rem',
        background: '#f5f5f7',
        borderRadius: '16px', padding: '1.5rem 0',
        maxWidth: '700px', width: '100%',
        position: 'relative', zIndex: 1,
      }}>
        {[
          { value: count.customers.toLocaleString() + '+', label: 'Happy Customers' },
          { value: count.products + '+', label: 'Curated Products' },
          { value: count.countries + '+', label: 'Countries' },
          { value: count.rating + '/5', label: 'Average Rating' },
        ].map((stat, i, arr) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ textAlign: 'center', padding: '0 clamp(1rem, 3vw, 2rem)' }}>
              <div style={{
                fontSize: 'clamp(1.3rem, 2.5vw, 1.8rem)', fontWeight: 700,
                color: '#1d1d1f', fontFamily: "'Inter', sans-serif",
                marginBottom: '0.2rem',
              }}>{stat.value}</div>
              <div style={{
                fontSize: '0.7rem', color: '#86868b', fontWeight: 500,
                letterSpacing: '0.02em',
              }}>
                {stat.label}
              </div>
            </div>
            {i < arr.length - 1 && (
              <div style={{ width: '1px', height: '32px', background: 'rgba(0,0,0,0.08)' }} />
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
