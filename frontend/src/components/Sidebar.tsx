import { motion } from 'framer-motion'
import { Filter, Database, Youtube, BookOpen, ShieldCheck } from 'lucide-react'

interface SidebarProps {
  selectedSources: string[]
  setSelectedSources: (sources: string[]) => void
  minTrust: number
  setMinTrust: (val: number) => void
}

export const Sidebar = ({ selectedSources, setSelectedSources, minTrust, setMinTrust }: SidebarProps) => {
  const toggleSource = (source: string) => {
    if (selectedSources.includes(source)) {
      setSelectedSources(selectedSources.filter(s => s !== source))
    } else {
      setSelectedSources([...selectedSources, source])
    }
  }

  return (
    <div className="w-80 h-screen sticky top-0 p-10 glass border-r border-white/5 flex flex-col gap-16 overflow-y-auto z-50">
      <div className="flex flex-col gap-4 items-center mb-8">
        <div className="w-16 h-16 bg-white/5 rounded-3xl border border-white/10 flex items-center justify-center text-primary group-hover:scale-105 transition-transform">
          <Database size={32} />
        </div>
        <div className="flex flex-col items-center">
          <span className="text-xl font-bold tracking-tighter text-white">GutBut <span className="text-white/20 italic">Explorer</span></span>
          <span className="text-[10px] font-semibold uppercase text-white/20 tracking-widest">V 2.5 Diagnostic</span>
        </div>
      </div>

      <div className="flex flex-col gap-12">
        <section className="flex flex-col gap-6">
          <div className="flex items-center gap-2 text-white/40 uppercase text-[10px] font-semibold tracking-widest">
            <Filter size={14} />
            <span>Scope Analysis</span>
          </div>

          <div className="flex flex-col gap-3">
            <label className="text-[10px] font-bold text-white/20 uppercase tracking-widest px-1">Source Repository</label>
            <SourceToggle 
              label="Blog" 
              icon={<BookOpen size={16} />} 
              active={selectedSources.includes('blog')}
              onClick={() => toggleSource('blog')}
            />
            <SourceToggle 
              label="YouTube" 
              icon={<Youtube size={16} />} 
              active={selectedSources.includes('youtube')}
              onClick={() => toggleSource('youtube')}
            />
            <SourceToggle 
              label="PubMed" 
              icon={<ShieldCheck size={16} />} 
              active={selectedSources.includes('pubmed')}
              onClick={() => toggleSource('pubmed')}
            />
          </div>
        </section>

        <section className="flex flex-col gap-6">
          <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-wider text-white/20 px-1">
            <label>Trust Confidence</label>
            <span className="text-primary font-bold">{(minTrust * 100).toFixed(0)}%</span>
          </div>
          <div className="px-1">
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.05" 
              value={minTrust}
              onChange={(e) => setMinTrust(parseFloat(e.target.value))}
              className="w-full h-1 bg-white/10 rounded-full appearance-none cursor-pointer accent-primary"
            />
          </div>
          <p className="text-[10px] text-white/30 font-medium uppercase tracking-tight leading-relaxed">
            Minimum reliability coefficient required for ingestion listing.
          </p>
        </section>
      </div>

      <div className="mt-auto pt-10 border-t border-white/5">
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-semibold uppercase text-white/30 tracking-widest">Metadata Standard</span>
          <span className="text-xs font-medium text-white/60">IEEE 1484.12.1-2020</span>
        </div>
      </div>
    </div>
  )
}

const SourceToggle = ({ label, icon, active, onClick }: any) => (
  <motion.button 
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className={`flex items-center gap-4 p-4 rounded-2xl border transition-all duration-300 font-bold text-sm ${
      active 
        ? 'bg-primary/5 border-primary/20 text-primary shadow-[0_0_20px_rgba(0,201,255,0.05)]' 
        : 'bg-white/[0.02] border-white/5 text-white/30 hover:bg-white/5'
    }`}
  >
    {icon}
    <span>{label}</span>
  </motion.button>
)
