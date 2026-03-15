import { useState, useEffect } from 'react'
import { PRODUCTS } from '../data'

const NAMES = ['Emma S.', 'Liam K.', 'Sophia R.', 'Noah T.', 'Ava M.', 'Jackson L.', 'Mia W.', 'Oliver B.']
const LOCATIONS = ['New York', 'London', 'Tokyo', 'Sydney', 'Paris', 'Berlin', 'Toronto', 'Dubai', 'Seoul', 'Miami']
const TIMES = ['just now', '2 min ago', '5 min ago', '8 min ago', '12 min ago']

export default function SocialProof() {
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

    const initial = setTimeout(show, 8000)
    const interval = setInterval(show, 15000 + Math.random() * 10000)

    return () => {
      clearTimeout(initial)
      clearInterval(interval)
    }
  }, [])

  if (!notification) return null

  return (
    <div style={{
      position: 'fixed', bottom: '5.5rem', left: '2rem', zIndex: 7000,
      animation: visible ? 'socialProofIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)' : 'socialProofOut 0.4s ease-in forwards',
      pointerEvents: visible ? 'auto' : 'none',
    }}>
      <div style={{
        background: '#ffffff',
        border: '1px solid rgba(0,0,0,0.06)',
        borderRadius: '14px',
        padding: '0.8rem 1rem',
        display: 'flex', alignItems: 'center', gap: '0.7rem',
        boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
        maxWidth: '300px',
      }}>
        <div style={{
          width: '40px', height: '40px', borderRadius: '10px',
          background: '#f5f5f7', flexShrink: 0, overflow: 'hidden',
        }}>
          {notification.product.image && (
            <img src={notification.product.image} alt="" style={{
              width: '100%', height: '100%', objectFit: 'cover',
            }} />
          )}
        </div>
        <div>
          <div style={{ fontSize: '0.78rem', color: '#1d1d1f' }}>
            <span style={{ fontWeight: 600 }}>{notification.name}</span>
            {' '}from {notification.location}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#6e6e73', marginTop: '0.1rem' }}>
            purchased <span style={{ fontWeight: 600 }}>{notification.product.name}</span>
          </div>
          <div style={{ fontSize: '0.65rem', color: '#aeaeb2', marginTop: '0.15rem' }}>
            {notification.time}
          </div>
        </div>
      </div>
    </div>
  )
}
