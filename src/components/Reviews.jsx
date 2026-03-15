import { useInView } from '../hooks'
import { REVIEWS } from '../data'

export default function Reviews() {
  const [ref, visible] = useInView()

  const ReviewCard = ({ review }) => (
    <div style={{
      minWidth: '340px', maxWidth: '340px', borderRadius: '18px',
      padding: '1.8rem', flexShrink: 0,
      background: '#ffffff',
      border: '1px solid rgba(0,0,0,0.06)',
      boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.7rem', marginBottom: '0.8rem' }}>
        <div style={{
          width: '36px', height: '36px', borderRadius: '50%',
          background: '#f5f5f7',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#1d1d1f', fontWeight: 600, fontSize: '0.82rem',
          fontFamily: "'Inter', sans-serif",
        }}>{review.avatar}</div>
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#1d1d1f' }}>{review.name}</div>
          <div style={{ fontSize: '0.7rem', color: '#86868b' }}>{review.location}</div>
        </div>
      </div>
      <div style={{ marginBottom: '0.6rem', fontSize: '0.82rem', color: '#ff9500', letterSpacing: '1px' }}>
        {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
      </div>
      <p style={{
        fontSize: '0.92rem', color: '#6e6e73', lineHeight: 1.65,
      }}>
        "{review.text}"
      </p>
      {review.product && (
        <div style={{
          marginTop: '0.8rem', paddingTop: '0.7rem',
          borderTop: '1px solid rgba(0,0,0,0.06)',
          fontSize: '0.72rem', color: '#86868b', fontWeight: 500,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <span>Purchased: {review.product}</span>
          <span style={{
            background: '#f5f5f7', color: '#86868b',
            padding: '0.15rem 0.5rem', borderRadius: '980px',
            fontSize: '0.6rem', fontWeight: 600, letterSpacing: '0.02em',
          }}>Verified</span>
        </div>
      )}
    </div>
  )

  return (
    <section id="reviews" style={{
      padding: '6rem 0', overflow: 'hidden',
      background: '#f5f5f7',
    }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 2rem' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '3rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(15px)',
          transition: 'all 0.6s',
        }}>
          <p style={{
            fontSize: '0.8rem', fontWeight: 500, color: '#86868b',
            letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.6rem',
          }}>Customer Reviews</p>
          <h2 style={{
            fontFamily: "'Inter', -apple-system, sans-serif",
            fontSize: 'clamp(2.4rem, 5vw, 3.5rem)',
            fontWeight: 700, color: '#1d1d1f', letterSpacing: '-0.03em',
          }}>
            What People Are Saying
          </h2>
          <p style={{ color: '#6e6e73', fontSize: '1rem', margin: '0.5rem auto 0' }}>
            4.8/5 from 12,000+ verified reviews
          </p>
        </div>
      </div>

      <div className="marquee-container" style={{ marginBottom: '1rem' }}>
        <div className="marquee-track">
          {[...REVIEWS.slice(0, 6), ...REVIEWS.slice(0, 6)].map((review, i) => (
            <ReviewCard key={i} review={review} />
          ))}
        </div>
      </div>

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
