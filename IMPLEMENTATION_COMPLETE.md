# ✅ Supabase連携実装完了

## 実装内容

### 1. 初期化

**ファイル:** `bot/supabase_client.py`

```python
from supabase import create_client, Client
from discord.ext import tasks

class SupabaseClient:
    def __init__(self, bot):
        self.bot = bot
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.client = None
        
    async def initialize(self):
        self.client = create_client(self.supabase_url, self.supabase_key)
        logger.info("✅ Supabase client initialized")
```

**環境変数:**
- `SUPABASE_URL`: Supabaseプロジェクトのurl
- `SUPABASE_KEY`: service_roleキー（Bot用）

### 2. 10秒ごとの統計送信

**実装:** `tasks.loop(seconds=10)`デコレータを使用

```python
@tasks.loop(seconds=10)
async def health_monitor_loop(self):
    """10秒ごとにシステムメトリクスを送信"""
    try:
        await self._send_system_stats()
    except Exception as e:
        logger.error(f"❌ Health monitor error: {e}")

@health_monitor_loop.before_loop
async def before_health_monitor(self):
    """ヘルスモニター開始前の待機"""
    await self.bot.wait_until_ready()
    logger.info("🔄 Health monitor started (10s interval)")
```

**送信データ:**
```python
{
    'bot_id': 'primary',
    'cpu_usage': psutil.cpu_percent(interval=0.1),  # CPU使用率
    'ram_usage': psutil.virtual_memory().percent,   # RAM使用率
    'server_count': len(self.bot.guilds),           # サーバー数
    'memory_rss': memory_rss,                       # プロセスメモリ
    'ping_gateway': ping_gateway,                   # Discord Ping
    'ping_lavalink': ping_lavalink,                 # Lavalink Ping
    'uptime': uptime,                               # 稼働時間
    'timestamp': datetime.utcnow().isoformat()
}
```

**保存先:** `system_stats`テーブル

### 3. 会話ログの保存

**実装場所:** `bot/main.py` - `handle_ai_response()`メソッド内

```python
# Geminiが回答した際に自動保存
if response:
    # Send response
    await message.reply(response)
    
    # Save to Supabase conversation_logs (エラーハンドリング付き)
    try:
        await self.supabase_client.save_conversation_log(
            user_id=message.author.id,
            user_name=message.author.display_name,
            prompt=message.content,
            response=response
        )
    except Exception as e:
        logger.error(f"Failed to save conversation log to Supabase: {e}")
```

**保存データ:**
```python
{
    'user_id': str(user_id),
    'user_name': user_name,
    'prompt': prompt,           # ユーザーの質問
    'response': response,       # AIの回答
    'timestamp': datetime.utcnow().isoformat()
}
```

**保存先:** `conversation_logs`テーブル

### 4. 音楽ログの保存

**実装場所:** `bot/main.py` - `handle_music_request()`メソッド内（2箇所）

```python
# 曲が再生される際に自動保存
try:
    await vc.play(track)
    queue.current = track
    logger.info(f"Started playing: {track.title}")
    
    # Save to Supabase music_logs (エラーハンドリング付き)
    try:
        await self.supabase_client.save_music_log(
            guild_id=message.guild.id,
            song_title=track.title,
            requested_by=message.author.display_name,
            requested_by_id=message.author.id
        )
    except Exception as log_err:
        logger.error(f"Failed to save music log to Supabase: {log_err}")
except Exception as play_err:
    logger.error(f"Failed to play track: {play_err}")
```

**保存データ:**
```python
{
    'guild_id': str(guild_id),
    'song_title': song_title,
    'requested_by': requested_by,       # ユーザー名
    'requested_by_id': str(requested_by_id),
    'timestamp': datetime.utcnow().isoformat()
}
```

**保存先:** `music_logs`テーブル

### 5. エラーハンドリング

すべてのSupabase操作は`try-except`で囲まれており、エラーが発生してもBotは停止しません。

**実装例:**

```python
# システム統計送信
@tasks.loop(seconds=10)
async def health_monitor_loop(self):
    try:
        await self._send_system_stats()
    except Exception as e:
        logger.error(f"❌ Health monitor error: {e}")
        # Botは継続して動作

# 会話ログ保存
try:
    await self.supabase_client.save_conversation_log(...)
except Exception as e:
    logger.error(f"Failed to save conversation log: {e}")
    # エラーをログに記録してスキップ

# 音楽ログ保存
try:
    await self.supabase_client.save_music_log(...)
except Exception as log_err:
    logger.error(f"Failed to save music log: {log_err}")
    # エラーをログに記録してスキップ
```

