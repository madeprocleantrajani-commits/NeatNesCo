export default function CartDrawer({ isOpen, onClose, cart, onUpdateQty, onRemove, darkMode }) {
  const items = cart.reduce((acc, product) => {
    const existing = acc.find(i => i.product.id === product.id)
    if (existing) existing.qty++
    else acc.push({ product, qty: 1 })
    return acc
  }, [])

  const subtotal = items.reduce((sum, i) => sum + i.product.price * i.qty, 0)
  const savings = items.reduce((sum, i) => sum + (i.product.originalPrice - i.product.price) * i.qty, 0)
  const shipping = subtotal > 50 ? 0 : 4.99

  return (
    <>
      {/* Overlay */}
      {isOpen && <div onClick={onClose} style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
        backdropFilter: 'blur(4px)', zIndex: 9998,
        animation: 'modalOverlayIn 0.3s ease-out',
      }} />}

      {/* Drawer */}
      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0,
        width: '100%', maxWidth: '420px', zIndex: 9999,
        background: 'var(--bg-card)',
        transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex', flexDirection: 'column',
        boxShadow: isOpen ? '-16px 0 48px rgba(0,0,0,0.15)' : 'none',
        borderLeft: '1px solid var(--border-subtle)',
      }}>
        {/* Header */}
        <div style={{
          padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-subtle)',
        }}>
          <div>
            <h3 style={{
              fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)',
              display: 'flex', alignItems: 'center', gap: '0.5rem',
            }}>
              🛒 Your Cart
              {cart.length > 0 && (
                <span style={{
                  background: '#2d6a4f', color: '#fff', borderRadius: '100px',
                  padding: '0.1rem 0.6rem', fontSize: '0.72rem', fontWeight: 700,
                }}>{items.length} item{items.length !== 1 ? 's' : ''}</span>
              )}
            </h3>
          </div>
          <button onClick={onClose} style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
            border: 'none', cursor: 'pointer', fontSize: '1rem',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--text-primary)', transition: 'all 0.2s',
          }}>✕</button>
        </div>

        {/* Free shipping progress */}
        {subtotal < 50 && cart.length > 0 && (
          <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
            <div style={{
              fontSize: '0.78rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem',
              display: 'flex', justifyContent: 'space-between',
            }}>
              <span>🚚 Add ${(50 - subtotal).toFixed(2)} more for FREE shipping</span>
              <span style={{ fontWeight: 600 }}>${subtotal.toFixed(2)} / $50</span>
            </div>
            <div style={{
              height: '4px', borderRadius: '2px',
              background: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
              overflow: 'hidden',
            }}>
              <div style={{
                height: '100%', borderRadius: '2px',
                background: 'linear-gradient(90deg, #2d6a4f, #52b788)',
                width: `${Math.min((subtotal / 50) * 100, 100)}%`,
                transition: 'width 0.5s ease',
              }} />
            </div>
          </div>
        )}

        {/* Cart items */}
        <div style={{
          flex: 1, overflowY: 'auto', padding: '1rem 1.5rem',
        }}>
          {items.length === 0 ? (
            <div style={{
              textAlign: 'center', padding: '4rem 1rem',
              color: 'var(--text-tertiary)',
            }}>
              <div style={{ fontSize: '3.5rem', marginBottom: '1rem', opacity: 0.5 }}>🛒</div>
              <p style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                Your cart is empty
              </p>
              <p style={{ fontSize: '0.88rem' }}>Looks like you haven't found your thing yet.</p>
              <button onClick={onClose} style={{
                marginTop: '1.5rem', background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
                color: '#fff', border: 'none', padding: '0.8rem 2rem',
                borderRadius: '100px', fontSize: '0.88rem', fontWeight: 600,
                cursor: 'pointer',
              }}>Browse Products</button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {items.map(({ product, qty }) => (
                <div key={product.id} style={{
                  display: 'flex', gap: '1rem', padding: '1rem',
                  borderRadius: '16px',
                  background: darkMode ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)',
                  border: '1px solid var(--border-subtle)',
                }}>
                  {/* Product image */}
                  <div style={{
                    width: '72px', height: '72px', borderRadius: '14px',
                    background: product.gradient,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '2rem', flexShrink: 0,
                  }}>
                    {product.emoji}
                  </div>

                  {/* Details */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '0.5rem' }}>
                      <h4 style={{
                        fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)',
                        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      }}>{product.name}</h4>
                      <button onClick={() => onRemove(product.id)} style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: 'var(--text-muted)', fontSize: '0.8rem', padding: '0.2rem',
                        flexShrink: 0, transition: 'color 0.2s',
                      }}>✕</button>
                    </div>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.6rem' }}>
                      {product.category}
                    </p>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{
                        display: 'flex', alignItems: 'center',
                        borderRadius: '8px', overflow: 'hidden',
                        border: '1px solid var(--border-subtle)',
                      }}>
                        <button onClick={() => onUpdateQty(product.id, -1)} style={{
                          width: '28px', height: '28px', border: 'none',
                          background: 'transparent', cursor: 'pointer',
                          fontSize: '0.85rem', color: 'var(--text-primary)',
                        }}>−</button>
                        <span style={{
                          padding: '0 0.5rem', fontSize: '0.8rem', fontWeight: 700,
                          color: 'var(--text-primary)',
                        }}>{qty}</span>
                        <button onClick={() => onUpdateQty(product.id, 1)} style={{
                          width: '28px', height: '28px', border: 'none',
                          background: 'transparent', cursor: 'pointer',
                          fontSize: '0.85rem', color: 'var(--text-primary)',
                        }}>+</button>
                      </div>
                      <span style={{
                        fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)',
                      }}>
                        ${(product.price * qty).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer / checkout */}
        {items.length > 0 && (
          <div style={{
            padding: '1.5rem', borderTop: '1px solid var(--border-subtle)',
            background: darkMode ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.02)',
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <span>Subtotal</span>
                <span style={{ fontWeight: 600 }}>${subtotal.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#2d6a4f' }}>
                <span>You save</span>
                <span style={{ fontWeight: 600 }}>-${savings.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <span>Shipping</span>
                <span style={{ fontWeight: 600 }}>{shipping === 0 ? 'FREE 🎉' : `$${shipping.toFixed(2)}`}</span>
              </div>
              <div style={{
                height: '1px', background: 'var(--border-subtle)', margin: '0.3rem 0',
              }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                <span>Total</span>
                <span>${(subtotal + shipping).toFixed(2)}</span>
              </div>
            </div>

            <button style={{
              width: '100%', padding: '1rem', borderRadius: '14px',
              background: 'linear-gradient(135deg, #2d6a4f, #52b788)',
              color: '#fff', border: 'none', fontSize: '1rem', fontWeight: 700,
              cursor: 'pointer', transition: 'all 0.3s',
              boxShadow: '0 4px 16px rgba(45,106,79,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
            }}>
              🔒 Secure Checkout
            </button>

            <div style={{
              display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '1rem',
              fontSize: '0.72rem', color: 'var(--text-muted)',
            }}>
              <span>💳 Visa</span>
              <span>💳 Mastercard</span>
              <span> Apple Pay</span>
              <span>🅿️ PayPal</span>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
