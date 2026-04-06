import { motion } from 'framer-motion'

export const DNAVisual = () => {
  const dots = 30; // More dots for a bigger, more detailed structure
  const radius = 80; // Larger radius for a "bigger" feel
  const heightStep = 18; // Slightly more spacing for a "straight" look
  
  return (
    <div className="relative w-full h-full flex items-center justify-center perspective-[1200px]">
      <motion.div 
        animate={{ rotateY: 360 }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        className="relative w-64 h-[540px] preserve-3d"
      >
        {/* Strand 1 */}
        {Array.from({ length: dots }).map((_, i) => (
          <div key={`s1-${i}`} className="absolute left-1/2 top-0" style={{ transform: `translateY(${i * heightStep}px) rotateY(${i * 24}deg) translateZ(${radius}px)` }}>
            <div className="w-2 h-2 rounded-full bg-[#00c9ff] shadow-[0_0_15px_#00c9ff]" />
            {/* Connecting rung */}
            <div 
              className="absolute h-[1px] bg-gradient-to-r from-[#00c9ff]/40 to-transparent origin-left"
              style={{ width: radius * 2, transform: `translateX(0) rotateY(180deg)` }}
            />
          </div>
        ))}

        {/* Strand 2 */}
        {Array.from({ length: dots }).map((_, i) => (
          <div key={`s2-${i}`} className="absolute left-1/2 top-0" style={{ transform: `translateY(${i * heightStep}px) rotateY(${i * 24 + 180}deg) translateZ(${radius}px)` }}>
            <div className="w-2 h-2 rounded-full bg-[#00c9ff] shadow-[0_0_15px_#00c9ff]" />
          </div>
        ))}
      </motion.div>
    </div>
  )
}
