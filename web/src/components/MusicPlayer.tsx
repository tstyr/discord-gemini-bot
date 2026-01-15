'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useRef } from 'react'
import { 
  Play, 
  Pause, 
  SkipForward, 
  Volume2, 
  Shuffle, 
  Repeat,
  Music,
  Clock,
  User,
  List,
  Disc3
} from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Track {
  title: string
  author: string
  length: number
  position?: number
  artwork?: string
  uri: string
}

interface MusicStatus {
  playing: boolean
  connected: boolean
  paused: boolean
  volume: number
  current_track?: Track
  queue: Track[]
  loop_mode: string
}

interface MusicPlayerProps {
  guildId: string
}

export default function MusicPlayer({ guildId }: MusicPlayerProps) {
  const [musicStatus, setMusicStatus] = useState<MusicStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [showQueue, setShowQueue] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()

  useEffect(() => {
    fetchMusicStatus()
    
    // Set up real-time updates
    const interval = setInterval(fetchMusicStatus, 2000)
    
    // Start audio visualizer
    startVisualizer()
    
    return () => {
      clearInterval(interval)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [guildId])

  const fetchMusicStatus = async () => {
    try {
      const response = await apiClient.getMusicStatus(guildId)
      if (response.success && response.data) {
        setMusicStatus(response.data)
      }
    } catch (error) {
      console.error('Failed to fetch music status:', error)
    } finally {
      setLoading(false)
    }
  }

  const controlMusic = async (action: string) => {
    try {
      await apiClient.controlMusic(guildId, action)
      // Refresh status after control
      setTimeout(fetchMusicStatus, 500)
    } catch (error) {
      console.error('Failed to control music:', error)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const startVisualizer = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const draw = () => {
      const width = canvas.width
      const height = canvas.height
      
      ctx.clearRect(0, 0, width, height)
      
      // Create gradient
      const gradient = ctx.createLinearGradient(0, 0, width, 0)
      gradient.addColorStop(0, '#ff66aa')
      gradient.addColorStop(0.5, '#00ffcc')
      gradient.addColorStop(1, '#aa66ff')
      
      ctx.fillStyle = gradient
      
      // Draw animated bars
      const barCount = 32
      const barWidth = width / barCount
      const time = Date.now() * 0.005
      
      for (let i = 0; i < barCount; i++) {
        const barHeight = (Math.sin(time + i * 0.5) * 0.5 + 0.5) * height * 0.8
        const x = i * barWidth
        const y = height - barHeight
        
        ctx.fillRect(x, y, barWidth - 2, barHeight)
      }
      
      animationRef.current = requestAnimationFrame(draw)
    }
    
    draw()
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

  if (!musicStatus?.connected) {
    return (
      <div className="text-center py-12">
        <Music className="w-16 h-16 mx-auto mb-4 text-gray-500" />
        <p className="text-gray-400">音楽プレイヤーは接続されていません</p>
        <p className="text-gray-500 text-sm mt-2">Discord で `/play` コマンドを使用してください</p>
      </div>
    )
  }

  const currentTrack = musicStatus.current_track

  return (
    <div className="space-y-6">
      {/* Current Track Display */}
      <AnimatePresence>
        {currentTrack && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative overflow-hidden rounded-2xl bg-osu-card border border-osu-border"
          >
            {/* Background Artwork */}
            {currentTrack.artwork && (
              <div 
                className="absolute inset-0 bg-cover bg-center opacity-20 blur-sm scale-110"
                style={{ backgroundImage: `url(${currentTrack.artwork})` }}
              />
            )}
            
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-osu-pink/20 via-transparent to-osu-cyan/20" />
            
            <div className="relative p-8">
              <div className="flex items-center gap-6">
                {/* Album Art */}
                <motion.div
                  animate={{ rotate: musicStatus.playing && !musicStatus.paused ? 360 : 0 }}
                  transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                  className="flex-shrink-0"
                >
                  <div className="w-24 h-24 rounded-xl overflow-hidden bg-osu-darker border-2 border-osu-pink/50 flex items-center justify-center">
                    {currentTrack.artwork ? (
                      <img 
                        src={currentTrack.artwork}
                        alt={currentTrack.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Disc3 className="w-12 h-12 text-osu-pink" />
                    )}
                  </div>
                </motion.div>

                {/* Track Info */}
                <div className="flex-1 min-w-0">
                  <h2 className="text-2xl font-bold text-white mb-2 truncate">
                    {currentTrack.title}
                  </h2>
                  <div className="flex items-center gap-4 text-gray-400 mb-4">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      <span className="truncate">{currentTrack.author}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>{formatTime(currentTrack.length)}</span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-400">
                      <span>{formatTime(currentTrack.position || 0)}</span>
                      <span>{formatTime(currentTrack.length)}</span>
                    </div>
                    <div className="w-full h-2 bg-osu-darker rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-osu-gradient rounded-full"
                        initial={{ width: 0 }}
                        animate={{ 
                          width: `${((currentTrack.position || 0) / currentTrack.length) * 100}%` 
                        }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Audio Visualizer */}
      <div className="bg-osu-card border border-osu-border rounded-xl p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Volume2 className="w-5 h-5 text-osu-cyan" />
          オーディオビジュアライザー
        </h3>
        <canvas
          ref={canvasRef}
          width={800}
          height={120}
          className="w-full h-24 rounded-lg bg-osu-darker"
        />
      </div>

      {/* Controls */}
      <div className="bg-osu-card border border-osu-border rounded-xl p-6">
        <div className="flex items-center justify-center gap-4">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="p-3 bg-osu-purple/20 text-osu-purple rounded-full hover:bg-osu-purple/30 transition-colors duration-200"
          >
            <Shuffle className="w-5 h-5" />
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => controlMusic('skip')}
            className="p-4 bg-osu-cyan/20 text-osu-cyan rounded-full hover:bg-osu-cyan/30 transition-colors duration-200"
          >
            <SkipForward className="w-6 h-6" />
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => controlMusic(musicStatus.paused ? 'resume' : 'pause')}
            className="p-6 bg-osu-gradient rounded-full shadow-lg hover:shadow-xl transition-shadow duration-200"
          >
            {musicStatus.paused ? (
              <Play className="w-8 h-8 text-white ml-1" />
            ) : (
              <Pause className="w-8 h-8 text-white" />
            )}
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => controlMusic('stop')}
            className="p-4 bg-red-500/20 text-red-500 rounded-full hover:bg-red-500/30 transition-colors duration-200"
          >
            <SkipForward className="w-6 h-6" />
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="p-3 bg-osu-pink/20 text-osu-pink rounded-full hover:bg-osu-pink/30 transition-colors duration-200"
          >
            <Repeat className="w-5 h-5" />
          </motion.button>
        </div>
      </div>

      {/* Queue */}
      <div className="bg-osu-card border border-osu-border rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <List className="w-5 h-5 text-osu-pink" />
            再生キュー
          </h3>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowQueue(!showQueue)}
            className="text-gray-400 hover:text-white transition-colors duration-200"
          >
            {showQueue ? '隠す' : '表示'}
          </motion.button>
        </div>

        <AnimatePresence>
          {showQueue && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              {musicStatus.queue.length > 0 ? (
                musicStatus.queue.map((track, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center gap-3 p-3 bg-osu-darker rounded-lg hover:bg-osu-border transition-colors duration-200"
                  >
                    <div className="w-8 h-8 bg-osu-gradient rounded-lg flex items-center justify-center text-white font-bold text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-medium truncate">{track.title}</p>
                      <p className="text-gray-400 text-sm truncate">{track.author}</p>
                    </div>
                    <div className="text-gray-400 text-sm">
                      {formatTime(track.length)}
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <List className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>キューは空です</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}