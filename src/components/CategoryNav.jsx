import { useInView } from '../hooks'

const CATEGORY_IMAGES = [
  { name: 'Home', image: 'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=400&q=80' },
  { name: 'Tech', image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80' },
  { name: 'Kitchen', image: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80' },
  { name: 'Bedroom', image: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=400&q=80' },
  { name: 'Office', image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&q=80' },
  { name: 'Lifestyle', image: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&q=80' },
]

export default function CategoryNav({ onCategorySelect }) {
  const [ref, visible] = useInView()

  const handleClick = (cat) => {
    onCategorySelect(cat)
    document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section ref={ref} style={{
      padding: '3rem 2rem',
      background: '#ffffff',
      opacity: visible ? 1 : 0,
      transform: visible ? 'translateY(0)' : 'translateY(15px)',
      transition: 'all 0.6s',
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <p style={{
          fontSize: '0.8rem', fontWeight: 500, color: '#86868b',
          letterSpacing: '0.06em', textTransform: 'uppercase',
          textAlign: 'center', marginBottom: '1.5rem',
        }}>Shop by Category</p>

        <div className="category-strip" style={{
          display: 'flex', gap: '1.5rem', justifyContent: 'center',
          overflowX: 'auto', scrollbarWidth: 'none',
          WebkitOverflowScrolling: 'touch',
          padding: '0.5rem 0',
        }}>
          {CATEGORY_IMAGES.map((cat) => (
            <div
              key={cat.name}
              onClick={() => handleClick(cat.name)}
              style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center',
                gap: '0.5rem', cursor: 'pointer', flexShrink: 0,
                transition: 'all 0.3s',
              }}
              onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-3px)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <div style={{
                width: '80px', height: '80px', borderRadius: '50%',
                overflow: 'hidden', border: '2px solid rgba(0,0,0,0.06)',
                transition: 'border-color 0.3s',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(0,0,0,0.2)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(0,0,0,0.06)'}
              >
                <img src={cat.image} alt={cat.name} loading="lazy" style={{
                  width: '100%', height: '100%', objectFit: 'cover',
                }} />
              </div>
              <span style={{
                fontSize: '0.75rem', fontWeight: 600, color: '#1d1d1f',
                fontFamily: "'Inter', sans-serif",
              }}>{cat.name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
