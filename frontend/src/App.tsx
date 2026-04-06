import { useState, useEffect, useMemo } from 'react'
import axios from 'axios'
import { SourceCard } from './components/SourceCard'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ShieldCheck, 
  Award, 
  Database, 
  Download, 
  SlidersHorizontal, 
  Search, 
  Info, 
  Globe,
  Zap,
  Loader2,
  AlertCircle
} from 'lucide-react'

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [sources, setSources] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSources, setSelectedSources] = useState(['blog', 'youtube', 'pubmed'])
  const [minTrust, setMinTrust] = useState(0.0)
  const [searchQuery, setSearchQuery] = useState('')
  
  // Real-time Analysis State
  const [inputUrl, setInputUrl] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);

      try {
        const response = await fetch(`${BASE_URL}/api/scraped`, {
          signal: controller.signal
        });
        clearTimeout(timeout);
        const data = await response.json();
        setSources(Array.isArray(data) ? data : []);
      } catch (err) {
        clearTimeout(timeout);
        console.error('Error fetching data or timeout:', err);
        setSources([]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputUrl.trim()) return

    setIsAnalyzing(true)
    setError(null)

    try {
      const response = await fetch(`${BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: inputUrl })
      })
      const result = await response.json()

      if (result && !result.error) {
        const newSource = { ...result, isNew: true }
        // Prepend new result to sources immediately
        setSources(prev => Array.isArray(prev) ? [newSource, ...prev] : [newSource])
        setInputUrl('')
        
        // Auto-scroll to the top to see the new entry
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } else {
        throw new Error(result.error || 'Failed to analyze source')
      }
    } catch (err: any) {
      console.error('Analysis error:', err)
      setError(err.message || 'Analysis engine unreachable. Ensure server is running.')
      setTimeout(() => setError(null), 5000)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const filteredData = useMemo(() => {
    if (!Array.isArray(sources)) return []
    return sources.filter(item => {
      const matchSource = selectedSources.includes(item.source_type)
      const matchTrust = item.trust_score >= minTrust
      const matchSearch = 
        item.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.topic_tags && item.topic_tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase())))
      
      return matchSource && matchTrust && matchSearch
    })
  }, [sources, selectedSources, minTrust, searchQuery])

  const stats = useMemo(() => {
    if (!Array.isArray(sources) || !sources.length) return { avg: 0, total: 0 }
    const totalTrust = sources.reduce((sum, s) => sum + (s.trust_score || 0), 0)
    const avg = totalTrust / sources.length
    return { 
      avg: (avg).toFixed(2), 
      total: sources.length
    }
  }, [sources])

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(sources, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'trust_master_registry.json'; a.click()
  }

  const toggleSource = (type: string) => {
    setSelectedSources(prev => 
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    )
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4 bg-[#0b0d11]">
        <Loader2 size={32} className="text-[#00c9ff] animate-spin" />
        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-white/20 animate-pulse">Initializing Trust Registry</span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0b0d11] text-white selection:bg-[#00c9ff]/30">
      <div className="max-w-[1440px] mx-auto px-8 py-10 flex flex-col gap-8">
        
        {/* Balanced Hero Section */}
        <header className="relative flex min-h-[440px] items-center p-12 diagnostic-card border-none bg-gradient-to-br from-[#13171f] via-[#0b0e14] to-[#080a0e] group overflow-hidden">
          {/* Constrained DNA Visual */}
          <div className="absolute right-0 top-0 w-2/5 h-full opacity-40 group-hover:opacity-100 transition-opacity duration-1000 z-0">
             {/* DNA Visual Removed for Performance */}
          </div>
          
          <div className="flex flex-col gap-8 relative z-10 w-3/5">
            <div className="flex items-center gap-3 text-[#00c9ff] font-black uppercase text-[10px] tracking-[0.4em]">
              <ShieldCheck size={16} />
              <span>Bio-Intelligence Analytics Core</span>
            </div>
            
            <div className="flex flex-col gap-2">
              <h1 className="text-7xl font-black tracking-tighter leading-[0.9] text-white">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00c9ff] via-[#00f2fe] to-white/10 uppercase italic">Trust Intelligence Engine</span>
              </h1>
              <p className="text-sm text-white/30 max-w-lg font-medium leading-relaxed tracking-tight border-l border-white/10 pl-6 my-2 uppercase">
                Dynamic clinical-grade provenance engine. Analyze any source integrity and AI-modeled confidence in real-time.
              </p>
            </div>

            {/* NEW: Dynamic Analysis Input */}
            <form onSubmit={handleAnalyze} className="relative max-w-lg w-full group">
              <div className="absolute inset-0 bg-gradient-to-r from-[#00c9ff]/20 to-[#00f2fe]/20 blur-xl opacity-50 group-focus-within:opacity-100 transition-opacity" />
              <div className="relative flex gap-2 p-2 bg-black/40 border border-white/5 rounded-2xl backdrop-blur-3xl shadow-2xl focus-within:border-[#00c9ff]/30 transition-all">
                <input 
                  type="text" 
                  placeholder="Analyze source URL (YouTube, PubMed, Blog)..."
                  value={inputUrl}
                  onChange={(e) => setInputUrl(e.target.value)}
                  className="flex-grow bg-transparent border-none outline-none px-4 py-2 text-xs font-bold tracking-tight text-white/80 placeholder:text-white/10"
                />
                <button 
                  disabled={isAnalyzing || !inputUrl}
                  className="btn-diagnostic btn-primary min-w-[140px] h-12 rounded-xl text-[9px] shadow-[0_0_20px_rgba(0,201,255,0.2)] disabled:opacity-50 disabled:grayscale transition-all"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 size={14} className="animate-spin" />
                      <span>Sequencing...</span>
                    </>
                  ) : (
                    <>
                      <Zap size={14} fill="currentColor" />
                      <span>Analyze Source</span>
                    </>
                  )}
                </button>
              </div>
              
              {/* Error Alert */}
              <AnimatePresence>
                {error && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute -bottom-14 left-0 right-0 flex items-center gap-2 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-[10px] font-black uppercase text-rose-400 tracking-widest"
                  >
                    <AlertCircle size={14} />
                    <span>{error}</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </form>

            <div className="flex gap-10 items-center">
               <HeaderMetric label="Aggregate Trust" value={`${stats.avg}`} icon={<Award size={16} className="text-[#00c9ff]" />} />
               <HeaderMetric label="Nodes Audited" value={stats.total} icon={<Database size={16} className="text-[#00c9ff]" />} />
               <div className="h-10 w-[1px] bg-white/5" />
               <button onClick={downloadJson} className="btn-diagnostic btn-secondary h-14 px-8 rounded-2xl group/btn text-[9px] hover:bg-[#00c9ff] hover:text-black hover:border-transparent transition-all">
                  <Download size={16} className="group-hover/btn:translate-y-1 transition-transform" />
                  <span>Export Registry</span>
               </button>
            </div>
          </div>
        </header>

        {/* Dense Control Bar */}
        <div className="flex flex-col lg:flex-row gap-6 items-center justify-between p-6 diagnostic-card border-none glass-panel">
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-label mr-2">
                    <SlidersHorizontal size={14} className="text-[#00c9ff]" />
                    <span>Audit Matrix</span>
                </div>
                <div className="flex gap-2">
                    {['blog', 'youtube', 'pubmed'].map(type => (
                        <button 
                            key={type}
                            onClick={() => toggleSource(type)}
                            className={`px-5 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest border transition-all duration-300 ${
                                selectedSources.includes(type) 
                                ? 'bg-[#00c9ff] text-black border-[#00c9ff] shadow-[0_0_15px_rgba(0,201,255,0.2)]' 
                                : 'bg-transparent text-white/10 border-white/5 hover:border-white/20 hover:text-white/30'
                            }`}
                        >
                            {type}
                        </button>
                    ))}
                </div>
            </div>

            <div className="flex items-center gap-8 w-full lg:w-auto">
                <div className="flex flex-col gap-2 w-full lg:w-48">
                    <div className="flex justify-between items-center text-[9px] font-black uppercase tracking-widest text-white/20">
                        <span>Trust Threshold</span>
                        <span className="text-[#00c9ff] font-bold">{minTrust.toFixed(2)}</span>
                    </div>
                    <input 
                        type="range" min="0.0" max="1.0" step="0.05"
                        value={minTrust}
                        onChange={(e) => setMinTrust(parseFloat(e.target.value))}
                        className="w-full accent-[#00c9ff] h-1 bg-white/5 rounded-full appearance-none cursor-pointer"
                    />
                </div>
                
                <div className="relative w-full lg:w-72 group">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-white/10 group-focus-within:text-[#00c9ff] transition-all duration-300" size={14} />
                    <input 
                        type="text" 
                        placeholder="Search identities or provenance..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-[#0b0d11] border border-white/5 rounded-xl py-3.5 pl-11 pr-4 text-[10px] font-bold uppercase tracking-widest focus:border-[#00c9ff]/30 focus:bg-white/[0.01] transition-all outline-none"
                    />
                </div>
            </div>
        </div>

        {/* High-Density Source Registry */}
        <main className="flex flex-col gap-6">
            <div className="flex justify-between items-center px-4">
                <h3 className="text-label flex items-center gap-2">
                    <Database size={12} />
                    <span>Audit Registry <span className="text-white/10 ml-2">[{filteredData.length} entries]</span></span>
                </h3>
            </div>
            <div className="flex flex-col gap-6">
                <AnimatePresence mode="popLayout" initial={false}>
                    {filteredData.length > 0 ? (
                        filteredData.map((item) => (
                            <SourceCard key={item.source_url} item={item} />
                        ))
                    ) : (
                        <motion.div 
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                            className="p-20 rounded-[2rem] border-2 border-dashed border-white/5 flex flex-col items-center justify-center gap-4 text-white/5"
                        >
                            <Info size={48} strokeWidth={1} />
                            <span className="text-[10px] font-black uppercase tracking-[0.4em]">Zero Results in Registry</span>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main>

        <footer className="py-10 border-t border-white/5 flex justify-between items-center text-label text-white/5">
            <span>© 2026 Trust Intelligence Engine</span>
            <div className="flex gap-8">
                <span className="flex items-center gap-2 tracking-[0.2em]"><Globe size={10} /> Validated Registry</span>
                <span className="flex items-center gap-2 tracking-[0.2em]"><ShieldCheck size={10} /> Integrity Enforced</span>
            </div>
        </footer>
      </div>
    </div>
  )
}

const HeaderMetric = ({ label, value, icon }: any) => (
    <div className="flex items-center gap-4">
        <div className="p-2.5 bg-white/[0.02] rounded-xl border border-white/5">
            {icon}
        </div>
        <div className="flex flex-col">
            <span className="text-[8px] font-black uppercase tracking-widest text-white/10 mb-1">{label}</span>
            <span className="text-3xl font-black tracking-tighter tabular-nums text-white/70">{value}</span>
        </div>
    </div>
)
