import { PRODUCTS } from '../data'

export default function CartDrawer({ isOpen, onClose, cart, onUpdateQty, onRemove, onAddToCart }) {
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
      {isOpen && <div onClick={onClose} style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.2)',
        backdropFilter: 'blur(8px)', zIndex: 9998,
        animation: 'modalOverlayIn 0.3s ease-out',
      }} />}

      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0,
        width: '100%', maxWidth: '400px', zIndex: 9999,
        background: '#ffffff',
        transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex', flexDirection: 'column',
        boxShadow: isOpen ? '-8px 0 30px rgba(0,0,0,0.08)' : 'none',
      }}>
        {/* Header */}
        <div style={{
          padding: '1.2rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          borderBottom: '1px solid rgba(0,0,0,0.06)',
        }}>
          <h3 style={{
            fontSize: '1.05rem', fontWeight: 600, color: '#1d1d1f',
            display: 'flex', alignItems: 'center', gap: '0.4rem',
            fontFamily: "'Inter', sans-serif",
          }}>
            Your Cart
            {cart.length > 0 && (
              <span style={{
                background: '#1d1d1f', color: '#fff', borderRadius: '980px',
                padding: '0.1rem 0.5rem', fontSize: '0.68rem', fontWeight: 600,
              }}>{items.length}</span>
            )}
          </h3>
          <button onClick={onClose} style={{
            width: '32px', height: '32px', borderRadius: '50%',
            background: 'rgba(0,0,0,0.04)',
            border: 'none', cursor: 'pointer', fontSize: '0.85rem',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#1d1d1f',
          }}>×</button>
        </div>

        {/* Free shipping */}
        {subtotal < 50 && cart.length > 0 && (
          <div style={{ padding: '0.8rem 1.5rem', borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
            <div style={{
              fontSize: '0.75rem', color: '#86868b', marginBottom: '0.4rem',
              display: 'flex', justifyContent: 'space-between',
            }}>
              <span>Add ${(50 - subtotal).toFixed(2)} more for free shipping</span>
              <span style={{ fontWeight: 600 }}>${subtotal.toFixed(2)} / $50</span>
            </div>
            <div style={{
              height: '3px', borderRadius: '2px', background: 'rgba(0,0,0,0.06)', overflow: 'hidden',
            }}>
              <div style={{
                height: '100%', borderRadius: '2px', background: '#1d1d1f',
                width: `${Math.min((subtotal / 50) * 100, 100)}%`,
                transition: 'width 0.5s ease',
              }} />
            </div>
          </div>
        )}

        {/* Items */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 1.5rem' }}>
          {items.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem 1rem', color: '#86868b' }}>
              <p style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.3rem', color: '#6e6e73' }}>
                Your cart is empty
              </p>
              <p style={{ fontSize: '0.85rem' }}>Looks like you haven't found your thing yet.</p>
              <button onClick={onClose} style={{
                marginTop: '1.2rem', background: '#1d1d1f', color: '#fff',
                border: 'none', padding: '0.7rem 1.8rem', borderRadius: '980px',
                fontSize: '0.85rem', fontWeight: 500, cursor: 'pointer',
                fontFamily: "'Inter', sans-serif",
              }}>Browse Products</button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              {items.map(({ product, qty }) => (
                <div key={product.id} style={{
                  display: 'flex', gap: '0.8rem', padding: '0.8rem',
                  borderRadius: '14px', background: '#f5f5f7',
                }}>
                  <div style={{
                    width: '64px', height: '64px', borderRadius: '12px',
                    background: '#e8e8ed', flexShrink: 0, overflow: 'hidden',
                  }}>
                    {product.image && (
                      <img src={product.image} alt={product.name} style={{
                        width: '100%', height: '100%', objectFit: 'cover',
                      }} />
                    )}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '0.4rem' }}>
                      <h4 style={{
                        fontSize: '0.85rem', fontWeight: 600, color: '#1d1d1f',
                        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      }}>{product.name}</h4>
                      <button onClick={() => onRemove(product.id)} style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: '#aeaeb2', fontSize: '0.75rem', padding: '0.2rem', flexShrink: 0,
                      }}>×</button>
                    </div>
                    <p style={{ fontSize: '0.7rem', color: '#aeaeb2', marginBottom: '0.4rem' }}>{product.category}</p>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{
                        display: 'flex', alignItems: 'center',
                        borderRadius: '6px', overflow: 'hidden', background: '#ffffff',
                      }}>
                        <button onClick={() => onUpdateQty(product.id, -1)} style={{
                          width: '26px', height: '26px', border: 'none',
                          background: 'transparent', cursor: 'pointer',
                          fontSize: '0.8rem', color: '#1d1d1f',
                        }}>-</button>
                        <span style={{ padding: '0 0.4rem', fontSize: '0.78rem', fontWeight: 600, color: '#1d1d1f' }}>{qty}</span>
                        <button onClick={() => onUpdateQty(product.id, 1)} style={{
                          width: '26px', height: '26px', border: 'none',
                          background: 'transparent', cursor: 'pointer',
                          fontSize: '0.8rem', color: '#1d1d1f',
                        }}>+</button>
                      </div>
                      <span style={{ fontWeight: 600, fontSize: '0.88rem', color: '#1d1d1f' }}>
                        ${(product.price * qty).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Upsells */}
          {items.length > 0 && (() => {
            const cartIds = new Set(items.map(i => i.product.id))
            const recommendations = PRODUCTS
              .filter(p => !cartIds.has(p.id))
              .sort((a, b) => b.reviews - a.reviews)
              .slice(0, 3)
            if (recommendations.length === 0) return null
            return (
              <div style={{ marginTop: '1.2rem', paddingTop: '1rem', borderTop: '1px solid rgba(0,0,0,0.06)' }}>
                <p style={{
                  fontSize: '0.75rem', fontWeight: 600, color: '#86868b',
                  textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.6rem',
                }}>You might also like</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {recommendations.map(p => (
                    <div key={p.id} className="cart-item" style={{
                      display: 'flex', alignItems: 'center', gap: '0.6rem',
                      padding: '0.5rem', borderRadius: '10px', background: '#f5f5f7',
                    }}>
                      <div style={{
                        width: '48px', height: '48px', borderRadius: '8px',
                        overflow: 'hidden', flexShrink: 0, background: '#e8e8ed',
                      }}>
                        <img src={p.image} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{
                          fontSize: '0.78rem', fontWeight: 600, color: '#1d1d1f',
                          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                        }}>{p.name}</p>
                        <p style={{ fontSize: '0.72rem', color: '#6e6e73', fontWeight: 500 }}>${p.price}</p>
                      </div>
                      <button onClick={() => onAddToCart(p)} style={{
                        width: '30px', height: '30px', borderRadius: '50%',
                        background: '#1d1d1f', color: '#fff', border: 'none',
                        cursor: 'pointer', fontSize: '1rem', fontWeight: 300,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0,
                      }}>+</button>
                    </div>
                  ))}
                </div>
              </div>
            )
          })()}
        </div>

        {/* Checkout */}
        {items.length > 0 && (
          <div style={{ padding: '1.2rem 1.5rem', borderTop: '1px solid rgba(0,0,0,0.06)', background: '#f5f5f7' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: '#6e6e73' }}>
                <span>Subtotal</span>
                <span style={{ fontWeight: 600 }}>${subtotal.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: '#86868b' }}>
                <span>You save</span>
                <span style={{ fontWeight: 600 }}>-${savings.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: '#6e6e73' }}>
                <span>Shipping</span>
                <span style={{ fontWeight: 600 }}>{shipping === 0 ? 'Free' : `$${shipping.toFixed(2)}`}</span>
              </div>
              <div style={{ height: '1px', background: 'rgba(0,0,0,0.06)', margin: '0.2rem 0' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1rem', fontWeight: 700, color: '#1d1d1f' }}>
                <span>Total</span>
                <span>${(subtotal + shipping).toFixed(2)}</span>
              </div>
            </div>

            <button onClick={() => {
              const lineItems = items.map(i => `${i.product.variantId}:${i.qty}`).join(',')
              window.open(`https://8hendy-8i.myshopify.com/cart/${lineItems}`, '_blank')
            }} style={{
              width: '100%', padding: '0.85rem', borderRadius: '12px',
              background: '#1d1d1f', color: '#fff',
              border: 'none', fontSize: '0.95rem', fontWeight: 500,
              cursor: 'pointer', fontFamily: "'Inter', sans-serif",
            }}>
              Checkout — ${(subtotal + shipping).toFixed(2)}
            </button>

            <p style={{
              textAlign: 'center', fontSize: '0.65rem', color: '#aeaeb2',
              marginTop: '0.4rem', fontStyle: 'italic',
            }}>
              Secure checkout via Shopify
            </p>

            <div style={{
              display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '0.5rem',
              fontSize: '0.7rem', color: '#aeaeb2',
            }}>
              <span>Visa</span>
              <span>Mastercard</span>
              <span>Apple Pay</span>
              <span>PayPal</span>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
