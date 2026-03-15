import { useState, useEffect, useRef, useCallback } from 'react'

// ─── Intersection Observer Hook ──────────────────────────────────────────────

export function useInView(options = {}) {
  const ref = useRef(null)
  const [isVisible, setIsVisible] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true)
        observer.unobserve(el)
      }
    }, { threshold: 0.1, ...options })
    observer.observe(el)
    return () => observer.unobserve(el)
  }, [])
  return [ref, isVisible]
}

// ─── 3D Tilt Hook ────────────────────────────────────────────────────────────

export function useTilt(intensity = 15) {
  const ref = useRef(null)

  const handleMove = useCallback((e) => {
    const el = ref.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width
    const y = (e.clientY - rect.top) / rect.height
    const rotateX = (0.5 - y) * intensity
    const rotateY = (x - 0.5) * intensity
    el.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`
    el.style.setProperty('--mouse-x', `${x * 100}%`)
    el.style.setProperty('--mouse-y', `${y * 100}%`)
  }, [intensity])

  const handleLeave = useCallback(() => {
    const el = ref.current
    if (!el) return
    el.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)'
  }, [])

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.addEventListener('mousemove', handleMove)
    el.addEventListener('mouseleave', handleLeave)
    return () => {
      el.removeEventListener('mousemove', handleMove)
      el.removeEventListener('mouseleave', handleLeave)
    }
  }, [handleMove, handleLeave])

  return ref
}

// ─── Countdown Timer Hook ────────────────────────────────────────────────────

export function useCountdown(hours = 23, minutes = 59, seconds = 59) {
  const [time, setTime] = useState({ h: hours, m: minutes, s: seconds })

  useEffect(() => {
    const tick = setInterval(() => {
      setTime(prev => {
        let { h, m, s } = prev
        s--
        if (s < 0) { s = 59; m-- }
        if (m < 0) { m = 59; h-- }
        if (h < 0) { h = 23; m = 59; s = 59 }
        return { h, m, s }
      })
    }, 1000)
    return () => clearInterval(tick)
  }, [])

  return time
}

// ─── Parallax Scroll Hook ────────────────────────────────────────────────────

export function useParallax(speed = 0.3) {
  const ref = useRef(null)

  useEffect(() => {
    const handleScroll = () => {
      const el = ref.current
      if (!el) return
      const rect = el.getBoundingClientRect()
      const offset = rect.top * speed
      el.style.transform = `translateY(${offset}px)`
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [speed])

  return ref
}
