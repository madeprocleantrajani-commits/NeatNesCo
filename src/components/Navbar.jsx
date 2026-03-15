import { useState, useEffect } from 'react'

export default function Navbar({ cartCount, onCartClick }) {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [menuOpen])

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
      padding: '0 clamp(1rem, 4vw, 3rem)', height: '48px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      background: scrolled ? 'rgba(255,255,255,0.85)' : 'rgba(255,255,255,0.72)',
      backdropFilter: 'blur(20px) saturate(1.8)',
      WebkitBackdropFilter: 'blur(20px) saturate(1.8)',
      borderBottom: '0.5px solid rgba(0,0,0,0.08)',
      transition: 'all 0.3s',
    }}>
      {/* Logo */}
      <a href="#" style={{
        fontFamily: "'Inter', -apple-system, sans-serif",
        fontSize: '1.15rem', fontWeight: 700,
        color: '#1d1d1f', textDecoration: 'none',
        letterSpacing: '-0.03em',
      }}>
        NeatNesCo
      </a>

      {/* Desktop nav */}
      <div style={{
        display: 'flex', gap: '1.8rem', alignItems: 'center',
      }} className="nav-links-desktop">
        {['Products', 'Reviews', 'FAQ'].map(item => (
          <a key={item} href={`#${item.toLowerCase()}`} style={{
            color: '#1d1d1f', textDecoration: 'none', fontSize: '0.8rem',
            fontWeight: 400, transition: 'opacity 0.2s',
            fontFamily: "'Inter', sans-serif",
            opacity: 0.8,
          }} className="nav-link">
            {item}
          </a>
        ))}

        <button onClick={onCartClick} style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
          background: 'transparent',
          color: '#1d1d1f',
          padding: '0.4rem 0',
          fontSize: '0.8rem', fontWeight: 400,
          border: 'none', cursor: 'pointer',
          fontFamily: "'Inter', sans-serif",
          opacity: 0.8,
        }}>
          Cart
          {cartCount > 0 && (
            <span style={{
              background: '#1d1d1f', color: '#fff', borderRadius: '50%',
              width: '16px', height: '16px', display: 'inline-flex',
              alignItems: 'center', justifyContent: 'center', fontSize: '0.55rem',
              fontWeight: 700,
            }}>{cartCount}</span>
          )}
        </button>
      </div>

      {/* Mobile */}
      <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center' }} className="mobile-menu-btn">
        <button onClick={onCartClick} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          fontSize: '0.8rem', fontWeight: 400, color: '#1d1d1f',
          fontFamily: "'Inter', sans-serif",
        }}>
          Cart{cartCount > 0 ? ` (${cartCount})` : ''}
        </button>
        <button onClick={() => setMenuOpen(!menuOpen)} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          padding: '0.5rem', position: 'relative', zIndex: 1001,
        }}>
          <div style={{
            width: '17px', height: '1px', background: '#1d1d1f',
            transition: 'all 0.3s',
            transform: menuOpen ? 'rotate(45deg) translateY(3px)' : 'none',
            marginBottom: menuOpen ? 0 : '5px',
          }} />
          <div style={{
            width: '17px', height: '1px', background: '#1d1d1f',
            transition: 'all 0.3s',
            opacity: menuOpen ? 0 : 1,
            marginBottom: menuOpen ? 0 : '5px',
          }} />
          <div style={{
            width: '17px', height: '1px', background: '#1d1d1f',
            transition: 'all 0.3s',
            transform: menuOpen ? 'rotate(-45deg) translateY(-3px)' : 'none',
          }} />
        </button>
      </div>

      {/* Mobile menu */}
      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0,
        width: '100%', maxWidth: '320px',
        background: 'rgba(255,255,255,0.98)',
        backdropFilter: 'blur(40px)',
        transform: menuOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex', flexDirection: 'column', padding: '5rem 2rem 2rem',
        gap: '0.5rem', zIndex: 999,
        boxShadow: menuOpen ? '-10px 0 40px rgba(0,0,0,0.06)' : 'none',
      }}>
        {['Products', 'Reviews', 'FAQ'].map((item, i) => (
          <a key={item} href={`#${item.toLowerCase()}`}
             onClick={() => setMenuOpen(false)}
             style={{
               color: '#1d1d1f', textDecoration: 'none', fontSize: '1.2rem', fontWeight: 600,
               padding: '0.8rem 0', borderBottom: '0.5px solid rgba(0,0,0,0.06)',
               opacity: menuOpen ? 1 : 0, transform: menuOpen ? 'translateX(0)' : 'translateX(20px)',
               transition: `all 0.3s ${i * 0.06 + 0.1}s`,
               fontFamily: "'Inter', sans-serif",
             }}>
            {item}
          </a>
        ))}
        <button onClick={() => { onCartClick(); setMenuOpen(false) }} style={{
          background: '#1d1d1f', color: '#fff',
          padding: '0.9rem 2rem',
          borderRadius: '980px', fontSize: '0.95rem', fontWeight: 500,
          border: 'none', cursor: 'pointer', marginTop: '1rem',
          opacity: menuOpen ? 1 : 0, transform: menuOpen ? 'translateX(0)' : 'translateX(20px)',
          transition: 'all 0.3s 0.35s',
          fontFamily: "'Inter', sans-serif",
        }}>View Cart{cartCount > 0 ? ` (${cartCount})` : ''}</button>
      </div>

      {menuOpen && <div onClick={() => setMenuOpen(false)} style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.15)', zIndex: 998,
      }} />}
    </nav>
  )
}
