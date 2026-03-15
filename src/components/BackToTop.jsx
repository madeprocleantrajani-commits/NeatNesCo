import { useState, useEffect } from 'react'

export default function BackToTop({ darkMode }) {
  const [show, setShow] = useState(false)

  useEffect(() => {
    const onScroll = () => setShow(window.scrollY > 500)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      style={{
        position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 6000,
        width: '48px', height: '48px', borderRadius: '14px',
        background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
        border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 4px 20px rgba(45,106,79,0.35)',
        opacity: show ? 1 : 0,
        transform: show ? 'translateY(0) scale(1)' : 'translateY(20px) scale(0.8)',
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        pointerEvents: show ? 'auto' : 'none',
        animation: show ? 'floatUp 3s ease-in-out infinite' : 'none',
        color: '#fff',
        fontSize: '1.2rem',
      }}
    >
      ↑
    </button>
  )
}
