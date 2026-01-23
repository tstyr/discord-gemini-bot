# Bot側スキーマ修正プロンプト

以下のプロンプトをAIに渡して、Bot側のSupabase連携コードを修正してください。

---

## 🤖 AIへの指示

discord-gemini-botのSupabase連携コードにスキーマエラーがあります。以下の修正を行ってください。

### 問題

現在のコードが、存在しないカラムを送信しようとしています：

1. **bot_logs テーブル**: `scope`, `timestamp` カラムが存在しない
2. **system_stats テーブル**: `bot_id` カラムが存在しない
3. **command_queue テーブル**: `command_type` カラムが存在しない

### 正しいスキーマ

#### bot_logs テーブル
```sql
CREATE TABLE bot_logs (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  level TEXT,           -- "INFO", "WARNING", "ERROR"
  message TEXT,         -- ログメッセージ
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**送信するデータ**:
```python
{
    "level": "INFO",
    "message": "Bot started"
}
```

#### system_stats テーブル
```sql
CREATE TABLE system_stats (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  cpu_usage NUMERIC,
  ram_rss NUMERIC,
  ram_heap NUMERIC,
  ping_gateway INT,
  ping_lavalink INT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**送信するデータ**:
```python
{
    "cpu_usage": 45.2,
    "ram_rss": 128.5,
    "ram_heap": 256.3,
    "ping_gateway": 50,
    "ping_lavalink": 30  # または None
}
```

#### command_queue テーブル
```sql
CREATE TABLE command_queue (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  command TEXT NOT NULL,
  payload JSONB,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**取得するデータ**:
```python
{
    "id": "uuid",
    "command": "pause",  # コマンド名
    "payload": {...},    # コマンドのパラメータ
    "status": "pending"
}
```

### 修正内容

#### 1. supabase_client.py を以下のコードに置き換えてください

```python
"""
Supabase Client for Discord Bot Dashboard
ダッシュボードのスキーマに完全対応
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("⚠️ Warning: Supabase credentials not found in .env")
    supabase = None
else:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        supabase = None


def send_system_stats(cpu_usage, ram_rss, ram_heap, ping_gateway, ping_lavalink=None):
    """システム統計をSupabaseに送信"""
    if not supabase:
        return None
    
    try:
        data = {
            "cpu_usage": float(cpu_usage),
            "ram_rss": float(ram_rss),
            "ram_heap": float(ram_heap),
            "ping_gateway": int(ping_gateway),
            "ping_lavalink": int(ping_lavalink) if ping_lavalink else None
        }
        
        result = supabase.table("system_stats").insert(data).execute()
        print(f"✅ System stats sent: CPU={cpu_usage:.1f}%, RAM={ram_rss:.1f}MB")
        return result
        
    except Exception as e:
        print(f"❌ Failed to send system stats: {e}")
        return None


def log_bot_event(level, message):
    """BotログをSupabaseに送信"""
    if not supabase:
        return None
    
    try:
        data = {
            "level": str(level).upper(),
            "message": str(message)
        }
        
        result = supabase.table("bot_logs").insert(data).execute()
        return result
        
    except Exception as e:
        print(f"❌ Failed to log event: {e}")
        return None


def log_gemini_usage(guild_id, user_id, prompt_tokens, completion_tokens, total_tokens, model="gemini-pro"):
    """Gemini API使用ログを記録"""
    if not supabase:
        return None
    
    try:
        data = {
            "guild_id": str(guild_id),
            "user_id": str(user_id),
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "total_tokens": int(total_tokens),
            "model": str(model)
        }
        
        result = supabase.table("gemini_usage").insert(data).execute()
        print(f"✅ Gemini usage logged: {total_tokens} tokens")
        return result
        
    except Exception as e:
        print(f"❌ Failed to log Gemini usage: {e}")
        return None


def log_music_play(guild_id, track_title, track_url, duration_ms, requested_by):
    """音楽再生ログを記録"""
    if not supabase:
        return None
    
    try:
        data = {
            "guild_id": str(guild_id),
            "track_title": str(track_title),
            "track_url": str(track_url),
            "duration_ms": int(duration_ms),
            "requested_by": str(requested_by)
        }
        
        result = supabase.table("music_history").insert(data).execute()
        print(f"✅ Music play logged: {track_title}")
        return result
        
    except Exception as e:
        print(f"❌ Failed to log music play: {e}")
        return None


def update_active_session(guild_id, track_title=None, position_ms=0, duration_ms=0, is_playing=True):
    """アクティブセッション情報を更新"""
    if not supabase:
        return None
    
    try:
        data = {
            "guild_id": str(guild_id),
            "track_title": str(track_title) if track_title else None,
            "position_ms": int(position_ms),
            "duration_ms": int(duration_ms),
            "is_playing": bool(is_playing)
        }
        
        result = supabase.table("active_sessions").upsert(data).execute()
        print(f"✅ Active session updated: {track_title}")
        return result
        
    except Exception as e:
        print(f"❌ Failed to update active session: {e}")
        return None


def remove_active_session(guild_id):
    """アクティブセッションを削除"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("active_sessions").delete().eq("guild_id", str(guild_id)).execute()
        print(f"✅ Active session removed")
        return result
        
    except Exception as e:
        print(f"❌ Failed to remove active session: {e}")
        return None


def get_pending_commands():
    """pending状態のコマンドを取得"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("command_queue")\
            .select("*")\
            .eq("status", "pending")\
            .order("created_at", desc=False)\
            .limit(10)\
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"❌ Failed to get pending commands: {e}")
        return []


def update_command_status(command_id, status):
    """コマンドのステータスを更新"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("command_queue")\
            .update({"status": str(status)})\
            .eq("id", str(command_id))\
            .execute()
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to update command status: {e}")
        return None
```

#### 2. メインBotファイルで以下のように使用してください

```python
import psutil
from discord.ext import tasks
from supabase_client import (
    send_system_stats,
    log_bot_event,
    log_gemini_usage,
    log_music_play,
    update_active_session,
    remove_active_session,
    get_pending_commands,
    update_command_status
)

# Bot起動時
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # システム統計送信タスクを開始
    system_stats_task.start(bot)
    
    # コマンドキュー監視タスクを開始
    command_queue_task.start()
    
    # 起動ログを送信
    log_bot_event("INFO", f"Bot started: {bot.user}")


# システム統計送信タスク（5分ごと）
@tasks.loop(minutes=5)
async def system_stats_task(bot):
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        process = psutil.Process()
        memory_info = process.memory_info()
        ram_rss = memory_info.rss / (1024 * 1024)  # MB
        ram_heap = memory_info.vms / (1024 * 1024)  # MB
        ping_gateway = round(bot.latency * 1000)  # ms
        
        send_system_stats(
            cpu_usage=cpu_usage,
            ram_rss=ram_rss,
            ram_heap=ram_heap,
            ping_gateway=ping_gateway,
            ping_lavalink=None
        )
        
    except Exception as e:
        print(f"Error in system stats task: {e}")


# コマンドキュー監視タスク（5秒ごと）
@tasks.loop(seconds=5)
async def command_queue_task():
    try:
        commands = get_pending_commands()
        
        for cmd in commands:
            command_id = cmd["id"]
            command = cmd["command"]  # ✅ 正しい
            payload = cmd.get("payload", {})
            
            print(f"📥 Received command: {command}")
            
            # 処理中に変更
            update_command_status(command_id, "processing")
            
            try:
                # コマンドを実行
                if command == "pause":
                    # 一時停止処理
                    pass
                elif command == "resume":
                    # 再開処理
                    pass
                elif command == "skip":
                    # スキップ処理
                    pass
                
                # 完了
                update_command_status(command_id, "completed")
                
            except Exception as e:
                print(f"Error executing command: {e}")
                update_command_status(command_id, "failed")
                
    except Exception as e:
        print(f"Error in command queue task: {e}")


# Gemini API使用時
async def chat_command(ctx, message):
    try:
        # Gemini APIを呼び出す
        response = await gemini_model.generate_content(message)
        
        # ログを記録
        log_gemini_usage(
            guild_id=str(ctx.guild.id),
            user_id=str(ctx.author.id),
            prompt_tokens=response.usage_metadata.prompt_token_count,
            completion_tokens=response.usage_metadata.candidates_token_count,
            total_tokens=response.usage_metadata.total_token_count,
            model="gemini-pro"
        )
        
        await ctx.send(response.text)
        
    except Exception as e:
        log_bot_event("ERROR", f"Chat command error: {e}")


# 音楽再生時
async def play_command(ctx, query):
    try:
        # 曲を検索・再生
        track = await search_track(query)
        
        # 再生ログを記録
        log_music_play(
            guild_id=str(ctx.guild.id),
            track_title=track.title,
            track_url=track.uri,
            duration_ms=track.length,
            requested_by=str(ctx.author.name)
        )
        
        # アクティブセッションを更新
        update_active_session(
            guild_id=str(ctx.guild.id),
            track_title=track.title,
            position_ms=0,
            duration_ms=track.length,
            is_playing=True
        )
        
        await ctx.send(f"🎵 再生中: {track.title}")
        
    except Exception as e:
        log_bot_event("ERROR", f"Play command error: {e}")


# 音楽停止時
async def stop_command(ctx):
    try:
        # 音楽を停止
        voice_client.stop()
        
        # アクティブセッションを削除
        remove_active_session(guild_id=str(ctx.guild.id))
        
        await ctx.send("⏹️ 停止しました")
        
    except Exception as e:
        log_bot_event("ERROR", f"Stop command error: {e}")
```

### 削除すべきコード

以下のコードを見つけて削除してください：

```python
# ❌ 削除
data = {
    "bot_id": "...",  # 存在しないカラム
    "scope": "...",   # 存在しないカラム
    "timestamp": "...",  # 存在しないカラム（created_atが自動）
}

# ❌ 削除
command_type = cmd["command_type"]  # 存在しないカラム
```

### 確認方法

修正後、Bot再起動時に以下が表示されればOK：

```
✅ Supabase client initialized
Logged in as YourBot#1234
✅ System stats sent: CPU=45.2%, RAM=128.5MB
```

エラーメッセージが消えて、ダッシュボードにデータが表示されます。

### トラブルシューティング

もしまだエラーが出る場合：

1. **エラーメッセージを確認**
   - どのカラムが見つからないか確認

2. **送信しているデータを確認**
   ```python
   print(f"Sending data: {data}")
   ```

3. **Supabaseのテーブル構造を確認**
   - Supabaseダッシュボード → Table Editor
   - 各テーブルのカラムを確認

---

## ✅ 完了

この修正により、Bot側のコードがダッシュボードのデータベーススキーマと完全に一致します。

エラーが消えて、リアルタイムでデータが表示されるようになります！
