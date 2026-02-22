# Supabase統合セットアップガイド

このガイドでは、Discord BotとSupabaseを統合し、外部ダッシュボードから制御可能にする手順を説明します。

## 📋 概要

### システムアーキテクチャ

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│   Discord Bot   │◄────────┤   Supabase   ├────────►│   Dashboard     │
│    (Koyeb)      │         │  (PostgreSQL)│         │    (Vercel)     │
└─────────────────┘         └──────────────┘         └─────────────────┘
     │                             │                          │
     ├─ 5秒ごとにメトリクス送信    │                          │
     ├─ コマンドキューを監視       │                          │
     ├─ アクティブセッション更新   │                          │
     └─ ログをミラーリング         │                          │
                                   │                          │
                                   └─ Realtime購読            │
                                   └─ コマンド発行            │
```

## 🚀 セットアップ手順

### 1. Supabaseプロジェクトの作成

1. [Supabase](https://supabase.com)にアクセスしてアカウントを作成
2. 新しいプロジェクトを作成
3. プロジェクトのURLとAPIキーを取得

### 2. データベーススキーマの作成

1. SupabaseダッシュボードのSQL Editorを開く
2. `bot/supabase_schema.sql`の内容をコピー＆ペースト
3. 実行してテーブルを作成

作成されるテーブル：
- `system_stats` - システムメトリクス（CPU、メモリ、Ping等）
- `command_queue` - リモートコマンドキュー（Realtime対応）
- `active_sessions` - アクティブな音楽セッション
- `job_logs` - コマンド実行ログ
- `bot_logs` - Botのコンソールログ

### 3. Bot側の環境変数設定

`.env`ファイルに以下を追加：

```env
# Supabase設定
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
```

**重要:** `SUPABASE_KEY`には`service_role`キーを使用してください（`anon`キーではなく）。
これはBot側でデータベースへの完全なアクセス権限が必要なためです。

### 4. 依存関係のインストール

```bash
cd bot
pip install -r requirements.txt
```

新しく追加されたパッケージ：
- `supabase>=2.0.0` - Supabase Python SDK
- `psutil>=5.9.0` - システムメトリクス取得

### 5. Botの起動

```bash
python main.py
```

起動時に以下のログが表示されれば成功：
```
✅ Supabase client initialized
✅ system_stats table exists
✅ command_queue table exists
✅ active_sessions table exists
🔄 Health monitor started
🔄 Command queue polling started
✅ Supabase log handler initialized
```

## 📊 実装された機能

### 1. Internal Health Monitor

5秒ごとに以下のメトリクスを`system_stats`テーブルに送信：

- `cpu_usage` - CPU使用率（%）
- `memory_rss` - メモリ使用量（MB）
- `memory_heap` - ヒープメモリ（MB）
- `ping_gateway` - Discord Gateway Ping（ms）
- `ping_lavalink` - Lavalink Ping（ms）
- `guild_count` - 参加サーバー数
- `uptime` - 稼働時間（秒）

### 2. Active Voice Session Sync

音楽再生時に`active_sessions`テーブルを自動更新：

- `guild_id` - サーバーID
- `track_title` - 曲名
- `position_ms` - 再生位置（ミリ秒）
- `duration_ms` - 曲の長さ（ミリ秒）
- `is_playing` - 再生中かどうか
- `voice_members_count` - ボイスチャンネルの人数

イベント：
- `on_wavelink_track_start` - 曲開始時
- `on_wavelink_track_end` - 曲終了時
- `on_voice_state_update` - メンバー参加/退出時

### 3. Realtime Remote Control

`command_queue`テーブルを1秒ごとにポーリングし、`pending`状態のコマンドを実行：

対応コマンド：
- `MUSIC_PLAY` - 音楽再生
  ```json
  {"url": "https://youtube.com/...", "guild_id": "123456789"}
  ```
- `MUSIC_SKIP` - スキップ
  ```json
  {"guild_id": "123456789"}
  ```
- `MUSIC_STOP` - 停止
  ```json
  {"guild_id": "123456789"}
  ```
- `MUSIC_VOLUME` - 音量調整
  ```json
  {"guild_id": "123456789", "volume": 50}
  ```
- `MUSIC_SEEK` - シーク
  ```json
  {"guild_id": "123456789", "position": 30000}
  ```
- `SYS_MAINTENANCE` - メンテナンスモード
  ```json
  {"enabled": true}
  ```

実行結果は`status`フィールドに反映：
- `pending` → `processing` → `completed` / `failed`

### 4. Console Mirroring

すべてのログを`bot_logs`テーブルに非同期で送信：

- `level` - ログレベル（debug, info, warning, error, critical）
- `message` - ログメッセージ
- `scope` - スコープ（general, music, ai, database, api）
- `created_at` - タイムスタンプ

10秒ごとに最大100件をバッチ送信。

### 5. Graceful Shutdown

`SIGTERM`シグナル受信時：
1. すべてのギルドで音楽を停止
2. Supabaseに`offline`状態を記録
3. ログをフラッシュ
4. 接続をクローズ

## 🎯 ダッシュボード側の実装

ダッシュボード（Next.js）側では以下を実装してください：

### 1. Supabaseクライアントの初期化

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

### 2. システムメトリクスの表示

```typescript
const { data: stats } = await supabase
  .from('system_stats')
  .select('*')
  .eq('bot_id', 'primary')
  .single()

// stats.cpu_usage, stats.memory_rss, etc.
```

### 3. アクティブセッションの表示

```typescript
const { data: sessions } = await supabase
  .from('active_sessions')
  .select('*')

// sessions[0].track_title, sessions[0].is_playing, etc.
```

### 4. Realtimeでコマンドキューを監視

```typescript
const channel = supabase
  .channel('command-updates')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'command_queue'
    },
    (payload) => {
      console.log('Command updated:', payload.new)
    }
  )
  .subscribe()
```

### 5. コマンドの発行

```typescript
const { data, error } = await supabase
  .from('command_queue')
  .insert({
    command_type: 'MUSIC_PLAY',
    payload: {
      url: 'https://youtube.com/watch?v=...',
      guild_id: '123456789'
    }
  })
```

## 🔒 セキュリティ

### Row Level Security (RLS)

スキーマには以下のポリシーが設定されています：

1. **認証済みユーザー** - 読み取り専用アクセス
2. **Service Role** - 完全アクセス（Bot用）
3. **認証済みユーザー** - `command_queue`への挿入のみ許可

### 環境変数の管理

- Bot側: `service_role`キーを使用（完全アクセス）
- Dashboard側: `anon`キーを使用（RLS制限付き）

## 🐛 トラブルシューティング

### Supabaseに接続できない

```
❌ Failed to initialize Supabase: ...
```

対処法：
1. `SUPABASE_URL`と`SUPABASE_KEY`が正しいか確認
2. Supabaseプロジェクトが起動しているか確認
3. ネットワーク接続を確認

### コマンドが実行されない

対処法：
1. `command_queue`テーブルの`status`を確認
2. `job_logs`テーブルでエラーを確認
3. Bot側のログを確認

### ログが送信されない

対処法：
1. `bot_logs`テーブルが存在するか確認
2. ログハンドラーが初期化されているか確認
3. ネットワーク接続を確認

## 📚 参考資料

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Wavelink Documentation](https://wavelink.dev/)

## 🎉 完了

これでBotとSupabaseの統合が完了しました！
次は別プロジェクトでダッシュボードを作成し、Supabase経由でBotを制御できるようにしてください。
