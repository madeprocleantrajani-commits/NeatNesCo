import { useState } from 'react'
import { useInView } from '../hooks'
import { PRODUCTS, CATEGORIES } from '../data'
import ProductCard from './ProductCard'

export default function Products({ onAddToCart, onQuickView, wishlist, onToggleWishlist, darkMode }) {
  const [ref, visible] = useInView()
  const [activeCategory, setActiveCategory] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')
  const [showAll, setShowAll] = useState(false)

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
      padding: '4rem 2rem 4rem', position: 'relative', zIndex: 1,
    }}>
      <div style={{ maxWidth: '1240px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '2.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s',
        }}>
          <span className="section-tag">This Week's Drops</span>
          <h2 style={{
            fontFamily: "'Playfair Display', serif", fontSize: 'clamp(2rem, 4vw, 3.5rem)',
            fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem',
            letterSpacing: '-0.03em',
          }}>
            Trending Products
          </h2>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '1.05rem', maxWidth: '500px', margin: '0 auto 2rem' }}>
            Hand-picked finds that are actually worth your money.
          </p>

          {/* Search bar */}
          <div style={{
            maxWidth: '460px', margin: '0 auto 2rem', position: 'relative',
          }}>
            <div style={{
              position: 'absolute', left: '1.2rem', top: '50%', transform: 'translateY(-50%)',
              fontSize: '1rem', opacity: 0.4,
            }}>🔍</div>
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{
                width: '100%', padding: '0.9rem 1.2rem 0.9rem 3rem',
                borderRadius: '16px', fontSize: '0.92rem',
                border: `1px solid var(--border-subtle)`,
                background: darkMode ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.02)',
                color: 'var(--text-primary)',
                outline: 'none',
                transition: 'all 0.3s',
                fontFamily: "'Inter', sans-serif",
              }}
              onFocus={e => {
                e.target.style.borderColor = 'rgba(45,106,79,0.4)'
                e.target.style.boxShadow = '0 0 0 4px rgba(45,106,79,0.08)'
              }}
              onBlur={e => {
                e.target.style.borderColor = 'var(--border-subtle)'
                e.target.style.boxShadow = 'none'
              }}
            />
          </div>
        </div>

        {/* Category filters */}
        <div style={{
          display: 'flex', gap: '0.5rem', justifyContent: 'center',
          marginBottom: '2.5rem', flexWrap: 'wrap',
          opacity: visible ? 1 : 0, transition: 'opacity 0.6s 0.2s',
        }}>
          {CATEGORIES.map(cat => (
            <button key={cat} onClick={() => { setActiveCategory(cat); setShowAll(false) }} style={{
              background: activeCategory === cat
                ? 'linear-gradient(135deg, #2d6a4f, #52b788)'
                : (darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)'),
              color: activeCategory === cat ? '#fff' : 'var(--text-secondary)',
              border: 'none', padding: '0.55rem 1.3rem', borderRadius: '100px',
              fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: activeCategory === cat ? '0 4px 16px rgba(45,106,79,0.25)' : 'none',
            }}>
              {cat}
            </button>
          ))}
        </div>

        {/* Products grid */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '1.5rem',
        }}>
          {displayed.map((product, i) => (
            <ProductCard
              key={product.id}
              product={product}
              delay={i}
              onAddToCart={onAddToCart}
              onQuickView={onQuickView}
              isWishlisted={wishlist.includes(product.id)}
              onToggleWishlist={onToggleWishlist}
              darkMode={darkMode}
            />
          ))}
        </div>

        {/* Empty state */}
        {filtered.length === 0 && (
          <div style={{
            textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-tertiary)',
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
            <p style={{ fontSize: '1.1rem', fontWeight: 600 }}>No products found</p>
            <p style={{ fontSize: '0.9rem' }}>Try a different search or category</p>
          </div>
        )}

        {/* Show more */}
        {!showAll && filtered.length > 8 && (
          <div style={{ textAlign: 'center', marginTop: '3rem' }}>
            <button onClick={() => setShowAll(true)} style={{
              background: 'transparent',
              color: 'var(--text-primary)',
              border: `2px solid var(--border-subtle)`,
              padding: '0.9rem 2.5rem', borderRadius: '100px',
              fontSize: '0.95rem', fontWeight: 600, cursor: 'pointer',
              transition: 'all 0.3s',
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            }}>
              View All Products
              <span style={{
                background: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
                padding: '0.15rem 0.6rem', borderRadius: '100px', fontSize: '0.78rem',
              }}>{filtered.length}</span>
            </button>
          </div>
        )}
      </div>
    </section>
  )
}
