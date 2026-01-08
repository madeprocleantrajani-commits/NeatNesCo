import React, { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';

// Vertex shader for particle morphing
const vertexShader = `
  uniform float uTime;
  uniform float uProgress;
  uniform float uDispersion;
  uniform vec2 uMouse;
  uniform float uMouseStrength;

  attribute float aSize;
  attribute vec3 aTargetPosition;
  attribute vec3 aRandomness;
  attribute float aAlpha;

  varying float vAlpha;
  varying float vProgress;

  void main() {
    vAlpha = aAlpha;
    vProgress = uProgress;

    // Calculate dispersed position
    vec3 dispersedPos = position + aRandomness * (1.0 - uProgress) * uDispersion;

    // Mix between dispersed and target position based on progress
    vec3 finalPos = mix(dispersedPos, aTargetPosition, uProgress);

    // Add wave animation
    float wave = sin(uTime * 2.0 + position.x * 3.0 + position.y * 2.0) * 0.02 * (1.0 - uProgress * 0.5);
    finalPos.z += wave;

    // Mouse interaction - repel particles near mouse
    vec4 mvPosition = modelViewMatrix * vec4(finalPos, 1.0);
    vec2 screenPos = mvPosition.xy / mvPosition.w;
    float distToMouse = length(screenPos - uMouse);
    float mouseInfluence = smoothstep(0.5, 0.0, distToMouse) * uMouseStrength;

    vec2 pushDir = normalize(screenPos - uMouse + vec2(0.001));
    finalPos.xy += pushDir * mouseInfluence * 0.3;

    mvPosition = modelViewMatrix * vec4(finalPos, 1.0);

    gl_Position = projectionMatrix * mvPosition;

    // Size attenuation
    float sizeAtten = (300.0 / -mvPosition.z);
    gl_PointSize = aSize * sizeAtten * (0.5 + uProgress * 0.5);
  }
`;

// Fragment shader for particles
const fragmentShader = `
  uniform vec3 uColor;
  uniform float uProgress;

  varying float vAlpha;
  varying float vProgress;

  void main() {
    // Create soft circular particle
    vec2 center = gl_PointCoord - vec2(0.5);
    float dist = length(center);

    // Soft edge
    float alpha = 1.0 - smoothstep(0.3, 0.5, dist);

    // Add stronger glow effect for techy look
    float glow = exp(-dist * 2.5) * 0.8;
    alpha = max(alpha, glow);

    // Fade based on progress and original alpha
    alpha *= vAlpha * (0.5 + vProgress * 0.5);

    // Techy cyan color with variation
    vec3 cyanBase = vec3(0.0, 0.76, 1.0); // #00c3ff
    vec3 finalColor = mix(cyanBase, uColor, vProgress * 0.6);

    // Add subtle color variation based on position
    finalColor += vec3(0.05, 0.1, 0.15) * (1.0 - vProgress);

    gl_FragColor = vec4(finalColor, alpha);
  }
`;

// Particle system component
function ParticleSystem({ imageUrl, particleCount = 15000 }) {
  const pointsRef = useRef();
  const [imageData, setImageData] = useState(null);
  const mouse = useRef({ x: 0, y: 0 });
  const progressRef = useRef({ value: 0 });
  const { size } = useThree();

  // Load and process image
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      // Scale down for performance while keeping quality
      const maxSize = 200;
      const scale = Math.min(maxSize / img.width, maxSize / img.height);
      canvas.width = img.width * scale;
      canvas.height = img.height * scale;

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
      setImageData({ data: data.data, width: canvas.width, height: canvas.height });
    };
    img.src = imageUrl;
  }, [imageUrl]);

  // Create particle geometry from image
  const { positions, targetPositions, sizes, randomness, alphas } = useMemo(() => {
    if (!imageData) return { positions: null, targetPositions: null, sizes: null, randomness: null, alphas: null };

    const { data, width, height } = imageData;
    const positions = [];
    const targetPositions = [];
    const sizes = [];
    const randomness = [];
    const alphas = [];

    const aspectRatio = width / height;
    const scaleX = aspectRatio > 1 ? 1 : aspectRatio;
    const scaleY = aspectRatio > 1 ? 1 / aspectRatio : 1;

    // Sample pixels from image
    const step = Math.max(1, Math.floor(Math.sqrt((width * height) / particleCount)));

    for (let y = 0; y < height; y += step) {
      for (let x = 0; x < width; x += step) {
        const i = (y * width + x) * 4;
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const a = data[i + 3];

        // Skip transparent or very dark pixels
        const brightness = (r + g + b) / 3;
        if (a < 50 || brightness < 10) continue;

        // Calculate position (centered, normalized)
        const px = (x / width - 0.5) * 2 * scaleX;
        const py = -(y / height - 0.5) * 2 * scaleY;
        const pz = (brightness / 255 - 0.5) * 0.3; // Slight depth based on brightness

        // Target position (where particle should form)
        targetPositions.push(px, py, pz);

        // Initial scattered position
        const angle = Math.random() * Math.PI * 2;
        const radius = 2 + Math.random() * 3;
        positions.push(
          Math.cos(angle) * radius,
          Math.sin(angle) * radius + (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2
        );

        // Random direction for dispersion animation
        randomness.push(
          (Math.random() - 0.5) * 4,
          (Math.random() - 0.5) * 4,
          (Math.random() - 0.5) * 2
        );

        // Size based on brightness
        sizes.push(Math.max(2, brightness / 50) + Math.random() * 2);

        // Alpha based on brightness
        alphas.push(0.3 + (brightness / 255) * 0.7);
      }
    }

    return {
      positions: new Float32Array(positions),
      targetPositions: new Float32Array(targetPositions),
      sizes: new Float32Array(sizes),
      randomness: new Float32Array(randomness),
      alphas: new Float32Array(alphas)
    };
  }, [imageData, particleCount]);

  // Create shader material
  const shaderMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uProgress: { value: 0 },
        uDispersion: { value: 1.5 },
        uMouse: { value: new THREE.Vector2(0, 0) },
        uMouseStrength: { value: 0 },
        uColor: { value: new THREE.Color('#ffffff') }
      },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });
  }, []);

  // Handle mouse movement
  useEffect(() => {
    const handleMouseMove = (e) => {
      mouse.current.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.current.y = -(e.clientY / window.innerHeight) * 2 + 1;
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Animation loop
  useFrame((state, delta) => {
    if (!pointsRef.current) return;

    const material = pointsRef.current.material;
    const time = state.clock.elapsedTime;
    material.uniforms.uTime.value = time;

    // Smooth mouse following
    material.uniforms.uMouse.value.lerp(
      new THREE.Vector2(mouse.current.x, mouse.current.y),
      0.1
    );

    // Automatic form/disperse cycle (like Lando Norris site)
    // Cycle: disperse -> form -> hold -> disperse -> repeat
    const cycleDuration = 8; // seconds per full cycle
    const cycleTime = time % cycleDuration;

    let targetProgress;
    if (cycleTime < 2) {
      // 0-2s: Form (disperse to formed)
      targetProgress = cycleTime / 2;
    } else if (cycleTime < 5) {
      // 2-5s: Hold formed
      targetProgress = 1;
    } else if (cycleTime < 7) {
      // 5-7s: Disperse (formed to dispersed)
      targetProgress = 1 - (cycleTime - 5) / 2;
    } else {
      // 7-8s: Hold dispersed
      targetProgress = 0;
    }

    // Smooth the transition
    progressRef.current.value += (targetProgress - progressRef.current.value) * delta * 3;
    material.uniforms.uProgress.value = progressRef.current.value;

    // Mouse influence strength - stronger when mouse moves
    const mouseSpeed = Math.abs(mouse.current.x) + Math.abs(mouse.current.y);
    material.uniforms.uMouseStrength.value += (mouseSpeed * 0.8 - material.uniforms.uMouseStrength.value) * 0.1;
  });

  if (!positions) return null;

  return (
    <points ref={pointsRef} material={shaderMaterial}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-aTargetPosition"
          count={targetPositions.length / 3}
          array={targetPositions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-aSize"
          count={sizes.length}
          array={sizes}
          itemSize={1}
        />
        <bufferAttribute
          attach="attributes-aRandomness"
          count={randomness.length / 3}
          array={randomness}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-aAlpha"
          count={alphas.length}
          array={alphas}
          itemSize={1}
        />
      </bufferGeometry>
    </points>
  );
}

// Main export component
export default function ParticleMorph({ imageUrl, style }) {
  return (
    <div style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      ...style
    }}>
      <Canvas
        camera={{ position: [0, 0, 2.5], fov: 50 }}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance'
        }}
        style={{ background: 'transparent' }}
      >
        <ParticleSystem imageUrl={imageUrl} particleCount={20000} />
      </Canvas>
    </div>
  );
}
