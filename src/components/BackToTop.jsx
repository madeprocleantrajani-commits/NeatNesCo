import { useState, useEffect } from 'react'

export default function BackToTop() {
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
        position: 'fixed', bottom: '5.5rem', right: '2rem', zIndex: 6000,
        width: '40px', height: '40px', borderRadius: '50%',
        background: '#1d1d1f',
        border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        opacity: show ? 1 : 0,
        transform: show ? 'translateY(0)' : 'translateY(10px)',
        transition: 'all 0.3s',
        pointerEvents: show ? 'auto' : 'none',
        color: '#fff',
        fontSize: '0.9rem',
        fontWeight: 300,
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      }}
    >
      ↑
    </button>
  )
}
