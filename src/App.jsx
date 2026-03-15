import { useState, useCallback } from 'react'
import { getGlobalStyles } from './styles'
import SplashScreen from './components/SplashScreen'
import Navbar from './components/Navbar'
import FlashSaleBanner from './components/FlashSaleBanner'
import Hero from './components/Hero'
import BrandsMarquee from './components/BrandsMarquee'
import CategoryNav from './components/CategoryNav'
import Products from './components/Products'
import Features from './components/Features'
import Reviews from './components/Reviews'
import AsSeenOn from './components/AsSeenOn'
import FAQ from './components/FAQ'
import Newsletter from './components/Newsletter'
import Footer from './components/Footer'
import CartDrawer from './components/CartDrawer'
import QuickViewModal from './components/QuickViewModal'
import Toast from './components/Toast'
import SocialProof from './components/SocialProof'
import BackToTop from './components/BackToTop'
import ChatBot from './components/ChatBot'

export default function App() {
  const [splashDone, setSplashDone] = useState(false)
  const [cart, setCart] = useState([])
  const [cartOpen, setCartOpen] = useState(false)
  const [quickViewProduct, setQuickViewProduct] = useState(null)
  const [wishlist, setWishlist] = useState([])
  const [toasts, setToasts] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(null)

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

  return (
    <>
      <style>{getGlobalStyles()}</style>

      {!splashDone && <SplashScreen onComplete={() => setSplashDone(true)} />}

      <Navbar
        cartCount={cart.length}
        wishlistCount={wishlist.length}
        onCartClick={() => setCartOpen(true)}
      />

      <FlashSaleBanner />

      <Hero onQuickView={setQuickViewProduct} />

      <BrandsMarquee />

      <CategoryNav onCategorySelect={setSelectedCategory} />

      <Products
        onAddToCart={handleAddToCart}
        onQuickView={setQuickViewProduct}
        wishlist={wishlist}
        onToggleWishlist={handleToggleWishlist}
        externalCategory={selectedCategory}
      />

      <Features />

      <Reviews />

      <AsSeenOn />

      <FAQ />

      <Newsletter />

      <Footer />

      <CartDrawer
        isOpen={cartOpen}
        onClose={() => setCartOpen(false)}
        cart={cart}
        onUpdateQty={handleUpdateQty}
        onRemove={handleRemoveFromCart}
        onAddToCart={handleAddToCart}
      />

      {quickViewProduct && (
        <QuickViewModal
          product={quickViewProduct}
          onClose={() => setQuickViewProduct(null)}
          onAddToCart={handleAddToCart}
        />
      )}

      <Toast toasts={toasts} />
      <SocialProof />
      <BackToTop />
      <ChatBot />
    </>
  )
}
