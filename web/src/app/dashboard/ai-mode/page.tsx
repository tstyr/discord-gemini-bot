'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import Card from '@/components/Card'
import { apiClient, Guild } from '@/lib/api'
import { 
  Bot, 
  Server, 
  Zap, 
  Code, 
  Palette, 
  Briefcase,
  CheckCircle,
  Loader2
} from 'lucide-react'

interface AiMode {
  current_mode: string
  available_modes: Record<string, string>
}

const modeIcons = {
  standard: Zap,
  creative: Palette,
  coder: Code,
  assistant: Briefcase,
}

const modeColors = {
  standard: 'text-osu-pink',
  creative: 'text-osu-purple',
  coder: 'text-osu-cyan',
  assistant: 'text-green-500',
}

const modeBgColors = {
  standard: 'bg-osu-pink/20',
  creative: 'bg-osu-purple/20',
  coder: 'bg-osu-cyan/20',
  assistant: 'bg-green-500/20',
}

export default function AiModePage() {
  const [guilds, setGuilds] = useState<Guild[]>([])
  const [selectedGuild, setSelectedGuild] = useState<string>('')
  const [aiMode, setAiMode] = useState<AiMode | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    fetchGuilds()
  }, [])

  useEffect(() => {
    if (selectedGuild) {
      fetchAiMode(selectedGuild)
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

  const fetchAiMode = async (guildId: string) => {
    const response = await apiClient.getAiMode(guildId)
    if (response.success && response.data) {
      setAiMode(response.data)
    }
  }

  const changeMode = async (mode: string) => {
    setUpdating(true)
    
    const response = await apiClient.setAiMode(selectedGuild, mode)
    
    if (response.success && aiMode) {
      setAiMode({ ...aiMode, current_mode: mode })
    }
    
    setUpdating(false)
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
      <div className="absolute top-0 left-1/3 w-96 h-96 bg-osu-purple/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/3 w-96 h-96 bg-osu-cyan/5 rounded-full blur-3xl" />

      <div className="relative z-10 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Bot className="w-8 h-8 text-osu-purple" />
            AIモード設定
          </h1>
          <p className="text-gray-400">
            サーバーごとにAIの応答スタイルを設定できます
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Guild Selector */}
          <Card delay={0.1}>
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Server className="w-5 h-5 text-osu-pink" />
              サーバー選択
            </h2>
            
            <div className="space-y-2">
              {guilds.map((guild) => (
                <motion.button
                  key={guild.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setSelectedGuild(guild.id)}
                  className={`
                    w-full p-3 rounded-lg text-left transition-all duration-200
                    ${selectedGuild === guild.id
                      ? 'bg-osu-gradient text-white'
                      : 'bg-osu-darker text-gray-300 hover:bg-osu-border'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-osu-card rounded-lg flex items-center justify-center">
                      {guild.icon ? (
                        <img 
                          src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`}
                          alt={guild.name}
                          className="w-full h-full rounded-lg"
                        />
                      ) : (
                        <Server className="w-4 h-4" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">{guild.name}</p>
                      <p className="text-sm opacity-70">{guild.member_count}人</p>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </Card>

          {/* Mode Selection */}
          <div className="lg:col-span-3">
            <Card delay={0.2}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <Bot className="w-5 h-5 text-osu-cyan" />
                  AIモード選択
                </h2>
                {aiMode && (
                  <div className="text-sm text-gray-400">
                    現在: <span className="text-white font-medium">{aiMode.current_mode}</span>
                  </div>
                )}
              </div>

              {aiMode && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(aiMode.available_modes).map(([mode, description], index) => {
                    const Icon = modeIcons[mode as keyof typeof modeIcons] || Bot
                    const isActive = aiMode.current_mode === mode
                    
                    return (
                      <motion.div
                        key={mode}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        className={`
                          p-6 rounded-xl border-2 transition-all duration-300 cursor-pointer
                          ${isActive
                            ? 'border-osu-pink bg-osu-pink/10'
                            : 'border-osu-border bg-osu-darker hover:border-osu-pink/50'
                          }
                        `}
                        onClick={() => !updating && changeMode(mode)}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className={`p-3 rounded-xl ${modeBgColors[mode as keyof typeof modeBgColors] || 'bg-gray-500/20'}`}>
                            <Icon className={`w-6 h-6 ${modeColors[mode as keyof typeof modeColors] || 'text-gray-500'}`} />
                          </div>
                          
                          {isActive && (
                            <CheckCircle className="w-5 h-5 text-osu-pink" />
                          )}
                        </div>
                        
                        <h3 className="text-lg font-semibold text-white mb-2 capitalize">
                          {mode}モード
                        </h3>
                        
                        <p className="text-gray-400 text-sm leading-relaxed">
                          {description}
                        </p>
                        
                        {updating && isActive && (
                          <div className="mt-4 flex items-center gap-2 text-osu-pink">
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span className="text-sm">更新中...</span>
                          </div>
                        )}
                      </motion.div>
                    )
                  })}
                </div>
              )}

              {!aiMode && (
                <div className="text-center py-8 text-gray-400">
                  <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>AIモード情報を読み込み中...</p>
                </div>
              )}
            </Card>
          </div>
        </div>

        {/* Mode Details */}
        {aiMode && (
          <Card delay={0.3} className="mt-8">
            <h2 className="text-xl font-semibold text-white mb-4">モード詳細</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="p-4 bg-osu-pink/20 rounded-xl mb-3 inline-block">
                  <Zap className="w-6 h-6 text-osu-pink" />
                </div>
                <h3 className="font-semibold text-white mb-2">Standard</h3>
                <p className="text-gray-400 text-sm">バランスの取れた汎用的な応答</p>
              </div>
              
              <div className="text-center">
                <div className="p-4 bg-osu-purple/20 rounded-xl mb-3 inline-block">
                  <Palette className="w-6 h-6 text-osu-purple" />
                </div>
                <h3 className="font-semibold text-white mb-2">Creative</h3>
                <p className="text-gray-400 text-sm">創造性を重視した応答</p>
              </div>
              
              <div className="text-center">
                <div className="p-4 bg-osu-cyan/20 rounded-xl mb-3 inline-block">
                  <Code className="w-6 h-6 text-osu-cyan" />
                </div>
                <h3 className="font-semibold text-white mb-2">Coder</h3>
                <p className="text-gray-400 text-sm">プログラミング専門の技術的応答</p>
              </div>
              
              <div className="text-center">
                <div className="p-4 bg-green-500/20 rounded-xl mb-3 inline-block">
                  <Briefcase className="w-6 h-6 text-green-500" />
                </div>
                <h3 className="font-semibold text-white mb-2">Assistant</h3>
                <p className="text-gray-400 text-sm">フォーマルで生産性重視</p>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}