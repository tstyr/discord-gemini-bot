'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useRef, useCallback } from 'react'
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
  Disc3,
  Headphones,
  Radio,
  Settings,
  Maximize2,
  Eye,
  EyeOff,
  Sliders
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import io from 'socket.io-client'

interface Track {
  title: string
  author: string
  length: number
  position?: number
  artwork?: string
  uri: string
  stream_url?: string
  lyrics?: string[]
}

interface MusicStatus {
  playing: boolean
  connected: boolean
  paused: boolean
  volume: number
  current_track?: Track
  queue: Track[]
  loop_mode: string
  playback_mode: 'discord' | 'web'
}

interface AdvancedMusicPlayerProps {
  guildId: string
}

export default function AdvancedMusicPlayer({ guildId }: AdvancedMusicPlayerProps) {
  const [musicStatus, setMusicStatus] = useState<MusicStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [showQueue, setShowQueue] = useState(false)
  const [showLyrics, setShowLyrics] = useState(false)
  const [showVisualizer, setShowVisualizer] = useState(true)
  const [playbackMode, setPlaybackMode] = useState<'discord' | 'web'>('discord')
  const [webAudioPlaying, setWebAudioPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [volume, setVolume] = useState(0.8)
  
  // Audio context and analysis
  const audioRef = useRef<HTMLAudioElement>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const spectrumCanvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const socketRef = useRef<any>(null)

  // EQ settings
  const [eqSettings, setEqSettings] = useState({
    bass: 0,
    mid: 0,
    treble: 0,
    presence: 0
  })

  useEffect(() => {
    initializeSocket()
    fetchMusicStatus()
    initializeWebAudio()
    
    const interval = setInterval(fetchMusicStatus, 2000)
    
    return () => {
      clearInterval(interval)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [guildId])

  const initializeSocket = () => {
    socketRef.current = io('http://localhost:8000')
    
    socketRef.current.on('music_event', (data: any) => {
      if (data.guild_id === guildId) {
        handleMusicEvent(data)
      }
    })
    
    socketRef.current.on('sync_playback', (data: any) => {
      if (data.guild_id === guildId && playbackMode === 'web') {
        syncWebPlayback(data)
      }
    })
  }

  const initializeWebAudio = () => {
    if (typeof window !== 'undefined') {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
      
      if (audioRef.current && audioContextRef.current) {
        const source = audioContextRef.current.createMediaElementSource(audioRef.current)
        analyserRef.current = audioContextRef.current.createAnalyser()
        const gainNode = audioContextRef.current.createGain()
        
        // Create EQ filters
        const bassFilter = audioContextRef.current.createBiquadFilter()
        const midFilter = audioContextRef.current.createBiquadFilter()
        const trebleFilter = audioContextRef.current.createBiquadFilter()
        
        bassFilter.type = 'lowshelf'
        bassFilter.frequency.value = 320
        midFilter.type = 'peaking'
        midFilter.frequency.value = 1000
        trebleFilter.type = 'highshelf'
        trebleFilter.frequency.value = 3200
        
        // Connect audio graph
        source.connect(bassFilter)
        bassFilter.connect(midFilter)
        midFilter.connect(trebleFilter)
        trebleFilter.connect(gainNode)
        gainNode.connect(analyserRef.current)
        analyserRef.current.connect(audioContextRef.current.destination)
        
        analyserRef.current.fftSize = 2048
        startVisualizer()
      }
    }
  }

  const fetchMusicStatus = async () => {
    try {
      const response = await apiClient.getMusicStatus(guildId)
      if (response.success && response.data) {
        setMusicStatus(response.data)
        setPlaybackMode(response.data.playback_mode || 'discord')
      }
    } catch (error) {
      console.error('Failed to fetch music status:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMusicEvent = (data: any) => {
    switch (data.type) {
      case 'track_start':
        if (playbackMode === 'web' && data.track.stream_url) {
          playWebAudio(data.track.stream_url)
        }
        break
      case 'track_pause':
        if (playbackMode === 'web' && audioRef.current) {
          audioRef.current.pause()
        }
        break
      case 'track_resume':
        if (playbackMode === 'web' && audioRef.current) {
          audioRef.current.play()
        }
        break
    }
  }

  const syncWebPlayback = (data: any) => {
    if (audioRef.current) {
      audioRef.current.currentTime = data.position
      if (data.playing && audioRef.current.paused) {
        audioRef.current.play()
      } else if (!data.playing && !audioRef.current.paused) {
        audioRef.current.pause()
      }
    }
  }

  const playWebAudio = async (streamUrl: string) => {
    if (audioRef.current && audioContextRef.current) {
      try {
        if (audioContextRef.current.state === 'suspended') {
          await audioContextRef.current.resume()
        }
        
        audioRef.current.src = streamUrl
        audioRef.current.volume = volume
        await audioRef.current.play()
        setWebAudioPlaying(true)
      } catch (error) {
        console.error('Error playing web audio:', error)
      }
    }
  }

  const togglePlaybackMode = async () => {
    const newMode = playbackMode === 'discord' ? 'web' : 'discord'
    setPlaybackMode(newMode)
    
    try {
      await apiClient.setPlaybackMode(guildId, newMode)
      
      if (newMode === 'web' && musicStatus?.current_track) {
        // Request high-quality stream URL
        const streamResponse = await apiClient.getStreamUrl(musicStatus.current_track.uri)
        if (streamResponse.success && streamResponse.data.stream_url) {
          await playWebAudio(streamResponse.data.stream_url)
        }
      } else if (newMode === 'discord' && audioRef.current) {
        audioRef.current.pause()
        setWebAudioPlaying(false)
      }
    } catch (error) {
      console.error('Error switching playback mode:', error)
    }
  }

  const controlMusic = async (action: string) => {
    try {
      if (playbackMode === 'web' && audioRef.current) {
        // Handle web audio controls
        switch (action) {
          case 'pause':
            audioRef.current.pause()
            setWebAudioPlaying(false)
            break
          case 'resume':
            await audioRef.current.play()
            setWebAudioPlaying(true)
            break
          case 'skip':
            // Request next track
            await apiClient.controlMusic(guildId, 'skip')
            break
        }
      } else {
        // Handle Discord controls
        await apiClient.controlMusic(guildId, action)
      }
      
      // Broadcast to other clients
      if (socketRef.current) {
        socketRef.current.emit('music_control', {
          guild_id: guildId,
          action,
          mode: playbackMode,
          position: audioRef.current?.currentTime || 0
        })
      }
      
      setTimeout(fetchMusicStatus, 500)
    } catch (error) {
      console.error('Failed to control music:', error)
    }
  }

  const applyEQ = (settings: typeof eqSettings) => {
    // Apply EQ settings to Web Audio API filters
    // This would be implemented with the filter nodes created in initializeWebAudio
    setEqSettings(settings)
  }

  const getAIEQSettings = async (genre: string) => {
    try {
      const response = await apiClient.getAIEQSettings(genre)
      if (response.success && response.data) {
        applyEQ(response.data)
      }
    } catch (error) {
      console.error('Error getting AI EQ settings:', error)
    }
  }

  const startVisualizer = () => {
    const drawVisualizer = () => {
      if (!canvasRef.current || !analyserRef.current) return
      
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      
      const bufferLength = analyserRef.current.frequencyBinCount
      const dataArray = new Uint8Array(bufferLength)
      analyserRef.current.getByteFrequencyData(dataArray)
      
      const width = canvas.width
      const height = canvas.height
      
      ctx.clearRect(0, 0, width, height)
      
      // Circular visualizer (osu! style)
      const centerX = width / 2
      const centerY = height / 2
      const radius = Math.min(width, height) / 4
      
      ctx.strokeStyle = '#ff66aa'
      ctx.lineWidth = 2
      
      for (let i = 0; i < bufferLength; i++) {
        const angle = (i / bufferLength) * Math.PI * 2
        const amplitude = dataArray[i] / 255
        const x1 = centerX + Math.cos(angle) * radius
        const y1 = centerY + Math.sin(angle) * radius
        const x2 = centerX + Math.cos(angle) * (radius + amplitude * 50)
        const y2 = centerY + Math.sin(angle) * (radius + amplitude * 50)
        
        const gradient = ctx.createLinearGradient(x1, y1, x2, y2)
        gradient.addColorStop(0, '#ff66aa')
        gradient.addColorStop(1, '#00ffcc')
        
        ctx.strokeStyle = gradient
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()
      }
      
      animationRef.current = requestAnimationFrame(drawVisualizer)
    }
    
    drawVisualizer()
  }

  const drawSpectrum = () => {
    if (!spectrumCanvasRef.current || !analyserRef.current) return
    
    const canvas = spectrumCanvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    const bufferLength = analyserRef.current.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    analyserRef.current.getByteFrequencyData(dataArray)
    
    const width = canvas.width
    const height = canvas.height
    const barWidth = width / bufferLength
    
    ctx.clearRect(0, 0, width, height)
    
    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * height
      const x = i * barWidth
      const y = height - barHeight
      
      const gradient = ctx.createLinearGradient(0, height, 0, 0)
      gradient.addColorStop(0, '#ff66aa')
      gradient.addColorStop(0.5, '#00ffcc')
      gradient.addColorStop(1, '#aa66ff')
      
      ctx.fillStyle = gradient
      ctx.fillRect(x, y, barWidth - 1, barHeight)
    }
  }

  useEffect(() => {
    if (showVisualizer && analyserRef.current) {
      const interval = setInterval(drawSpectrum, 50)
      return () => clearInterval(interval)
    }
  }, [showVisualizer])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const extractMainColor = (imageUrl: string): Promise<string> => {
    return new Promise((resolve) => {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          resolve('#ff66aa')
          return
        }
        
        canvas.width = img.width
        canvas.height = img.height
        ctx.drawImage(img, 0, 0)
        
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        const data = imageData.data
        
        let r = 0, g = 0, b = 0
        for (let i = 0; i < data.length; i += 4) {
          r += data[i]
          g += data[i + 1]
          b += data[i + 2]
        }
        
        const pixelCount = data.length / 4
        r = Math.floor(r / pixelCount)
        g = Math.floor(g / pixelCount)
        b = Math.floor(b / pixelCount)
        
        resolve(`rgb(${r}, ${g}, ${b})`)
      }
      img.onerror = () => resolve('#ff66aa')
      img.src = imageUrl
    })
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

  const currentTrack = musicStatus?.current_track

  return (
    <div className="space-y-6">
      {/* Hidden audio element for web playback */}
      <audio
        ref={audioRef}
        onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
        onEnded={() => setWebAudioPlaying(false)}
        crossOrigin="anonymous"
      />

      {/* Playback Mode Toggle */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-center gap-4 p-4 bg-osu-card border border-osu-border rounded-xl"
      >
        <div className="flex items-center gap-2">
          <Radio className="w-5 h-5 text-gray-400" />
          <span className="text-gray-400">再生モード:</span>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={togglePlaybackMode}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300 ${
            playbackMode === 'discord'
              ? 'bg-osu-purple/20 text-osu-purple border border-osu-purple/50'
              : 'bg-osu-cyan/20 text-osu-cyan border border-osu-cyan/50'
          }`}
        >
          {playbackMode === 'discord' ? (
            <>
              <Radio className="w-4 h-4" />
              <span>Discord VC (低遅延)</span>
            </>
          ) : (
            <>
              <Headphones className="w-4 h-4" />
              <span>Web Audio (高音質)</span>
            </>
          )}
        </motion.button>
        
        <div className="text-sm text-gray-500">
          {playbackMode === 'discord' ? '64-96kbps' : '256kbps AAC'}
        </div>
      </motion.div>

      {/* Enhanced Current Track Display */}
      <AnimatePresence>
        {currentTrack && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative overflow-hidden rounded-2xl bg-osu-card border border-osu-border"
          >
            {/* Dynamic Background */}
            {currentTrack.artwork && (
              <motion.div 
                className="absolute inset-0 bg-cover bg-center opacity-20 blur-sm scale-110"
                style={{ backgroundImage: `url(${currentTrack.artwork})` }}
                animate={{ 
                  filter: playbackMode === 'web' ? 'blur(8px) brightness(1.2)' : 'blur(8px) brightness(0.8)'
                }}
                transition={{ duration: 1 }}
              />
            )}
            
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-osu-pink/20 via-transparent to-osu-cyan/20" />
            
            <div className="relative p-8">
              <div className="flex items-center gap-6">
                {/* Enhanced Album Art */}
                <motion.div
                  animate={{ 
                    rotate: (playbackMode === 'web' ? webAudioPlaying : musicStatus.playing && !musicStatus.paused) ? 360 : 0,
                    scale: playbackMode === 'web' ? 1.1 : 1
                  }}
                  transition={{ 
                    rotate: { duration: 10, repeat: Infinity, ease: "linear" },
                    scale: { duration: 0.5 }
                  }}
                  className="flex-shrink-0"
                >
                  <div className={`w-32 h-32 rounded-xl overflow-hidden border-2 flex items-center justify-center ${
                    playbackMode === 'web' 
                      ? 'border-osu-cyan/70 shadow-lg shadow-osu-cyan/30' 
                      : 'border-osu-pink/50'
                  }`}>
                    {currentTrack.artwork ? (
                      <img 
                        src={currentTrack.artwork}
                        alt={currentTrack.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Disc3 className="w-16 h-16 text-osu-pink" />
                    )}
                  </div>
                </motion.div>

                {/* Enhanced Track Info */}
                <div className="flex-1 min-w-0">
                  <motion.h2 
                    className="text-3xl font-bold text-white mb-2 truncate"
                    animate={{ 
                      textShadow: playbackMode === 'web' ? '0 0 10px rgba(0, 255, 204, 0.5)' : 'none'
                    }}
                  >
                    {currentTrack.title}
                  </motion.h2>
                  <div className="flex items-center gap-4 text-gray-400 mb-4">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      <span className="truncate">{currentTrack.author}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>{formatTime(currentTrack.length)}</span>
                    </div>
                    {playbackMode === 'web' && (
                      <div className="flex items-center gap-2 text-osu-cyan">
                        <Headphones className="w-4 h-4" />
                        <span className="text-sm font-medium">高音質</span>
                      </div>
                    )}
                  </div>

                  {/* Enhanced Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-400">
                      <span>{formatTime(playbackMode === 'web' ? currentTime : (currentTrack.position || 0))}</span>
                      <span>{formatTime(currentTrack.length)}</span>
                    </div>
                    <div className="w-full h-3 bg-osu-darker rounded-full overflow-hidden">
                      <motion.div
                        className={`h-full rounded-full ${
                          playbackMode === 'web' 
                            ? 'bg-gradient-to-r from-osu-cyan to-osu-purple' 
                            : 'bg-osu-gradient'
                        }`}
                        initial={{ width: 0 }}
                        animate={{ 
                          width: `${((playbackMode === 'web' ? currentTime : (currentTrack.position || 0)) / currentTrack.length) * 100}%` 
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

      {/* Visualizer Controls */}
      <div className="flex items-center justify-center gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowVisualizer(!showVisualizer)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors duration-200 ${
            showVisualizer ? 'bg-osu-pink/20 text-osu-pink' : 'bg-gray-500/20 text-gray-500'
          }`}
        >
          {showVisualizer ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          ビジュアライザー
        </motion.button>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowLyrics(!showLyrics)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors duration-200 ${
            showLyrics ? 'bg-osu-cyan/20 text-osu-cyan' : 'bg-gray-500/20 text-gray-500'
          }`}
        >
          <Music className="w-4 h-4" />
          歌詞表示
        </motion.button>
      </div>

      {/* Enhanced Visualizer */}
      <AnimatePresence>
        {showVisualizer && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-osu-card border border-osu-border rounded-xl p-6"
          >
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Volume2 className="w-5 h-5 text-osu-cyan" />
              高解像度ビジュアライザー
            </h3>
            
            {/* Circular Visualizer */}
            <canvas
              ref={canvasRef}
              width={800}
              height={400}
              className="w-full h-48 rounded-lg bg-osu-darker mb-4"
            />
            
            {/* Spectrum Analyzer */}
            <h4 className="text-white font-medium mb-2">スペクトラムアナライザー</h4>
            <canvas
              ref={spectrumCanvasRef}
              width={800}
              height={100}
              className="w-full h-16 rounded-lg bg-osu-darker"
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Lyrics Display */}
      <AnimatePresence>
        {showLyrics && currentTrack?.lyrics && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-osu-card border border-osu-border rounded-xl p-6"
          >
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Music className="w-5 h-5 text-osu-pink" />
              歌詞 (AI推測)
            </h3>
            
            <div className="max-h-64 overflow-y-auto custom-scrollbar">
              {currentTrack.lyrics.map((line, index) => (
                <motion.p
                  key={index}
                  initial={{ opacity: 0.5 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-gray-300 leading-relaxed mb-2"
                >
                  {line}
                </motion.p>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Enhanced Controls */}
      <div className="bg-osu-card border border-osu-border rounded-xl p-6">
        <div className="flex items-center justify-center gap-4 mb-6">
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
            onClick={() => controlMusic((playbackMode === 'web' ? webAudioPlaying : !musicStatus?.paused) ? 'pause' : 'resume')}
            className={`p-6 rounded-full shadow-lg hover:shadow-xl transition-shadow duration-200 ${
              playbackMode === 'web' 
                ? 'bg-gradient-to-r from-osu-cyan to-osu-purple' 
                : 'bg-osu-gradient'
            }`}
          >
            {(playbackMode === 'web' ? webAudioPlaying : !musicStatus?.paused) ? (
              <Pause className="w-8 h-8 text-white" />
            ) : (
              <Play className="w-8 h-8 text-white ml-1" />
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

        {/* EQ Controls (Web mode only) */}
        {playbackMode === 'web' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="border-t border-osu-border pt-4"
          >
            <h4 className="text-white font-medium mb-4 flex items-center gap-2">
              <Sliders className="w-4 h-4" />
              イコライザー (高音質モード専用)
            </h4>
            
            <div className="grid grid-cols-4 gap-4">
              {Object.entries(eqSettings).map(([band, value]) => (
                <div key={band} className="text-center">
                  <label className="text-gray-400 text-sm capitalize">{band}</label>
                  <input
                    type="range"
                    min="-12"
                    max="12"
                    value={value}
                    onChange={(e) => setEqSettings(prev => ({ ...prev, [band]: parseInt(e.target.value) }))}
                    className="w-full mt-2"
                  />
                  <span className="text-white text-xs">{value}dB</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}