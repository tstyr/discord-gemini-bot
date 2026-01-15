'use client'

import { motion } from 'framer-motion'
import Card from '@/components/Card'
import NetworkStats from '@/components/NetworkStats'
import { Activity, Wifi, Server, Zap } from 'lucide-react'

export default function NetworkPage() {
  return (
    <div className="min-h-screen bg-osu-dark relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-0 right-1/3 w-96 h-96 bg-osu-cyan/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-osu-pink/5 rounded-full blur-3xl" />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-0.5 bg-gradient-to-r from-transparent via-osu-cyan/20 to-transparent -rotate-12" />

      <div className="relative z-10 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Activity className="w-8 h-8 text-osu-cyan" />
            ネットワーク監視
          </h1>
          <p className="text-gray-400">
            Botのリアルタイム通信状況とパフォーマンス監視
          </p>
        </motion.div>

        {/* Network Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card delay={0.1}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">接続状態</p>
                <p className="text-2xl font-bold text-green-500">オンライン</p>
                <p className="text-green-500 text-sm flex items-center gap-1 mt-1">
                  <Wifi className="w-3 h-3" />
                  安定接続
                </p>
              </div>
              <div className="p-3 bg-green-500/20 rounded-xl">
                <Wifi className="w-6 h-6 text-green-500" />
              </div>
            </div>
          </Card>

          <Card delay={0.2}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">アクティブ接続</p>
                <p className="text-2xl font-bold text-osu-cyan">24</p>
                <p className="text-green-500 text-sm flex items-center gap-1 mt-1">
                  <Server className="w-3 h-3" />
                  +3 今日
                </p>
              </div>
              <div className="p-3 bg-osu-cyan/20 rounded-xl">
                <Server className="w-6 h-6 text-osu-cyan" />
              </div>
            </div>
          </Card>

          <Card delay={0.3}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">平均レイテンシ</p>
                <p className="text-2xl font-bold text-osu-purple">28ms</p>
                <p className="text-green-500 text-sm flex items-center gap-1 mt-1">
                  <Zap className="w-3 h-3" />
                  -5ms 改善
                </p>
              </div>
              <div className="p-3 bg-osu-purple/20 rounded-xl">
                <Zap className="w-6 h-6 text-osu-purple" />
              </div>
            </div>
          </Card>
        </div>

        {/* Real-time Network Monitoring */}
        <Card delay={0.4}>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-osu-cyan" />
              リアルタイム通信監視
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              ネットワークトラフィックとパフォーマンスメトリクス
            </p>
          </div>

          <NetworkStats maxDataPoints={60} updateInterval={1000} />
        </Card>

        {/* System Information */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          <Card delay={0.5}>
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Server className="w-5 h-5 text-osu-pink" />
              システム情報
            </h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">Bot バージョン</span>
                <span className="text-white font-semibold">v2.1.0</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">Python バージョン</span>
                <span className="text-white font-semibold">3.11.5</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">discord.py</span>
                <span className="text-white font-semibold">2.3.2</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">稼働時間</span>
                <span className="text-white font-semibold">2日 14時間</span>
              </div>
            </div>
          </Card>

          <Card delay={0.6}>
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-osu-purple" />
              パフォーマンス
            </h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">CPU使用率</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-osu-border rounded-full overflow-hidden">
                    <div className="w-1/4 h-full bg-osu-cyan rounded-full"></div>
                  </div>
                  <span className="text-white font-semibold">25%</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">メモリ使用量</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-osu-border rounded-full overflow-hidden">
                    <div className="w-2/5 h-full bg-osu-pink rounded-full"></div>
                  </div>
                  <span className="text-white font-semibold">156MB</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">ディスク使用量</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-osu-border rounded-full overflow-hidden">
                    <div className="w-1/5 h-full bg-osu-purple rounded-full"></div>
                  </div>
                  <span className="text-white font-semibold">2.1GB</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-osu-darker rounded-lg">
                <span className="text-gray-400">WebSocket接続</span>
                <span className="text-green-500 font-semibold">3 active</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}