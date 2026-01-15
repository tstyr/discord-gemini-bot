'use client'

import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  delay?: number
  hover?: boolean
}

export default function Card({ children, className = '', delay = 0, hover = true }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={hover ? { y: -5, scale: 1.02 } : {}}
      className={`
        bg-osu-card border border-osu-border rounded-xl p-6
        backdrop-blur-sm relative overflow-hidden
        shadow-lg hover:shadow-xl transition-shadow duration-300
        ${className}
      `}
    >
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-osu-pink/5 to-osu-purple/5 pointer-events-none" />
      
      {/* Diagonal line accent */}
      <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
        <div className="absolute top-4 right-4 w-24 h-0.5 bg-osu-pink rotate-45 transform origin-left" />
        <div className="absolute top-8 right-8 w-16 h-0.5 bg-osu-cyan rotate-45 transform origin-left" />
      </div>
      
      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  )
}

export function CardTitle({ children, className = '' }: { children: ReactNode, className?: string }) {
  return (
    <h3 className={`text-xl font-bold text-white mb-4 ${className}`}>
      {children}
    </h3>
  )
}

export function CardContent({ children, className = '' }: { children: ReactNode, className?: string }) {
  return (
    <div className={`text-gray-300 ${className}`}>
      {children}
    </div>
  )
}