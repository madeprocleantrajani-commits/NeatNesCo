import { useInView } from '../hooks'

const PLATFORMS = ['TikTok', 'Instagram', 'YouTube', 'Pinterest', 'Reddit']

export default function AsSeenOn() {
  const [ref, visible] = useInView()

  return (
    <section ref={ref} style={{
      padding: '3.5rem 2rem',
      background: '#f5f5f7',
      opacity: visible ? 1 : 0,
      transform: visible ? 'translateY(0)' : 'translateY(15px)',
      transition: 'all 0.6s',
    }}>
      <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
        <p style={{
          fontSize: '0.75rem', fontWeight: 500, color: '#86868b',
          letterSpacing: '0.08em', textTransform: 'uppercase',
          marginBottom: '1.5rem',
        }}>Trending On</p>

        <div style={{
          display: 'flex', gap: 'clamp(1.5rem, 4vw, 3rem)',
          justifyContent: 'center', flexWrap: 'wrap',
          marginBottom: '1.2rem',
        }}>
          {PLATFORMS.map(platform => (
            <span key={platform} style={{
              fontSize: 'clamp(1rem, 2vw, 1.3rem)', fontWeight: 700,
              color: '#aeaeb2',
              fontFamily: "'Inter', sans-serif",
              letterSpacing: '-0.02em',
              transition: 'color 0.2s',
              cursor: 'default',
            }}
            onMouseEnter={e => e.target.style.color = '#6e6e73'}
            onMouseLeave={e => e.target.style.color = '#aeaeb2'}
            >
              {platform}
            </span>
          ))}
        </div>

        <p style={{
          fontSize: '0.85rem', color: '#86868b', fontWeight: 500,
        }}>
          Over 50M views across social media
        </p>
      </div>
    </section>
  )
}
