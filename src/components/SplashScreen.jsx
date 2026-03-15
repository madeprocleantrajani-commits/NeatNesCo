import { useState, useEffect } from 'react'

export default function SplashScreen({ onComplete }) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false)
      setTimeout(onComplete, 500)
    }, 1800)
    return () => clearTimeout(timer)
  }, [onComplete])

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 10000,
      background: '#ffffff',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexDirection: 'column', gap: '1.2rem',
      opacity: visible ? 1 : 0,
      transition: 'opacity 0.5s ease',
      pointerEvents: visible ? 'all' : 'none',
    }}>
      {/* Logo */}
      <div style={{
        animation: 'splashLogo 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards',
        opacity: 0,
      }}>
        <span style={{
          fontFamily: "'Inter', -apple-system, sans-serif",
          fontSize: '2rem', fontWeight: 600, color: '#1d1d1f',
          letterSpacing: '-0.03em',
        }}>
          NeatNesCo
        </span>
      </div>

      {/* Animated line */}
      <div style={{
        height: '1px',
        background: 'rgba(0,0,0,0.2)',
        borderRadius: '1px',
        animation: 'splashLine 1s 0.3s ease forwards',
        width: 0,
      }} />

      {/* Tagline */}
      <p style={{
        color: '#86868b',
        fontSize: '0.82rem',
        fontWeight: 400,
        letterSpacing: '0.06em',
        textTransform: 'uppercase',
        animation: 'splashText 0.8s 0.5s ease forwards',
        opacity: 0,
        fontFamily: "'Inter', sans-serif",
      }}>
        Neat Finds, Neatly Delivered
      </p>
    </div>
  )
}
