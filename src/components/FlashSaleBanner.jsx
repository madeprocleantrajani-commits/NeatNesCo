import { useCountdown } from '../hooks'

export default function FlashSaleBanner({ darkMode }) {
  const time = useCountdown(11, 47, 33)

  return (
    <div style={{
      position: 'fixed', top: '72px', left: 0, right: 0, zIndex: 999,
      background: 'linear-gradient(90deg, #2d6a4f 0%, #1a4731 30%, #2d6a4f 50%, #1a4731 70%, #2d6a4f 100%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 6s linear infinite',
      padding: '0.55rem 1rem',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 'clamp(0.5rem, 2vw, 1.5rem)',
      flexWrap: 'wrap',
      boxShadow: '0 2px 12px rgba(45,106,79,0.3)',
    }}>
      <span style={{
        fontSize: '0.82rem', fontWeight: 700, color: '#fff',
        display: 'flex', alignItems: 'center', gap: '0.4rem',
        letterSpacing: '0.03em',
      }}>
        <span style={{ fontSize: '1rem' }}>⚡</span>
        FLASH SALE — UP TO 50% OFF
      </span>

      <div style={{
        display: 'flex', gap: '0.35rem', alignItems: 'center',
      }}>
        {[
          { val: String(time.h).padStart(2, '0'), label: 'HRS' },
          { val: String(time.m).padStart(2, '0'), label: 'MIN' },
          { val: String(time.s).padStart(2, '0'), label: 'SEC' },
        ].map((unit, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <div style={{
              background: 'rgba(255,255,255,0.15)',
              backdropFilter: 'blur(8px)',
              borderRadius: '6px',
              padding: '0.25rem 0.5rem',
              minWidth: '36px',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#fff', fontFamily: "'Inter', monospace" }}>
                {unit.val}
              </div>
            </div>
            {i < 2 && <span style={{ color: 'rgba(255,255,255,0.6)', fontWeight: 700, fontSize: '0.85rem' }}>:</span>}
          </div>
        ))}
      </div>

      <a href="#products" style={{
        background: '#fff', color: '#2d6a4f',
        padding: '0.3rem 1rem', borderRadius: '100px',
        fontSize: '0.75rem', fontWeight: 700, textDecoration: 'none',
        transition: 'all 0.2s',
        letterSpacing: '0.02em',
      }}>
        SHOP NOW →
      </a>
    </div>
  )
}
