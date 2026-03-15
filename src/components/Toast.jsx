export default function Toast({ toasts }) {
  return (
    <div style={{
      position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 8000,
      display: 'flex', flexDirection: 'column', gap: '0.5rem',
      pointerEvents: 'none',
    }}>
      {toasts.map(toast => (
        <div key={toast.id} style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px',
          padding: '0.8rem 1.2rem',
          display: 'flex', alignItems: 'center', gap: '0.8rem',
          boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
          backdropFilter: 'blur(20px)',
          animation: toast.removing
            ? 'toastSlideOut 0.3s ease-in forwards'
            : 'toastSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
          pointerEvents: 'auto',
          maxWidth: '320px',
        }}>
          <div style={{
            width: '40px', height: '40px', borderRadius: '12px',
            background: toast.product?.gradient || 'linear-gradient(135deg, #2d6a4f, #52b788)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.3rem', flexShrink: 0,
          }}>
            {toast.product?.emoji || '✓'}
          </div>
          <div>
            <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {toast.title || 'Added to cart'}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
              {toast.message}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
