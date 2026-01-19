# ダッシュボード実装ガイド

このガイドでは、Next.js 14 (App Router) + Supabaseを使用して、Discord Botを制御・監視するダッシュボードを実装する方法を説明します。

## 📋 前提条件

- Node.js 18以上
- Supabaseプロジェクトが作成済み
- Bot側でSupabase統合が完了している

## 🚀 プロジェクトセットアップ

### 1. Next.jsプロジェクトの作成

```bash
npx create-next-app@latest discord-bot-dashboard
cd discord-bot-dashboard
```

設定：
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- App Router: Yes
- Import alias: Yes (@/*)

### 2. 必要なパッケージのインストール

```bash
npm install @supabase/supabase-js
npm install @supabase/ssr
npm install recharts
npm install lucide-react
npm install date-fns
npm install @tremor/react
```

### 3. 環境変数の設定

`.env.local`を作成：

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 📁 プロジェクト構造

```
discord-bot-dashboard/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                    # ダッシュボードホーム
│   ├── analytics/
│   │   └── page.tsx                # 分析ページ
│   ├── music/
│   │   └── page.tsx                # 音楽制御ページ
│   ├── logs/
│   │   └── page.tsx                # ログビューア
│   └── api/
│       └── command/
│           └── route.ts            # コマンド発行API
├── components/
│   ├── SystemStats.tsx             # システムメトリクス表示
│   ├── ActiveSessions.tsx          # アクティブセッション表示
│   ├── MusicController.tsx         # 音楽制御UI
│   ├── LogViewer.tsx               # ログビューア
│   └── CommandQueue.tsx            # コマンドキュー表示
├── lib/
│   ├── supabase.ts                 # Supabaseクライアント
│   └── types.ts                    # 型定義
└── .env.local
```

## 🔧 実装

### 1. Supabaseクライアントの設定

`lib/supabase.ts`:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})
```

### 2. 型定義

`lib/types.ts`:

```typescript
export interface SystemStats {
  bot_id: string
  cpu_usage: number
  memory_rss: number
  memory_heap: number
  ping_gateway: number
  ping_lavalink: number
  guild_count: number
  uptime: number
  status: 'online' | 'offline'
  updated_at: string
}

export interface ActiveSession {
  guild_id: string
  track_title: string
  position_ms: number
  duration_ms: number
  is_playing: boolean
  voice_members_count: number
  updated_at: string
}

export interface CommandQueue {
  id: string
  command_type: string
  payload: any
  status: 'pending' | 'processing' | 'completed' | 'failed'
  result?: string
  error?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface BotLog {
  id: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
  message: string
  scope: string
  created_at: string
}
```

### 3. システムメトリクス表示コンポーネント

`components/SystemStats.tsx`:

```typescript
'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { SystemStats } from '@/lib/types'
import { Card, Metric, Text, Flex, ProgressBar } from '@tremor/react'
import { Activity, Cpu, HardDrive, Wifi, Server } from 'lucide-react'

export default function SystemStatsComponent() {
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 初回データ取得
    fetchStats()

    // Realtimeで更新を監視
    const channel = supabase
      .channel('system-stats-changes')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'system_stats'
        },
        (payload) => {
          setStats(payload.new as SystemStats)
        }
      )
      .subscribe()

    // 5秒ごとにポーリング（フォールバック）
    const interval = setInterval(fetchStats, 5000)

    return () => {
      channel.unsubscribe()
      clearInterval(interval)
    }
  }, [])

  async function fetchStats() {
    const { data, error } = await supabase
      .from('system_stats')
      .select('*')
      .eq('bot_id', 'primary')
      .single()

    if (data) {
      setStats(data)
      setLoading(false)
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  if (!stats) {
    return <div>No data available</div>
  }

  const isOnline = stats.status === 'online'
  const uptimeHours = Math.floor(stats.uptime / 3600)
  const uptimeMinutes = Math.floor((stats.uptime % 3600) / 60)

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* ステータス */}
      <Card>
        <Flex alignItems="start">
          <div>
            <Text>Bot Status</Text>
            <Metric className={isOnline ? 'text-green-500' : 'text-red-500'}>
              {isOnline ? 'Online' : 'Offline'}
            </Metric>
          </div>
          <Activity className={isOnline ? 'text-green-500' : 'text-red-500'} />
        </Flex>
        <Text className="mt-2">
          Uptime: {uptimeHours}h {uptimeMinutes}m
        </Text>
      </Card>

      {/* CPU使用率 */}
      <Card>
        <Flex alignItems="start">
          <div className="w-full">
            <Text>CPU Usage</Text>
            <Metric>{stats.cpu_usage.toFixed(1)}%</Metric>
            <ProgressBar value={stats.cpu_usage} className="mt-2" />
          </div>
          <Cpu />
        </Flex>
      </Card>

      {/* メモリ使用量 */}
      <Card>
        <Flex alignItems="start">
          <div className="w-full">
            <Text>Memory Usage</Text>
            <Metric>{stats.memory_rss.toFixed(0)} MB</Metric>
            <ProgressBar 
              value={(stats.memory_rss / 512) * 100} 
              className="mt-2" 
            />
          </div>
          <HardDrive />
        </Flex>
      </Card>

      {/* Discord Gateway Ping */}
      <Card>
        <Flex alignItems="start">
          <div>
            <Text>Gateway Ping</Text>
            <Metric>{stats.ping_gateway.toFixed(0)} ms</Metric>
          </div>
          <Wifi />
        </Flex>
      </Card>

      {/* Lavalink Ping */}
      <Card>
        <Flex alignItems="start">
          <div>
            <Text>Lavalink Ping</Text>
            <Metric>{stats.ping_lavalink.toFixed(0)} ms</Metric>
          </div>
          <Server />
        </Flex>
      </Card>

      {/* サーバー数 */}
      <Card>
        <Flex alignItems="start">
          <div>
            <Text>Guilds</Text>
            <Metric>{stats.guild_count}</Metric>
          </div>
          <Server />
        </Flex>
      </Card>
    </div>
  )
}
```

### 4. アクティブセッション表示

`components/ActiveSessions.tsx`:

```typescript
'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { ActiveSession } from '@/lib/types'
import { Card, Title, Text, Flex, ProgressBar } from '@tremor/react'
import { Music, Users, Play, Pause } from 'lucide-react'

