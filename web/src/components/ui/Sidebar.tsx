'use client'
import { motion } from 'framer-motion'
import { Home, BarChart3, Settings, MessageSquare, Zap } from 'lucide-react'
import Link from 'next/link'

const navItems = [
  { icon: Home, label: 'ダッシュボード', href: '/' },
  { icon: BarChart3, label: '統計', href: '/stats' },
  { icon: MessageSquare, label: '会話履歴', href: '/conversations' },
  { icon: Settings, label: '設定', href: '/settings' },
]

export function Sidebar() {
  return (
    <motion.aside
      className="fixed left-0 top-0 h-full w-64 bg-osu-darker border-r border-osu-border z-50"
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* ロゴ */}
      <div className="p-6 border-b border-osu-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-osu-pink to-osu-purple flex items-center justify-center">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-lg">AI Bot</h1>
            <p className="text-xs text-gray-500">Dashboard</p>
          </div>
        </div>
      </div>

      {/* ナビゲーション */}
      <nav className="p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-400 hover:text-white hover:bg-osu-card transition-all group"
                >
                  <Icon className="w-5 h-5 group-hover:text-osu-pink transition-colors" />
                  <span>{item.label}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </motion.aside>
  )
}
