'use client'
import { motion } from 'framer-motion'
import { Sparkles, Code, Lightbulb, Bot } from 'lucide-react'

const modes = [
  { id: 'standard', name: 'Standard', icon: Bot, description: '標準モード' },
  { id: 'assistant', name: 'Assistant', icon: Lightbulb, description: '効率的なアシスタント' },
  { id: 'creative', name: 'Creative', icon: Sparkles, description: '創造的モード' },
  { id: 'code_expert', name: 'Code Expert', icon: Code, description: 'コード専門家' },
]

interface ModeSelectorProps {
  currentMode: string
  onModeChange: (mode: string) => void
}

export function ModeSelector({ currentMode, onModeChange }: ModeSelectorProps) {
  return (
    <div className="osu-card p-6">
      <h3 className="text-lg font-semibold mb-4">AIモード</h3>
      <div className="grid grid-cols-2 gap-3">
        {modes.map((mode) => {
          const Icon = mode.icon
          const isActive = currentMode === mode.id
          return (
            <motion.button
              key={mode.id}
              onClick={() => onModeChange(mode.id)}
              className={`p-4 rounded-xl border transition-all text-left ${
                isActive
                  ? 'border-osu-pink bg-osu-pink/10'
                  : 'border-osu-border hover:border-osu-pink/50'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon className={`w-5 h-5 mb-2 ${isActive ? 'text-osu-pink' : 'text-gray-400'}`} />
              <p className="font-medium">{mode.name}</p>
              <p className="text-xs text-gray-500">{mode.description}</p>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}
