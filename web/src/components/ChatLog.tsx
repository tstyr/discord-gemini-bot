'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import { 
  MessageSquare, 
  Bot, 
  User, 
  Zap, 
  Clock, 
  Hash,
  Filter,
  Search
} from 'lucide-react'
import { apiClient } from '@/lib/api'

interface ChatMessage {
  id: string
  user_id: string
  username: string
  user_avatar?: string
  channel_id: string
  channel_name: string
  guild_id: string
  guild_name: string
  user_message: string
  ai_response: string
  tokens_used: number
  ai_mode: string
  response_time: number
  timestamp: string
}

interface ChatLogProps {
  guildId?: string
  limit?: number
}

export default function ChatLog({ guildId, limit = 50 }: ChatLogProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [selectedMode, setSelectedMode] = useState('all')

  useEffect(() => {
    fetchChatLogs()
    
    // Set up real-time updates (polling for now, can be upgraded to WebSocket)
    const interval = setInterval(fetchChatLogs, 5000)
    return () => clearInterval(interval)
  }, [guildId, limit])

  const fetchChatLogs = async () => {
    try {
      const response = await apiClient.getChatLogs(guildId, limit)
      if (response.success && response.data) {
        setMessages(response.data as ChatMessage[])
      }
    } catch (error) {
      console.error('Failed to fetch chat logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredMessages = messages.filter(msg => {
    const matchesFilter = filter === '' || 
      msg.username.toLowerCase().includes(filter.toLowerCase()) ||
      msg.user_message.toLowerCase().includes(filter.toLowerCase()) ||
      msg.ai_response.toLowerCase().includes(filter.toLowerCase())
    
    const matchesMode = selectedMode === 'all' || msg.ai_mode === selectedMode
    
    return matchesFilter && matchesMode
  })

  const getModeColor = (mode: string) => {
    const colors = {
      standard: 'text-osu-pink',
      creative: 'text-osu-purple',
      coder: 'text-osu-cyan',
      assistant: 'text-green-500'
    }
    return colors[mode as keyof typeof colors] || 'text-gray-400'
  }

  const getModeBg = (mode: string) => {
    const colors = {
      standard: 'bg-osu-pink/10',
      creative: 'bg-osu-purple/10',
      coder: 'bg-osu-cyan/10',
      assistant: 'bg-green-500/10'
    }
    return colors[mode as keyof typeof colors] || 'bg-gray-500/10'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-osu-pink border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="ユーザー名やメッセージで検索..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-osu-darker border border-osu-border rounded-lg text-white placeholder-gray-400 focus:border-osu-pink focus:outline-none"
          />
        </div>
        
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <select
            value={selectedMode}
            onChange={(e) => setSelectedMode(e.target.value)}
            className="pl-10 pr-8 py-2 bg-osu-darker border border-osu-border rounded-lg text-white focus:border-osu-pink focus:outline-none appearance-none"
          >
            <option value="all">全モード</option>
            <option value="standard">Standard</option>
            <option value="creative">Creative</option>
            <option value="coder">Coder</option>
            <option value="assistant">Assistant</option>
          </select>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
        <AnimatePresence>
          {filteredMessages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              whileHover={{ 
                scale: 1.02, 
                boxShadow: '0 0 20px rgba(255, 102, 170, 0.3)' 
              }}
              className="relative group"
            >
              {/* Background user avatar (blurred) */}
              <div className="absolute inset-0 overflow-hidden rounded-xl opacity-5 group-hover:opacity-10 transition-opacity duration-300">
                {message.user_avatar ? (
                  <img 
                    src={message.user_avatar}
                    alt=""
                    className="w-full h-full object-cover blur-sm scale-110"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-osu-pink/20 to-osu-cyan/20" />
                )}
              </div>

              {/* Glow effect on hover */}
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-osu-pink/0 via-osu-pink/5 to-osu-cyan/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm" />

              <div className="relative bg-osu-card/80 backdrop-blur-md border border-osu-border rounded-xl p-4 hover:border-osu-pink/50 transition-all duration-300">
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-osu-gradient rounded-lg flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="text-white font-medium">{message.username}</p>
                      <div className="flex items-center gap-2 text-xs text-gray-400">
                        <Hash className="w-3 h-3" />
                        <span>{message.channel_name}</span>
                        <span>•</span>
                        <span>{message.guild_name}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <div className={`px-2 py-1 rounded-md text-xs font-medium ${getModeBg(message.ai_mode)} ${getModeColor(message.ai_mode)}`}>
                      {message.ai_mode}
                    </div>
                    <div className="text-xs text-gray-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(message.timestamp).toLocaleTimeString('ja-JP', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="space-y-3">
                  {/* User Message */}
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-osu-darker rounded-lg">
                      <MessageSquare className="w-4 h-4 text-osu-cyan" />
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {message.user_message}
                      </p>
                    </div>
                  </div>

                  {/* AI Response */}
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-osu-pink/20 rounded-lg">
                      <Bot className="w-4 h-4 text-osu-pink" />
                    </div>
                    <div className="flex-1">
                      <p className="text-white text-sm leading-relaxed">
                        {message.ai_response}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Footer Stats */}
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-osu-border/50">
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <div className="flex items-center gap-1">
                      <Zap className="w-3 h-3" />
                      <span>{message.tokens_used} tokens</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>{message.response_time.toFixed(2)}s</span>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    {new Date(message.timestamp).toLocaleDateString('ja-JP')}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredMessages.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>会話ログが見つかりません</p>
            {filter && (
              <p className="text-sm mt-2">検索条件を変更してみてください</p>
            )}
          </div>
        )}
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6 pt-6 border-t border-osu-border">
        <div className="text-center">
          <div className="text-2xl font-bold text-osu-pink mb-1">
            {filteredMessages.length}
          </div>
          <div className="text-gray-400 text-sm">表示中のメッセージ</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-osu-cyan mb-1">
            {filteredMessages.reduce((sum, msg) => sum + msg.tokens_used, 0).toLocaleString()}
          </div>
          <div className="text-gray-400 text-sm">総トークン数</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-osu-purple mb-1">
            {new Set(filteredMessages.map(msg => msg.user_id)).size}
          </div>
          <div className="text-gray-400 text-sm">ユニークユーザー</div>
        </div>
      </div>
    </div>
  )
}