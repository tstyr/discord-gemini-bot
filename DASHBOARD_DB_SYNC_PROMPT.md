# 🎯 Discord Bot Dashboard - データベース同期プロンプト

このプロンプトは、Supabaseデータベーススキーマと完全に同期したダッシュボードを構築するためのものです。

---

## 📊 現在のSupabaseスキーマ（bot/supabase_schema_clean.sql）

### 重要なテーブル構造

#### 1. system_stats（システム統計）
```sql
CREATE TABLE system_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id TEXT DEFAULT 'primary',
    cpu_usage REAL DEFAULT 0,
    ram_usage REAL DEFAULT 0,
    memory_rss REAL DEFAULT 0,
    memory_heap REAL DEFAULT 0,
    ping_gateway REAL DEFAULT 0,
    ping_lavalink REAL DEFAULT 0,
    server_count INTEGER DEFAULT 0,
    guild_count INTEGER DEFAULT 0,
    uptime INTEGER DEFAULT 0,
    status TEXT DEFAULT 'online',
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 2. conversation_logs（会話ログ）
```sql
CREATE TABLE conversation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3. music_logs（音楽ログ）
```sql
CREATE TABLE music_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    song_title TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    requested_by_id TEXT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 4. music_history（音楽再生履歴・詳細版）
```sql
CREATE TABLE music_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    track_title TEXT NOT NULL,
    track_url TEXT,
    duration_ms INTEGER DEFAULT 0,
    requested_by TEXT NOT NULL,
    requested_by_id TEXT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 5. gemini_usage（Gemini使用統計）
