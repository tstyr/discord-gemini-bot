'use client'

import { motion } from 'framer-motion'
import { useState, useEffect, useRef } from 'react'
import { 
  Activity, 
  Wifi, 
  WifiOff, 
  ArrowUp, 
  ArrowDown,
  Zap,
  Server
} from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Area,
  AreaChart
} from 'recharts'

interface NetworkData {
  timestamp: string
  rx_bytes: number
  tx_bytes: number
  rx_packets: number
  tx_packets: number
  latency: number
  connected_users: number
}

interface NetworkStatsProps {
  maxDataPoints?: number
  updateInterval?: number
}

export default function NetworkStats({ maxDataPoints = 50, updateInterval = 1000 }: NetworkStatsProps) {
  const [networkData, setNetworkData] = useState<NetworkData[]>([])
  const [isConnected, setIsConnected] = useState(true)
  const [currentStats, setCurrentStats] = useState({
    rx_rate: 0,
    tx_rate: 0,
    total_rx: 0,
    total_tx: 0,
    latency: 0,
    connected_users: 0
  })
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const lastDataRef = useRef<NetworkData | null>(null)

  useEffect(() => {
    // Start real-time monitoring
    startMonitoring()
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [updateInterval])

  const startMonitoring = () => {
    intervalRef.current = setInterval(async () => {
      try {
        // Simulate network data (replace with actual API call)
        const newData = await fetchNetworkData()
        
        setNetworkData((prev: NetworkData[]) => {
          const updated = [...prev, newData]
          return updated.slice(-maxDataPoints)
        })

        // Calculate rates
        if (lastDataRef.current) {
          const timeDiff = (new Date(newData.timestamp).getTime() - new Date(lastDataRef.current.timestamp).getTime()) / 1000
          const rxRate = (newData.rx_bytes - lastDataRef.current.rx_bytes) / timeDiff
          const txRate = (newData.tx_bytes - lastDataRef.current.tx_bytes) / timeDiff
          
          setCurrentStats({
            rx_rate: rxRate,
            tx_rate: txRate,
            total_rx: newData.rx_bytes,
            total_tx: newData.tx_bytes,
            latency: newData.latency,
            connected_users: newData.connected_users
          })
        }
        
        lastDataRef.current = newData
        setIsConnected(true)
      } catch (error) {
        console.error('Network monitoring error:', error)
        setIsConnected(false)
      }
    }, updateInterval)
  }

  const fetchNetworkData = async (): Promise<NetworkData> => {
    // Mock data - replace with actual API call to bot
    const now = new Date()
    const baseRx = Math.random() * 1000 + 500
    const baseTx = Math.random() * 800 + 300
    
    return {
      timestamp: now.toISOString(),
      rx_bytes: (lastDataRef.current?.rx_bytes || 0) + baseRx,
      tx_bytes: (lastDataRef.current?.tx_bytes || 0) + baseTx,
      rx_packets: (lastDataRef.current?.rx_packets || 0) + Math.floor(Math.random() * 10 + 5),
      tx_packets: (lastDataRef.current?.tx_packets || 0) + Math.floor(Math.random() * 8 + 3),
      latency: Math.random() * 50 + 10,
      connected_users: Math.floor(Math.random() * 5 + 15)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const formatRate = (bytesPerSecond: number) => {
    return formatBytes(bytesPerSecond) + '/s'
  }

  // Prepare chart data
  const chartData = networkData.map((data: NetworkData, index: number) => ({
    time: new Date(data.timestamp).toLocaleTimeString('ja-JP', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    }),
    rx: data.rx_bytes / 1024, // Convert to KB
    tx: data.tx_bytes / 1024,
    latency: data.latency
  }))

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <motion.div
            animate={{ 
              scale: isConnected ? [1, 1.2, 1] : 1,
              rotate: isConnected ? 0 : 180
            }}
            transition={{ 
              scale: { duration: 2, repeat: Infinity },
              rotate: { duration: 0.5 }
            }}
            className={`p-2 rounded-lg ${isConnected ? 'bg-green-500/20' : 'bg-red-500/20'}`}
          >
            {isConnected ? (
              <Wifi className="w-5 h-5 text-green-500" />
            ) : (
              <WifiOff className="w-5 h-5 text-red-500" />
            )}
          </motion.div>
          <div>
            <h3 className="text-white font-semibold">ネットワーク状態</h3>
            <p className={`text-sm ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
              {isConnected ? 'オンライン' : 'オフライン'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <div className="flex items-center gap-1">
            <Server className="w-4 h-4" />
            <span>{currentStats.connected_users} users</span>
          </div>
          <div className="flex items-center gap-1">
            <Activity className="w-4 h-4" />
            <span>{currentStats.latency.toFixed(0)}ms</span>
          </div>
        </div>
      </div>

      {/* Real-time Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-osu-card/50 backdrop-blur-md border border-osu-border rounded-lg p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <ArrowDown className="w-4 h-4 text-osu-cyan" />
            <span className="text-gray-400 text-sm">受信</span>
          </div>
          <div className="text-xl font-bold text-osu-cyan">
            {formatRate(currentStats.rx_rate)}
          </div>
          <div className="text-xs text-gray-500">
            総計: {formatBytes(currentStats.total_rx)}
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-osu-card/50 backdrop-blur-md border border-osu-border rounded-lg p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <ArrowUp className="w-4 h-4 text-osu-pink" />
            <span className="text-gray-400 text-sm">送信</span>
          </div>
          <div className="text-xl font-bold text-osu-pink">
            {formatRate(currentStats.tx_rate)}
          </div>
          <div className="text-xs text-gray-500">
            総計: {formatBytes(currentStats.total_tx)}
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-osu-card/50 backdrop-blur-md border border-osu-border rounded-lg p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-osu-purple" />
            <span className="text-gray-400 text-sm">レイテンシ</span>
          </div>
          <div className="text-xl font-bold text-osu-purple">
            {currentStats.latency.toFixed(0)}ms
          </div>
          <div className="text-xs text-gray-500">
            平均応答時間
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-osu-card/50 backdrop-blur-md border border-osu-border rounded-lg p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <Server className="w-4 h-4 text-green-500" />
            <span className="text-gray-400 text-sm">接続数</span>
          </div>
          <div className="text-xl font-bold text-green-500">
            {currentStats.connected_users}
          </div>
          <div className="text-xs text-gray-500">
            アクティブユーザー
          </div>
        </motion.div>
      </div>

      {/* Network Traffic Chart */}
      <div className="bg-osu-card/30 backdrop-blur-md border border-osu-border rounded-xl p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-osu-cyan" />
          ネットワークトラフィック
        </h3>
        
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="rxGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00ffcc" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#00ffcc" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="txGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ff66aa" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ff66aa" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis 
                dataKey="time" 
                stroke="#666" 
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                stroke="#666" 
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value: number) => `${value}KB`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1a1a', 
                  border: '1px solid #333',
                  borderRadius: '8px',
                  backdropFilter: 'blur(10px)'
                }}
                labelStyle={{ color: '#fff' }}
              />
              <Area
                type="monotone"
                dataKey="rx"
                stroke="#00ffcc"
                strokeWidth={2}
                fill="url(#rxGradient)"
                name="受信 (KB)"
              />
              <Area
                type="monotone"
                dataKey="tx"
                stroke="#ff66aa"
                strokeWidth={2}
                fill="url(#txGradient)"
                name="送信 (KB)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Latency Chart */}
      <div className="bg-osu-card/30 backdrop-blur-md border border-osu-border rounded-xl p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-osu-purple" />
          レイテンシ監視
        </h3>
        
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis 
                dataKey="time" 
                stroke="#666" 
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                stroke="#666" 
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value: number) => `${value}ms`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a1a1a', 
                  border: '1px solid #333',
                  borderRadius: '8px',
                  backdropFilter: 'blur(10px)'
                }}
                labelStyle={{ color: '#fff' }}
              />
              <Line
                type="monotone"
                dataKey="latency"
                stroke="#aa66ff"
                strokeWidth={3}
                dot={false}
                name="レイテンシ (ms)"
                filter="drop-shadow(0 0 6px #aa66ff)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}