import { useInView } from '../hooks'
import { TIMELINE } from '../data'

export default function StoryTimeline() {
  const [ref, visible] = useInView()

  return (
    <section id="story" style={{
      padding: '6rem 2rem',
      background: '#ffffff',
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '4rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(15px)',
          transition: 'all 0.6s',
        }}>
          <p style={{
            fontSize: '0.8rem', fontWeight: 500, color: '#86868b',
            letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.6rem',
          }}>Our Journey</p>
          <h2 style={{
            fontFamily: "'Inter', -apple-system, sans-serif",
            fontSize: 'clamp(2.4rem, 5vw, 3.5rem)',
            fontWeight: 700, color: '#1d1d1f', letterSpacing: '-0.03em',
          }}>
            The NeatNesCo Story
          </h2>
          <p style={{
            color: '#6e6e73', fontSize: '1.1rem', maxWidth: '540px', margin: '0.6rem auto 0',
            lineHeight: 1.6,
          }}>
            From overpaying to curating — here's how we got here.
          </p>
        </div>

        <div className="story-timeline" style={{ position: 'relative', paddingLeft: '3rem' }}>
          {/* Vertical line */}
          <div style={{
            position: 'absolute', left: '11px', top: '8px', bottom: '8px',
            width: '1px',
            background: 'linear-gradient(180deg, rgba(0,0,0,0.12), rgba(0,0,0,0.04))',
          }} />

          {TIMELINE.map((item, i) => {
            const [itemRef, itemVisible] = useInView()
            return (
              <div key={i} ref={itemRef} style={{
                marginBottom: i < TIMELINE.length - 1 ? '2.5rem' : 0,
                position: 'relative',
                opacity: itemVisible ? 1 : 0,
                transform: itemVisible ? 'translateX(0)' : 'translateX(-15px)',
                transition: `all 0.5s ${i * 0.12}s cubic-bezier(0.4, 0, 0.2, 1)`,
              }}>
                {/* Dot */}
                <div style={{
                  position: 'absolute', left: '-3rem',
                  width: '24px', height: '24px', borderRadius: '50%',
                  background: i === TIMELINE.length - 1 ? '#1d1d1f' : '#e8e8ed',
                  border: '3px solid #ffffff',
                  boxShadow: i === TIMELINE.length - 1
                    ? '0 0 0 2px rgba(0,0,0,0.1)'
                    : '0 0 0 1px rgba(0,0,0,0.06)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  {i === TIMELINE.length - 1 && (
                    <div style={{ width: '5px', height: '5px', borderRadius: '50%', background: '#ffffff' }} />
                  )}
                </div>

                <div style={{
                  borderRadius: '16px', padding: '1.5rem',
                  background: '#f5f5f7',
                  border: '1px solid rgba(0,0,0,0.04)',
                }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '0.7rem', marginBottom: '0.6rem',
                  }}>
                    <span style={{
                      fontSize: '0.7rem', fontWeight: 600,
                      color: '#86868b',
                      background: '#ffffff',
                      padding: '0.2rem 0.6rem', borderRadius: '980px',
                      border: '1px solid rgba(0,0,0,0.06)',
                    }}>
                      {item.year}
                    </span>
                    <h3 style={{
                      fontSize: '1.05rem', fontWeight: 600, color: '#1d1d1f',
                      fontFamily: "'Inter', sans-serif",
                    }}>
                      {item.title}
                    </h3>
                  </div>
                  <p style={{
                    fontSize: '0.9rem', color: '#6e6e73', lineHeight: 1.6,
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
