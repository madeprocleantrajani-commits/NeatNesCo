import { useInView } from '../hooks'
import { REVIEWS } from '../data'

export default function Reviews({ darkMode }) {
  const [ref, visible] = useInView()

  const ReviewCard = ({ review }) => (
    <div className="glass-card" style={{
      minWidth: '360px', maxWidth: '360px', borderRadius: '24px',
      padding: '2rem', flexShrink: 0, position: 'relative', overflow: 'hidden',
    }}>
      {/* Subtle quote mark */}
      <div style={{
        position: 'absolute', top: '0.5rem', right: '1.5rem',
        fontSize: '5rem', fontFamily: "'Playfair Display', serif",
        color: darkMode ? 'rgba(45,106,79,0.06)' : 'rgba(45,106,79,0.05)',
        lineHeight: 1, pointerEvents: 'none',
      }}>"</div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1rem', position: 'relative' }}>
        <div style={{
          width: '44px', height: '44px', borderRadius: '14px',
          background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontWeight: 700, fontSize: '0.95rem',
          boxShadow: '0 4px 12px rgba(45,106,79,0.25)',
        }}>{review.avatar}</div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>{review.name}</div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{review.location}</div>
        </div>
      </div>
      <div className="star-rating" style={{ marginBottom: '0.75rem', fontSize: '0.88rem', letterSpacing: '2px' }}>
        {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
      </div>
      <p style={{
        fontSize: '0.92rem', color: 'var(--text-secondary)', lineHeight: 1.65,
        fontStyle: 'italic',
      }}>
        "{review.text}"
      </p>
      {review.product && (
        <div style={{
          marginTop: '1rem', paddingTop: '0.8rem',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500,
          display: 'flex', alignItems: 'center', gap: '0.4rem',
        }}>
          <span style={{ opacity: 0.6 }}>📦</span>
          Purchased: {review.product}
        </div>
      )}
    </div>
  )

  return (
    <section id="reviews" style={{
      padding: '6rem 0', overflow: 'hidden', position: 'relative', zIndex: 1,
    }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 2rem' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '3rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s',
        }}>
          <span className="section-tag">Social Proof</span>
          <h2 style={{
            fontFamily: "'Playfair Display', serif", fontSize: 'clamp(2rem, 4vw, 3.5rem)',
            fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.03em',
          }}>
            What People Are Saying
          </h2>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '1.05rem', maxWidth: '480px', margin: '0.5rem auto 0' }}>
            Real reviews from real customers. No fluff.
          </p>
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem',
            marginTop: '1.5rem',
          }}>
            <div style={{
              display: 'flex', gap: '-0.3rem',
            }}>
              {['S', 'J', 'P', 'M', 'E'].map((a, i) => (
                <div key={i} style={{
                  width: '32px', height: '32px', borderRadius: '50%',
                  background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#fff', fontSize: '0.7rem', fontWeight: 700,
                  border: `2px solid var(--bg-primary)`,
                  marginLeft: i > 0 ? '-8px' : '0',
                  position: 'relative', zIndex: 5 - i,
                }}>{a}</div>
              ))}
            </div>
            <div>
              <span className="star-rating" style={{ fontSize: '0.85rem' }}>★★★★★</span>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-tertiary)', marginLeft: '0.3rem' }}>
                4.8/5 from 12,000+ reviews
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 1 - scrolling left */}
      <div className="marquee-container" style={{ marginBottom: '1.5rem' }}>
        <div className="marquee-track">
          {[...REVIEWS.slice(0, 6), ...REVIEWS.slice(0, 6)].map((review, i) => (
            <ReviewCard key={i} review={review} />
          ))}
        </div>
      </div>

      {/* Row 2 - scrolling right */}
      <div className="marquee-container">
        <div className="marquee-track-reverse">
          {[...REVIEWS.slice(6), ...REVIEWS.slice(6)].map((review, i) => (
            <ReviewCard key={i} review={review} />
          ))}
        </div>
      </div>
    </section>
  )
}
