# Supabaseリアルタイム統合実装完了

## ✅ 実装完了内容

### タスク1: システム統計の定時送信（10秒間隔）

**実装場所:** `bot/supabase_client.py`

```python
async def _health_monitor_loop(self):
    """10秒ごとにシステムメトリクスを送信"""
    while self.is_running:
        await self._send_system_stats()
        await asyncio.sleep(10)  # 10秒間隔
```

**送信データ:**
- ✅ CPU使用率 (`cpu_usage`)
- ✅ RAM使用率 (`ram_usage`) - システム全体のメモリ使用率
- ✅ サーバー数 (`server_count`) - 参加しているDiscordサーバー数
- ✅ その他のメトリクス（メモリ、Ping、稼働時間）

**データベース保存:**
- `INSERT`で履歴として保存（UPSERTではなく）
- タイムスタンプ付きで時系列データとして蓄積
- ダッシュボードでグラフ表示可能

### タスク2: ログ保存機能

#### 2-1. 会話ログ

**実装場所:** 
- `bot/supabase_client.py` - `save_conversation_log()`メソッド
- `bot/main.py` - AI応答時に自動保存

**保存タイミング:** Geminiが回答を生成した直後

**保存データ:**
```python
{
    'user_id': str,        # ユーザーID
    'user_name': str,      # ユーザー名
    'prompt': str,         # ユーザーの質問
    'response': str,       # AIの回答
    'timestamp': datetime  # タイムスタンプ
}
```

**実装コード:**
```python
# main.py内
await self.supabase_client.save_conversation_log(
    user_id=message.author.id,
    user_name=message.author.display_name,
    prompt=message.content,
    response=response
)
```

#### 2-2. 音楽ログ

**実装場所:**
- `bot/supabase_client.py` - `save_music_log()`メソッド
- `bot/main.py` - 音楽再生時に自動保存（2箇所）

**保存タイミング:** `play`コマンドで曲が再生された直後

**保存データ:**
```python
{
    'guild_id': str,           # サーバーID
    'song_title': str,         # 曲名
    'requested_by': str,       # リクエストしたユーザー名
    'requested_by_id': str,    # リクエストしたユーザーID
    'timestamp': datetime      # タイムスタンプ
}
```

**実装コード:**
```python
# main.py内（音楽再生時）
await self.supabase_client.save_music_log(
    guild_id=message.guild.id,
    song_title=track.title,
    requested_by=message.author.display_name,
    requested_by_id=message.author.id
)
```

### タスク3: 環境変数と依存関係

#### 環境変数

**設定場所:** `bot/.env`

```env
# Supabase設定
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
```

**初期化コード:** `bot/supabase_client.py`
```python
self.supabase_url = os.getenv('SUPABASE_URL')
self.supabase_key = os.getenv('SUPABASE_KEY')
self.client = create_client(self.supabase_url, self.supabase_key)
```

#### 依存関係

**ファイル:** `bot/requirements.txt`

```txt
supabase>=2.0.0  # Supabase Python SDK
psutil>=5.9.0    # システムメトリクス取得
```

## 📊 Supabaseテーブル定義

### 1. system_stats（システム統計）

```sql
CREATE TABLE system_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id TEXT DEFAULT 'primary',
    cpu_usage REAL DEFAULT 0,           -- CPU使用率（%）
    ram_usage REAL DEFAULT 0,           -- RAM使用率（%）
    memory_rss REAL DEFAULT 0,          -- プロセスメモリ（MB）
    memory_heap REAL DEFAULT 0,         -- ヒープメモリ（MB）
    ping_gateway REAL DEFAULT 0,        -- Discord Gateway Ping（ms）
    ping_lavalink REAL DEFAULT 0,       -- Lavalink Ping（ms）
    server_count INTEGER DEFAULT 0,     -- サーバー数
    guild_count INTEGER DEFAULT 0,      -- ギルド数（互換性）
    uptime INTEGER DEFAULT 0,           -- 稼働時間（秒）
    status TEXT DEFAULT 'online',       -- ステータス
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_system_stats_timestamp ON system_stats(timestamp DESC);
CREATE INDEX idx_system_stats_bot_id ON system_stats(bot_id, timestamp DESC);
```

**特徴:**
- 10秒ごとに新しいレコードを`INSERT`
- 時系列データとして蓄積
- グラフ表示に最適
- 7日以上前のデータは自動削除（オプション）

### 2. conversation_logs（会話ログ）

```sql
CREATE TABLE conversation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,              -- ユーザーID
    user_name TEXT NOT NULL,            -- ユーザー名
    prompt TEXT NOT NULL,               -- ユーザーの質問
    response TEXT NOT NULL,             -- AIの回答
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversation_logs_user_id ON conversation_logs(user_id, timestamp DESC);
CREATE INDEX idx_conversation_logs_timestamp ON conversation_logs(timestamp DESC);
```

