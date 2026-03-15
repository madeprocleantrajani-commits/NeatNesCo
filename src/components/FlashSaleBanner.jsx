import { useCountdown } from '../hooks'

export default function FlashSaleBanner() {
  const time = useCountdown(11, 47, 33)

  return (
    <div style={{
      position: 'fixed', top: '48px', left: 0, right: 0, zIndex: 999,
      background: '#1d1d1f',
      padding: '0.45rem 1rem',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 'clamp(0.5rem, 2vw, 1.2rem)',
      flexWrap: 'wrap',
    }}>
      <span style={{
        fontSize: '0.75rem', fontWeight: 500, color: '#ffffff',
        letterSpacing: '0.02em',
      }}>
        Flash Sale — Up to 50% Off
      </span>

      <div style={{
        display: 'flex', gap: '0.3rem', alignItems: 'center',
      }}>
        {[
          { val: String(time.h).padStart(2, '0'), label: 'H' },
          { val: String(time.m).padStart(2, '0'), label: 'M' },
          { val: String(time.s).padStart(2, '0'), label: 'S' },
        ].map((unit, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <div style={{
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '4px',
              padding: '0.15rem 0.4rem',
              minWidth: '28px',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#fff', fontFamily: "'Inter', monospace" }}>
                {unit.val}
              </div>
            </div>
            {i < 2 && <span style={{ color: 'rgba(255,255,255,0.4)', fontWeight: 500, fontSize: '0.75rem' }}>:</span>}
          </div>
        ))}
      </div>

      <a href="#products" style={{
        color: '#ffffff', opacity: 0.9,
        fontSize: '0.75rem', fontWeight: 500, textDecoration: 'none',
        fontFamily: "'Inter', sans-serif",
      }}>
        Shop Now
      </a>
    </div>
  )
}
