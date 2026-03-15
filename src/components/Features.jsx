import { useState } from 'react'
import { useInView } from '../hooks'
import { FEATURES } from '../data'

export default function Features() {
  const [ref, visible] = useInView()

  return (
    <section id="about" style={{
      padding: '6rem 2rem',
      background: '#f5f5f7',
    }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '3.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(15px)',
          transition: 'all 0.6s',
        }}>
          <p style={{
            fontSize: '0.8rem', fontWeight: 500, color: '#86868b',
            letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '0.8rem',
          }}>Why NeatNesCo</p>
          <h2 style={{
            fontFamily: "'Inter', -apple-system, sans-serif",
            fontSize: 'clamp(2.8rem, 7vw, 4.5rem)',
            fontWeight: 700, color: '#1d1d1f', letterSpacing: '-0.04em',
            lineHeight: 1.05,
          }}>
            The NeatNesCo<br />Standard.
          </h2>
          <p style={{ color: '#6e6e73', fontSize: '1.1rem', margin: '0.8rem auto 0' }}>
            Quality you can trust, every time.
          </p>
        </div>

        <div className="features-grid bento-grid" style={{
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1rem',
        }}>
          {FEATURES.map((feat, i) => {
            const [cardRef, cardVisible] = useInView()
            const [hovered, setHovered] = useState(false)
            const isWide = i === 0 || i === FEATURES.length - 1
            return (
              <div key={i} ref={cardRef}
                onMouseEnter={() => setHovered(true)}
                onMouseLeave={() => setHovered(false)}
                style={{
                  borderRadius: '20px', padding: '2.2rem',
                  background: hovered ? '#ffffff' : '#ffffff',
                  border: '1px solid rgba(0,0,0,0.06)',
                  opacity: cardVisible ? 1 : 0,
                  transform: cardVisible
                    ? (hovered ? 'translateY(-4px)' : 'translateY(0)')
                    : 'translateY(20px)',
                  transition: `all 0.4s cubic-bezier(0.4, 0, 0.2, 1) ${i * 0.06}s`,
                  cursor: 'default',
                  gridColumn: isWide ? 'span 2' : undefined,
                  boxShadow: hovered ? '0 8px 30px rgba(0,0,0,0.08)' : '0 1px 3px rgba(0,0,0,0.04)',
              }}>
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  marginBottom: '1rem',
                }}>
                  <div style={{
                    width: '48px', height: '48px', borderRadius: '14px',
                    background: '#f5f5f7',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '0.85rem', fontWeight: 700, color: '#1d1d1f',
                    fontFamily: "'Inter', sans-serif", letterSpacing: '-0.02em',
                  }}>{feat.title.charAt(0)}</div>
                  {feat.stat && (
                    <span style={{
                      fontSize: '0.7rem', fontWeight: 600,
                      color: '#86868b',
                      background: '#f5f5f7',
                      padding: '0.25rem 0.7rem', borderRadius: '980px',
                    }}>
                      {feat.stat}
                    </span>
                  )}
                </div>
                <h3 style={{
                  fontSize: '1.2rem', fontWeight: 600, marginBottom: '0.5rem',
                  color: '#1d1d1f', fontFamily: "'Inter', sans-serif",
                }}>
                  {feat.title}
                </h3>
                <p style={{ fontSize: '0.95rem', color: '#6e6e73', lineHeight: 1.65 }}>
                  {feat.desc}
                </p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