**特徴:**
- すべての会話を記録
- ユーザーごとの履歴検索が可能
- 90日以上前のデータは自動削除（オプション）

### 3. music_logs（音楽ログ）

```sql
CREATE TABLE music_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,             -- サーバーID
    song_title TEXT NOT NULL,           -- 曲名
    requested_by TEXT NOT NULL,         -- リクエストユーザー名
    requested_by_id TEXT NOT NULL,      -- リクエストユーザーID
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_music_logs_guild_id ON music_logs(guild_id, timestamp DESC);
CREATE INDEX idx_music_logs_timestamp ON music_logs(timestamp DESC);
```

**特徴:**
- すべての音楽再生を記録
- サーバーごとの再生履歴
- 人気曲の分析が可能
- 90日以上前のデータは自動削除（オプション）

## 🚀 セットアップ手順

### 1. Supabaseプロジェクトの作成

1. [Supabase](https://supabase.com)にアクセス
2. 新しいプロジェクトを作成
3. プロジェクトURLとAPIキーを取得

### 2. データベーススキーマの実行

1. SupabaseダッシュボードのSQL Editorを開く
2. `bot/supabase_schema.sql`の内容をコピー＆ペースト
3. 実行してテーブルを作成

### 3. 環境変数の設定

`bot/.env`に追加：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
```

**重要:** `service_role`キーを使用してください（`anon`キーではなく）

### 4. 依存関係のインストール

```bash
cd bot
pip install -r requirements.txt
```

### 5. Botの起動

```bash
python main.py
```

起動時のログ確認：
```
✅ Supabase client initialized
✅ system_stats table exists
✅ conversation_logs table exists
✅ music_logs table exists
🔄 Health monitor started (10s interval)
```

## 📈 ダッシュボードでのデータ取得

### システム統計の取得（最新10件）

```typescript
const { data: stats } = await supabase
  .from('system_stats')
  .select('*')
  .order('timestamp', { ascending: false })
  .limit(10)
```

### システム統計のグラフ表示（過去1時間）

```typescript
const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString()

const { data: stats } = await supabase
  .from('system_stats')
  .select('timestamp, cpu_usage, ram_usage, server_count')
  .gte('timestamp', oneHourAgo)
  .order('timestamp', { ascending: true })
```

### 会話ログの取得（最新50件）

```typescript
const { data: logs } = await supabase
  .from('conversation_logs')
  .select('*')
  .order('timestamp', { ascending: false })
  .limit(50)
```

### 音楽ログの取得（特定サーバー）

```typescript
const { data: musicLogs } = await supabase
  .from('music_logs')
  .select('*')
  .eq('guild_id', guildId)
  .order('timestamp', { ascending: false })
  .limit(20)
```

### 人気曲ランキング

```typescript
const { data: popularSongs } = await supabase
  .from('music_logs')
  .select('song_title, count')
  .order('count', { ascending: false })
  .limit(10)
```

## 🔍 データ分析例

### CPU使用率の平均（過去24時間）

```sql
SELECT AVG(cpu_usage) as avg_cpu
FROM system_stats
WHERE timestamp > NOW() - INTERVAL '24 hours';
```

### 最もアクティブなユーザー（会話数）

```sql
SELECT user_name, COUNT(*) as conversation_count
FROM conversation_logs
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY user_name
ORDER BY conversation_count DESC
LIMIT 10;
```

### サーバーごとの音楽再生回数

```sql
SELECT guild_id, COUNT(*) as play_count
FROM music_logs
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY guild_id
ORDER BY play_count DESC;
```

## 🎯 実装のポイント

### 1. 非同期処理

すべてのSupabase操作は非同期で実行され、Bot本体の動作をブロックしません。

### 2. エラーハンドリング

Supabaseへの接続エラーが発生しても、Bot本体は正常に動作し続けます。

### 3. データ保持期間

- システム統計: 7日間
- 会話ログ: 90日間
- 音楽ログ: 90日間
- Botログ: 30日間

自動削除関数で古いデータを定期的にクリーンアップします。

### 4. パフォーマンス

- インデックスを適切に設定
- バッチ処理でログを送信
- 10秒間隔で負荷を分散

## 🎉 完了

これで、Webダッシュボードにリアルタイムでデータが反映されるようになりました！

- ✅ 10秒ごとのシステム統計送信
- ✅ 会話ログの自動保存
- ✅ 音楽ログの自動保存
- ✅ 環境変数の設定
- ✅ 依存関係の追加
- ✅ Supabaseテーブル定義

ダッシュボード側で上記のクエリを使用して、リアルタイムでデータを表示できます！
