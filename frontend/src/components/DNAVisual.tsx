import { motion } from 'framer-motion'

export const DNAVisual = () => {
    // Generate nodes for the double helix
    const nodeCount = 20;
    const helixRadius = 40;
    const helixHeight = 400;
    
    return (
        <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
            <svg viewBox={`0 0 200 ${helixHeight}`} className="w-full h-full opacity-60">
                {/* Strand 1 (Sine) */}
                <motion.path 
                    d={`M 100 0 ${Array.from({ length: nodeCount }).map((_, i) => {
                        const y = (i / nodeCount) * helixHeight;
                        const x = 100 + Math.sin(i * 0.8) * helixRadius;
                        return `L ${x} ${y}`;
                    }).join(' ')}`}
                    fill="none"
                    stroke="#00c9ff"
                    strokeWidth="0.5"
                    strokeDasharray="4 4"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />
                
                {/* Strand 2 (Cosine) */}
                <motion.path 
                    d={`M 100 0 ${Array.from({ length: nodeCount }).map((_, i) => {
                        const y = (i / nodeCount) * helixHeight;
                        const x = 100 - Math.sin(i * 0.8) * helixRadius;
                        return `L ${x} ${y}`;
                    }).join(' ')}`}
                    fill="none"
                    stroke="#00f2fe"
                    strokeWidth="0.5"
                    strokeDasharray="4 4"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />

                {/* Nodes & Bridges */}
                {Array.from({ length: nodeCount }).map((_, i) => {
                    const y = (i / nodeCount) * helixHeight;
                    const x1 = 100 + Math.sin(i * 0.8 + (Date.now() / 1000)) * helixRadius;
                    const x2 = 100 - Math.sin(i * 0.8 + (Date.now() / 1000)) * helixRadius;
                    
                    return (
                        <g key={i}>
                            {/* Connection Bridge */}
                            <motion.line 
                                x1={x1} y1={y} x2={x2} y2={y} 
                                stroke="white" strokeWidth="0.2" opacity="0.1"
                                animate={{ x1: 100 + Math.sin(i * 0.8 + 2) * helixRadius, x2: 100 - Math.sin(i * 0.8 + 2) * helixRadius }}
                                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", repeatType: "reverse" }}
                            />
                            {/* Particle 1 */}
                            <motion.circle 
                                r="2.5" fill="#00c9ff"
                                animate={{ cx: 100 + Math.sin(i * 0.8 + 2) * helixRadius, cy: y }}
                                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", repeatType: "reverse" }}
                            >
                                <animate attributeName="opacity" values="0.8;0.3;0.8" dur="3s" repeatCount="indefinite" />
                            </motion.circle>
                            {/* Particle 2 */}
                            <motion.circle 
                                r="2.5" fill="#00f2fe"
                                animate={{ cx: 100 - Math.sin(i * 0.8 + 2) * helixRadius, cy: y }}
                                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", repeatType: "reverse" }}
                            >
                                <animate attributeName="opacity" values="0.3;0.8;0.3" dur="3s" repeatCount="indefinite" />
                            </motion.circle>
                        </g>
                    )
                })}
            </svg>
            
            {/* Ambient Glow */}
            <div className="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-[#0b0d11] to-transparent pointer-events-none" />
            <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-[#0b0d11] to-transparent pointer-events-none" />
        </div>
    )
}
