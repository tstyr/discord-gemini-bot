'use client'
import { motion } from 'framer-motion'

interface GlowOrbProps {
  color: 'pink' | 'cyan' | 'purple'
  size?: number
  top?: string
  left?: string
  right?: string
  bottom?: string
}

const colorMap = {
  pink: 'rgba(255, 102, 170, 0.15)',
  cyan: 'rgba(0, 255, 204, 0.15)',
  purple: 'rgba(170, 102, 255, 0.15)',
}

export function GlowOrb({ color, size = 400, top, left, right, bottom }: GlowOrbProps) {
  return (
    <motion.div
      className="fixed rounded-full blur-3xl pointer-events-none"
      style={{
        width: size,
        height: size,
        background: colorMap[color],
        top,
        left,
        right,
        bottom,
      }}
      animate={{
        scale: [1, 1.1, 1],
        opacity: [0.5, 0.7, 0.5],
      }}
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  )
}
