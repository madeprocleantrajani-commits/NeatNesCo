import { useState } from 'react'
import { useInView } from '../hooks'
import { FAQ_ITEMS } from '../data'

function FAQItem({ item, isOpen, onToggle, index, darkMode }) {
  const [ref, visible] = useInView()

  return (
    <div ref={ref} style={{
      borderRadius: '18px',
      border: `1px solid ${isOpen ? 'rgba(45,106,79,0.15)' : 'var(--border-subtle)'}`,
      background: isOpen
        ? (darkMode ? 'rgba(45,106,79,0.06)' : 'rgba(45,106,79,0.02)')
        : 'var(--bg-card)',
      overflow: 'hidden',
      transition: 'all 0.3s',
      opacity: visible ? 1 : 0,
      transform: visible ? 'translateY(0)' : 'translateY(15px)',
      transitionDelay: `${index * 0.05}s`,
      boxShadow: isOpen ? 'var(--shadow-md)' : 'var(--shadow-sm)',
    }}>
      <button onClick={onToggle} style={{
        width: '100%', textAlign: 'left',
        padding: '1.3rem 1.5rem',
        background: 'transparent', border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        gap: '1rem',
        color: 'var(--text-primary)',
        fontFamily: "'Inter', sans-serif",
      }}>
        <span style={{ fontSize: '0.95rem', fontWeight: 600, lineHeight: 1.4 }}>
          {item.q}
        </span>
        <span style={{
          width: '28px', height: '28px', borderRadius: '8px',
          background: isOpen ? 'rgba(45,106,79,0.12)' : (darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)'),
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.85rem', fontWeight: 600,
          transition: 'all 0.3s',
          transform: isOpen ? 'rotate(45deg)' : 'rotate(0)',
          color: isOpen ? '#2d6a4f' : 'var(--text-tertiary)',
          flexShrink: 0,
        }}>+</span>
      </button>
      <div className={`faq-answer ${isOpen ? 'open' : ''}`}>
        <div className="faq-answer-inner">
          <div style={{
            padding: '0 1.5rem 1.3rem',
            fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.75,
          }}>
            {item.a}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function FAQ({ darkMode }) {
  const [ref, visible] = useInView()
  const [openIndex, setOpenIndex] = useState(0)

  return (
    <section id="faq" style={{
      padding: '6rem 2rem', position: 'relative', zIndex: 1,
    }}>
      <div style={{ maxWidth: '760px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '3rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s',
        }}>
          <span className="section-tag">FAQ</span>
          <h2 style={{
            fontFamily: "'Playfair Display', serif", fontSize: 'clamp(2rem, 4vw, 3.5rem)',
            fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.03em',
          }}>
            Got Questions?
          </h2>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '1.05rem', maxWidth: '480px', margin: '0.5rem auto 0' }}>
            Everything you need to know. Can't find an answer? Chat with us 24/7.
          </p>
        </div>

        <div className="faq-container" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {FAQ_ITEMS.map((item, i) => (
            <FAQItem
              key={i}
              item={item}
              index={i}
              isOpen={openIndex === i}
              onToggle={() => setOpenIndex(openIndex === i ? -1 : i)}
              darkMode={darkMode}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
