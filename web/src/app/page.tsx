'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { MessageSquare, Zap, Users, TrendingUp } from 'lucide-react'
import { Sidebar } from '@/components/ui/Sidebar'
import { StatCard } from '@/components/ui/StatCard'
import { ModeSelector } from '@/components/ui/ModeSelector'
import { GlowOrb } from '@/components/ui/GlowOrb'

export default function Dashboard() {
  const [currentMode, setCurrentMode] = useState('standard')

  const stats = {
    totalMessages: 12847,
    totalTokens: 1284500,
    activeUsers: 342,
    avgResponseTime: 1.2,
  }

  return (
    <div className="min-h-screen">
      <GlowOrb color="pink" size={500} top="-10%" right="-10%" />
      <GlowOrb color="purple" size={400} bottom="10%" left="20%" />
      <GlowOrb color="cyan" size={300} top="50%" right="30%" />

      <Sidebar />

      <main className="ml-64 p-8 relative z-10">
        <motion.div className="mb-8" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold mb-2">ダッシュボード</h1>
          <p className="text-gray-400">AI Botの使用状況を確認</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard title="総メッセージ数" value={stats.totalMessages} icon={MessageSquare} trend={{ value: 12, isUp: true }} accentColor="pink" />
          <StatCard title="総トークン消費" value={stats.totalTokens} icon={Zap} trend={{ value: 8, isUp: true }} accentColor="cyan" />
          <StatCard title="アクティブユーザー" value={stats.activeUsers} icon={Users} trend={{ value: 5, isUp: true }} accentColor="purple" />
          <StatCard title="平均応答時間" value={`${stats.avgResponseTime}s`} icon={TrendingUp} accentColor="pink" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ModeSelector currentMode={currentMode} onModeChange={setCurrentMode} />
          
          <motion.div className="osu-card p-6" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <h3 className="text-lg font-semibold mb-4">最近のアクティビティ</h3>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-osu-darker">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-osu-pink to-osu-purple" />
                  <div className="flex-1">
                    <p className="text-sm">User#{i}がチャットを使用</p>
                    <p className="text-xs text-gray-500">{i}分前</p>
                  </div>
                  <span className="text-xs text-osu-cyan">+{i * 50} tokens</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
