'use client'
import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: string | number
  icon: ReactNode
  trend?: string
  color?: 'pink' | 'cyan' | 'purple'
  delay?: number
}

const colorMap = {
  pink: 'from-osu-pink/20 to-osu-pink/5 border-osu-pink/30',
  cyan: 'from-osu-cyan/20 to-osu-cyan/5 border-osu-cyan/30',
  purple: 'from-osu-purple/20 to-osu-purple/5 border-osu-purple/30',
}

const iconColorMap = {
  pink: 'text-osu-pink',
  cyan: 'text-osu-cyan',
  purple: 'text-osu-purple',
}

export default function StatCard({ title, value, icon, trend, color = 'pink', delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className={`bg-gradient-to-br ${colorMap[color]} border rounded-2xl p-5`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold">{value}</p>
          {trend && <p className="text-osu-cyan text-sm mt-1">{trend}</p>}
        </div>
        <div className={`${iconColorMap[color]} opacity-80`}>{icon}</div>
      </div>
    </motion.div>
  )
}
