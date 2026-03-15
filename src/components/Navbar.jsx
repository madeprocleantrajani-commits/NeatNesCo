import { useState, useEffect } from 'react'

export default function Navbar({ cartCount, wishlistCount, onCartClick, onDarkModeToggle, darkMode }) {
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

  const navBg = scrolled
    ? (darkMode ? 'rgba(10,10,10,0.92)' : 'rgba(250,250,248,0.88)')
    : 'transparent'

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
      padding: '0 clamp(1rem, 4vw, 3rem)', height: '72px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      background: navBg,
      backdropFilter: scrolled ? 'blur(24px) saturate(1.4)' : 'none',
      WebkitBackdropFilter: scrolled ? 'blur(24px) saturate(1.4)' : 'none',
      borderBottom: scrolled ? '1px solid var(--border-subtle)' : 'none',
      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    }}>
      {/* Logo */}
      <a href="#" style={{
        fontFamily: "'Playfair Display', serif", fontSize: '1.5rem', fontWeight: 700,
        color: 'var(--text-primary)', textDecoration: 'none', letterSpacing: '-0.03em',
        display: 'flex', alignItems: 'center', gap: '0.3rem',
      }}>
        <span style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          width: '34px', height: '34px', borderRadius: '10px',
          background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
          color: '#fff', fontSize: '0.9rem', fontWeight: 800,
          fontFamily: "'Playfair Display', serif",
          boxShadow: '0 2px 12px rgba(45,106,79,0.3)',
        }}>N</span>
        <span>eat<span style={{ color: '#2d6a4f' }}>Nes</span>Co</span>
      </a>

      {/* Desktop nav */}
      <div style={{
        display: 'flex', gap: '2rem', alignItems: 'center',
      }} className="nav-links-desktop">
        {['Products', 'Story', 'Reviews', 'FAQ'].map(item => (
          <a key={item} href={`#${item.toLowerCase()}`} style={{
            color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '0.9rem',
            fontWeight: 500, transition: 'color 0.2s',
          }} className="nav-link">
            {item}
          </a>
        ))}

        {/* Dark mode toggle */}
        <button onClick={onDarkModeToggle} style={{
          background: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px', width: '40px', height: '40px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', fontSize: '1.1rem',
          transition: 'all 0.3s',
        }}>
          {darkMode ? '☀️' : '🌙'}
        </button>

        {/* Wishlist */}
        <div style={{ position: 'relative' }}>
          <a href="#products" style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            width: '40px', height: '40px', borderRadius: '12px',
            background: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)',
            border: '1px solid var(--border-subtle)',
            textDecoration: 'none', fontSize: '1.1rem',
            transition: 'all 0.3s',
          }}>
            ♡
          </a>
          {wishlistCount > 0 && (
            <span style={{
              position: 'absolute', top: '-4px', right: '-4px',
              background: '#e63946', color: '#fff', borderRadius: '50%',
              width: '18px', height: '18px', display: 'flex',
              alignItems: 'center', justifyContent: 'center', fontSize: '0.6rem',
              fontWeight: 800, border: '2px solid var(--bg-primary)',
            }}>{wishlistCount}</span>
          )}
        </div>

        {/* Cart button */}
        <button onClick={onCartClick} className="shiny-btn" style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.6rem',
          background: darkMode ? '#fff' : '#1a1a1a',
          color: darkMode ? '#1a1a1a' : '#fff',
          padding: '0.65rem 1.6rem',
          borderRadius: '100px', fontSize: '0.88rem', fontWeight: 600,
          border: 'none', cursor: 'pointer',
          position: 'relative', overflow: 'hidden',
          transition: 'all 0.3s',
          boxShadow: '0 2px 12px rgba(0,0,0,0.15)',
        }}>
          <span style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            🛒 Cart
            {cartCount > 0 && (
              <span style={{
                background: '#e63946', color: '#fff', borderRadius: '50%',
                width: '20px', height: '20px', display: 'inline-flex',
                alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem',
                fontWeight: 800,
              }}>{cartCount}</span>
            )}
          </span>
        </button>
      </div>

      {/* Mobile hamburger */}
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }} className="mobile-menu-btn">
        <button onClick={onDarkModeToggle} style={{
          background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.2rem',
          padding: '0.5rem',
        }}>
          {darkMode ? '☀️' : '🌙'}
        </button>
        <button onClick={onCartClick} style={{
          background: 'none', border: 'none', cursor: 'pointer', position: 'relative',
          fontSize: '1.2rem', padding: '0.5rem',
        }}>
          🛒
          {cartCount > 0 && (
            <span style={{
              position: 'absolute', top: '2px', right: '0',
              background: '#e63946', color: '#fff', borderRadius: '50%',
              width: '16px', height: '16px', display: 'flex',
              alignItems: 'center', justifyContent: 'center', fontSize: '0.55rem',
              fontWeight: 800,
            }}>{cartCount}</span>
          )}
        </button>
        <button onClick={() => setMenuOpen(!menuOpen)} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          padding: '0.5rem', position: 'relative', zIndex: 1001,
        }}>
          <div style={{
            width: '24px', height: '2px', background: 'var(--text-primary)',
            transition: 'all 0.3s',
            transform: menuOpen ? 'rotate(45deg) translateY(4px)' : 'none',
            marginBottom: menuOpen ? 0 : '6px',
          }} />
          <div style={{
            width: '24px', height: '2px', background: 'var(--text-primary)',
            transition: 'all 0.3s',
            opacity: menuOpen ? 0 : 1,
            marginBottom: menuOpen ? 0 : '6px',
          }} />
          <div style={{
            width: '24px', height: '2px', background: 'var(--text-primary)',
            transition: 'all 0.3s',
            transform: menuOpen ? 'rotate(-45deg) translateY(-4px)' : 'none',
          }} />
        </button>
      </div>

      {/* Mobile slide-out menu */}
      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0,
        width: '100%', maxWidth: '340px',
        background: darkMode ? 'rgba(10,10,10,0.98)' : 'rgba(250,250,248,0.98)',
        backdropFilter: 'blur(30px)',
        transform: menuOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex', flexDirection: 'column', padding: '6rem 2rem 2rem',
        gap: '0.5rem', zIndex: 999,
        boxShadow: menuOpen ? '-20px 0 60px rgba(0,0,0,0.2)' : 'none',
      }}>
        {['Products', 'Story', 'Reviews', 'FAQ'].map((item, i) => (
          <a key={item} href={`#${item.toLowerCase()}`}
             onClick={() => setMenuOpen(false)}
             style={{
               color: 'var(--text-primary)', textDecoration: 'none', fontSize: '1.5rem', fontWeight: 600,
               padding: '1rem 0', borderBottom: '1px solid var(--border-subtle)',
               opacity: menuOpen ? 1 : 0, transform: menuOpen ? 'translateX(0)' : 'translateX(20px)',
               transition: `all 0.3s ${i * 0.08 + 0.15}s cubic-bezier(0.4, 0, 0.2, 1)`,
             }}>
            {item}
          </a>
        ))}
        <button onClick={() => { onCartClick(); setMenuOpen(false) }} style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
          background: darkMode ? '#fff' : '#1a1a1a',
          color: darkMode ? '#1a1a1a' : '#fff',
          padding: '1rem 2rem',
          borderRadius: '100px', fontSize: '1rem', fontWeight: 600,
          border: 'none', cursor: 'pointer', marginTop: '1rem',
          opacity: menuOpen ? 1 : 0, transform: menuOpen ? 'translateX(0)' : 'translateX(20px)',
          transition: 'all 0.3s 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>🛒 View Cart {cartCount > 0 && `(${cartCount})`}</button>
      </div>

      {menuOpen && <div onClick={() => setMenuOpen(false)} style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)', zIndex: 998,
      }} />}
    </nav>
  )
}
