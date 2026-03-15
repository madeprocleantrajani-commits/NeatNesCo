import { useState } from 'react'
import { useInView } from '../hooks'

export default function Newsletter() {
  const [ref, visible] = useInView()
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (email) setSubmitted(true)
  }

  return (
    <section style={{
      padding: '6rem 2rem',
      background: '#ffffff',
    }}>
      <div ref={ref} style={{
        maxWidth: '560px', margin: '0 auto', textAlign: 'center',
        opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(15px)',
        transition: 'all 0.6s',
      }}>
        <p style={{
          fontSize: '0.8rem', fontWeight: 500, color: '#86868b',
          letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.6rem',
        }}>Stay Updated</p>

        <h2 style={{
          fontFamily: "'Inter', -apple-system, sans-serif",
          fontSize: 'clamp(2.6rem, 6vw, 3.8rem)',
          fontWeight: 700, color: '#1d1d1f', marginBottom: '0.8rem',
          letterSpacing: '-0.04em', lineHeight: 1.1,
        }}>
          Don't Miss<br />a Drop.
        </h2>
        <p style={{
          color: '#6e6e73', marginBottom: '0.6rem',
          fontSize: '1.1rem', lineHeight: 1.6,
        }}>
          Get 10% off your first order + exclusive early access.
        </p>

        {submitted ? (
          <div style={{
            background: '#f5f5f7',
            border: '1px solid rgba(0,0,0,0.06)',
            borderRadius: '16px', padding: '1.5rem', color: '#1d1d1f',
            fontSize: '0.95rem', fontWeight: 500,
            animation: 'fadeIn 0.5s ease-out',
          }}>
            You're in! Check your inbox for your 10% off code.
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{
            display: 'flex', gap: '0.6rem', maxWidth: '480px', margin: '1.5rem auto 0',
            flexWrap: 'wrap', justifyContent: 'center',
          }}>
            <input
              type="email" placeholder="your@email.com" value={email}
              onChange={e => setEmail(e.target.value)} required
              style={{
                flex: 1, minWidth: '240px', padding: '0.9rem 1.2rem', borderRadius: '12px',
                border: '1px solid rgba(0,0,0,0.12)', background: '#ffffff',
                color: '#1d1d1f', fontSize: '0.95rem', outline: 'none',
                transition: 'all 0.2s', fontFamily: "'Inter', sans-serif",
              }}
              onFocus={e => {
                e.target.style.borderColor = 'rgba(0,0,0,0.3)'
                e.target.style.boxShadow = '0 0 0 3px rgba(0,0,0,0.04)'
              }}
              onBlur={e => {
                e.target.style.borderColor = 'rgba(0,0,0,0.12)'
                e.target.style.boxShadow = 'none'
              }}
            />
            <button type="submit" className="subscribe-btn shiny-btn" style={{
              background: '#1d1d1f', color: '#ffffff',
              padding: '0.9rem 1.8rem',
              borderRadius: '12px', border: 'none', fontSize: '0.95rem',
              fontWeight: 500, cursor: 'pointer', transition: 'all 0.2s',
              fontFamily: "'Inter', sans-serif",
            }}>
              Subscribe
            </button>
          </form>
        )}

        <p style={{
          color: '#aeaeb2', fontSize: '0.75rem', marginTop: '1.2rem',
        }}>
          Join 50,000+ others. No spam, unsubscribe anytime.
        </p>
      </div>
    </section>
  )
}
