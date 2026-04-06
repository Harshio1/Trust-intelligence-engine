import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Float, Stars } from '@react-three/drei'
import * as THREE from 'three'

const DNAHelix = () => {
  const groupRef = useRef<THREE.Group>(null!)
  const numPoints = 30
  const step = 0.3
  const twist = 0.4
  const radius = 1.8

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    groupRef.current.rotation.y = time * 0.4
    // Smooth vertical wave motion
    groupRef.current.position.y = Math.sin(time * 0.5) * 0.1
  })

  return (
    <group ref={groupRef}>
      {Array.from({ length: numPoints }).map((_, i) => {
        const y = (i - numPoints / 2) * step
        const angle = i * twist
        
        const x1 = Math.cos(angle) * radius
        const z1 = Math.sin(angle) * radius
        
        const x2 = Math.cos(angle + Math.PI) * radius
        const z2 = Math.sin(angle + Math.PI) * radius

        return (
          <group key={i}>
            {/* Strand 1 Node */}
            <mesh position={[x1, y, z1]}>
              <sphereGeometry args={[0.08, 16, 16]} />
              <meshStandardMaterial 
                color="#00c9ff" 
                emissive="#00c9ff" 
                emissiveIntensity={4} 
                toneMapped={false}
              />
            </mesh>

            {/* Strand 2 Node */}
            <mesh position={[x2, y, z2]}>
              <sphereGeometry args={[0.08, 16, 16]} />
              <meshStandardMaterial 
                color="#00f2fe" 
                emissive="#00f2fe" 
                emissiveIntensity={2}
                toneMapped={false}
              />
            </mesh>

            {/* Connecting Rung (Base Pair) */}
            {i % 2 === 0 && (
              <mesh 
                position={[0, y, 0]} 
                rotation={[0, 0, Math.PI / 2]} 
                scale={[1, radius * 2, 1]}
              >
                <cylinderGeometry args={[0.015, 0.015, 1, 6]} />
                <meshStandardMaterial 
                  color="#ffffff" 
                  transparent 
                  opacity={0.1} 
                  emissive="#00c9ff"
                  emissiveIntensity={0.5}
                />
              </mesh>
            )}
          </group>
        )
      })}
      
      {/* Explicit Strand Lines for Structure */}
      <StrandLine points={numPoints} step={step} twist={twist} radius={radius} phase={0} color="#00c9ff" />
      <StrandLine points={numPoints} step={step} twist={twist} radius={radius} phase={Math.PI} color="#00f2fe" />
    </group>
  )
}

const StrandLine = ({ points, step, twist, radius, phase, color }: any) => {
    const linePoints = []
    for (let i = 0; i < points; i++) {
        const y = (i - points / 2) * step
        const angle = i * twist + phase
        linePoints.push(new THREE.Vector3(Math.cos(angle) * radius, y, Math.sin(angle) * radius))
    }
    const curve = new THREE.CatmullRomCurve3(linePoints)
    const geometry = new THREE.TubeGeometry(curve, 60, 0.015, 8, false)
    
    return (
        <mesh geometry={geometry}>
            <meshStandardMaterial color={color} transparent opacity={0.3} emissive={color} emissiveIntensity={1} />
        </mesh>
    )
}

export const DNA = () => {
  return (
    <div className="w-full h-full">
      <Canvas camera={{ position: [0, 0, 12], fov: 40 }} gl={{ antialias: true }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#00c9ff" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#00f2fe" />
        <Float speed={1.2} rotationIntensity={0.5} floatIntensity={0.5}>
          <DNAHelix />
        </Float>
        <Stars radius={50} depth={50} count={1000} factor={4} saturation={0} fade speed={1} />
      </Canvas>
    </div>
  )
}
