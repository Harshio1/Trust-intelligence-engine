import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { 
  ExternalLink, 
  Globe, 
  BarChart3, 
  Database, 
  Download, 
  Copy, 
  Check, 
  Activity,
  AlertTriangle,
  Clock,
  Layers,
  ChevronRight,
  Info,
  Sparkles
} from 'lucide-react'

interface SourceCardProps {
  item: any
}

export const SourceCard = ({ item }: SourceCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isCopied, setIsCopied] = useState(false)
  const score = item?.trust_score ?? 0

  const getStatusClass = (s: number) => {
    if (s >= 0.8) return 'status-high'
    if (s >= 0.5) return 'status-medium'
    return 'status-low'
  }

  const getStatusBg = (s: number) => {
    if (s >= 0.8) return 'status-high-bg'
    if (s >= 0.5) return 'status-medium-bg'
    return 'status-low-bg'
  }

  const downloadJSON = () => {
    const filename = `${item.source_type}_${item.author?.replace(/\s+/g, '_').toLowerCase() || 'source'}.json`
    const blob = new Blob([JSON.stringify(item, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(item, null, 2))
    setIsCopied(false)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  return (
    <motion.div 
      layout 
      initial={item.isNew ? { scale: 0.95, opacity: 0 } : false}
      animate={{ scale: 1, opacity: 1 }}
      className={`diagnostic-card hover:bg-white/[0.01] transition-colors relative overflow-hidden ${item.isNew ? 'ring-2 ring-[#00c9ff]/20' : ''}`}
    >
      {/* New Analysis Glow Effect */}
      {item.isNew && (
        <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-[#00c9ff] to-transparent animate-pulse-subtle" />
      )}

      <div className="p-5 flex flex-col gap-6">
        
        {/* Compact Header */}
        <div className="flex justify-between items-center bg-white/[0.02] -mx-5 -mt-5 p-5 border-b border-white/5">
          <div className="flex items-center gap-6">
            <div className={`p-3 rounded-xl border ${getStatusClass(score)} relative`}>
               <Activity size={20} />
               {item.isNew && (
                 <div className="absolute -top-1 -right-1 flex h-3 w-3">
                   <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00c9ff] opacity-75"></span>
                   <span className="relative inline-flex rounded-full h-3 w-3 bg-[#00c9ff]"></span>
                 </div>
               )}
            </div>
            <div className="flex flex-col">
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-black uppercase tracking-widest text-[#00c9ff]">{item.source_type}</span>
                    <a href={item.source_url} target="_blank" rel="noreferrer" className="text-white/20 hover:text-white transition-colors"><ExternalLink size={10} /></a>
                    {item.isNew && (
                      <span className="flex items-center gap-1.5 px-2 py-0.5 bg-[#00c9ff]/10 border border-[#00c9ff]/20 rounded text-[8px] font-black uppercase text-[#00c9ff] tracking-widest ml-2">
                        <Sparkles size={8} /> Newly Analyzed
                      </span>
                    )}
                </div>
                <h2 className="text-xl font-black tracking-tight text-white/90 line-clamp-1" title={item?.title || item?.author || "Unknown Source"}>
                    {item?.title || item?.author || "Unknown Source"}
                </h2>
            </div>
          </div>

          <div className="flex items-center gap-4 bg-black/20 px-5 py-2 rounded-2xl border border-white/5">
            <div className="flex flex-col items-end">
                <span className="text-[9px] font-black uppercase tracking-widest text-white/20">Trust Reliability</span>
                <span className={`text-2xl font-black tracking-tighter ${getStatusClass(score).split(' ')[0]}`}>
                    {(Number(score) || 0).toFixed(2)}
                </span>
            </div>
            <div className="h-8 w-[1px] bg-white/10" />
            <button 
                onClick={() => setIsExpanded(!isExpanded)} 
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-[9px] font-black uppercase tracking-widest ${
                    isExpanded ? 'bg-[#00c9ff] text-black shadow-[0_0_10px_rgba(0,201,255,0.3)]' : 'bg-white/5 hover:bg-white/10 text-white/40'
                }`}
            >
                <Layers size={14} />
                <span>{isExpanded ? 'Collapse Audit' : 'Detailed Audit'}</span>
            </button>
          </div>
        </div>

        {/* Unified Utility Row (Combined Info & Tags) */}
        <div className="flex flex-wrap items-center justify-between gap-4">
           <div className="flex flex-wrap items-center gap-8 border-r border-white/5 pr-8">
              <UtilityItem label="AUTHOR" value={item?.author || 'Anonymous'} icon={<Info size={12} />} />
              <UtilityItem label="DATE" value={item?.published_date || 'Unknown'} icon={<Clock size={12} />} />
              <UtilityItem label="REGION" value={item?.region || 'GLOBAL'} icon={<Globe size={12} />} />
           </div>

           <div className="flex flex-wrap gap-2 flex-grow px-4">
              {Array.isArray(item.topic_tags) && item.topic_tags.slice(0, 4).map((tag: string, i: number) => (
                <span key={i} className="px-2.5 py-1 bg-white/[0.03] border border-white/5 rounded-md text-[9px] font-black text-white/30 uppercase tracking-widest">
                  #{tag}
                </span>
              ))}
           </div>

           <div className="flex gap-2">
              <button onClick={downloadJSON} className="p-2.5 rounded-xl bg-white/5 border border-white/5 hover:border-white/20 text-white/40 hover:text-white transition-all shadow-lg" title="Download JSON">
                <Download size={14} />
              </button>
              <button onClick={copyToClipboard} className="p-2.5 rounded-xl bg-white/5 border border-white/5 hover:border-white/20 text-white/40 hover:text-white transition-all shadow-lg" title="Copy Raw Data">
                {isCopied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
              </button>
           </div>
        </div>

        {/* Expandable Audit Section */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="flex flex-col gap-8 pt-5 border-t border-white/5"
            >
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                
                {/* Reliability Breakdown */}
                <div className="flex flex-col gap-6">
                  <SectionLabel icon={<BarChart3 size={14} />} label="Statistical Signal Breakdown" />
                  
                  {Array.isArray(item.abuse_flags) && item.abuse_flags.length > 0 && (
                    <div className="p-4 bg-rose-500/5 border border-rose-500/10 rounded-2xl flex flex-wrap gap-2">
                        {item.abuse_flags.map((flag: string, i: number) => (
                          <span key={i} className="px-2 py-1 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded text-[8px] font-black uppercase tracking-widest">
                            {flag}
                          </span>
                        ))}
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-x-10 gap-y-4">
                    {item?.trust_breakdown && Object.entries(item.trust_breakdown).map(([key, val]: any, i) => (
                      <div key={i} className="flex flex-col gap-2">
                        <div className="flex justify-between items-center text-[9px] font-black uppercase tracking-widest text-white/20">
                          <span>{key.replace('_', ' ')}</span>
                          <span className="text-white/40">{(Number(val) || 0).toFixed(2)}</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: `${(Number(val) || 0) * 100}%` }}
                            className={`h-full ${getStatusBg(Number(val) || 0)}`}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Explicit Strengths / Weaknesses Mapping */}
                <div className="grid grid-cols-2 gap-8">
                   <div className="flex flex-col gap-4">
                      <SectionLabel icon={<Check size={14} className="text-emerald-400" />} label="Source Strengths" />
                      <div className="flex flex-col gap-2">
                         {Array.isArray(item.strengths) && item.strengths.length > 0 ? item.strengths.map((s: string, i: number) => (
                            <div key={i} className="flex items-start gap-2 group">
                               <ChevronRight size={12} className="text-emerald-400/50 mt-0.5 group-hover:translate-x-0.5 transition-transform" />
                               <span className="text-[10px] font-bold text-white/50 uppercase tracking-tight">{s}</span>
                            </div>
                         )) : <span className="text-[10px] text-white/10 uppercase italic">None identified</span>}
                      </div>
                   </div>

                   <div className="flex flex-col gap-4">
                      <SectionLabel icon={<AlertTriangle size={14} className="text-rose-400" />} label="Potential Risks" />
                      <div className="flex flex-col gap-2">
                         {Array.isArray(item.weaknesses) && item.weaknesses.length > 0 ? item.weaknesses.map((w: string, i: number) => (
                            <div key={i} className="flex items-start gap-2 group">
                               <ChevronRight size={12} className="text-rose-400/50 mt-0.5 group-hover:translate-x-0.5 transition-transform" />
                               <span className="text-[10px] font-bold text-white/50 uppercase tracking-tight">{w}</span>
                            </div>
                         )) : <span className="text-[10px] text-white/10 uppercase italic">Minimum risk noted</span>}
                      </div>
                   </div>
                </div>
              </div>

              {/* Content Chunks (Dense List) */}
              <div className="flex flex-col gap-6 pt-5 border-t border-white/5">
                 <SectionLabel icon={<Database size={14} />} label={`Provenance Data Fragments (${item.content_chunks?.length || 0})`} />
                 <div className="grid grid-cols-1 gap-2">
                    {Array.isArray(item.content_chunks) && item.content_chunks.slice(0, 3).map((chunk: string, i: number) => (
                      <div key={i} className="p-4 bg-white/[0.01] border border-white/5 rounded-xl flex gap-4 group hover:bg-white/[0.02] transition-colors">
                        <span className="text-[9px] font-black text-white/10 mt-0.5">0{i+1}</span>
                        <p className="text-[11px] text-white/30 leading-tight group-hover:text-white/50 transition-colors uppercase tracking-tight line-clamp-2">{chunk}</p>
                      </div>
                    ))}
                 </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

const UtilityItem = ({ label, value, icon }: any) => (
  <div className="flex items-center gap-3">
    <div className="p-2 bg-white/5 rounded-lg text-white/20">
      {icon}
    </div>
    <div className="flex flex-col">
      <span className="text-[8px] font-black text-white/10 tracking-[0.2em]">{label}</span>
      <span className="text-[10px] font-bold text-white/50 tracking-tight">{value || 'N/A'}</span>
    </div>
  </div>
)

const SectionLabel = ({ icon, label }: any) => (
  <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-white/20">
    {icon}
    <span>{label}</span>
  </div>
)