export default function ActiveSessions() {
  const [sessions, setSessions] = useState<ActiveSession[]>([])

  useEffect(() => {
    fetchSessions()

    const channel = supabase
      .channel('active-sessions-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'active_sessions'
        },
        () => {
          fetchSessions()
        }
      )
      .subscribe()

    const interval = setInterval(fetchSessions, 2000)

    return () => {
      channel.unsubscribe()
      clearInterval(interval)
    }
  }, [])

  async function fetchSessions() {
    const { data } = await supabase
      .from('active_sessions')
      .select('*')
      .order('updated_at', { ascending: false })

    if (data) {
      setSessions(data)
    }
  }

  if (sessions.length === 0) {
    return (
      <Card>
        <Title>Active Music Sessions</Title>
        <Text className="mt-4">No active sessions</Text>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Title>Active Music Sessions</Title>
      {sessions.map((session) => {
        const progress = (session.position_ms / session.duration_ms) * 100
        const positionMin = Math.floor(session.position_ms / 60000)
        const positionSec = Math.floor((session.position_ms % 60000) / 1000)
        const durationMin = Math.floor(session.duration_ms / 60000)
        const durationSec = Math.floor((session.duration_ms % 60000) / 1000)

        return (
          <Card key={session.guild_id}>
            <Flex>
              <div className="flex-1">
                <Flex alignItems="start">
                  <Music className="mr-2" />
                  <div className="flex-1">
                    <Text className="font-semibold">{session.track_title}</Text>
                    <Text className="text-sm text-gray-500">
                      Guild ID: {session.guild_id}
                    </Text>
                  </div>
                  {session.is_playing ? (
                    <Play className="text-green-500" size={20} />
                  ) : (
                    <Pause className="text-yellow-500" size={20} />
                  )}
                </Flex>

                <div className="mt-4">
                  <ProgressBar value={progress} className="mb-2" />
                  <Flex>
                    <Text className="text-sm">
                      {positionMin}:{positionSec.toString().padStart(2, '0')}
                    </Text>
                    <Text className="text-sm">
                      {durationMin}:{durationSec.toString().padStart(2, '0')}
                    </Text>
                  </Flex>
                </div>

                <Flex className="mt-2">
                  <Users size={16} className="mr-1" />
                  <Text className="text-sm">
                    {session.voice_members_count} listeners
                  </Text>
                </Flex>
              </div>
            </Flex>
          </Card>
        )
      })}
    </div>
  )
}
```

### 5. 音楽制御コンポーネント

`components/MusicController.tsx`:

```typescript
'use client'

