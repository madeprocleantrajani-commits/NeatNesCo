import { useState } from 'react'
import { useInView } from '../hooks'
import { FAQ_ITEMS } from '../data'

function FAQItem({ item, isOpen, onToggle, index }) {
  const [ref, visible] = useInView()

  return (
    <div ref={ref} style={{
      borderRadius: '14px',
      borderTop: `1px solid ${isOpen ? 'rgba(0,0,0,0.12)' : 'rgba(0,0,0,0.06)'}`,
      borderRight: `1px solid ${isOpen ? 'rgba(0,0,0,0.12)' : 'rgba(0,0,0,0.06)'}`,
      borderBottom: `1px solid ${isOpen ? 'rgba(0,0,0,0.12)' : 'rgba(0,0,0,0.06)'}`,
      borderLeft: isOpen ? '3px solid #1d1d1f' : `1px solid ${isOpen ? 'rgba(0,0,0,0.12)' : 'rgba(0,0,0,0.06)'}`,
      background: isOpen ? '#f5f5f7' : '#ffffff',
      overflow: 'hidden',
      transition: 'all 0.3s',
      opacity: visible ? 1 : 0,
      transform: visible ? 'translateY(0)' : 'translateY(10px)',
      transitionDelay: `${index * 0.04}s`,
    }}>
      <button onClick={onToggle} style={{
        width: '100%', textAlign: 'left',
        padding: '1.1rem 1.3rem',
        background: 'transparent', border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        gap: '1rem', color: '#1d1d1f',
        fontFamily: "'Inter', sans-serif",
      }}>
        <span style={{ fontSize: '0.92rem', fontWeight: 500, lineHeight: 1.4 }}>
          {item.q}
        </span>
        <span style={{
          fontSize: '1.1rem', fontWeight: 300,
          transition: 'all 0.3s',
          transform: isOpen ? 'rotate(45deg)' : 'rotate(0)',
          color: isOpen ? '#1d1d1f' : '#aeaeb2',
          flexShrink: 0,
        }}>+</span>
      </button>
      <div className={`faq-answer ${isOpen ? 'open' : ''}`}>
        <div className="faq-answer-inner">
          <div style={{
            padding: '0 1.3rem 1.1rem',
            fontSize: '0.88rem', color: '#6e6e73', lineHeight: 1.7,
          }}>
            {item.a}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function FAQ() {
  const [ref, visible] = useInView()
  const [openIndex, setOpenIndex] = useState(0)

  return (
    <section id="faq" style={{
      padding: '6rem 2rem',
      background: '#ffffff',
    }}>
      <div style={{ maxWidth: '700px', margin: '0 auto' }}>
        <div ref={ref} style={{
          textAlign: 'center', marginBottom: '2.5rem',
          opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(15px)',
          transition: 'all 0.6s',
        }}>
          <p style={{
            fontSize: '0.8rem', fontWeight: 500, color: '#86868b',
            letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.6rem',
          }}>FAQ</p>
          <h2 style={{
            fontFamily: "'Inter', -apple-system, sans-serif",
            fontSize: 'clamp(2.4rem, 5vw, 3.5rem)',
            fontWeight: 700, color: '#1d1d1f', letterSpacing: '-0.03em',
          }}>
            Got Questions?
          </h2>
          <p style={{ color: '#6e6e73', fontSize: '1rem', margin: '0.5rem auto 0' }}>
            Quick answers to common questions.
          </p>
        </div>

        <div className="faq-container" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {FAQ_ITEMS.map((item, i) => (
            <FAQItem
              key={i} item={item} index={i}
              isOpen={openIndex === i}
              onToggle={() => setOpenIndex(openIndex === i ? -1 : i)}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
