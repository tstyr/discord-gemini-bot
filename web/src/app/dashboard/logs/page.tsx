'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import Card from '@/components/Card'
import ChatLog from '@/components/ChatLog'
import { MessageSquare, Filter, Download, RefreshCw } from 'lucide-react'

export default function LogsPage() {
  const [selectedGuild, setSelectedGuild] = useState<string>('all')
  const [refreshKey, setRefreshKey] = useState(0)

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1)
  }

  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Export logs')
  }

  return (
    <div className="min-h-screen bg-osu-dark relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-osu-purple/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-osu-cyan/5 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-0.5 bg-gradient-to-r from-transparent via-osu-pink/10 to-transparent rotate-12" />

      <div className="relative z-10 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <MessageSquare className="w-8 h-8 text-osu-purple" />
            会話ログ
          </h1>
          <p className="text-gray-400">
            AIとユーザーの会話履歴をリアルタイムで表示
          </p>
        </motion.div>

        {/* Controls */}
        <Card delay={0.1} className="mb-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-gray-400" />
                <select
                  value={selectedGuild}
                  onChange={(e) => setSelectedGuild(e.target.value)}
                  className="bg-osu-darker border border-osu-border rounded-lg px-3 py-2 text-white focus:border-osu-pink focus:outline-none"
                >
                  <option value="all">全サーバー</option>
                  {/* TODO: Add guild options */}
                </select>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleRefresh}
                className="flex items-center gap-2 px-4 py-2 bg-osu-cyan/20 text-osu-cyan rounded-lg hover:bg-osu-cyan/30 transition-colors duration-200"
              >
                <RefreshCw className="w-4 h-4" />
                更新
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 bg-osu-pink/20 text-osu-pink rounded-lg hover:bg-osu-pink/30 transition-colors duration-200"
              >
                <Download className="w-4 h-4" />
                エクスポート
              </motion.button>
            </div>
          </div>
        </Card>

        {/* Chat Logs */}
        <Card delay={0.2}>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-osu-purple" />
              リアルタイム会話ログ
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              最新の会話から順番に表示されます
            </p>
          </div>

          <ChatLog 
            key={refreshKey}
            guildId={selectedGuild === 'all' ? undefined : selectedGuild} 
            limit={100} 
          />
        </Card>
      </div>
    </div>
  )
}