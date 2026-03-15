import { useState, useRef } from 'react'
import { useInView } from '../hooks'
import ProductImage from './ProductImage'

export default function ProductCard({ product, delay, onAddToCart, onQuickView, isWishlisted, onToggleWishlist }) {
  const [ref, visible] = useInView()
  const cardRef = useRef(null)
  const [hovered, setHovered] = useState(false)
  const [added, setAdded] = useState(false)
  const [quickAdded, setQuickAdded] = useState(false)

  const discount = Math.round((1 - product.price / product.originalPrice) * 100)
  const stockLeft = ((product.id * 7 + 3) % 20) + 1

  const handleAdd = (e) => {
    e.stopPropagation()
    setAdded(true)
    onAddToCart(product)
    setTimeout(() => setAdded(false), 1500)
  }

  const handleQuickAdd = (e) => {
    e.stopPropagation()
    setQuickAdded(true)
    onAddToCart(product)
    setTimeout(() => setQuickAdded(false), 1200)
  }

  // Urgency signal logic
  const getUrgencySignal = () => {
    if (stockLeft <= 5) {
      return <span style={{ color: '#ff3b30' }}>Only {stockLeft} left in stock</span>
    }
    if (product.reviews > 3000) {
      return <span style={{ color: '#86868b' }}>{product.reviews.toLocaleString()} sold</span>
    }
    if (product.reviews > 1500) {
      return <span style={{ color: '#86868b' }}>Trending this week</span>
    }
    return null
  }

  const urgency = getUrgencySignal()

  return (
    <div
      ref={el => { ref.current = el; cardRef.current = el }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => onQuickView(product)}
      className="product-card"
      style={{
        position: 'relative', borderRadius: '18px', overflow: 'hidden',
        background: '#ffffff',
        border: '1px solid rgba(0,0,0,0.06)',
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        opacity: visible ? 1 : 0,
        transitionDelay: visible ? `${delay * 0.05}s` : '0s',
        cursor: 'pointer',
      }}
    >
      {/* Product image */}
      <div style={{
        height: '320px', position: 'relative', overflow: 'hidden',
        background: '#f5f5f7',
      }}>
        <ProductImage
          src={product.image}
          hoverSrc={product.images?.[1]}
          alt={product.name}
          hovered={hovered}
          style={{ borderRadius: 0 }}
        />

        {/* Badge */}
        {product.badge && (
          <span style={{
            position: 'absolute', top: '0.8rem', left: '0.8rem',
            background: '#1d1d1f',
            color: '#fff', padding: '0.25rem 0.7rem', borderRadius: '980px',
            fontSize: '0.65rem', fontWeight: 600, letterSpacing: '0.02em',
            zIndex: 4,
          }}>
            {product.badge}
          </span>
        )}

        {/* Discount */}
        <span style={{
          position: 'absolute', top: '0.8rem', right: '0.8rem',
          background: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(8px)',
          color: '#1d1d1f', padding: '0.2rem 0.6rem', borderRadius: '980px',
          fontSize: '0.7rem', fontWeight: 600, zIndex: 4,
        }}>
          -{discount}%
        </span>

        {/* Quick view label */}
        <div style={{
          position: 'absolute', bottom: '0.8rem', left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(8px)',
          color: '#1d1d1f', padding: '0.3rem 0.9rem', borderRadius: '980px',
          fontSize: '0.7rem', fontWeight: 500, zIndex: 4,
          opacity: hovered ? 1 : 0, transition: 'all 0.3s',
        }}>
          Quick View
        </div>

        {/* Quick-add "+" button */}
        <button
          onClick={handleQuickAdd}
          className="quick-add-btn"
          style={{
            position: 'absolute', bottom: '0.8rem', right: '0.8rem',
            width: '36px', height: '36px', borderRadius: '50%',
            background: quickAdded ? '#1d1d1f' : 'rgba(255,255,255,0.92)',
            backdropFilter: 'blur(8px)',
            border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.1rem', fontWeight: 300,
            color: quickAdded ? '#fff' : '#1d1d1f',
            transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
            opacity: hovered ? 1 : 0,
            transform: hovered ? 'scale(1)' : 'scale(0.8)',
            zIndex: 5,
            fontFamily: "'Inter', sans-serif",
          }}
          onMouseEnter={e => {
            if (!quickAdded) {
              e.currentTarget.style.background = '#1d1d1f'
              e.currentTarget.style.color = '#fff'
            }
          }}
          onMouseLeave={e => {
            if (!quickAdded) {
              e.currentTarget.style.background = 'rgba(255,255,255,0.92)'
              e.currentTarget.style.color = '#1d1d1f'
            }
          }}
        >
          {quickAdded ? '\u2713' : '+'}
        </button>
      </div>

      {/* Product info */}
      <div style={{ padding: '1.2rem 1rem' }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          marginBottom: '0.3rem',
        }}>
          <div style={{
            fontSize: '0.65rem', color: '#86868b', textTransform: 'uppercase',
            letterSpacing: '0.08em', fontWeight: 500,
          }}>
            {product.category}
          </div>
          {product.rating && (
            <div style={{
              fontSize: '0.72rem', color: '#86868b', fontWeight: 400,
              display: 'flex', alignItems: 'center', gap: '0.2rem',
            }}>
              {product.rating}
              <span style={{ color: '#aeaeb2', fontWeight: 400 }}>
                ({product.reviews?.toLocaleString()})
              </span>
            </div>
          )}
        </div>

        <h3 style={{
          fontSize: '1.08rem', fontWeight: 600, marginBottom: '0.3rem',
          color: '#1d1d1f', letterSpacing: '-0.01em',
          fontFamily: "'Inter', sans-serif",
        }}>
          {product.name}
        </h3>
        <p style={{
          fontSize: '0.88rem', color: '#6e6e73', lineHeight: 1.5,
          marginBottom: '0.6rem',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
        }}>
          {product.description}
        </p>

        {/* Urgency signal */}
        {urgency && (
          <p style={{
            fontSize: '0.7rem', fontWeight: 500,
            marginBottom: '0.6rem',
          }}>
            {urgency}
          </p>
        )}

        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem' }}>
            <span style={{
              fontSize: '1.25rem', fontWeight: 700, color: '#1d1d1f',
            }}>
              ${product.price}
            </span>
            <span style={{
              fontSize: '0.75rem', color: '#aeaeb2', textDecoration: 'line-through',
            }}>
              ${product.originalPrice}
            </span>
          </div>
          <button onClick={handleAdd} style={{
            background: '#1d1d1f',
            color: '#fff',
            border: 'none',
            padding: '0.5rem 1.2rem', borderRadius: '980px', fontSize: '0.78rem',
            fontWeight: 500, cursor: 'pointer',
            transition: 'all 0.3s',
            fontFamily: "'Inter', sans-serif",
          }}>
            {added ? 'Added' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  )
}
