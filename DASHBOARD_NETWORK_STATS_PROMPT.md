# Webダッシュボード - ネットワーク統計ページ実装プロンプト

## 概要

Supabaseの`network_stats`テーブルからデータを取得し、リアルタイムでネットワーク統計を表示するページを実装します。

## 前提条件

- Next.js 14+ (App Router)
- Supabase Client
- Chart.js / Recharts
- TailwindCSS

## ファイル構成

```
web/
├── app/
│   ├── network/
│   │   └── page.tsx          # ネットワーク統計ページ
│   └── layout.tsx
├── components/
│   ├── NetworkChart.tsx      # ネットワークグラフコンポーネント
│   └── NetworkStats.tsx      # 統計カードコンポーネント
└── lib/
    └── supabase.ts           # Supabase client
```

## 実装

### 1. Supabase Client設定

#### `lib/supabase.ts`

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 型定義
export interface NetworkStat {
  id: string
  bytes_sent: number
  bytes_recv: number
  bytes_total: number
  mb_sent: number
  mb_recv: number
  mb_total: number
  recorded_at: string
  created_at: string
}

export interface SystemStat {
  id: string
  cpu_usage: number
  ram_usage: number
  memory_rss: number
  memory_heap: number
  ping_gateway: number
  ping_lavalink: number
  server_count: number
  guild_count: number
  uptime: number
  status: string
  recorded_at: string
  created_at: string
}
```

### 2. ネットワーク統計ページ

#### `app/network/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { supabase, NetworkStat } from '@/lib/supabase'
import NetworkChart from '@/components/NetworkChart'
import NetworkStats from '@/components/NetworkStats'

export default function NetworkPage() {
  const [stats, setStats] = useState<NetworkStat[]>([])
  const [totalSent, setTotalSent] = useState(0)
  const [totalRecv, setTotalRecv] = useState(0)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState<'1h' | '24h' | '7d' | '30d'>('24h')

  useEffect(() => {
    fetchStats()
    setupRealtime()
  }, [period])

  const fetchStats = async () => {
    setLoading(true)
    
    // 期間の計算
    const now = new Date()
    let startDate = new Date()
    
    switch (period) {
      case '1h':
        startDate.setHours(now.getHours() - 1)
        break
      case '24h':
        startDate.setDate(now.getDate() - 1)
        break
      case '7d':
        startDate.setDate(now.getDate() - 7)
        break
      case '30d':
        startDate.setDate(now.getDate() - 30)
        break
    }

    const { data, error } = await supabase
      .from('network_stats')
      .select('*')
      .gte('recorded_at', startDate.toISOString())
      .order('recorded_at', { ascending: true })

    if (data) {
      setStats(data)
      setTotalSent(data.reduce((sum, s) => sum + s.mb_sent, 0))
      setTotalRecv(data.reduce((sum, s) => sum + s.mb_recv, 0))
    }
    
    setLoading(false)
  }

  const setupRealtime = () => {
    const channel = supabase
      .channel('network_stats_changes')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'network_stats'
        },
        (payload) => {
          const newStat = payload.new as NetworkStat
          
          setStats(prev => {
            const updated = [...prev, newStat]
            // 期間に応じて古いデータを削除
            const limit = period === '1h' ? 360 : period === '24h' ? 8640 : 60480
            return updated.slice(-limit)
          })
          
          setTotalSent(prev => prev + newStat.mb_sent)
          setTotalRecv(prev => prev + newStat.mb_recv)
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }

  const formatBytes = (mb: number) => {
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(2)} GB`
    }
    return `${mb.toFixed(2)} MB`
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Network Statistics</h1>
          
          {/* 期間選択 */}
          <div className="flex gap-2">
            {(['1h', '24h', '7d', '30d'] as const).map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  period === p
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {p === '1h' ? '1 Hour' : p === '24h' ? '24 Hours' : p === '7d' ? '7 Days' : '30 Days'}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* 統計カード */}
            <NetworkStats
              totalSent={totalSent}
              totalRecv={totalRecv}
              dataPoints={stats.length}
            />

            {/* グラフ */}
            <div className="mt-8">
              <NetworkChart stats={stats} period={period} />
            </div>

            {/* 詳細テーブル */}
            <div className="mt-8 bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Sent
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Received
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stats.slice(-20).reverse().map((stat) => (
                      <tr key={stat.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(stat.recorded_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatBytes(stat.mb_sent)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatBytes(stat.mb_recv)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {formatBytes(stat.mb_total)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
```

### 3. 統計カードコンポーネント

#### `components/NetworkStats.tsx`

```typescript
interface NetworkStatsProps {
  totalSent: number
  totalRecv: number
  dataPoints: number
}

export default function NetworkStats({ totalSent, totalRecv, dataPoints }: NetworkStatsProps) {
  const formatBytes = (mb: number) => {
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(2)} GB`
    }
    return `${mb.toFixed(2)} MB`
  }

  const avgPer10s = dataPoints > 0 ? (totalSent + totalRecv) / dataPoints : 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0 bg-red-100 rounded-md p-3">
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11l5-5m0 0l5 5m-5-5v12" />
            </svg>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">Total Sent</dt>
              <dd className="text-2xl font-semibold text-gray-900">{formatBytes(totalSent)}</dd>
            </dl>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
            <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 13l-5 5m0 0l-5-5m5 5V6" />
            </svg>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">Total Received</dt>
              <dd className="text-2xl font-semibold text-gray-900">{formatBytes(totalRecv)}</dd>
            </dl>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
            <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">Total</dt>
              <dd className="text-2xl font-semibold text-gray-900">{formatBytes(totalSent + totalRecv)}</dd>
            </dl>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0 bg-purple-100 rounded-md p-3">
            <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">Avg/10s</dt>
              <dd className="text-2xl font-semibold text-gray-900">{formatBytes(avgPer10s)}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 4. ネットワークグラフコンポーネント

