import { motion } from 'framer-motion'

export const DNAVisual = () => {
  const dots = 30; 
  const radius = 80; 
  const heightStep = 18; 
  
  return (
    <div className="relative w-full h-full flex items-center justify-center perspective-[1200px]">
      <div className="relative w-64 h-[540px] preserve-3d">
        {Array.from({ length: dots }).map((_, i) => (
          <div key={`rung-${i}`} className="absolute left-1/2 top-0 preserve-3d" style={{ transform: `translateY(${i * heightStep}px)` }}>
            
            {/* Strand 1 Dot */}
            <motion.div 
              animate={{ rotateY: [i * 24, i * 24 + 360] }}
              transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
              className="absolute preserve-3d"
              style={{ transformStyle: 'preserve-3d' }}
            >
              <div style={{ transform: `translateZ(${radius}px)` }}>
                <div className="w-2 h-2 rounded-full bg-[#00c9ff] shadow-[0_0_15px_#00c9ff]" />
              </div>

              {/* Connecting Rung - Rotates with the dots */}
              <div 
                className="absolute h-[0.5px] bg-gradient-to-r from-[#00c9ff]/40 via-[#00c9ff]/10 to-transparent origin-center"
                style={{ width: radius * 2, transform: `translateX(-50%) translateZ(0)` }}
              />

              {/* Strand 2 Dot (Opposite side) */}
              <div style={{ transform: `rotateY(180deg) translateZ(${radius}px)` }}>
                <div className="w-2 h-2 rounded-full bg-[#00c9ff] shadow-[0_0_15px_#00c9ff]" />
              </div>
            </motion.div>
            
          </div>
        ))}
      </div>
    </div>
  )
}
