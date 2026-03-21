import { useState, useRef, useEffect } from 'react'
import { PRODUCTS, FAQ_ITEMS } from '../data'

const BOT_NAME = 'NeatNesCo Assistant'

const QUICK_REPLIES = [
  'Shipping info',
  'Return policy',
  'Track my order',
  'Product recommendations',
  'Payment methods',
]

function getBotResponse(input) {
  const q = input.toLowerCase()

  // Shipping
  if (q.includes('ship') || q.includes('deliver') || q.includes('how long')) {
    return 'Orders ship within 24-48 hours. Estimated delivery is 12-20 business days. All orders include free tracking. Orders over $25 get free shipping!'
  }

  // Returns
  if (q.includes('return') || q.includes('refund') || q.includes('money back')) {
    return 'We offer a hassle-free 30-day return policy on all products. If you\'re not satisfied, reach out to us and we\'ll arrange a full refund — we even cover return shipping costs.'
  }

  // Tracking
  if (q.includes('track') || q.includes('where is my order') || q.includes('order status')) {
    return 'Once your order ships, you\'ll receive an email with a tracking number and link. You can also email us at support@neatnesco.com with your order number and we\'ll check the status for you.'
  }

  // Payment
  if (q.includes('pay') || q.includes('credit card') || q.includes('apple pay') || q.includes('visa')) {
    return 'We accept Visa, Mastercard, Amex, Apple Pay, Google Pay, PayPal, and Shop Pay. All transactions are secured with 256-bit SSL encryption.'
  }

  // Product recommendations
  if (q.includes('recommend') || q.includes('best') || q.includes('popular') || q.includes('what should')) {
    const top = PRODUCTS.filter(p => p.rating >= 4.8).slice(0, 3)
    return `Our top-rated products right now:\n\n${top.map(p => `${p.name} — $${p.price} (${p.rating}/5 from ${p.reviews.toLocaleString()} reviews)`).join('\n')}\n\nScroll down to browse all products!`
  }

  // Price / cost
  if (q.includes('price') || q.includes('cost') || q.includes('how much') || q.includes('expensive')) {
    return 'Our products range from $16.99 to $59.99. Every item is curated for the best quality-to-price ratio. We also run flash sales with up to 50% off regularly!'
  }

  // Contact / support
  if (q.includes('contact') || q.includes('support') || q.includes('help') || q.includes('email') || q.includes('phone')) {
    return 'You can reach our support team anytime at support@neatnesco.com. We typically respond within 2 hours. We\'re here to help!'
  }

  // Cancel / modify order
  if (q.includes('cancel') || q.includes('modify') || q.includes('change my order')) {
    return 'You can cancel or modify your order within 2 hours of placing it. After that, orders enter fulfillment. Contact support@neatnesco.com and we\'ll do our best to help.'
  }

  // Wholesale / bulk
  if (q.includes('wholesale') || q.includes('bulk') || q.includes('business')) {
    return 'Yes! For orders of 10+ units, we offer tiered wholesale pricing. Contact our business team at wholesale@neatnesco.com for a custom quote.'
  }

  // International
  if (q.includes('international') || q.includes('country') || q.includes('worldwide') || q.includes('global')) {
    return 'We ship to 30+ countries worldwide! International shipping typically takes 15-25 business days. Customs fees, if applicable, are the responsibility of the customer.'
  }

  // Quality / authentic
  if (q.includes('quality') || q.includes('authentic') || q.includes('real') || q.includes('legit')) {
    return 'Every product is sourced directly from verified manufacturers and undergoes our rigorous 12-point quality check. We test every product ourselves before listing it.'
  }

  // Escalation / speak to human
  if (q.includes('human') || q.includes('person') || q.includes('agent') || q.includes('speak to') || q.includes('talk to') || q.includes('representative') || q.includes('manager')) {
    return 'I totally understand — for complex issues, our human support team is ready to help. Email support@neatnesco.com and a real person will reply within 2 hours. You can also include your order number for faster help!'
  }

  // Broken / damaged / complaint
  if (q.includes('broken') || q.includes('damaged') || q.includes('wrong item') || q.includes('defective') || q.includes('not working') || q.includes('complaint') || q.includes('problem with')) {
    return 'I\'m really sorry to hear that! Please email support@neatnesco.com with your order number and a photo of the issue. Our team will get you a replacement or full refund within 24 hours — we take this seriously.'
  }

  // Discount / coupon
  if (q.includes('discount') || q.includes('coupon') || q.includes('promo') || q.includes('code')) {
    return 'Check our Flash Sale banner at the top — we\'re running up to 50% off right now! We also send exclusive discount codes to newsletter subscribers. Sign up at the bottom of the page to never miss a deal!'
  }

  // Greeting
  if (q.includes('hello') || q.includes('hi') || q.includes('hey') || q === 'yo') {
    return 'Hey there! Welcome to NeatNesCo. I can help you with shipping info, returns, product recommendations, or anything else. What can I help you with?'
  }

  // Thanks
  if (q.includes('thank') || q.includes('thanks') || q.includes('appreciate')) {
    return 'You\'re welcome! If you need anything else, I\'m here. Happy shopping!'
  }

  // Default
  return 'Great question! For anything specific, our support team can help at support@neatnesco.com (average reply time: under 2 hours). Or try asking me about shipping, returns, payments, or product recommendations!'
}

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hey! I\'m the NeatNesCo assistant. How can I help you today?', time: new Date() }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  useEffect(() => {
    if (isOpen) inputRef.current?.focus()
  }, [isOpen])

  const sendMessage = (text) => {
    if (!text.trim()) return

    const userMsg = { role: 'user', text: text.trim(), time: new Date() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsTyping(true)

    // Simulate typing delay
    setTimeout(() => {
      const response = getBotResponse(text)
      setMessages(prev => [...prev, { role: 'bot', text: response, time: new Date() }])
      setIsTyping(false)
    }, 600 + Math.random() * 800)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <>
      {/* Chat toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 8000,
          width: '52px', height: '52px', borderRadius: '50%',
          background: '#1d1d1f', color: '#fff',
          border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          transform: isOpen ? 'scale(0.9)' : 'scale(1)',
        }}
      >
        <span style={{
          fontSize: '1.2rem', lineHeight: 1,
          transition: 'transform 0.3s',
          transform: isOpen ? 'rotate(45deg)' : 'rotate(0)',
          display: 'block',
        }}>
          {isOpen ? '+' : '?'}
        </span>
      </button>

      {/* Chat window */}
      <div style={{
        position: 'fixed', bottom: '6rem', right: '2rem', zIndex: 8000,
        width: '380px', maxWidth: 'calc(100vw - 2rem)',
        height: '520px', maxHeight: 'calc(100vh - 10rem)',
        background: '#ffffff',
        borderRadius: '18px',
        border: '1px solid rgba(0,0,0,0.08)',
        boxShadow: '0 12px 40px rgba(0,0,0,0.12)',
        display: 'flex', flexDirection: 'column',
        overflow: 'hidden',
        transform: isOpen ? 'translateY(0) scale(1)' : 'translateY(20px) scale(0.95)',
        opacity: isOpen ? 1 : 0,
        pointerEvents: isOpen ? 'auto' : 'none',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      }}>
        {/* Header */}
        <div style={{
          padding: '1rem 1.2rem',
          borderBottom: '1px solid rgba(0,0,0,0.06)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{
              width: '36px', height: '36px', borderRadius: '50%',
              background: '#1d1d1f', color: '#fff',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.8rem', fontWeight: 700,
              fontFamily: "'Inter', sans-serif",
            }}>N</div>
            <div>
              <div style={{
                fontSize: '0.88rem', fontWeight: 600, color: '#1d1d1f',
                fontFamily: "'Inter', sans-serif",
              }}>{BOT_NAME}</div>
              <div style={{
                fontSize: '0.68rem', color: '#86868b',
                display: 'flex', alignItems: 'center', gap: '0.3rem',
              }}>
                <span style={{
                  width: '6px', height: '6px', borderRadius: '50%',
                  background: '#34c759', display: 'inline-block',
                }} />
                Online now
              </div>
            </div>
          </div>
          <button onClick={() => setIsOpen(false)} style={{
            width: '28px', height: '28px', borderRadius: '50%',
            background: 'rgba(0,0,0,0.04)', border: 'none',
            cursor: 'pointer', fontSize: '0.8rem', color: '#86868b',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>x</button>
        </div>

        {/* Messages */}
        <div style={{
          flex: 1, overflowY: 'auto', padding: '1rem',
          display: 'flex', flexDirection: 'column', gap: '0.8rem',
        }}>
          {messages.map((msg, i) => (
            <div key={i} style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}>
              <div style={{
                maxWidth: '80%',
                padding: '0.7rem 1rem',
                borderRadius: msg.role === 'user'
                  ? '16px 16px 4px 16px'
                  : '16px 16px 16px 4px',
                background: msg.role === 'user' ? '#1d1d1f' : '#f5f5f7',
                color: msg.role === 'user' ? '#fff' : '#1d1d1f',
                fontSize: '0.85rem', lineHeight: 1.5,
                fontFamily: "'Inter', sans-serif",
                whiteSpace: 'pre-line',
              }}>
                {msg.text}
                <div style={{
                  fontSize: '0.6rem', marginTop: '0.3rem',
                  color: msg.role === 'user' ? 'rgba(255,255,255,0.5)' : '#aeaeb2',
                  textAlign: msg.role === 'user' ? 'right' : 'left',
                }}>
                  {formatTime(msg.time)}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{
                padding: '0.7rem 1rem', borderRadius: '16px 16px 16px 4px',
                background: '#f5f5f7', fontSize: '0.85rem', color: '#86868b',
              }}>
                <span className="typing-dots">...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick replies */}
        {messages.length <= 2 && (
          <div style={{
            padding: '0 1rem 0.5rem',
            display: 'flex', gap: '0.4rem', flexWrap: 'wrap',
          }}>
            {QUICK_REPLIES.map(reply => (
              <button key={reply} onClick={() => sendMessage(reply)} style={{
                background: '#f5f5f7', border: '1px solid rgba(0,0,0,0.06)',
                padding: '0.35rem 0.8rem', borderRadius: '980px',
                fontSize: '0.72rem', fontWeight: 500, color: '#1d1d1f',
                cursor: 'pointer', fontFamily: "'Inter', sans-serif",
                transition: 'all 0.2s',
              }}>
                {reply}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <form onSubmit={handleSubmit} style={{
          padding: '0.8rem 1rem',
          borderTop: '1px solid rgba(0,0,0,0.06)',
          display: 'flex', gap: '0.5rem', alignItems: 'center',
        }}>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type a message..."
            style={{
              flex: 1, padding: '0.65rem 1rem',
              borderRadius: '980px', border: '1px solid rgba(0,0,0,0.1)',
              background: '#f5f5f7', color: '#1d1d1f',
              fontSize: '0.85rem', outline: 'none',
              fontFamily: "'Inter', sans-serif",
              transition: 'border-color 0.2s',
            }}
            onFocus={e => e.target.style.borderColor = 'rgba(0,0,0,0.3)'}
            onBlur={e => e.target.style.borderColor = 'rgba(0,0,0,0.1)'}
          />
          <button type="submit" disabled={!input.trim()} style={{
            width: '36px', height: '36px', borderRadius: '50%',
            background: input.trim() ? '#1d1d1f' : '#e8e8ed',
            color: '#fff', border: 'none', cursor: input.trim() ? 'pointer' : 'default',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.9rem', transition: 'all 0.2s',
            fontFamily: "'Inter', sans-serif",
          }}>
            <span style={{ transform: 'rotate(-45deg)', display: 'block', lineHeight: 1 }}>&#8593;</span>
          </button>
        </form>
      </div>
    </>
  )
}
