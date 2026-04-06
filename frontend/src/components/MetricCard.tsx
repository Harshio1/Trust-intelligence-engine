import { motion } from 'framer-motion'

interface MetricCardProps {
  label: string
  value: string | number
  icon: React.ReactNode
  delay?: number
}

export const MetricCard = ({ label, value, icon, delay = 0 }: MetricCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{ scale: 1.02 }}
      className="glass-card p-6 flex flex-col gap-2"
    >
      <div className="flex justify-between items-start">
        <span className="text-white/60 font-medium">{label}</span>
        <div className="p-2 bg-white/5 rounded-lg text-primary">
          {icon}
        </div>
      </div>
      <span className="text-3xl font-extrabold tracking-tight">{value}</span>
    </motion.div>
  )
}
