import { useState, useCallback } from 'react'
import { getGlobalStyles } from './styles'
import SplashScreen from './components/SplashScreen'
import FloatingParticles from './components/FloatingParticles'
import Navbar from './components/Navbar'
import FlashSaleBanner from './components/FlashSaleBanner'
import Hero from './components/Hero'
import BrandsMarquee from './components/BrandsMarquee'
import Products from './components/Products'
import Features from './components/Features'
import StoryTimeline from './components/StoryTimeline'
import Reviews from './components/Reviews'
import FAQ from './components/FAQ'
import Newsletter from './components/Newsletter'
import Footer from './components/Footer'
import CartDrawer from './components/CartDrawer'
import QuickViewModal from './components/QuickViewModal'
import Toast from './components/Toast'
import SocialProof from './components/SocialProof'
import BackToTop from './components/BackToTop'

export default function App() {
  // ─── State ──────────────────────────────────────────────────────────────
  const [splashDone, setSplashDone] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [cart, setCart] = useState([])
  const [cartOpen, setCartOpen] = useState(false)
  const [quickViewProduct, setQuickViewProduct] = useState(null)
  const [wishlist, setWishlist] = useState([])
  const [toasts, setToasts] = useState([])

  // ─── Handlers ───────────────────────────────────────────────────────────
  const addToast = useCallback((toast) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { ...toast, id }])
    setTimeout(() => {
      setToasts(prev => prev.map(t => t.id === id ? { ...t, removing: true } : t))
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 300)
    }, 3000)
  }, [])

  const handleAddToCart = useCallback((product) => {
    setCart(prev => [...prev, product])
    addToast({
      product,
      title: 'Added to cart!',
      message: `${product.name} — $${product.price}`,
    })
  }, [addToast])

  const handleUpdateQty = useCallback((productId, delta) => {
    setCart(prev => {
      const items = [...prev]
      if (delta > 0) {
        const product = items.find(p => p.id === productId)
        if (product) return [...items, product]
      } else {
        const idx = items.findIndex(p => p.id === productId)
        if (idx !== -1) items.splice(idx, 1)
      }
      return items
    })
  }, [])

  const handleRemoveFromCart = useCallback((productId) => {
    setCart(prev => prev.filter(p => p.id !== productId))
  }, [])

  const handleToggleWishlist = useCallback((productId) => {
    setWishlist(prev =>
      prev.includes(productId)
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    )
  }, [])

  const handleDarkModeToggle = useCallback(() => {
    setDarkMode(prev => !prev)
  }, [])

  // ─── Render ─────────────────────────────────────────────────────────────
  return (
    <>
      <style>{getGlobalStyles(darkMode)}</style>

      {!splashDone && <SplashScreen onComplete={() => setSplashDone(true)} />}

      <FloatingParticles darkMode={darkMode} />

      {/* Cursor glow */}
      <div
        ref={el => {
          if (!el) return
          const handler = (e) => {
            el.style.left = e.clientX + 'px'
            el.style.top = e.clientY + 'px'
          }
          window.addEventListener('mousemove', handler)
          el._cleanup = () => window.removeEventListener('mousemove', handler)
        }}
        style={{
          position: 'fixed', width: '700px', height: '700px',
          borderRadius: '50%', pointerEvents: 'none', zIndex: 0,
          background: darkMode
            ? 'radial-gradient(circle, rgba(45,106,79,0.06) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(45,106,79,0.04) 0%, transparent 70%)',
          transform: 'translate(-50%, -50%)',
          transition: 'left 0.15s ease-out, top 0.15s ease-out',
        }}
      />

      <Navbar
        cartCount={cart.length}
        wishlistCount={wishlist.length}
        onCartClick={() => setCartOpen(true)}
        onDarkModeToggle={handleDarkModeToggle}
        darkMode={darkMode}
      />

      <FlashSaleBanner darkMode={darkMode} />

      <Hero darkMode={darkMode} />

      <BrandsMarquee darkMode={darkMode} />

      <Products
        onAddToCart={handleAddToCart}
        onQuickView={setQuickViewProduct}
        wishlist={wishlist}
        onToggleWishlist={handleToggleWishlist}
        darkMode={darkMode}
      />

      <div className="section-divider" />

      <Features darkMode={darkMode} />

      <div className="section-divider" />

      <StoryTimeline darkMode={darkMode} />

      <div className="section-divider" />

      <Reviews darkMode={darkMode} />

      <FAQ darkMode={darkMode} />

      <Newsletter darkMode={darkMode} />

      <Footer darkMode={darkMode} />

      {/* Overlays */}
      <CartDrawer
        isOpen={cartOpen}
        onClose={() => setCartOpen(false)}
        cart={cart}
        onUpdateQty={handleUpdateQty}
        onRemove={handleRemoveFromCart}
        darkMode={darkMode}
      />

      {quickViewProduct && (
        <QuickViewModal
          product={quickViewProduct}
          onClose={() => setQuickViewProduct(null)}
          onAddToCart={handleAddToCart}
          darkMode={darkMode}
        />
      )}

      <Toast toasts={toasts} />
      <SocialProof darkMode={darkMode} />
      <BackToTop darkMode={darkMode} />
    </>
  )
}
