export default function Footer({ darkMode }) {
  return (
    <footer style={{
      background: darkMode ? '#050505' : '#0a0a0a',
      color: 'rgba(255,255,255,0.4)', padding: '5rem 2rem 2rem',
      position: 'relative', zIndex: 1,
    }}>
      {/* Top gradient line */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: '1px',
        background: 'linear-gradient(90deg, transparent, rgba(45,106,79,0.3), transparent)',
      }} />

      <div style={{
        maxWidth: '1200px', margin: '0 auto',
        display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: '3rem', marginBottom: '3.5rem',
      }}>
        <div>
          <h3 style={{
            fontFamily: "'Playfair Display', serif", fontSize: '1.4rem',
            fontWeight: 700, color: '#fff', marginBottom: '1rem',
            display: 'flex', alignItems: 'center', gap: '0.3rem',
          }}>
            <span style={{
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              width: '30px', height: '30px', borderRadius: '9px',
              background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
              color: '#fff', fontSize: '0.8rem', fontWeight: 800,
              boxShadow: '0 2px 8px rgba(45,106,79,0.3)',
            }}>N</span>
            eat<span style={{ color: '#52b788' }}>Nes</span>Co
          </h3>
          <p style={{ fontSize: '0.88rem', lineHeight: 1.75, marginBottom: '1.2rem' }}>
            Curating the internet's best trending products. Neat finds, neatly delivered — since 2023.
          </p>
          <div style={{ display: 'flex', gap: '0.6rem' }}>
            {[
              { label: 'IG', color: '#E1306C' },
              { label: 'TT', color: '#000' },
              { label: 'X', color: '#1DA1F2' },
              { label: 'YT', color: '#FF0000' },
            ].map(social => (
              <a key={social.label} href="#" style={{
                width: '38px', height: '38px', borderRadius: '10px',
                background: 'rgba(255,255,255,0.06)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'rgba(255,255,255,0.4)', textDecoration: 'none',
                fontSize: '0.72rem', fontWeight: 700, transition: 'all 0.3s',
                border: '1px solid rgba(255,255,255,0.04)',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'rgba(45,106,79,0.15)'
                e.currentTarget.style.borderColor = 'rgba(45,106,79,0.2)'
                e.currentTarget.style.color = '#52b788'
                e.currentTarget.style.transform = 'translateY(-2px)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.06)'
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.04)'
                e.currentTarget.style.color = 'rgba(255,255,255,0.4)'
                e.currentTarget.style.transform = 'translateY(0)'
              }}>
                {social.label}
              </a>
            ))}
          </div>
        </div>

        <div>
          <h4 style={{
            color: 'rgba(255,255,255,0.6)', fontSize: '0.75rem', fontWeight: 700,
            marginBottom: '1.2rem', textTransform: 'uppercase', letterSpacing: '0.12em',
          }}>Shop</h4>
          {['New Arrivals', 'Best Sellers', 'On Sale', 'All Products', 'Gift Cards'].map(item => (
            <a key={item} href="#products" style={{
              display: 'block', color: 'rgba(255,255,255,0.35)', textDecoration: 'none',
              fontSize: '0.88rem', marginBottom: '0.8rem', transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.target.style.color = '#52b788'; e.target.style.paddingLeft = '4px' }}
            onMouseLeave={e => { e.target.style.color = 'rgba(255,255,255,0.35)'; e.target.style.paddingLeft = '0' }}>
              {item}
            </a>
          ))}
        </div>

        <div>
          <h4 style={{
            color: 'rgba(255,255,255,0.6)', fontSize: '0.75rem', fontWeight: 700,
            marginBottom: '1.2rem', textTransform: 'uppercase', letterSpacing: '0.12em',
          }}>Company</h4>
          {['About Us', 'Contact', 'FAQ', 'Shipping & Returns', 'Wholesale'].map(item => (
            <a key={item} href={item === 'FAQ' ? '#faq' : '#story'} style={{
              display: 'block', color: 'rgba(255,255,255,0.35)', textDecoration: 'none',
              fontSize: '0.88rem', marginBottom: '0.8rem', transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.target.style.color = '#52b788'; e.target.style.paddingLeft = '4px' }}
            onMouseLeave={e => { e.target.style.color = 'rgba(255,255,255,0.35)'; e.target.style.paddingLeft = '0' }}>
              {item}
            </a>
          ))}
        </div>

        <div>
          <h4 style={{
            color: 'rgba(255,255,255,0.6)', fontSize: '0.75rem', fontWeight: 700,
            marginBottom: '1.2rem', textTransform: 'uppercase', letterSpacing: '0.12em',
          }}>Legal</h4>
          {['Privacy Policy', 'Terms of Service', 'Refund Policy', 'Cookie Policy', 'Accessibility'].map(item => (
            <a key={item} href="#" style={{
              display: 'block', color: 'rgba(255,255,255,0.35)', textDecoration: 'none',
              fontSize: '0.88rem', marginBottom: '0.8rem', transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.target.style.color = '#52b788'; e.target.style.paddingLeft = '4px' }}
            onMouseLeave={e => { e.target.style.color = 'rgba(255,255,255,0.35)'; e.target.style.paddingLeft = '0' }}>
              {item}
            </a>
          ))}
        </div>
      </div>

      {/* Bottom bar */}
      <div style={{
        borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '1.5rem',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        flexWrap: 'wrap', gap: '1rem', fontSize: '0.75rem',
      }}>
        <span>&copy; 2024 NeatNesCo. All rights reserved.</span>
        <span style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>Powered with ♡</span>
          <span style={{ color: '#2d6a4f' }}>●</span>
          <span>Neat finds, neatly delivered</span>
        </span>
      </div>
    </footer>
  )
}
