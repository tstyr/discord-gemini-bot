'use client'

import { motion } from 'framer-motion'
import { 
  Home, 
  BarChart3, 
  Settings, 
  MessageSquare, 
  Users, 
  Zap,
  Bot,
  Activity,
  Plus,
  Music
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const menuItems = [
  { icon: Home, label: 'ダッシュボード', href: '/dashboard' },
  { icon: BarChart3, label: '統計', href: '/dashboard/stats' },
  { icon: MessageSquare, label: 'チャンネル', href: '/dashboard/channels' },
  { icon: Plus, label: 'セットアップ', href: '/dashboard/setup' },
  { icon: Bot, label: 'AIモード', href: '/dashboard/ai-mode' },
  { icon: Music, label: '音楽プレイヤー', href: '/dashboard/music' },
  { icon: MessageSquare, label: '会話ログ', href: '/dashboard/logs' },
  { icon: Activity, label: 'ネットワーク', href: '/dashboard/network' },
  { icon: Zap, label: 'リソース', href: '/dashboard/resources' },
  { icon: Users, label: 'サーバー', href: '/dashboard/guilds' },
  { icon: Settings, label: '設定', href: '/dashboard/settings' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <motion.div
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="w-20 bg-osu-darker border-r border-osu-border flex flex-col items-center py-6 relative overflow-hidden"
    >
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-b from-osu-pink/5 to-osu-purple/5" />
      <div className="absolute -top-10 -left-10 w-20 h-20 bg-osu-cyan/10 rounded-full blur-xl" />
      <div className="absolute -bottom-10 -right-10 w-20 h-20 bg-osu-pink/10 rounded-full blur-xl" />
      
      {/* Logo */}
      <motion.div
        whileHover={{ scale: 1.1, rotate: 5 }}
        className="mb-8 p-3 bg-osu-gradient rounded-xl shadow-lg relative z-10"
      >
        <Zap className="w-6 h-6 text-white" />
      </motion.div>

      {/* Menu Items */}
      <nav className="flex flex-col space-y-4 relative z-10">
        {menuItems.map((item, index) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Link href={item.href}>
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className={`
                    p-3 rounded-xl transition-all duration-300 relative group
                    ${isActive 
                      ? 'bg-osu-gradient shadow-lg' 
                      : 'bg-osu-card hover:bg-osu-border'
                    }
                  `}
                >
                  <Icon 
                    className={`
                      w-5 h-5 transition-colors duration-300
                      ${isActive ? 'text-white' : 'text-gray-400 group-hover:text-osu-pink'}
                    `} 
                  />
                  
                  {/* Tooltip */}
                  <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 bg-osu-card border border-osu-border rounded-lg px-3 py-2 text-sm text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap z-50">
                    {item.label}
                    <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-osu-border" />
                  </div>
                </motion.div>
              </Link>
            </motion.div>
          )
        })}
      </nav>
    </motion.div>
  )
}

export { Sidebar }