#### `components/NetworkChart.tsx`

```typescript
'use client'

import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { NetworkStat } from '@/lib/supabase'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface NetworkChartProps {
  stats: NetworkStat[]
  period: '1h' | '24h' | '7d' | '30d'
}

export default function NetworkChart({ stats, period }: NetworkChartProps) {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    if (period === '1h') {
      return date.toLocaleTimeString()
    } else if (period === '24h') {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
    }
  }

  const data = {
    labels: stats.map(s => formatTime(s.recorded_at)),
    datasets: [
      {
        label: 'Sent (MB)',
        data: stats.map(s => s.mb_sent),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Received (MB)',
        data: stats.map(s => s.mb_recv),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Network Traffic Over Time'
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'MB'
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div style={{ height: '400px' }}>
        <Line data={data} options={options} />
      </div>
    </div>
  )
}
```

## 環境変数設定

### `.env.local`

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## パッケージインストール

```bash
npm install @supabase/supabase-js
npm install react-chartjs-2 chart.js
npm install @types/react-chartjs-2 --save-dev
```

## ナビゲーション追加

### `app/layout.tsx`

```typescript
<nav>
  <Link href="/dashboard">Dashboard</Link>
  <Link href="/network">Network Stats</Link>
  <Link href="/analytics">Analytics</Link>
</nav>
```

## テスト

1. Supabaseで`network_stats`テーブルが作成されていることを確認
2. Botが起動してデータが送信されていることを確認
3. Webダッシュボードにアクセス: `http://localhost:3000/network`
4. リアルタイム更新が動作することを確認

## トラブルシューティング

### データが表示されない
- Supabase RLSポリシーを確認
- ブラウザのコンソールでエラーを確認
- Supabaseのテーブルにデータがあるか確認

### リアルタイム更新が動作しない
- Supabase Realtimeが有効か確認
- 無料プランの制限を確認
- ブラウザのWebSocket接続を確認

### グラフが表示されない
- Chart.jsが正しくインストールされているか確認
- データ形式が正しいか確認
