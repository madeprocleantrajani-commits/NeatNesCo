import { useState } from 'react'
import { useInView } from '../hooks'

export default function Newsletter({ darkMode }) {
  const [ref, visible] = useInView()
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (email) setSubmitted(true)
  }

  return (
    <section style={{
      padding: '6rem 2rem', position: 'relative', overflow: 'hidden', zIndex: 1,
      background: 'linear-gradient(135deg, #0d1a12 0%, #1a3726 30%, #0d1a12 60%, #1a2e1f 100%)',
    }}>
      {/* Animated grid background */}
      <div style={{
        position: 'absolute', inset: 0, opacity: 0.04,
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px)',
        backgroundSize: '50px 50px',
      }} />

      {/* Decorative circles */}
      <div style={{
        position: 'absolute', top: '-120px', right: '-120px',
        width: '450px', height: '450px', borderRadius: '50%',
        border: '1px solid rgba(45,106,79,0.2)',
      }} />
      <div style={{
        position: 'absolute', top: '-80px', right: '-80px',
        width: '350px', height: '350px', borderRadius: '50%',
        border: '1px solid rgba(45,106,79,0.1)',
      }} />
      <div style={{
        position: 'absolute', bottom: '-150px', left: '-150px',
        width: '500px', height: '500px', borderRadius: '50%',
        border: '1px solid rgba(45,106,79,0.12)',
      }} />

      {/* Glow */}
      <div style={{
        position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        width: '600px', height: '400px',
        background: 'radial-gradient(ellipse, rgba(45,106,79,0.2) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      <div ref={ref} style={{
        maxWidth: '620px', margin: '0 auto', textAlign: 'center',
        position: 'relative', zIndex: 1,
        opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.6s',
      }}>
        <div style={{
          width: '64px', height: '64px', borderRadius: '20px',
          background: 'rgba(45,106,79,0.15)', border: '1px solid rgba(45,106,79,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1.8rem', margin: '0 auto 1.5rem',
        }}>📬</div>

        <h2 style={{
          fontFamily: "'Playfair Display', serif", fontSize: 'clamp(1.8rem, 4vw, 3rem)',
          fontWeight: 700, color: '#fff', marginBottom: '0.8rem', letterSpacing: '-0.03em',
        }}>
          Don't Miss a Drop
        </h2>
        <p style={{
          color: 'rgba(255,255,255,0.45)', marginBottom: '2.5rem',
          fontSize: '1.05rem', lineHeight: 1.65,
        }}>
          First access to new products, exclusive deals, and curated drops.
          <br />No spam, ever. Unsubscribe anytime.
        </p>

        {submitted ? (
          <div style={{
            background: 'rgba(45,106,79,0.2)', border: '1px solid rgba(45,106,79,0.3)',
            borderRadius: '20px', padding: '1.8rem', color: '#a8dabc',
            fontSize: '1rem', fontWeight: 600,
            animation: 'fadeIn 0.5s ease-out',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
          }}>
            <span style={{ fontSize: '1.3rem' }}>🎉</span>
            You're in! Check your inbox for a welcome surprise.
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{
            display: 'flex', gap: '0.75rem', maxWidth: '500px', margin: '0 auto',
            flexWrap: 'wrap', justifyContent: 'center',
          }}>
            <input
              type="email" placeholder="your@email.com" value={email}
              onChange={e => setEmail(e.target.value)} required
              style={{
                flex: 1, minWidth: '240px', padding: '1.05rem 1.5rem', borderRadius: '14px',
                border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.06)',
                color: '#fff', fontSize: '1rem', outline: 'none',
                transition: 'all 0.3s', fontFamily: "'Inter', sans-serif",
                backdropFilter: 'blur(8px)',
              }}
              onFocus={e => {
                e.target.style.borderColor = 'rgba(45,106,79,0.5)'
                e.target.style.background = 'rgba(255,255,255,0.1)'
                e.target.style.boxShadow = '0 0 0 4px rgba(45,106,79,0.1)'
              }}
              onBlur={e => {
                e.target.style.borderColor = 'rgba(255,255,255,0.08)'
                e.target.style.background = 'rgba(255,255,255,0.06)'
                e.target.style.boxShadow = 'none'
              }}
            />
            <button type="submit" className="subscribe-btn" style={{
              background: 'linear-gradient(135deg, #2d6a4f, #52b788)', color: '#fff',
              padding: '1.05rem 2.2rem',
              borderRadius: '14px', border: 'none', fontSize: '1rem',
              fontWeight: 600, cursor: 'pointer', transition: 'all 0.3s',
              fontFamily: "'Inter', sans-serif",
              boxShadow: '0 4px 16px rgba(45,106,79,0.3)',
            }}>
              Subscribe →
            </button>
          </form>
        )}

        <p style={{
          color: 'rgba(255,255,255,0.2)', fontSize: '0.78rem', marginTop: '1.5rem',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
        }}>
          <span>🔒</span> Join 50,000+ others. We respect your privacy.
        </p>
      </div>
    </section>
  )
}
