'use client'
import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: { value: number; isUp: boolean }
  accentColor?: 'pink' | 'cyan' | 'purple'
}

const accentColors = {
  pink: 'from-osu-pink to-osu-purple',
  cyan: 'from-osu-cyan to-osu-pink',
  purple: 'from-osu-purple to-osu-cyan',
}

export function StatCard({ title, value, icon: Icon, trend, accentColor = 'pink' }: StatCardProps) {
  return (
    <motion.div
      className="osu-card p-6 relative overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.3 }}
    >
      {/* アクセントライン */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${accentColors[accentColor]}`} />
      
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold">{value.toLocaleString()}</p>
          {trend && (
            <p className={`text-sm mt-2 ${trend.isUp ? 'text-osu-cyan' : 'text-red-400'}`}>
              {trend.isUp ? '↑' : '↓'} {trend.value}% from last week
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-br ${accentColors[accentColor]} bg-opacity-20`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </motion.div>
  )
}
