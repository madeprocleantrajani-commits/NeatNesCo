import { useInView } from '../hooks'
import { BRANDS } from '../data'

export default function BrandsMarquee({ darkMode }) {
  const [ref, visible] = useInView()

  return (
    <section ref={ref} style={{
      padding: '3rem 0',
      borderTop: '1px solid var(--border-subtle)',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'relative', zIndex: 1,
      overflow: 'hidden',
      opacity: visible ? 1 : 0,
      transition: 'opacity 0.8s',
    }}>
      <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
        <span style={{
          fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)',
          letterSpacing: '0.15em', textTransform: 'uppercase',
        }}>
          As featured in
        </span>
      </div>
      <div className="marquee-container">
        <div className="brands-track">
          {[...BRANDS, ...BRANDS, ...BRANDS].map((brand, i) => (
            <span key={i} style={{
              fontSize: 'clamp(1rem, 2vw, 1.3rem)',
              fontWeight: 700,
              color: 'var(--text-muted)',
              whiteSpace: 'nowrap',
              opacity: 0.5,
              transition: 'opacity 0.3s',
              letterSpacing: '-0.01em',
              fontFamily: "'Inter', sans-serif",
            }}>
              {brand}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
