'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import Card from '@/components/Card'
import AdvancedMusicPlayer from '@/components/AdvancedMusicPlayer'
import { apiClient, Guild } from '@/lib/api'
import { Music, Server, Headphones, Radio } from 'lucide-react'

export default function MusicPage() {
  const [guilds, setGuilds] = useState<Guild[]>([])
  const [selectedGuild, setSelectedGuild] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchGuilds()
  }, [])

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
      <div className="absolute top-0 right-1/3 w-96 h-96 bg-osu-pink/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-osu-cyan/5 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-0.5 bg-gradient-to-r from-transparent via-osu-purple/20 to-transparent -rotate-12" />

      <div className="relative z-10 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Music className="w-8 h-8 text-osu-pink" />
            音楽プレイヤー
          </h1>
          <p className="text-gray-400">
            osu!lazer風のモダンな音楽プレイヤー - AI選曲とリアルタイム制御
          </p>
        </motion.div>

        {/* Guild Selector */}
        <Card delay={0.1} className="mb-8">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Server className="w-5 h-5 text-osu-cyan" />
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

        {/* Music Player */}
        {selectedGuild && (
          <Card delay={0.2}>
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Headphones className="w-5 h-5 text-osu-pink" />
                音楽コントロール
              </h2>
              <p className="text-gray-400 text-sm mt-1">
                Discord の音楽再生をWebから制御できます
              </p>
            </div>

            <AdvancedMusicPlayer guildId={selectedGuild} />
          </Card>
        )}

        {/* Music Commands Guide */}
        <Card delay={0.3} className="mt-8">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <Radio className="w-5 h-5 text-osu-purple" />
            音楽コマンドガイド
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-white font-medium">基本コマンド</h3>
              <div className="space-y-3">
                {[
                  { command: '/play [曲名/URL]', description: '音楽を検索して再生' },
                  { command: '/skip', description: '現在の曲をスキップ' },
                  { command: '/stop', description: '再生を停止して切断' },
                  { command: '/queue', description: '再生キューを表示' }
                ].map((cmd, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-osu-darker rounded-lg">
                    <code className="text-osu-pink font-mono text-sm bg-osu-card px-2 py-1 rounded">
                      {cmd.command}
                    </code>
                    <span className="text-gray-400 text-sm">{cmd.description}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-white font-medium">AI機能</h3>
              <div className="space-y-3">
                {[
                  { command: '/recommend', description: '会話の流れからAIが選曲' },
                  { command: '「リラックスできる曲流して」', description: '自然言語での音楽リクエスト' },
                  { command: '「作業用BGM、ジャズ系で」', description: 'ジャンル指定での選曲' },
                  { command: '「盛り上がる曲ない？」', description: 'ムード指定での推薦' }
                ].map((cmd, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-osu-darker rounded-lg">
                    <code className="text-osu-cyan font-mono text-sm bg-osu-card px-2 py-1 rounded">
                      {cmd.command}
                    </code>
                    <span className="text-gray-400 text-sm">{cmd.description}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* Features */}
        <Card delay={0.4} className="mt-8">
          <h2 className="text-xl font-semibold text-white mb-4">音楽機能の特徴</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="p-4 bg-osu-pink/20 rounded-xl mb-3 inline-block">
                <Music className="w-6 h-6 text-osu-pink" />
              </div>
              <h3 className="font-semibold text-white mb-2">AI選曲システム</h3>
              <p className="text-gray-400 text-sm">Gemini AIが会話の文脈を読み取って最適な音楽を選曲</p>
            </div>
            
            <div className="text-center">
              <div className="p-4 bg-osu-cyan/20 rounded-xl mb-3 inline-block">
                <Headphones className="w-6 h-6 text-osu-cyan" />
              </div>
              <h3 className="font-semibold text-white mb-2">ハイブリッド再生</h3>
              <p className="text-gray-400 text-sm">Discord VCと高音質Web再生を自由に選択可能</p>
            </div>
            
            <div className="text-center">
              <div className="p-4 bg-osu-purple/20 rounded-xl mb-3 inline-block">
                <Radio className="w-6 h-6 text-osu-purple" />
              </div>
              <h3 className="font-semibold text-white mb-2">リアルタイム制御</h3>
              <p className="text-gray-400 text-sm">WebダッシュボードからDiscordの音楽を直接制御</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}