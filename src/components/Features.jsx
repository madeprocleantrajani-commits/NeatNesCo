import { useState } from 'react'
import { useInView } from '../hooks'
import { FEATURES } from '../data'

export default function Features({ darkMode }) {
  const [ref, visible] = useInView()

  return (
    <section id="about" style={{
      padding: '6rem 2rem',
      background: darkMode
        ? 'linear-gradient(180deg, #0a0a0a 0%, #0d1a12 50%, #0a0a0a 100%)'
        : 'linear-gradient(180deg, #fafaf8 0%, #f0ede6 50%, #fafaf8 100%)',
      position: 'relative', zIndex: 1,
    }}>
      {/* Noise texture */}
      <div className="noise-overlay" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} />

      <div style={{ maxWidth: '1200px', margin: '0 auto', position: 'relative' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '3.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s',
        }}>
          <span className="section-tag">Why NeatNesCo</span>
          <h2 style={{
            fontFamily: "'Playfair Display', serif", fontSize: 'clamp(2rem, 4vw, 3.5rem)',
            fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.03em',
          }}>
            Built Different
          </h2>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '1.05rem', maxWidth: '520px', margin: '0.5rem auto 0' }}>
            We're not your average store. Here's why 50,000+ people trust us.
          </p>
        </div>

        <div className="features-grid" style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '1.5rem',
        }}>
          {FEATURES.map((feat, i) => {
            const [cardRef, cardVisible] = useInView()
            const [hovered, setHovered] = useState(false)
            return (
              <div key={i} ref={cardRef}
                onMouseEnter={() => setHovered(true)}
                onMouseLeave={() => setHovered(false)}
                className="glass-card"
                style={{
                  borderRadius: '24px', padding: '2rem',
                  opacity: cardVisible ? 1 : 0,
                  transform: cardVisible
                    ? (hovered ? 'translateY(-6px)' : 'translateY(0)')
                    : 'translateY(30px)',
                  transition: `all 0.5s cubic-bezier(0.4, 0, 0.2, 1) ${i * 0.08}s`,
                  cursor: 'default',
                  position: 'relative',
                  overflow: 'hidden',
              }}>
                {/* Subtle gradient on hover */}
                <div style={{
                  position: 'absolute', inset: 0,
                  background: `radial-gradient(ellipse at ${hovered ? '30% 20%' : '50% 50%'}, rgba(45,106,79,${hovered ? 0.06 : 0}) 0%, transparent 70%)`,
                  transition: 'all 0.5s',
                  borderRadius: 'inherit',
                }} />

                <div style={{ position: 'relative', zIndex: 1 }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    marginBottom: '1.2rem',
                  }}>
                    <div style={{
                      width: '56px', height: '56px', borderRadius: '16px',
                      background: darkMode ? 'rgba(45,106,79,0.15)' : 'rgba(45,106,79,0.08)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '1.6rem',
                      transition: 'all 0.4s',
                      transform: hovered ? 'scale(1.1) rotate(-5deg)' : 'scale(1)',
                      boxShadow: hovered ? '0 4px 16px rgba(45,106,79,0.15)' : 'none',
                    }}>{feat.icon}</div>
                    {feat.stat && (
                      <span style={{
                        fontSize: '0.72rem', fontWeight: 700,
                        color: '#2d6a4f',
                        background: darkMode ? 'rgba(45,106,79,0.15)' : 'rgba(45,106,79,0.06)',
                        padding: '0.3rem 0.8rem', borderRadius: '100px',
                        border: '1px solid rgba(45,106,79,0.1)',
                      }}>
                        {feat.stat}
                      </span>
                    )}
                  </div>
                  <h3 style={{
                    fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem',
                    color: 'var(--text-primary)',
                  }}>
                    {feat.title}
                  </h3>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-tertiary)', lineHeight: 1.7 }}>
                    {feat.desc}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
