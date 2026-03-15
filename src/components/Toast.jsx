export default function Toast({ toasts }) {
  return (
    <div style={{
      position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 8000,
      display: 'flex', flexDirection: 'column', gap: '0.5rem',
      pointerEvents: 'none',
    }}>
      {toasts.map(toast => (
        <div key={toast.id} style={{
          background: '#ffffff',
          border: '1px solid rgba(0,0,0,0.06)',
          borderRadius: '14px',
          padding: '0.7rem 1rem',
          display: 'flex', alignItems: 'center', gap: '0.7rem',
          boxShadow: '0 8px 30px rgba(0,0,0,0.1)',
          animation: toast.removing
            ? 'toastSlideOut 0.3s ease-in forwards'
            : 'toastSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
          pointerEvents: 'auto',
          maxWidth: '300px',
        }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: '#f5f5f7', flexShrink: 0, overflow: 'hidden',
          }}>
            {toast.product?.image && (
              <img src={toast.product.image} alt="" style={{
                width: '100%', height: '100%', objectFit: 'cover',
              }} />
            )}
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#1d1d1f' }}>
              {toast.title || 'Added to cart'}
            </div>
            <div style={{ fontSize: '0.72rem', color: '#86868b' }}>
              {toast.message}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
