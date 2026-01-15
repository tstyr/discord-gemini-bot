'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import Card from '@/components/Card'
import { 
  Activity, 
  MessageSquare, 
  Users, 
  Zap, 
  TrendingUp,
  Bot,
  Server,
  Hash
} from 'lucide-react'

interface Stats {
  total_messages: number
  total_tokens: number
  unique_users: number
  avg_tokens: number
}

interface Guild {
  id: string
  name: string
  member_count: number
  icon: string | null
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [guilds, setGuilds] = useState<Guild[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [statsRes, guildsRes] = await Promise.all([
        fetch('http://localhost:8001/api/stats'),
        fetch('http://localhost:8001/api/guilds')
      ])

      if (statsRes.ok) {
        const statsData = await statsRes.json()
        setStats(statsData.data)
      }

      if (guildsRes.ok) {
        const guildsData = await guildsRes.json()
        setGuilds(guildsData.data)
      }
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-osu-dark flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-osu-pink border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-osu-dark relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-osu-pink/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-osu-cyan/5 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-0.5 bg-gradient-to-r from-transparent via-osu-pink/20 to-transparent rotate-12" />

      <div className="relative z-10 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            AI Bot Dashboard
          </h1>
          <p className="text-gray-400">
            Discord AIボットの統合管理システム
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card delay={0.1}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">総メッセージ数</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.total_messages?.toLocaleString() || '0'}
                </p>
              </div>
              <div className="p-3 bg-osu-pink/20 rounded-xl">
                <MessageSquare className="w-6 h-6 text-osu-pink" />
              </div>
            </div>
          </Card>

          <Card delay={0.2}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">トークン使用量</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.total_tokens?.toLocaleString() || '0'}
                </p>
              </div>
              <div className="p-3 bg-osu-cyan/20 rounded-xl">
                <Zap className="w-6 h-6 text-osu-cyan" />
              </div>
            </div>
          </Card>

          <Card delay={0.3}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">アクティブユーザー</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.unique_users || '0'}
                </p>
              </div>
              <div className="p-3 bg-osu-purple/20 rounded-xl">
                <Users className="w-6 h-6 text-osu-purple" />
              </div>
            </div>
          </Card>

          <Card delay={0.4}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">接続サーバー数</p>
                <p className="text-2xl font-bold text-white">
                  {guilds.length}
                </p>
              </div>
              <div className="p-3 bg-gradient-to-br from-osu-pink/20 to-osu-cyan/20 rounded-xl">
                <Server className="w-6 h-6 text-osu-pink" />
              </div>
            </div>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Bot Status */}
          <Card delay={0.5}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-osu-pink" />
                Bot稼働状況
              </h2>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-sm text-green-500">オンライン</span>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">平均応答時間</span>
                <span className="text-white font-semibold">~1.2秒</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">1メッセージあたりの平均トークン</span>
                <span className="text-white font-semibold">
                  {stats?.avg_tokens?.toFixed(1) || '0'}
                </span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">API稼働率</span>
                <span className="text-green-500 font-semibold">99.9%</span>
              </div>
            </div>
          </Card>

          {/* Connected Servers */}
          <Card delay={0.6}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Server className="w-5 h-5 text-osu-cyan" />
                接続中のサーバー
              </h2>
              <span className="text-sm text-gray-400">{guilds.length}個</span>
            </div>
            
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {guilds.slice(0, 5).map((guild, index) => (
                <motion.div
                  key={guild.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="flex items-center gap-3 p-3 bg-osu-darker rounded-lg hover:bg-osu-border transition-colors duration-200"
                >
                  <div className="w-10 h-10 bg-osu-gradient rounded-lg flex items-center justify-center">
                    {guild.icon ? (
                      <img 
                        src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`}
                        alt={guild.name}
                        className="w-full h-full rounded-lg"
                      />
                    ) : (
                      <Hash className="w-5 h-5 text-white" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-white font-medium">{guild.name}</p>
                    <p className="text-gray-400 text-sm">{guild.member_count}人</p>
                  </div>
                </motion.div>
              ))}
              
              {guilds.length > 5 && (
                <div className="text-center py-2">
                  <span className="text-gray-400 text-sm">
                    他 {guilds.length - 5} サーバー...
                  </span>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card delay={0.7} className="mt-8">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-osu-purple" />
            クイックアクション
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="p-4 bg-osu-darker rounded-lg border border-osu-border hover:border-osu-pink transition-colors duration-200 text-left"
            >
              <Bot className="w-6 h-6 text-osu-pink mb-2" />
              <p className="text-white font-medium">AIモード変更</p>
              <p className="text-gray-400 text-sm">現在: Standard</p>
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="p-4 bg-osu-darker rounded-lg border border-osu-border hover:border-osu-cyan transition-colors duration-200 text-left"
            >
              <Hash className="w-6 h-6 text-osu-cyan mb-2" />
              <p className="text-white font-medium">チャンネル設定</p>
              <p className="text-gray-400 text-sm">自動応答の管理</p>
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="p-4 bg-osu-darker rounded-lg border border-osu-border hover:border-osu-purple transition-colors duration-200 text-left"
            >
              <TrendingUp className="w-6 h-6 text-osu-purple mb-2" />
              <p className="text-white font-medium">詳細統計</p>
              <p className="text-gray-400 text-sm">使用量の詳細分析</p>
            </motion.button>
          </div>
        </Card>
      </div>
    </div>
  )
}