**エラー時の動作:**
- エラーメッセージをログに出力
- Bot本体は正常に動作を継続
- ユーザーへの応答は影響を受けない

## 依存関係

### requirements.txt

```txt
discord.py>=2.3.2
google-generativeai>=0.3.2
python-dotenv>=1.0.0
aiohttp>=3.9.1
fastapi>=0.104.1
uvicorn>=0.24.0
aiosqlite>=0.19.0
asyncpg>=0.27.0,<0.30.0
pydantic>=2.5.0
websockets>=12.0
wavelink>=3.2.0
PyNaCl>=1.5.0
python-socketio>=5.10.0
colorama>=0.4.6
youtube-search-python>=1.6.6
yt-dlp>=2023.12.30
supabase>=2.0.0    # ✅ Supabase Python SDK
psutil>=5.9.0      # ✅ システムメトリクス取得
```

**インストール:**
```bash
cd bot
pip install -r requirements.txt
```

## セットアップ手順

### 1. Supabaseプロジェクトの作成

1. [https://supabase.com](https://supabase.com) にアクセス
2. 新しいプロジェクトを作成
3. プロジェクトURLとAPIキーを取得

### 2. データベーススキーマの実行

1. SupabaseダッシュボードのSQL Editorを開く
2. `bot/supabase_schema.sql`の内容をコピー＆ペースト
3. 実行してテーブルを作成

### 3. 環境変数の設定

`bot/.env`に追加：

```env
# Supabase設定
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...（service_roleキー）
```

**重要:** `SUPABASE_KEY`には`service_role`キーを使用してください

### 4. Botの起動

```bash
python main.py
```

**起動時のログ確認:**
```
✅ Supabase client initialized
✅ system_stats table exists
✅ conversation_logs table exists
✅ music_logs table exists
🔄 Health monitor started (10s interval)
```

## 動作確認

### システム統計の確認

Supabaseダッシュボードで`system_stats`テーブルを確認：

```sql
SELECT * FROM system_stats 
ORDER BY timestamp DESC 
LIMIT 10;
```

10秒ごとに新しいレコードが追加されているはずです。

### 会話ログの確認

Botに話しかけて、`conversation_logs`テーブルを確認：

```sql
SELECT * FROM conversation_logs 
ORDER BY timestamp DESC 
LIMIT 10;
```

### 音楽ログの確認

音楽を再生して、`music_logs`テーブルを確認：

```sql
SELECT * FROM music_logs 
ORDER BY timestamp DESC 
LIMIT 10;
```

## トラブルシューティング

### Supabaseに接続できない

**エラー:**
```
⚠️  Supabase credentials not found. Remote control disabled.
```

**対処法:**
1. `.env`ファイルに`SUPABASE_URL`と`SUPABASE_KEY`が設定されているか確認
2. キーが正しいか確認（service_roleキーを使用）
3. Supabaseプロジェクトが起動しているか確認

### データが保存されない

**対処法:**
1. Supabaseダッシュボードでテーブルが作成されているか確認
2. Row Level Security (RLS) ポリシーが正しく設定されているか確認
3. Botのログでエラーメッセージを確認

### tasks.loopが動作しない

**対処法:**
1. `await self.bot.wait_until_ready()`が実行されているか確認
2. `health_monitor_loop.start()`が呼ばれているか確認
3. エラーログを確認

## まとめ

✅ **実装完了項目:**
1. Supabaseクライアントの初期化（環境変数使用）
2. 10秒ごとのシステム統計送信（tasks.loop使用）
3. 会話ログの自動保存（Gemini回答時）
4. 音楽ログの自動保存（音楽再生時）
5. 完全なエラーハンドリング（Bot停止を防ぐ）
6. requirements.txtへの依存関係追加

✅ **動作確認:**
- システム統計が10秒ごとに送信される
- 会話がログに記録される
- 音楽再生がログに記録される
- エラーが発生してもBotは停止しない

これで、Webダッシュボードへリアルタイムでデータが送信されるようになりました！
