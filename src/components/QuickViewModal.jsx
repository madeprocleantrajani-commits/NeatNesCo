import { useState } from 'react'

export default function QuickViewModal({ product, onClose, onAddToCart, darkMode }) {
  const [qty, setQty] = useState(1)
  const [added, setAdded] = useState(false)

  if (!product) return null

  const discount = Math.round((1 - product.price / product.originalPrice) * 100)

  const handleAdd = () => {
    for (let i = 0; i < qty; i++) onAddToCart(product)
    setAdded(true)
    setTimeout(() => { setAdded(false); onClose() }, 1200)
  }

  return (
    <div onClick={onClose} style={{
      position: 'fixed', inset: 0, zIndex: 9000,
      background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '2rem',
      animation: 'modalOverlayIn 0.3s ease-out',
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: 'var(--bg-card)',
        borderRadius: '28px',
        maxWidth: '720px', width: '100%',
        maxHeight: '85vh',
        overflow: 'auto',
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        border: '1px solid var(--border-subtle)',
        boxShadow: '0 32px 80px rgba(0,0,0,0.3)',
        animation: 'modalContentIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
        position: 'relative',
      }}>
        {/* Close button */}
        <button onClick={onClose} style={{
          position: 'absolute', top: '1rem', right: '1rem', zIndex: 10,
          width: '36px', height: '36px', borderRadius: '50%',
          background: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
          border: 'none', cursor: 'pointer', fontSize: '1rem',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'all 0.2s',
          color: 'var(--text-primary)',
        }}>✕</button>

        {/* Product image */}
        <div style={{
          background: product.gradient,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          padding: '3rem', minHeight: '320px', position: 'relative',
          borderRadius: '28px 0 0 28px',
        }}>
          <div style={{
            position: 'absolute', inset: 0,
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E")`,
            borderRadius: 'inherit', opacity: 0.5,
          }} />
          <span style={{
            fontSize: '7rem',
            filter: 'drop-shadow(0 12px 32px rgba(0,0,0,0.15))',
          }}>
            {product.emoji}
          </span>
          {product.badge && (
            <span style={{
              position: 'absolute', top: '1.5rem', left: '1.5rem',
              background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)',
              color: '#fff', padding: '0.4rem 1rem', borderRadius: '100px',
              fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}>
              {product.badge}
            </span>
          )}
        </div>

        {/* Product details */}
        <div style={{ padding: '2.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{
            fontSize: '0.7rem', color: '#2d6a4f', textTransform: 'uppercase',
            letterSpacing: '0.12em', fontWeight: 700,
            display: 'flex', alignItems: 'center', gap: '0.5rem',
          }}>
            <span style={{ width: '16px', height: '1.5px', background: '#2d6a4f' }} />
            {product.category}
          </div>

          <h2 style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: '1.8rem', fontWeight: 700,
            color: 'var(--text-primary)', letterSpacing: '-0.02em', lineHeight: 1.2,
          }}>
            {product.name}
          </h2>

          {/* Rating */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="star-rating" style={{ fontSize: '0.9rem', letterSpacing: '2px' }}>
              {'★'.repeat(Math.round(product.rating))}{'☆'.repeat(5 - Math.round(product.rating))}
            </span>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              {product.rating}
            </span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              ({product.reviews?.toLocaleString()} reviews)
            </span>
          </div>

          <p style={{
            fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.7,
          }}>
            {product.description}
          </p>

          {/* Features */}
          {product.features && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {product.features.map((feat, i) => (
                <span key={i} style={{
                  background: darkMode ? 'rgba(45,106,79,0.12)' : 'rgba(45,106,79,0.06)',
                  color: '#2d6a4f', padding: '0.3rem 0.8rem', borderRadius: '100px',
                  fontSize: '0.75rem', fontWeight: 600,
                  border: '1px solid rgba(45,106,79,0.1)',
                }}>
                  {feat}
                </span>
              ))}
            </div>
          )}

          {/* Price */}
          <div style={{
            display: 'flex', alignItems: 'baseline', gap: '0.8rem',
            marginTop: '0.5rem',
          }}>
            <span style={{
              fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)',
            }}>
              ${product.price}
            </span>
            <span style={{
              fontSize: '1.1rem', color: 'var(--text-muted)', textDecoration: 'line-through',
            }}>
              ${product.originalPrice}
            </span>
            <span style={{
              background: 'rgba(230,57,70,0.1)', color: '#e63946',
              padding: '0.2rem 0.7rem', borderRadius: '100px',
              fontSize: '0.78rem', fontWeight: 700,
            }}>
              Save {discount}%
            </span>
          </div>

          {/* Quantity + Add */}
          <div style={{
            display: 'flex', gap: '0.75rem', alignItems: 'center',
            marginTop: '0.5rem',
          }}>
            <div style={{
              display: 'flex', alignItems: 'center',
              background: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
              borderRadius: '12px', overflow: 'hidden',
              border: '1px solid var(--border-subtle)',
            }}>
              <button onClick={() => setQty(Math.max(1, qty - 1))} style={{
                width: '40px', height: '40px', border: 'none',
                background: 'transparent', cursor: 'pointer', fontSize: '1.1rem',
                color: 'var(--text-primary)', fontWeight: 600,
              }}>−</button>
              <span style={{
                padding: '0 0.8rem', fontWeight: 700, fontSize: '0.9rem',
                color: 'var(--text-primary)',
              }}>{qty}</span>
              <button onClick={() => setQty(qty + 1)} style={{
                width: '40px', height: '40px', border: 'none',
                background: 'transparent', cursor: 'pointer', fontSize: '1.1rem',
                color: 'var(--text-primary)', fontWeight: 600,
              }}>+</button>
            </div>
            <button onClick={handleAdd} style={{
              flex: 1, padding: '0.85rem 2rem', borderRadius: '12px',
              background: added ? 'linear-gradient(135deg, #2d6a4f, #52b788)' : 'linear-gradient(135deg, #2d6a4f, #40916c)',
              color: '#fff', border: 'none', fontSize: '0.95rem', fontWeight: 700,
              cursor: 'pointer', transition: 'all 0.3s',
              boxShadow: '0 4px 16px rgba(45,106,79,0.3)',
            }}>
              {added ? '✓ Added to Cart!' : `Add to Cart — $${(product.price * qty).toFixed(2)}`}
            </button>
          </div>

          {/* Trust signals */}
          <div style={{
            display: 'flex', gap: '1rem', marginTop: '0.5rem', flexWrap: 'wrap',
          }}>
            {['🚚 Free Shipping', '↩️ 30-Day Returns', '🔒 Secure Checkout'].map((item, i) => (
              <span key={i} style={{
                fontSize: '0.72rem', color: 'var(--text-tertiary)', fontWeight: 500,
              }}>
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
