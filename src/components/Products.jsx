import { useState, useEffect } from 'react'
import { useInView } from '../hooks'
import { PRODUCTS, CATEGORIES } from '../data'
import ProductCard from './ProductCard'

export default function Products({ onAddToCart, onQuickView, wishlist, onToggleWishlist, externalCategory }) {
  const [ref, visible] = useInView()
  const [activeCategory, setActiveCategory] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')
  const [showAll, setShowAll] = useState(false)

  useEffect(() => {
    if (externalCategory) {
      setActiveCategory(externalCategory)
      setShowAll(false)
    }
  }, [externalCategory])

  const filtered = PRODUCTS
    .filter(p => activeCategory === 'All' || p.category === activeCategory)
    .filter(p => {
      if (!searchQuery) return true
      const q = searchQuery.toLowerCase()
      return p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q) || p.category.toLowerCase().includes(q)
    })

  const displayed = showAll ? filtered : filtered.slice(0, 8)

  return (
    <section id="products" style={{
      padding: '5rem 2rem', background: '#ffffff',
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '2.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(15px)',
          transition: 'all 0.6s',
        }}>
          <p style={{
            fontSize: '0.8rem', fontWeight: 500, color: '#86868b',
            letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.6rem',
          }}>This Week's Drops</p>
          <h2 style={{
            fontFamily: "'Inter', -apple-system, sans-serif",
            fontSize: 'clamp(2.4rem, 5vw, 3.5rem)',
            fontWeight: 700, color: '#1d1d1f', marginBottom: '0.6rem',
            letterSpacing: '-0.03em',
          }}>
            Trending Products
          </h2>
          <div style={{ marginBottom: '1.5rem' }} />

          {/* Search */}
          <div style={{ maxWidth: '420px', margin: '0 auto 2rem' }}>
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{
                width: '100%', padding: '0.8rem 1.2rem',
                borderRadius: '12px', fontSize: '0.88rem',
                border: '1px solid rgba(0,0,0,0.1)',
                background: '#ffffff', color: '#1d1d1f',
                outline: 'none', transition: 'all 0.2s',
                fontFamily: "'Inter', sans-serif",
              }}
              onFocus={e => {
                e.target.style.borderColor = 'rgba(0,0,0,0.3)'
                e.target.style.boxShadow = '0 0 0 3px rgba(0,0,0,0.04)'
              }}
              onBlur={e => {
                e.target.style.borderColor = 'rgba(0,0,0,0.1)'
                e.target.style.boxShadow = 'none'
              }}
            />
          </div>
        </div>

        {/* Category filters */}
        <div style={{
          display: 'flex', gap: '0.3rem', justifyContent: 'center',
          marginBottom: '2.5rem', flexWrap: 'wrap',
          opacity: visible ? 1 : 0, transition: 'opacity 0.6s 0.2s',
        }}>
          {CATEGORIES.map(cat => (
            <button key={cat} onClick={() => { setActiveCategory(cat); setShowAll(false) }} style={{
              background: activeCategory === cat ? '#1d1d1f' : 'transparent',
              color: activeCategory === cat ? '#fff' : '#6e6e73',
              border: 'none', padding: '0.45rem 1rem', borderRadius: '980px',
              fontSize: '0.8rem', fontWeight: 500, cursor: 'pointer',
              transition: 'all 0.2s', fontFamily: "'Inter', sans-serif",
            }}>
              {cat}
            </button>
          ))}
        </div>

        {/* Grid */}
        <div className="products-grid" style={{
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1.2rem',
        }}>
          {displayed.map((product, i) => (
            <ProductCard
              key={product.id} product={product} delay={i}
              onAddToCart={onAddToCart} onQuickView={onQuickView}
              isWishlisted={wishlist.includes(product.id)}
              onToggleWishlist={onToggleWishlist}
            />
          ))}
        </div>

        {filtered.length === 0 && (
          <div style={{ textAlign: 'center', padding: '4rem 2rem', color: '#86868b' }}>
            <p style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '0.3rem' }}>No products found</p>
            <p style={{ fontSize: '0.88rem' }}>Try a different search or category</p>
          </div>
        )}

        {!showAll && filtered.length > 8 && (
          <div style={{ textAlign: 'center', marginTop: '3rem' }}>
            <button onClick={() => setShowAll(true)} style={{
              background: 'transparent', color: '#1d1d1f',
              border: 'none', padding: '0.8rem 0', fontSize: '0.95rem',
              fontWeight: 500, cursor: 'pointer', fontFamily: "'Inter', sans-serif",
            }}>
              View all {filtered.length} products →
            </button>
          </div>
        )}
      </div>
    </section>
  )
}
