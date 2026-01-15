'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import Card from '@/components/Card'
import { apiClient, Guild } from '@/lib/api'
import { 
  Hash, 
  Server, 
  Toggle, 
  CheckCircle, 
  XCircle,
  Loader2,
  MessageSquare,
  Lock,
  Globe,
  Trash2,
  User,
  Crown,
  Activity,
  AlertTriangle
} from 'lucide-react'

interface AiChannel {
  channel_id: number
  name: string
  exists: boolean
  creator_id?: number
  creator_name?: string
  creator_avatar?: string
  owner_id?: number
  owner_name?: string
  owner_avatar?: string
  created_at: string
}

interface AiChannelsData {
  public_channels: AiChannel[]
  private_channels: AiChannel[]
}

interface ChannelActivity {
  channel_id: number
  channel_name: string
  message_count: number
  last_activity: string
  avg_tokens: number
  exists: boolean
}

export default function ChannelsPage() {
  const [guilds, setGuilds] = useState<Guild[]>([])
  const [selectedGuild, setSelectedGuild] = useState<string>('')
  const [aiChannels, setAiChannels] = useState<AiChannelsData | null>(null)
  const [channelActivity, setChannelActivity] = useState<ChannelActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<string>('')

  useEffect(() => {
    fetchGuilds()
  }, [])

  useEffect(() => {
    if (selectedGuild) {
      fetchAiChannels(selectedGuild)
      fetchChannelActivity(selectedGuild)
    }
  }, [selectedGuild])

  const fetchGuilds = async () => {
    const response = await apiClient.getGuilds()
    if (response.success && response.data) {
      setGuilds(response.data)
      if (response.data.length > 0) {
        setSelectedGuild(response.data[0].id)
      }
    }
    setLoading(false)
  }

  const fetchAiChannels = async (guildId: string) => {
    const response = await apiClient.getAiChannels(guildId)
    if (response.success && response.data) {
      setAiChannels(response.data)
    }
  }

  const fetchChannelActivity = async (guildId: string) => {
    const response = await apiClient.getChannelActivity(guildId)
    if (response.success && response.data) {
      setChannelActivity(response.data)
    }
  }

  const deleteChannel = async (channelId: string) => {
    setDeleting(channelId)
    
    const response = await apiClient.deleteChannel(channelId, selectedGuild)
    
    if (response.success) {
      // Refresh data
      await fetchAiChannels(selectedGuild)
      await fetchChannelActivity(selectedGuild)
    }
    
    setDeleting('')
  }

  const getActivityLevel = (messageCount: number) => {
    if (messageCount >= 20) return { level: 'high', color: 'text-red-500', bg: 'bg-red-500/20' }
    if (messageCount >= 10) return { level: 'medium', color: 'text-yellow-500', bg: 'bg-yellow-500/20' }
    if (messageCount >= 1) return { level: 'low', color: 'text-green-500', bg: 'bg-green-500/20' }
    return { level: 'none', color: 'text-gray-500', bg: 'bg-gray-500/20' }
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
            <Hash className="w-8 h-8 text-osu-cyan" />
            AIチャンネル管理
          </h1>
          <p className="text-gray-400">
            パブリック・プライベートAIチャンネルの管理とアクティビティ監視
          </p>
        </motion.div>

        {/* Guild Selector */}
        <Card delay={0.1} className="mb-8">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Server className="w-5 h-5 text-osu-pink" />
              サーバー選択
            </h2>
            
            <select
              value={selectedGuild}
              onChange={(e) => setSelectedGuild(e.target.value)}
              className="bg-osu-darker border border-osu-border rounded-lg px-4 py-2 text-white focus:border-osu-pink focus:outline-none"
            >
              {guilds.map((guild) => (
                <option key={guild.id} value={guild.id}>
                  {guild.name}
                </option>
              ))}
            </select>
          </div>
        </Card>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Public Channels */}
          <Card delay={0.2}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Globe className="w-5 h-5 text-osu-cyan" />
                パブリックチャンネル
              </h2>
              <div className="text-sm text-gray-400">
                {aiChannels?.public_channels.length || 0} チャンネル
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
              {aiChannels?.public_channels.map((channel, index) => (
                <motion.div
                  key={channel.channel_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="flex items-center justify-between p-4 bg-osu-darker rounded-lg border border-osu-border hover:border-osu-cyan/50 transition-colors duration-200"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-osu-cyan/20 rounded-lg">
                      <Globe className="w-4 h-4 text-osu-cyan" />
                    </div>
                    <div>
                      <p className="text-white font-medium flex items-center gap-2">
                        #{channel.name}
                        {!channel.exists && (
                          <AlertTriangle className="w-4 h-4 text-yellow-500" title="チャンネルが削除されています" />
                        )}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-gray-400">
                        <User className="w-3 h-3" />
                        <span>{channel.creator_name}</span>
                      </div>
                    </div>
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => deleteChannel(channel.channel_id.toString())}
                    disabled={deleting === channel.channel_id.toString()}
                    className="p-2 bg-red-500/20 text-red-500 rounded-lg hover:bg-red-500/30 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {deleting === channel.channel_id.toString() ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </motion.button>
                </motion.div>
              ))}

              {(!aiChannels?.public_channels.length) && (
                <div className="text-center py-8 text-gray-400">
                  <Globe className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>パブリックチャンネルがありません</p>
                  <p className="text-sm mt-2">Discord で `/setup-public-chat` を実行してください</p>
                </div>
              )}
            </div>
          </Card>

          {/* Private Channels */}
          <Card delay={0.3}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Lock className="w-5 h-5 text-osu-purple" />
                プライベートチャンネル
              </h2>
              <div className="text-sm text-gray-400">
                {aiChannels?.private_channels.length || 0} チャンネル
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
              {aiChannels?.private_channels.map((channel, index) => (
                <motion.div
                  key={channel.channel_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="flex items-center justify-between p-4 bg-osu-darker rounded-lg border border-osu-border hover:border-osu-purple/50 transition-colors duration-200"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg overflow-hidden bg-osu-purple/20 flex items-center justify-center">
                      {channel.owner_avatar ? (
                        <img 
                          src={channel.owner_avatar}
                          alt={channel.owner_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <Lock className="w-4 h-4 text-osu-purple" />
                      )}
                    </div>
                    <div>
                      <p className="text-white font-medium flex items-center gap-2">
                        #{channel.name}
                        {!channel.exists && (
                          <AlertTriangle className="w-4 h-4 text-yellow-500" title="チャンネルが削除されています" />
                        )}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-gray-400">
                        <Crown className="w-3 h-3" />
                        <span>{channel.owner_name}</span>
                      </div>
                    </div>
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => deleteChannel(channel.channel_id.toString())}
                    disabled={deleting === channel.channel_id.toString()}
                    className="p-2 bg-red-500/20 text-red-500 rounded-lg hover:bg-red-500/30 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {deleting === channel.channel_id.toString() ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </motion.button>
                </motion.div>
              ))}

              {(!aiChannels?.private_channels.length) && (
                <div className="text-center py-8 text-gray-400">
                  <Lock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>プライベートチャンネルがありません</p>
                  <p className="text-sm mt-2">Discord で `/setup-private-chat` を実行してください</p>
                </div>
              )}
            </div>
          </Card>

          {/* Channel Activity Heatmap */}
          <Card delay={0.4}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-osu-pink" />
                アクティビティ (24h)
              </h2>
              <div className="text-sm text-gray-400">
                リアルタイム
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
              {channelActivity.map((activity, index) => {
                const activityLevel = getActivityLevel(activity.message_count)
                
                return (
                  <motion.div
                    key={activity.channel_id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className={`p-4 rounded-lg border border-osu-border ${activityLevel.bg} hover:scale-105 transition-all duration-200`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-white font-medium flex items-center gap-2">
                        #{activity.channel_name}
                        {!activity.exists && (
                          <AlertTriangle className="w-4 h-4 text-yellow-500" />
                        )}
                      </p>
                      <div className={`px-2 py-1 rounded-md text-xs font-medium ${activityLevel.bg} ${activityLevel.color}`}>
                        {activity.message_count} msgs
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-xs text-gray-400">
                      <div>
                        <span className="block">平均トークン</span>
                        <span className="text-white font-medium">{activity.avg_tokens.toFixed(1)}</span>
                      </div>
                      <div>
                        <span className="block">最終活動</span>
                        <span className="text-white font-medium">
                          {new Date(activity.last_activity).toLocaleTimeString('ja-JP', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )
              })}

              {channelActivity.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>24時間以内のアクティビティがありません</p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Summary Stats */}
        <Card delay={0.5} className="mt-8">
          <h2 className="text-xl font-semibold text-white mb-4">チャンネル統計</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-osu-cyan mb-2">
                {aiChannels?.public_channels.length || 0}
              </div>
              <div className="text-gray-400">パブリックチャンネル</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-osu-purple mb-2">
                {aiChannels?.private_channels.length || 0}
              </div>
              <div className="text-gray-400">プライベートチャンネル</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-osu-pink mb-2">
                {channelActivity.reduce((sum, activity) => sum + activity.message_count, 0)}
              </div>
              <div className="text-gray-400">24h メッセージ数</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-500 mb-2">
                {channelActivity.filter(a => a.message_count > 0).length}
              </div>
              <div className="text-gray-400">アクティブチャンネル</div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}