import { useState, useRef } from 'react'
import { useInView } from '../hooks'

export default function ProductCard({ product, delay, onAddToCart, onQuickView, isWishlisted, onToggleWishlist, darkMode }) {
  const [ref, visible] = useInView()
  const cardRef = useRef(null)
  const [hovered, setHovered] = useState(false)
  const [added, setAdded] = useState(false)

  const discount = Math.round((1 - product.price / product.originalPrice) * 100)

  const handleMouseMove = (e) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width
    const y = (e.clientY - rect.top) / rect.height
    const rotateX = (0.5 - y) * 8
    const rotateY = (x - 0.5) * 8
    cardRef.current.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px) scale(1.02)`
    cardRef.current.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
    cardRef.current.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
  }

  const handleMouseLeave = () => {
    setHovered(false)
    if (cardRef.current) {
      cardRef.current.style.transform = 'perspective(800px) rotateX(0) rotateY(0) translateY(0) scale(1)'
    }
  }

  const handleAdd = (e) => {
    e.stopPropagation()
    setAdded(true)
    onAddToCart(product)
    setTimeout(() => setAdded(false), 1500)
  }

  const badgeColors = {
    'Best Seller': 'linear-gradient(135deg, #2d6a4f, #52b788)',
    'Trending': 'linear-gradient(135deg, #e76f51, #f4a261)',
    'New': 'linear-gradient(135deg, #264653, #2a9d8f)',
    'Hot Deal': 'linear-gradient(135deg, #e63946, #f4845f)',
    'Flash Sale': 'linear-gradient(135deg, #7209b7, #b5179e)',
    'Exclusive': 'linear-gradient(135deg, #1a1a1a, #444)',
    'Popular': 'linear-gradient(135deg, #457b9d, #1d3557)',
    'Staff Pick': 'linear-gradient(135deg, #2d6a4f, #40916c)',
  }

  return (
    <div
      ref={el => { ref.current = el; cardRef.current = el }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={handleMouseLeave}
      onClick={() => onQuickView(product)}
      className="product-card"
      style={{
        position: 'relative', borderRadius: '24px', overflow: 'hidden',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        transformStyle: 'preserve-3d',
        transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        opacity: visible ? 1 : 0,
        transitionDelay: visible ? `${delay * 0.06}s` : '0s',
        boxShadow: hovered ? 'var(--shadow-lg)' : 'var(--shadow-sm)',
        cursor: 'pointer',
        willChange: 'transform',
      }}
    >
      {/* Spotlight overlay */}
      <div className="card-spotlight" style={{
        position: 'absolute', inset: 0, borderRadius: '24px',
        opacity: hovered ? 1 : 0, transition: 'opacity 0.4s', pointerEvents: 'none', zIndex: 2,
      }} />

      {/* Product visual */}
      <div style={{
        height: '240px', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: product.gradient, position: 'relative', overflow: 'hidden',
      }}>
        {/* Noise overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E")`,
          opacity: 0.5,
        }} />

        <span style={{
          fontSize: '5rem', filter: 'drop-shadow(0 8px 24px rgba(0,0,0,0.15))',
          transition: 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
          transform: hovered ? 'scale(1.25) rotate(-5deg) translateY(-5px)' : 'scale(1)',
        }}>
          {product.emoji}
        </span>

        {/* Badge */}
        {product.badge && (
          <span style={{
            position: 'absolute', top: '1rem', left: '1rem',
            background: badgeColors[product.badge] || '#6c757d',
            color: '#fff', padding: '0.35rem 0.9rem', borderRadius: '100px',
            fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.05em',
            textTransform: 'uppercase',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
          }}>
            {product.badge}
          </span>
        )}

        {/* Discount badge */}
        <span style={{
          position: 'absolute', top: '1rem', right: '1rem',
          background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(8px)',
          color: '#e63946', padding: '0.3rem 0.7rem', borderRadius: '100px',
          fontSize: '0.75rem', fontWeight: 800,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          -{discount}%
        </span>

        {/* Wishlist heart */}
        <button onClick={(e) => { e.stopPropagation(); onToggleWishlist(product.id) }} style={{
          position: 'absolute', bottom: '1rem', right: '1rem',
          background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(8px)',
          border: 'none', borderRadius: '50%',
          width: '36px', height: '36px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', fontSize: '1rem',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          transition: 'all 0.3s',
          transform: hovered ? 'scale(1)' : 'scale(0.8)',
          opacity: hovered || isWishlisted ? 1 : 0,
          animation: isWishlisted ? 'heartBeat 0.5s ease-in-out' : 'none',
        }}>
          {isWishlisted ? '❤️' : '🤍'}
        </button>

        {/* Quick view hint */}
        <div style={{
          position: 'absolute', bottom: '1rem', left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)',
          color: '#fff', padding: '0.35rem 1rem', borderRadius: '100px',
          fontSize: '0.72rem', fontWeight: 600,
          opacity: hovered ? 1 : 0, transition: 'all 0.3s',
          letterSpacing: '0.03em',
        }}>
          Quick View
        </div>
      </div>

      {/* Product info */}
      <div style={{ padding: '1.5rem' }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          marginBottom: '0.5rem',
        }}>
          <div style={{
            fontSize: '0.68rem', color: '#2d6a4f', textTransform: 'uppercase',
            letterSpacing: '0.1em', fontWeight: 700,
            display: 'flex', alignItems: 'center', gap: '0.4rem',
          }}>
            <span style={{ width: '12px', height: '1.5px', background: '#2d6a4f', borderRadius: '1px' }} />
            {product.category}
          </div>
          {product.rating && (
            <div style={{
              fontSize: '0.75rem', color: 'var(--text-tertiary)', fontWeight: 600,
              display: 'flex', alignItems: 'center', gap: '0.3rem',
            }}>
              <span className="star-rating">★</span> {product.rating}
              <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>
                ({product.reviews?.toLocaleString()})
              </span>
            </div>
          )}
        </div>

        <h3 style={{
          fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.4rem',
          color: 'var(--text-primary)', letterSpacing: '-0.01em',
        }}>
          {product.name}
        </h3>
        <p style={{
          fontSize: '0.86rem', color: 'var(--text-tertiary)', lineHeight: 1.55,
          marginBottom: '1.2rem',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
        }}>
          {product.description}
        </p>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
            <span style={{
              fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)',
            }}>
              ${product.price}
            </span>
            <span style={{
              fontSize: '0.85rem', color: 'var(--text-muted)', textDecoration: 'line-through',
            }}>
              ${product.originalPrice}
            </span>
          </div>
          <button onClick={handleAdd} style={{
            background: added ? 'linear-gradient(135deg, #2d6a4f, #52b788)' : (hovered ? 'linear-gradient(135deg, #2d6a4f, #52b788)' : (darkMode ? '#fff' : '#1a1a1a')),
            color: added || hovered ? '#fff' : (darkMode ? '#1a1a1a' : '#fff'),
            border: 'none',
            padding: '0.65rem 1.5rem', borderRadius: '100px', fontSize: '0.82rem',
            fontWeight: 600, cursor: 'pointer',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            transform: added ? 'scale(0.95)' : 'scale(1)',
            boxShadow: hovered ? '0 4px 16px rgba(45,106,79,0.3)' : 'none',
          }}>
            {added ? '✓ Added!' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  )
}
