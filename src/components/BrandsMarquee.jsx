import { useInView } from '../hooks'
import { BRANDS } from '../data'

export default function BrandsMarquee() {
  const [ref, visible] = useInView()

  return (
    <section ref={ref} style={{
      padding: '2rem 0',
      borderTop: '1px solid rgba(0,0,0,0.06)',
      borderBottom: '1px solid rgba(0,0,0,0.06)',
      overflow: 'hidden',
      opacity: visible ? 1 : 0,
      transition: 'opacity 0.6s',
      background: '#ffffff',
    }}>
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <span style={{
          fontSize: '0.7rem', fontWeight: 500, color: '#86868b',
          letterSpacing: '0.08em', textTransform: 'uppercase',
        }}>
          Loved by shoppers worldwide
        </span>
      </div>
      <div className="marquee-container">
        <div className="brands-track">
          {[...BRANDS, ...BRANDS, ...BRANDS].map((brand, i) => (
            <span key={i} style={{
              fontSize: 'clamp(0.9rem, 1.5vw, 1.1rem)',
              fontWeight: 600,
              color: '#aeaeb2',
              whiteSpace: 'nowrap',
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
