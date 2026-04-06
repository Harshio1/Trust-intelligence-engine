import { motion } from 'framer-motion'

export const DNAVisual = () => {
  const dots = 24;
  const radius = 60;
  
  return (
    <div className="relative w-full h-full flex items-center justify-center perspective-[1000px]">
      <motion.div 
        animate={{ rotateY: 360 }}
        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        className="relative w-48 h-[400px] preserve-3d"
      >
        {/* Strand 1 */}
        {Array.from({ length: dots }).map((_, i) => (
          <div key={`s1-${i}`} className="absolute left-1/2 top-0" style={{ transform: `translateY(${i * 16}px) rotateY(${i * 30}deg) translateZ(${radius}px)` }}>
            <div className="w-1.5 h-1.5 rounded-full bg-[#00c9ff] shadow-[0_0_10px_#00c9ff]" />
            {/* Connecting rung */}
            <div 
              className="absolute h-[1px] bg-gradient-to-r from-[#00c9ff]/40 to-transparent origin-left"
              style={{ width: radius * 2, transform: `translateX(0) rotateY(180deg)` }}
            />
          </div>
        ))}

        {/* Strand 2 */}
        {Array.from({ length: dots }).map((_, i) => (
          <div key={`s2-${i}`} className="absolute left-1/2 top-0" style={{ transform: `translateY(${i * 16}px) rotateY(${i * 30 + 180}deg) translateZ(${radius}px)` }}>
            <div className="w-1.5 h-1.5 rounded-full bg-[#00c9ff] shadow-[0_0_10px_#00c9ff]" />
          </div>
        ))}
      </motion.div>
    </div>
  )
}
