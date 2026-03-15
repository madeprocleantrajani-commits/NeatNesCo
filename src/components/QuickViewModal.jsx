import { useState, useRef, useEffect, useCallback } from 'react'

export default function QuickViewModal({ product, onClose, onAddToCart }) {
  const [qty, setQty] = useState(1)
  const [added, setAdded] = useState(false)
  const [activeImage, setActiveImage] = useState(0)
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageError, setImageError] = useState(false)
  const [selectedColor, setSelectedColor] = useState(0)
  const [showStickyBar, setShowStickyBar] = useState(false)
  const addBtnRef = useRef(null)
  const modalRef = useRef(null)

  useEffect(() => {
    const scrollEl = modalRef.current
    const btnEl = addBtnRef.current
    if (!scrollEl || !btnEl) return
    const observer = new IntersectionObserver(
      ([entry]) => setShowStickyBar(!entry.isIntersecting),
      { root: scrollEl, threshold: 0 }
    )
    observer.observe(btnEl)
    return () => observer.disconnect()
  }, [product])

  if (!product) return null

  const discount = Math.round((1 - product.price / product.originalPrice) * 100)
  const images = product.images || [product.image]

  const handleAdd = () => {
    for (let i = 0; i < qty; i++) onAddToCart(product)
    setAdded(true)
    setTimeout(() => { setAdded(false); onClose() }, 1200)
  }

  const nextImage = (e) => {
    e.stopPropagation()
    setImageLoaded(false)
    setActiveImage((activeImage + 1) % images.length)
  }

  const prevImage = (e) => {
    e.stopPropagation()
    setImageLoaded(false)
    setActiveImage((activeImage - 1 + images.length) % images.length)
  }

  return (
    <div onClick={onClose} style={{
      position: 'fixed', inset: 0, zIndex: 9000,
      background: 'rgba(0,0,0,0.3)', backdropFilter: 'blur(20px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '2rem',
      animation: 'modalOverlayIn 0.3s ease-out',
    }}>
      <div ref={modalRef} onClick={e => e.stopPropagation()} style={{
        background: '#ffffff',
        borderRadius: '20px',
        maxWidth: '800px', width: '100%',
        maxHeight: '85vh', overflow: 'auto',
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        boxShadow: '0 24px 60px rgba(0,0,0,0.15)',
        animation: 'modalContentIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
        position: 'relative',
      }}>
        {/* Close */}
        <button onClick={onClose} style={{
          position: 'absolute', top: '0.8rem', right: '0.8rem', zIndex: 10,
          width: '32px', height: '32px', borderRadius: '50%',
          background: 'rgba(0,0,0,0.04)',
          border: 'none', cursor: 'pointer', fontSize: '0.85rem',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#1d1d1f',
        }}>×</button>

        {/* Image */}
        <div style={{
          position: 'relative', minHeight: '380px', overflow: 'hidden',
          borderRadius: '20px 0 0 20px',
          background: '#f5f5f7',
        }}>
          {!imageError && (
            <img
              key={activeImage}
              src={images[activeImage]}
              alt={`${product.name} - view ${activeImage + 1}`}
              onLoad={() => setImageLoaded(true)}
              onError={() => setImageError(true)}
              style={{
                position: 'absolute', inset: 0,
                width: '100%', height: '100%', objectFit: 'cover',
                opacity: imageLoaded ? 1 : 0,
                transition: 'opacity 0.4s ease',
              }}
            />
          )}

          {images.length > 1 && (
            <>
              <button onClick={prevImage} style={{
                position: 'absolute', left: '0.6rem', top: '50%', transform: 'translateY(-50%)',
                width: '32px', height: '32px', borderRadius: '50%',
                background: 'rgba(255,255,255,0.9)', border: 'none', cursor: 'pointer',
                fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 1px 6px rgba(0,0,0,0.1)', zIndex: 5, color: '#1d1d1f',
              }}>‹</button>
              <button onClick={nextImage} style={{
                position: 'absolute', right: '0.6rem', top: '50%', transform: 'translateY(-50%)',
                width: '32px', height: '32px', borderRadius: '50%',
                background: 'rgba(255,255,255,0.9)', border: 'none', cursor: 'pointer',
                fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 1px 6px rgba(0,0,0,0.1)', zIndex: 5, color: '#1d1d1f',
              }}>›</button>
            </>
          )}

          {product.badge && (
            <span style={{
              position: 'absolute', top: '1rem', left: '1rem', zIndex: 5,
              background: '#1d1d1f', color: '#fff',
              padding: '0.3rem 0.8rem', borderRadius: '980px',
              fontSize: '0.68rem', fontWeight: 600,
            }}>
              {product.badge}
            </span>
          )}

          {images.length > 1 && (
            <div style={{
              position: 'absolute', bottom: '1rem', left: '50%', transform: 'translateX(-50%)',
              display: 'flex', gap: '0.35rem', zIndex: 5,
            }}>
              {images.map((_, i) => (
                <div key={i} onClick={(e) => { e.stopPropagation(); setImageLoaded(false); setActiveImage(i) }}
                  style={{
                    width: i === activeImage ? '16px' : '6px', height: '6px',
                    borderRadius: '3px', cursor: 'pointer',
                    background: i === activeImage ? '#1d1d1f' : 'rgba(0,0,0,0.2)',
                    transition: 'all 0.3s',
                }} />
              ))}
            </div>
          )}
        </div>

        {/* Details */}
        <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
          <div style={{
            fontSize: '0.68rem', color: '#86868b', textTransform: 'uppercase',
            letterSpacing: '0.08em', fontWeight: 500,
          }}>
            {product.category}
          </div>

          <h2 style={{
            fontFamily: "'Inter', -apple-system, sans-serif",
            fontSize: '1.5rem', fontWeight: 600,
            color: '#1d1d1f', letterSpacing: '-0.02em', lineHeight: 1.2,
          }}>
            {product.name}
          </h2>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.82rem', color: '#ff9500', letterSpacing: '1px' }}>
              {'★'.repeat(Math.round(product.rating))}{'☆'.repeat(5 - Math.round(product.rating))}
            </span>
            <span style={{ fontSize: '0.82rem', fontWeight: 500, color: '#6e6e73' }}>
              {product.rating}
            </span>
            <span style={{ fontSize: '0.78rem', color: '#aeaeb2' }}>
              ({product.reviews?.toLocaleString()} reviews)
            </span>
          </div>

          <p style={{ fontSize: '0.9rem', color: '#6e6e73', lineHeight: 1.6 }}>
            {product.description}
          </p>

          {/* Colors */}
          {product.colors && product.colors.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#86868b', fontWeight: 500 }}>Color:</span>
              <div style={{ display: 'flex', gap: '0.4rem' }}>
                {product.colors.map((color, i) => (
                  <button key={i} onClick={() => setSelectedColor(i)} style={{
                    width: '24px', height: '24px', borderRadius: '50%',
                    background: color,
                    border: i === selectedColor ? '2px solid #1d1d1f' : '2px solid rgba(0,0,0,0.1)',
                    cursor: 'pointer', padding: 0,
                    boxShadow: i === selectedColor ? '0 0 0 2px rgba(0,0,0,0.1)' : 'none',
                  }} />
                ))}
              </div>
            </div>
          )}

          {/* Features */}
          {product.features && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {product.features.map((feat, i) => (
                <span key={i} style={{
                  background: '#f5f5f7', color: '#6e6e73',
                  padding: '0.25rem 0.7rem', borderRadius: '980px',
                  fontSize: '0.72rem', fontWeight: 500,
                }}>
                  {feat}
                </span>
              ))}
            </div>
          )}

          {/* Price */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.6rem', marginTop: '0.3rem' }}>
            <span style={{ fontSize: '1.6rem', fontWeight: 600, color: '#1d1d1f' }}>
              ${product.price}
            </span>
            <span style={{ fontSize: '1rem', color: '#aeaeb2', textDecoration: 'line-through' }}>
              ${product.originalPrice}
            </span>
            <span style={{
              background: '#f5f5f7', color: '#1d1d1f',
              padding: '0.15rem 0.5rem', borderRadius: '980px',
              fontSize: '0.72rem', fontWeight: 600,
            }}>
              Save {discount}%
            </span>
          </div>

          {/* Qty + Add */}
          <div ref={addBtnRef} style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', marginTop: '0.3rem' }}>
            <div style={{
              display: 'flex', alignItems: 'center',
              background: '#f5f5f7',
              borderRadius: '10px', overflow: 'hidden',
            }}>
              <button onClick={() => setQty(Math.max(1, qty - 1))} style={{
                width: '36px', height: '36px', border: 'none',
                background: 'transparent', cursor: 'pointer', fontSize: '1rem',
                color: '#1d1d1f', fontWeight: 400,
              }}>−</button>
              <span style={{ padding: '0 0.6rem', fontWeight: 600, fontSize: '0.85rem', color: '#1d1d1f' }}>{qty}</span>
              <button onClick={() => setQty(qty + 1)} style={{
                width: '36px', height: '36px', border: 'none',
                background: 'transparent', cursor: 'pointer', fontSize: '1rem',
                color: '#1d1d1f', fontWeight: 400,
              }}>+</button>
            </div>
            <button onClick={handleAdd} style={{
              flex: 1, padding: '0.75rem 1.5rem', borderRadius: '10px',
              background: '#1d1d1f', color: '#fff',
              border: 'none', fontSize: '0.9rem', fontWeight: 500,
              cursor: 'pointer', transition: 'all 0.2s',
              fontFamily: "'Inter', sans-serif",
            }}>
              {added ? 'Added to Cart' : `Add to Cart — $${(product.price * qty).toFixed(2)}`}
            </button>
          </div>

          {/* Trust */}
          <div style={{ display: 'flex', gap: '1rem', marginTop: '0.3rem', flexWrap: 'wrap' }}>
            {['Free Shipping', '30-Day Returns', 'Secure Checkout'].map((item, i) => (
              <span key={i} style={{ fontSize: '0.7rem', color: '#aeaeb2', fontWeight: 500 }}>
                {item}
              </span>
            ))}
          </div>
        </div>

        {/* Sticky add-to-cart bar */}
        {showStickyBar && !added && (
          <div style={{
            position: 'sticky', bottom: 0, left: 0, right: 0,
            gridColumn: '1 / -1',
            background: 'rgba(255,255,255,0.92)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            borderTop: '1px solid rgba(0,0,0,0.06)',
            padding: '0.8rem 1.5rem',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem',
            borderRadius: '0 0 20px 20px',
            animation: 'stickyBarIn 0.3s ease-out',
          }}>
            <div style={{ minWidth: 0 }}>
              <p style={{
                fontSize: '0.82rem', fontWeight: 600, color: '#1d1d1f',
                whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              }}>{product.name}</p>
              <p style={{ fontSize: '0.85rem', fontWeight: 600, color: '#1d1d1f' }}>
                ${product.price}
              </p>
            </div>
            <button onClick={handleAdd} style={{
              padding: '0.65rem 1.5rem', borderRadius: '10px',
              background: '#1d1d1f', color: '#fff',
              border: 'none', fontSize: '0.85rem', fontWeight: 500,
              cursor: 'pointer', fontFamily: "'Inter', sans-serif",
              whiteSpace: 'nowrap', flexShrink: 0,
            }}>
              Add to Cart
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
