import { useInView } from '../hooks'
import { TIMELINE } from '../data'

export default function StoryTimeline({ darkMode }) {
  const [ref, visible] = useInView()

  return (
    <section id="story" style={{
      padding: '6rem 2rem', position: 'relative', zIndex: 1,
    }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '4rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s',
        }}>
          <span className="section-tag">Our Journey</span>
          <h2 style={{
            fontFamily: "'Playfair Display', serif", fontSize: 'clamp(2rem, 4vw, 3.5rem)',
            fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.03em',
          }}>
            The NeatNesCo Story
          </h2>
          <p style={{
            color: 'var(--text-tertiary)', fontSize: '1.05rem', maxWidth: '560px', margin: '0.5rem auto 0',
            lineHeight: 1.7,
          }}>
            What started as a frustration with overpriced trending products became a mission to make quality accessible.
          </p>
        </div>

        {/* Timeline */}
        <div className="story-timeline" style={{
          position: 'relative', paddingLeft: '3rem',
        }}>
          {/* Vertical line */}
          <div style={{
            position: 'absolute', left: '11px', top: '8px', bottom: '8px',
            width: '2px',
            background: darkMode
              ? 'linear-gradient(180deg, rgba(45,106,79,0.4), rgba(45,106,79,0.1))'
              : 'linear-gradient(180deg, rgba(45,106,79,0.3), rgba(45,106,79,0.05))',
          }} />

          {TIMELINE.map((item, i) => {
            const [itemRef, itemVisible] = useInView()
            return (
              <div key={i} ref={itemRef} style={{
                marginBottom: i < TIMELINE.length - 1 ? '3rem' : 0,
                position: 'relative',
                opacity: itemVisible ? 1 : 0,
                transform: itemVisible ? 'translateX(0)' : 'translateX(-20px)',
                transition: `all 0.6s ${i * 0.15}s cubic-bezier(0.4, 0, 0.2, 1)`,
              }}>
                {/* Dot */}
                <div style={{
                  position: 'absolute', left: '-3rem',
                  width: '24px', height: '24px', borderRadius: '50%',
                  background: i === TIMELINE.length - 1
                    ? 'linear-gradient(135deg, #2d6a4f, #52b788)'
                    : (darkMode ? 'rgba(45,106,79,0.2)' : 'rgba(45,106,79,0.12)'),
                  border: `3px solid ${darkMode ? '#0a0a0a' : '#fafaf8'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: i === TIMELINE.length - 1 ? '0 0 20px rgba(45,106,79,0.3)' : 'none',
                }}>
                  {i === TIMELINE.length - 1 && (
                    <div className="pulse-dot" style={{ width: '6px', height: '6px' }} />
                  )}
                </div>

                {/* Content */}
                <div className="glass-card" style={{
                  borderRadius: '20px', padding: '1.8rem',
                }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.8rem',
                  }}>
                    <span style={{
                      fontSize: '0.72rem', fontWeight: 700,
                      color: '#2d6a4f',
                      background: darkMode ? 'rgba(45,106,79,0.15)' : 'rgba(45,106,79,0.08)',
                      padding: '0.3rem 0.8rem', borderRadius: '100px',
                      border: '1px solid rgba(45,106,79,0.1)',
                      letterSpacing: '0.05em',
                    }}>
                      {item.year}
                    </span>
                    <h3 style={{
                      fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)',
                    }}>
                      {item.title}
                    </h3>
                  </div>
                  <p style={{
                    fontSize: '0.95rem', color: 'var(--text-tertiary)', lineHeight: 1.7,
                  }}>
                    {item.desc}
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
