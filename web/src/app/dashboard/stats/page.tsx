'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import Card from '@/components/Card'
import { apiClient, Stats, Guild } from '@/lib/api'
import { 
  BarChart3, 
  TrendingUp, 
  MessageSquare, 
  Zap, 
  Users, 
  Server,
  Calendar,
  Activity
} from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'

const COLORS = ['#ff66aa', '#00ffcc', '#aa66ff', '#ffaa00']

export default function StatsPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [guilds, setGuilds] = useState<Guild[]>([])
  const [selectedGuild, setSelectedGuild] = useState<string>('all')
  const [usageHistory, setUsageHistory] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    fetchStats()
    fetchUsageHistory()
  }, [selectedGuild])

  const fetchData = async () => {
    const guildsResponse = await apiClient.getGuilds()
    if (guildsResponse.success && guildsResponse.data) {
      setGuilds(guildsResponse.data)
    }
    setLoading(false)
  }

  const fetchStats = async () => {
    const guildId = selectedGuild === 'all' ? undefined : selectedGuild
    const response = await apiClient.getStats(guildId)
    if (response.success && response.data) {
      setStats(response.data)
    }
  }

  const fetchUsageHistory = async () => {
    const guildId = selectedGuild === 'all' ? undefined : selectedGuild
    const response = await apiClient.getUsageHistory(guildId)
    if (response.success && response.data) {
      setUsageHistory(response.data)
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

  // Mock data for charts (since we don't have real time-series data yet)
  const mockUsageData = [
    { name: '月', messages: 120, tokens: 1200 },
    { name: '火', messages: 190, tokens: 1900 },
    { name: '水', messages: 300, tokens: 3000 },
    { name: '木', messages: 280, tokens: 2800 },
    { name: '金', messages: 200, tokens: 2000 },
    { name: '土', messages: 150, tokens: 1500 },
    { name: '日', messages: 100, tokens: 1000 },
  ]

  const mockModeData = [
    { name: 'Standard', value: 45, color: '#ff66aa' },
    { name: 'Creative', value: 25, color: '#aa66ff' },
    { name: 'Coder', value: 20, color: '#00ffcc' },
    { name: 'Assistant', value: 10, color: '#ffaa00' },
  ]

  return (
    <div className="min-h-screen bg-osu-dark relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-osu-cyan/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-osu-pink/5 rounded-full blur-3xl" />

      <div className="relative z-10 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-osu-cyan" />
            使用統計
          </h1>
          <p className="text-gray-400">
            AIボットの詳細な使用状況とパフォーマンス分析
          </p>
        </motion.div>

        {/* Guild Selector */}
        <Card delay={0.1} className="mb-8">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Server className="w-5 h-5 text-osu-pink" />
              表示対象
            </h2>
            
            <select
              value={selectedGuild}
              onChange={(e) => setSelectedGuild(e.target.value)}
              className="bg-osu-darker border border-osu-border rounded-lg px-4 py-2 text-white focus:border-osu-pink focus:outline-none"
            >
              <option value="all">全サーバー</option>
              {guilds.map((guild) => (
                <option key={guild.id} value={guild.id}>
                  {guild.name}
                </option>
              ))}
            </select>
          </div>
        </Card>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card delay={0.2}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">総メッセージ数</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.total_messages?.toLocaleString() || '0'}
                </p>
                <p className="text-green-500 text-sm flex items-center gap-1 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  +12% 今週
                </p>
              </div>
              <div className="p-3 bg-osu-pink/20 rounded-xl">
                <MessageSquare className="w-6 h-6 text-osu-pink" />
              </div>
            </div>
          </Card>

          <Card delay={0.3}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">トークン使用量</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.total_tokens?.toLocaleString() || '0'}
                </p>
                <p className="text-green-500 text-sm flex items-center gap-1 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  +8% 今週
                </p>
              </div>
              <div className="p-3 bg-osu-cyan/20 rounded-xl">
                <Zap className="w-6 h-6 text-osu-cyan" />
              </div>
            </div>
          </Card>

          <Card delay={0.4}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">アクティブユーザー</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.unique_users || '0'}
                </p>
                <p className="text-green-500 text-sm flex items-center gap-1 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  +5% 今週
                </p>
              </div>
              <div className="p-3 bg-osu-purple/20 rounded-xl">
                <Users className="w-6 h-6 text-osu-purple" />
              </div>
            </div>
          </Card>

          <Card delay={0.5}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">平均応答時間</p>
                <p className="text-2xl font-bold text-white">1.2s</p>
                <p className="text-green-500 text-sm flex items-center gap-1 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  -3% 今週
                </p>
              </div>
              <div className="p-3 bg-gradient-to-br from-osu-pink/20 to-osu-cyan/20 rounded-xl">
                <Activity className="w-6 h-6 text-osu-pink" />
              </div>
            </div>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Usage Trend */}
          <Card delay={0.6}>
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-osu-pink" />
              使用量推移（7日間）
            </h2>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockUsageData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="name" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1a1a1a', 
                      border: '1px solid #333',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="messages" 
                    stroke="#ff66aa" 
                    strokeWidth={2}
                    name="メッセージ数"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="tokens" 
                    stroke="#00ffcc" 
                    strokeWidth={2}
                    name="トークン数"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Mode Usage */}
          <Card delay={0.7}>
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-osu-cyan" />
              AIモード使用率
            </h2>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={mockModeData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {mockModeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        {/* Detailed Stats */}
        <Card delay={0.8}>
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-osu-purple" />
            詳細統計
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-4 bg-osu-darker rounded-lg">
              <h3 className="text-white font-medium mb-2">今日の使用量</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">メッセージ</span>
                  <span className="text-white">42</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">トークン</span>
                  <span className="text-white">1,234</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">ユーザー</span>
                  <span className="text-white">15</span>
                </div>
              </div>
            </div>
            
            <div className="p-4 bg-osu-darker rounded-lg">
              <h3 className="text-white font-medium mb-2">今週の使用量</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">メッセージ</span>
                  <span className="text-white">287</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">トークン</span>
                  <span className="text-white">8,456</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">ユーザー</span>
                  <span className="text-white">52</span>
                </div>
              </div>
            </div>
            
            <div className="p-4 bg-osu-darker rounded-lg">
              <h3 className="text-white font-medium mb-2">今月の使用量</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">メッセージ</span>
                  <span className="text-white">1,234</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">トークン</span>
                  <span className="text-white">34,567</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">ユーザー</span>
                  <span className="text-white">128</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}