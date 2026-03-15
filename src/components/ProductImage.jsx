import { useState } from 'react'

export default function ProductImage({ src, hoverSrc, alt, style, className, hovered }) {
  const [loaded, setLoaded] = useState(false)
  const [hoverLoaded, setHoverLoaded] = useState(false)
  const [error, setError] = useState(false)

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: '100%',
      overflow: 'hidden',
      background: '#f5f5f7',
      ...style,
    }} className={className}>
      {/* Loading placeholder */}
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        opacity: (!loaded || error) ? 1 : 0,
        transition: 'opacity 0.4s ease',
        zIndex: 1,
        background: '#f5f5f7',
      }} />

      {/* Primary image */}
      {!error && (
        <img
          src={src}
          alt={alt}
          loading="lazy"
          onLoad={() => setLoaded(true)}
          onError={() => setError(true)}
          style={{
            position: 'absolute', inset: 0,
            width: '100%', height: '100%',
            objectFit: 'cover',
            opacity: (loaded && hovered && hoverSrc && hoverLoaded) ? 0 : (loaded ? 1 : 0),
            transition: 'opacity 0.5s ease',
            zIndex: 2,
          }}
        />
      )}

      {/* Hover image (crossfade) */}
      {hoverSrc && hoverSrc !== src && (
        <img
          src={hoverSrc}
          alt={`${alt} alternate`}
          loading="eager"
          onLoad={() => setHoverLoaded(true)}
          style={{
            position: 'absolute', inset: 0,
            width: '100%', height: '100%',
            objectFit: 'cover',
            opacity: (hovered && hoverLoaded) ? 1 : 0,
            transition: 'opacity 0.5s ease',
            zIndex: 3,
          }}
        />
      )}
    </div>
  )
}
