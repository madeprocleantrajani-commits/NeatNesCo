export default function Footer() {
  return (
    <footer style={{
      background: '#1d1d1f',
      color: 'rgba(255,255,255,0.6)', padding: '4rem 2rem 2rem',
      borderTop: '1px solid rgba(0,0,0,0.06)',
    }}>
      <div style={{
        maxWidth: '1100px', margin: '0 auto',
        display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '2.5rem', marginBottom: '3rem',
      }}>
        <div>
          <h3 style={{
            fontFamily: "'Inter', -apple-system, sans-serif",
            fontSize: '1.05rem', fontWeight: 600, color: '#f5f5f7',
            marginBottom: '0.8rem',
          }}>
            NeatNesCo
          </h3>
          <p style={{ fontSize: '0.82rem', lineHeight: 1.7, marginBottom: '1rem', color: 'rgba(255,255,255,0.6)' }}>
            Curating the internet's best trending products. Neat finds, neatly delivered — since 2023.
          </p>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {[
              { label: 'IG', url: 'https://instagram.com/neatnesco' },
              { label: 'TT', url: 'https://tiktok.com/@neatnesco' },
              { label: 'X', url: 'https://x.com/neatnesco' },
              { label: 'YT', url: 'https://youtube.com/@neatnesco' },
            ].map(social => (
              <a key={social.label} href={social.url} target="_blank" rel="noopener noreferrer" style={{
                width: '34px', height: '34px', borderRadius: '50%',
                background: 'rgba(255,255,255,0.06)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'rgba(255,255,255,0.6)', textDecoration: 'none',
                fontSize: '0.68rem', fontWeight: 600, transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.color = '#f5f5f7'; e.currentTarget.style.background = 'rgba(255,255,255,0.1)' }}
              onMouseLeave={e => { e.currentTarget.style.color = 'rgba(255,255,255,0.6)'; e.currentTarget.style.background = 'rgba(255,255,255,0.06)' }}>
                {social.label}
              </a>
            ))}
          </div>
        </div>

        <div>
          <h4 style={{
            color: '#f5f5f7', fontSize: '0.72rem', fontWeight: 600,
            marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.06em',
          }}>Shop</h4>
          {['New Arrivals', 'Best Sellers', 'On Sale', 'All Products', 'Gift Cards'].map(item => (
            <a key={item} href="#products" style={{
              display: 'block', color: 'rgba(255,255,255,0.6)', textDecoration: 'none',
              fontSize: '0.82rem', marginBottom: '0.6rem', transition: 'color 0.2s',
            }}
            onMouseEnter={e => e.target.style.color = '#f5f5f7'}
            onMouseLeave={e => e.target.style.color = 'rgba(255,255,255,0.6)'}>
              {item}
            </a>
          ))}
        </div>

        <div>
          <h4 style={{
            color: '#f5f5f7', fontSize: '0.72rem', fontWeight: 600,
            marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.06em',
          }}>Company</h4>
          <a href="mailto:support@neatnesco.com" style={{
            display: 'block', color: '#f5f5f7', textDecoration: 'none',
            fontSize: '0.82rem', marginBottom: '0.8rem', fontWeight: 500,
          }}>support@neatnesco.com</a>
          {['About Us', 'Contact', 'FAQ', 'Shipping & Returns', 'Wholesale'].map(item => (
            <a key={item} href={item === 'FAQ' ? '#faq' : '#story'} style={{
              display: 'block', color: 'rgba(255,255,255,0.6)', textDecoration: 'none',
              fontSize: '0.82rem', marginBottom: '0.6rem', transition: 'color 0.2s',
            }}
            onMouseEnter={e => e.target.style.color = '#f5f5f7'}
            onMouseLeave={e => e.target.style.color = 'rgba(255,255,255,0.6)'}>
              {item}
            </a>
          ))}
        </div>

        <div>
          <h4 style={{
            color: '#f5f5f7', fontSize: '0.72rem', fontWeight: 600,
            marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.06em',
          }}>Legal</h4>
          {['Privacy Policy', 'Terms of Service', 'Refund Policy', 'Cookie Policy', 'Accessibility'].map(item => (
            <a key={item} href="#faq" style={{
              display: 'block', color: 'rgba(255,255,255,0.6)', textDecoration: 'none',
              fontSize: '0.82rem', marginBottom: '0.6rem', transition: 'color 0.2s',
            }}
            onMouseEnter={e => e.target.style.color = '#f5f5f7'}
            onMouseLeave={e => e.target.style.color = 'rgba(255,255,255,0.6)'}>
              {item}
            </a>
          ))}
        </div>
      </div>

      <div style={{
        borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '1.2rem',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        flexWrap: 'wrap', gap: '0.8rem', fontSize: '0.72rem', color: 'rgba(255,255,255,0.45)',
      }}>
        <span>Copyright 2025 NeatNesCo. All rights reserved.</span>
        <span>Neat finds, neatly delivered</span>
      </div>
    </footer>
  )
}