import { useState } from 'react'
import { Card, Title, TextInput, Button, Select, SelectItem } from '@tremor/react'
import { Play, SkipForward, Square, Volume2 } from 'lucide-react'

export default function MusicController() {
  const [guildId, setGuildId] = useState('')
  const [url, setUrl] = useState('')
  const [volume, setVolume] = useState(100)
  const [loading, setLoading] = useState(false)

  async function sendCommand(commandType: string, payload: any) {
    setLoading(true)
    try {
      const response = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ commandType, payload })
      })

      if (response.ok) {
        alert('Command sent successfully!')
      } else {
        alert('Failed to send command')
      }
    } catch (error) {
      alert('Error sending command')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <Title>Music Controller</Title>
      
      <div className="mt-4 space-y-4">
        <div>
          <label className="text-sm font-medium">Guild ID</label>
          <TextInput
            value={guildId}
            onChange={(e) => setGuildId(e.target.value)}
            placeholder="Enter guild ID"
          />
        </div>

        <div>
          <label className="text-sm font-medium">Music URL</label>
          <TextInput
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="YouTube/Spotify URL"
          />
        </div>

        <div className="flex gap-2">
          <Button
            icon={Play}
            onClick={() => sendCommand('MUSIC_PLAY', { guild_id: guildId, url })}
            disabled={!guildId || !url || loading}
          >
            Play
          </Button>

          <Button
            icon={SkipForward}
            onClick={() => sendCommand('MUSIC_SKIP', { guild_id: guildId })}
            disabled={!guildId || loading}
            variant="secondary"
          >
            Skip
          </Button>

          <Button
            icon={Square}
            onClick={() => sendCommand('MUSIC_STOP', { guild_id: guildId })}
            disabled={!guildId || loading}
            color="red"
          >
            Stop
          </Button>
        </div>

        <div>
          <label className="text-sm font-medium">Volume: {volume}%</label>
          <input
            type="range"
            min="0"
            max="100"
            value={volume}
            onChange={(e) => setVolume(Number(e.target.value))}
            className="w-full"
          />
          <Button
            icon={Volume2}
            onClick={() => sendCommand('MUSIC_VOLUME', { guild_id: guildId, volume })}
            disabled={!guildId || loading}
            className="mt-2"
          >
            Set Volume
          </Button>
        </div>
      </div>
    </Card>
  )
}
```

### 6. コマンド発行API

`app/api/command/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function POST(request: NextRequest) {
  try {
    const { commandType, payload } = await request.json()

    const { data, error } = await supabase
      .from('command_queue')
      .insert({
        command_type: commandType,
        payload: payload,
        status: 'pending'
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ success: true, command: data })
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### 7. メインダッシュボードページ

`app/page.tsx`:

```typescript
import SystemStats from '@/components/SystemStats'
import ActiveSessions from '@/components/ActiveSessions'
import MusicController from '@/components/MusicController'

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-slate-50">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">
            Discord Bot Dashboard
          </h1>
          <p className="text-slate-600 mt-2">
            Monitor and control your Discord bot in real-time
          </p>
        </div>

        <SystemStats />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <ActiveSessions />
          <MusicController />
        </div>
      </div>
    </main>
  )
}
```

## 🎨 TrueNAS Scale風デザイン

Tailwind設定を追加して、Slateカラーベースのデザインを実現：

`tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          850: '#1e293b',
          950: '#0f172a',
        },
      },
    },
  },
  plugins: [],
}
export default config
```

## 🚀 デプロイ

### Vercelへのデプロイ

```bash
npm install -g vercel
vercel
```

環境変数を設定：
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## 📚 参考リンク

- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Tremor Documentation](https://www.tremor.so/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)

これで、Supabaseからリアルタイムでデータを取得し、Botを制御できるダッシュボードが完成します！