```sql
CREATE TABLE gemini_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    model TEXT DEFAULT 'gemini-pro',
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 6. active_sessions（アクティブセッション）
```sql
CREATE TABLE active_sessions (
    guild_id TEXT PRIMARY KEY,
    track_title TEXT,
    position_ms INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    is_playing BOOLEAN DEFAULT FALSE,
    voice_members_count INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 7. bot_logs（Botログ）
```sql
CREATE TABLE bot_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level TEXT NOT NULL CHECK (level IN ('debug', 'info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    scope TEXT DEFAULT 'general',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 8. command_queue（コマンドキュー）
```sql
CREATE TABLE command_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    command_type TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    result TEXT,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

---

## 🚀 ダッシュボード実装要件

### 技術スタック
- **フレームワーク**: Next.js 14 (App Router)
- **データベース**: Supabase
- **スタイリング**: Tailwind CSS
- **UI コンポーネント**: shadcn/ui または Tremor
- **チャート**: Recharts

### プロジェクト構造
```
dashboard/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                    # メインダッシュボード
│   ├── analytics/
│   │   └── page.tsx                # 分析ページ
│   ├── music/
│   │   └── page.tsx                # 音楽制御ページ
│   └── logs/
│       └── page.tsx                # ログビューア
├── components/
│   ├── SystemStats.tsx             # システムメトリクス
│   ├── ConversationLogs.tsx        # 会話ログ
│   ├── MusicLogs.tsx               # 音楽ログ
│   ├── ActiveSessions.tsx          # アクティブセッション
│   ├── GeminiStats.tsx             # Gemini統計
│   └── BotLogs.tsx                 # Botログ
├── lib/
│   ├── supabase.ts                 # Supabaseクライアント
│   └── types.ts                    # TypeScript型定義
└── .env.local
```

---

## 📝 TypeScript型定義（lib/types.ts）

```typescript
export interface SystemStats {
  id: string
  bot_id: string
  cpu_usage: number
  ram_usage: number
  memory_rss: number
  memory_heap: number
  ping_gateway: number
  ping_lavalink: number
  server_count: number
  guild_count: number
  uptime: number
  status: 'online' | 'offline'
  recorded_at: string
  updated_at: string
  created_at: string
}

export interface ConversationLog {
  id: string
  user_id: string
  user_name: string
  prompt: string
  response: string
  recorded_at: string
  created_at: string
}

export interface MusicLog {
  id: string
  guild_id: string
  song_title: string
  requested_by: string
  requested_by_id: string
  recorded_at: string
  created_at: string
}

export interface MusicHistory {
  id: string
  guild_id: string
  track_title: string
  track_url: string | null
  duration_ms: number
  requested_by: string
  requested_by_id: string
  recorded_at: string
  created_at: string
}

export interface GeminiUsage {
  id: string
  guild_id: string
  user_id: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  model: string
  recorded_at: string
  created_at: string
}

export interface ActiveSession {
  guild_id: string
  track_title: string | null
  position_ms: number
  duration_ms: number
  is_playing: boolean
  voice_members_count: number
  updated_at: string
  created_at: string
}

export interface BotLog {
  id: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
  message: string
  scope: string
  created_at: string
}

export interface CommandQueue {
  id: string
  command_type: string
  payload: Record<string, any>
  status: 'pending' | 'processing' | 'completed' | 'failed'
  result: string | null
  error: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
}
```

---

## 🔧 Supabaseクライアント設定（lib/supabase.ts）

```typescript
import { createClient } from '@supabase/supabase-js'
import { Database } from './database.types'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  },
  auth: {
    persistSession: false
  }
})

// ヘルパー関数
export async function getLatestSystemStats() {
  const { data, error } = await supabase
    .from('system_stats')
    .select('*')
    .order('recorded_at', { ascending: false })
    .limit(1)
    .single()

  if (error) throw error
  return data
}

export async function getConversationLogs(limit = 50) {
  const { data, error } = await supabase
    .from('conversation_logs')
    .select('*')
    .order('recorded_at', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data
}

export async function getMusicLogs(limit = 30) {
  const { data, error } = await supabase
    .from('music_logs')
    .select('*')
    .order('recorded_at', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data
}

export async function getActiveSessions() {
  const { data, error } = await supabase
    .from('active_sessions')
    .select('*')
    .order('updated_at', { ascending: false })

  if (error) throw error
  return data
}

export async function getGeminiUsageToday() {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const { data, error } = await supabase
    .from('gemini_usage')
    .select('*')
    .gte('recorded_at', today.toISOString())

  if (error) throw error
  return data
}

export async function getBotLogs(limit = 100, level?: string) {
  let query = supabase
    .from('bot_logs')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(limit)

  if (level) {
    query = query.eq('level', level)
  }

  const { data, error } = await query

  if (error) throw error
  return data
}
```

---

## 🎨 コンポーネント実装例

### SystemStats.tsx
```typescript
'use client'

import { useEffect, useState } from 'react'
import { getLatestSystemStats } from '@/lib/supabase'
import { SystemStats as SystemStatsType } from '@/lib/types'

export default function SystemStats() {
  const [stats, setStats] = useState<SystemStatsType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 10000) // 10秒ごとに更新
    return () => clearInterval(interval)
  }, [])

  async function fetchStats() {
    try {
      const data = await getLatestSystemStats()
      setStats(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="animate-pulse">Loading system stats...</div>
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>
  }

  if (!stats) {
    return <div className="text-gray-500">No data available</div>
  }

  const isOnline = stats.status === 'online'
  const uptimeHours = Math.floor(stats.uptime / 3600)
  const uptimeMinutes = Math.floor((stats.uptime % 3600) / 60)

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* ステータス */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Bot Status</h3>
        <p className={`text-2xl font-bold ${isOnline ? 'text-green-600' : 'text-red-600'}`}>
          {isOnline ? '🟢 Online' : '🔴 Offline'}
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Uptime: {uptimeHours}h {uptimeMinutes}m
        </p>
      </div>

      {/* CPU使用率 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">CPU Usage</h3>
        <p className="text-2xl font-bold">{stats.cpu_usage.toFixed(1)}%</p>
        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all" 
            style={{ width: `${Math.min(stats.cpu_usage, 100)}%` }}
          />
        </div>
      </div>

      {/* メモリ使用量 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Memory (RSS)</h3>
        <p className="text-2xl font-bold">{stats.memory_rss.toFixed(0)} MB</p>
        <p className="text-xs text-gray-400 mt-1">
          Heap: {stats.memory_heap.toFixed(0)} MB
        </p>
      </div>

      {/* Gateway Ping */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Gateway Ping</h3>
        <p className="text-2xl font-bold">{stats.ping_gateway.toFixed(0)} ms</p>
        {stats.ping_lavalink > 0 && (
          <p className="text-xs text-gray-400 mt-1">
            Lavalink: {stats.ping_lavalink.toFixed(0)} ms
          </p>
        )}
      </div>

      {/* サーバー数 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Servers</h3>
        <p className="text-2xl font-bold">{stats.guild_count}</p>
      </div>

      {/* 最終更新 */}
      <div className="bg-white p-6 rounded-lg shadow col-span-full">
        <h3 className="text-sm font-medium text-gray-500">Last Update</h3>
        <p className="text-sm">{new Date(stats.recorded_at).toLocaleString()}</p>
      </div>
    </div>
  )
}
```

### ConversationLogs.tsx
```typescript
'use client'

import { useEffect, useState } from 'react'
import { getConversationLogs } from '@/lib/supabase'
import { ConversationLog } from '@/lib/types'

export default function ConversationLogs() {
  const [logs, setLogs] = useState<ConversationLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 30000) // 30秒ごとに更新
    return () => clearInterval(interval)
  }, [])

  async function fetchLogs() {
    try {
      const data = await getConversationLogs(50)
      setLogs(data)
    } catch (error) {
      console.error('Failed to fetch conversation logs:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div>Loading conversations...</div>
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <h2 className="text-xl font-bold">💬 Conversation Logs</h2>
        <p className="text-sm text-gray-500">Latest {logs.length} conversations</p>
      </div>
      
      <div className="divide-y max-h-[600px] overflow-y-auto">
        {logs.map((log) => (
          <div key={log.id} className="p-4 hover:bg-gray-50 transition">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-sm">👤 {log.user_name}</span>
              <span className="text-xs text-gray-500">
                {new Date(log.recorded_at).toLocaleString()}
              </span>
            </div>
            <div className="text-sm space-y-1">
              <p className="text-gray-700">
                <span className="font-semibold text-blue-600">Q:</span> {log.prompt}
              </p>
              <p className="text-gray-600">
                <span className="font-semibold text-green-600">A:</span>{' '}
                {log.response.length > 200 
                  ? `${log.response.substring(0, 200)}...` 
                  : log.response}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 🔍 デバッグチェックリスト

### 1. 環境変数の確認
```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. Supabaseでデータ確認
```sql
-- システム統計
SELECT * FROM system_stats ORDER BY recorded_at DESC LIMIT 1;

-- 会話ログ
SELECT COUNT(*) FROM conversation_logs;

-- 音楽ログ
SELECT COUNT(*) FROM music_logs;

-- Gemini使用統計
SELECT SUM(total_tokens) FROM gemini_usage WHERE recorded_at >= CURRENT_DATE;
```

### 3. RLSポリシーの確認
Supabase Dashboard → Database → Tables → 各テーブル

以下のポリシーが設定されているか確認：
- ✅ `Allow authenticated read access` (SELECT)
- ✅ `Allow service role full access` (ALL)

### 4. ブラウザコンソールでテスト
```javascript
// F12 → Console
const { data, error } = await supabase.from('system_stats').select('*').limit(1)
console.log('Data:', data)
console.log('Error:', error)
```

---

## 📦 必要なパッケージ

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@supabase/supabase-js": "^2.38.0",
    "recharts": "^2.10.0",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## 🚀 セットアップ手順

### 1. プロジェクト作成
```bash
npx create-next-app@latest discord-bot-dashboard --typescript --tailwind --app
cd discord-bot-dashboard
```

### 2. パッケージインストール
```bash
npm install @supabase/supabase-js recharts date-fns
```

### 3. 環境変数設定
```bash
# .env.local を作成
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### 4. 開発サーバー起動
```bash
npm run dev
```

### 5. Vercelデプロイ
```bash
npm install -g vercel
vercel
```

環境変数を設定：
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

## ✅ 実装完了チェックリスト

- [ ] Supabaseクライアント設定完了
- [ ] TypeScript型定義作成完了
- [ ] SystemStatsコンポーネント実装完了
- [ ] ConversationLogsコンポーネント実装完了
- [ ] MusicLogsコンポーネント実装完了
- [ ] ActiveSessionsコンポーネント実装完了
- [ ] GeminiStatsコンポーネント実装完了
- [ ] BotLogsコンポーネント実装完了
- [ ] メインダッシュボードページ作成完了
- [ ] データが正しく表示されることを確認
- [ ] リアルタイム更新が動作することを確認
- [ ] Vercelデプロイ完了

---

## 🎉 完成！

このプロンプトに従って実装すれば、Supabaseのスキーマと完全に同期したダッシュボードが完成します。

**重要なポイント:**
- ✅ カラム名は`recorded_at`（Botのスキーマと一致）
- ✅ UUIDは`string`型で扱う
- ✅ `anon`キーを使用（Bot側は`service_role`）
- ✅ RLSポリシーで読み取り権限を付与
- ✅ 10秒〜30秒ごとに自動更新
