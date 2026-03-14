import { useState, useEffect } from 'react'

export default function SplashScreen({ onComplete }) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false)
      setTimeout(onComplete, 600)
    }, 2200)
    return () => clearTimeout(timer)
  }, [onComplete])

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 10000,
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a2e1f 50%, #0a0a0a 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexDirection: 'column', gap: '1.5rem',
      opacity: visible ? 1 : 0,
      transition: 'opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
      pointerEvents: visible ? 'all' : 'none',
    }}>
      {/* Noise texture */}
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E")`,
        backgroundRepeat: 'repeat',
        opacity: 0.5,
      }} />

      {/* Glow */}
      <div style={{
        position: 'absolute',
        width: '400px', height: '400px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(45,106,79,0.3) 0%, transparent 70%)',
        filter: 'blur(60px)',
        animation: 'pulse 3s ease-in-out infinite',
      }} />

      {/* Logo */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.5rem',
        animation: 'splashLogo 1.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        position: 'relative', zIndex: 1,
      }}>
        <div style={{
          width: '56px', height: '56px', borderRadius: '16px',
          background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontSize: '1.8rem', fontWeight: 800,
          fontFamily: "'Playfair Display', serif",
          boxShadow: '0 8px 32px rgba(45,106,79,0.4)',
        }}>N</div>
        <span style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: '2.5rem', fontWeight: 700, color: '#fff',
          letterSpacing: '-0.03em',
        }}>
          eat<span style={{ color: '#52b788' }}>Nes</span>Co
        </span>
      </div>

      {/* Animated line */}
      <div style={{
        height: '2px',
        background: 'linear-gradient(90deg, transparent, #52b788, transparent)',
        borderRadius: '1px',
        animation: 'splashLine 1.5s 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards',
        width: 0,
        position: 'relative', zIndex: 1,
      }} />

      {/* Tagline */}
      <p style={{
        color: 'rgba(255,255,255,0.5)',
        fontSize: '0.9rem',
        fontWeight: 500,
        letterSpacing: '0.15em',
        textTransform: 'uppercase',
        animation: 'splashText 1.5s 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards',
        opacity: 0,
        position: 'relative', zIndex: 1,
      }}>
        Neat Finds, Neatly Delivered
      </p>
    </div>
  )
}
