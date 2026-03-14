import { useState, useEffect } from 'react'
import { PRODUCTS, REVIEWS } from '../data'

const NAMES = ['Emma S.', 'Liam K.', 'Sophia R.', 'Noah T.', 'Ava M.', 'Jackson L.', 'Mia W.', 'Oliver B.']
const LOCATIONS = ['New York', 'London', 'Tokyo', 'Sydney', 'Paris', 'Berlin', 'Toronto', 'Dubai', 'Seoul', 'Miami']
const TIMES = ['just now', '2 min ago', '5 min ago', '8 min ago', '12 min ago']

export default function SocialProof({ darkMode }) {
  const [notification, setNotification] = useState(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const show = () => {
      const product = PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)]
      const name = NAMES[Math.floor(Math.random() * NAMES.length)]
      const location = LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)]
      const time = TIMES[Math.floor(Math.random() * TIMES.length)]

      setNotification({ product, name, location, time })
      setVisible(true)

      setTimeout(() => setVisible(false), 4000)
    }

    // First one after 8 seconds
    const initial = setTimeout(show, 8000)
    // Then every 15-25 seconds
    const interval = setInterval(show, 15000 + Math.random() * 10000)

    return () => {
      clearTimeout(initial)
      clearInterval(interval)
    }
  }, [])

  if (!notification) return null

  return (
    <div style={{
      position: 'fixed', bottom: '2rem', left: '2rem', zIndex: 7000,
      animation: visible ? 'socialProofIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)' : 'socialProofOut 0.4s ease-in forwards',
      pointerEvents: visible ? 'auto' : 'none',
    }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '18px',
        padding: '0.9rem 1.2rem',
        display: 'flex', alignItems: 'center', gap: '0.8rem',
        boxShadow: '0 12px 40px rgba(0,0,0,0.12)',
        backdropFilter: 'blur(20px)',
        maxWidth: '320px',
      }}>
        <div style={{
          width: '44px', height: '44px', borderRadius: '14px',
          background: notification.product.gradient,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1.5rem', flexShrink: 0,
        }}>
          {notification.product.emoji}
        </div>
        <div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)' }}>
            <span style={{ fontWeight: 700 }}>{notification.name}</span>
            {' '}from {notification.location}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
            purchased <span style={{ fontWeight: 600 }}>{notification.product.name}</span>
          </div>
          <div style={{
            fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '0.2rem',
            display: 'flex', alignItems: 'center', gap: '0.3rem',
          }}>
            <span style={{
              width: '5px', height: '5px', borderRadius: '50%', background: '#2d6a4f',
              display: 'inline-block',
            }} />
            {notification.time}
          </div>
        </div>
      </div>
    </div>
  )
}
