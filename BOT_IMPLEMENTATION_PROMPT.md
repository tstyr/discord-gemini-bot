# Discord Bot → Supabase連携実装プロンプト

このプロンプトをAIに渡して、discord-gemini-botにSupabase連携機能を追加してください。

---

## 🤖 AIへの指示

以下の要件に従って、Discord BotにSupabase連携機能を実装してください。

### 📋 実装要件

#### 1. 環境設定

**`.env`ファイルに以下を追加**:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

**`requirements.txt`に以下を追加**:
```
supabase-py>=2.0.0
python-dotenv>=1.0.0
psutil>=5.9.0
```

#### 2. Supabaseクライアントの作成

**ファイル**: `supabase_client.py`

```python
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
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Supabase client initialized")
```

#### 3. システム統計の送信（5分ごと）

**実装場所**: メインBotファイルまたは新規ファイル`dashboard_sync.py`

```python
import psutil
from discord.ext import tasks
from supabase_client import supabase

@tasks.loop(minutes=5)
async def send_system_stats(bot):
    """5分ごとにシステム統計をSupabaseに送信"""
    if not supabase:
        return
    
    try:
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # メモリ使用量（MB）
        process = psutil.Process()
        memory_info = process.memory_info()
        ram_rss = memory_info.rss / (1024 * 1024)  # MB
        ram_heap = memory_info.vms / (1024 * 1024)  # MB
        
        # Discord Gateway Ping
        ping_gateway = round(bot.latency * 1000)  # ms
        
        # データ送信
        data = {
            "cpu_usage": cpu_usage,
            "ram_rss": ram_rss,
            "ram_heap": ram_heap,
            "ping_gateway": ping_gateway,
            "ping_lavalink": None  # Lavalinkを使用している場合は設定
        }
        
        result = supabase.table("system_stats").insert(data).execute()
        print(f"✅ System stats sent: CPU={cpu_usage}%, RAM={ram_rss:.1f}MB, Ping={ping_gateway}ms")
        
    except Exception as e:
        print(f"❌ Error sending system stats: {e}")

# Bot起動時に開始
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    send_system_stats.start(bot)
```

#### 4. Gemini API使用ログの記録

**実装場所**: Gemini APIを呼び出している関数

```python
from supabase_client import supabase

async def log_gemini_usage(guild_id: str, user_id: str, response):
    """Gemini API使用ログをSupabaseに記録"""
    if not supabase:
        return
    
    try:
        # Gemini APIレスポンスからトークン数を取得
        usage = response.usage_metadata
        
        data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "prompt_tokens": usage.prompt_token_count,
            "completion_tokens": usage.candidates_token_count,
            "total_tokens": usage.total_token_count,
            "model": "gemini-pro"  # 使用しているモデル名
        }
        
        result = supabase.table("gemini_usage").insert(data).execute()
        print(f"✅ Gemini usage logged: {usage.total_token_count} tokens")
        
    except Exception as e:
        print(f"❌ Error logging Gemini usage: {e}")

# 使用例：Gemini APIレスポンス後に呼び出す
# response = await gemini_model.generate_content(prompt)
# await log_gemini_usage(str(ctx.guild.id), str(ctx.author.id), response)
```

#### 5. 音楽再生ログの記録

**実装場所**: 音楽再生コマンド（`play`コマンドなど）

```python
from supabase_client import supabase

async def log_music_play(guild_id: str, track_title: str, track_url: str, 
                        duration_ms: int, requested_by: str):
    """音楽再生ログをSupabaseに記録"""
    if not supabase:
        return
    
    try:
        data = {
            "guild_id": guild_id,
            "track_title": track_title,
            "track_url": track_url,
            "duration_ms": duration_ms,
            "requested_by": requested_by
        }
        
        result = supabase.table("music_history").insert(data).execute()
        print(f"✅ Music play logged: {track_title}")
        
    except Exception as e:
        print(f"❌ Error logging music play: {e}")

# 使用例：音楽再生開始時
# await log_music_play(
#     guild_id=str(ctx.guild.id),
#     track_title=track.title,
#     track_url=track.uri,
#     duration_ms=track.length,
#     requested_by=str(ctx.author.name)
# )
```

#### 6. アクティブセッションの更新

**実装場所**: 音楽再生状態が変わるたびに呼び出す

```python
from supabase_client import supabase

async def update_active_session(guild_id: str, track_title: str = None, 
                               position_ms: int = 0, duration_ms: int = 0, 
                               is_playing: bool = True):
    """アクティブセッション情報を更新"""
    if not supabase:
        return
    
    try:
        data = {
            "guild_id": guild_id,
            "track_title": track_title,
            "position_ms": position_ms,
            "duration_ms": duration_ms,
            "is_playing": is_playing
        }
        
        # upsert: 存在すれば更新、なければ挿入
        result = supabase.table("active_sessions").upsert(data).execute()
        print(f"✅ Active session updated: {track_title}")
        
    except Exception as e:
        print(f"❌ Error updating active session: {e}")

async def remove_active_session(guild_id: str):
    """アクティブセッションを削除（音楽停止時）"""
    if not supabase:
        return
    
    try:
        result = supabase.table("active_sessions").delete().eq("guild_id", guild_id).execute()
        print(f"✅ Active session removed for guild {guild_id}")
        
    except Exception as e:
        print(f"❌ Error removing active session: {e}")

# 使用例：
# 再生開始時
# await update_active_session(
#     guild_id=str(ctx.guild.id),
#     track_title=track.title,
#     position_ms=0,
#     duration_ms=track.length,
#     is_playing=True
# )
#
# 停止時
# await remove_active_session(guild_id=str(ctx.guild.id))
```

#### 7. Botログの送信

**実装場所**: エラーハンドラーや重要なイベント

```python
from supabase_client import supabase

async def log_bot_event(level: str, message: str):
    """BotログをSupabaseに送信"""
    if not supabase:
        return
    
    try:
        data = {
            "level": level,  # "INFO", "WARNING", "ERROR"
            "message": message
        }
        
        result = supabase.table("bot_logs").insert(data).execute()
        
    except Exception as e:
        print(f"❌ Error logging bot event: {e}")

# 使用例：
# await log_bot_event("INFO", "Bot started successfully")
# await log_bot_event("ERROR", f"Failed to play track: {error}")
# await log_bot_event("WARNING", "High memory usage detected")
```

#### 8. コマンドキューの監視（オプション）

**実装場所**: バックグラウンドタスク

```python
from discord.ext import tasks
from supabase_client import supabase

@tasks.loop(seconds=5)
async def check_command_queue(bot):
    """5秒ごとにコマンドキューをチェック"""
    if not supabase:
        return
    
    try:
        # pending状態のコマンドを取得
        result = supabase.table("command_queue")\
            .select("*")\
            .eq("status", "pending")\
            .execute()
        
        for command in result.data:
            command_id = command["id"]
            command_name = command["command"]
            payload = command["payload"]
            
            print(f"📥 Received command: {command_name}")
            
            # コマンドを処理中に変更
            supabase.table("command_queue")\
                .update({"status": "processing"})\
                .eq("id", command_id)\
                .execute()
            
            # コマンドを実行
            try:
                if command_name == "pause":
                    # 一時停止処理
                    guild_id = payload.get("guild_id")
                    # voice_client.pause()
                    status = "completed"
                    
                elif command_name == "resume":
                    # 再開処理
                    guild_id = payload.get("guild_id")
                    # voice_client.resume()
                    status = "completed"
                    
                elif command_name == "skip":
                    # スキップ処理
                    guild_id = payload.get("guild_id")
                    # voice_client.skip()
                    status = "completed"
                    
                else:
                    status = "failed"
                
                # ステータスを更新
                supabase.table("command_queue")\
                    .update({"status": status})\
                    .eq("id", command_id)\
                    .execute()
                    
            except Exception as e:
                print(f"❌ Error executing command: {e}")
                supabase.table("command_queue")\
                    .update({"status": "failed"})\
                    .eq("id", command_id)\
                    .execute()
                
    except Exception as e:
        print(f"❌ Error checking command queue: {e}")

# Bot起動時に開始
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_command_queue.start(bot)
```

---

## 📝 実装チェックリスト

実装が完了したら、以下を確認してください：

- [ ] `supabase-py`と`python-dotenv`をインストール
- [ ] `.env`にSupabase認証情報を追加
- [ ] `supabase_client.py`を作成
- [ ] システム統計の5分ごとの送信を実装
- [ ] Gemini API使用時のログ記録を実装
- [ ] 音楽再生時のログ記録を実装
- [ ] アクティブセッションの更新を実装
- [ ] Botログの送信を実装
- [ ] （オプション）コマンドキューの監視を実装

---

## 🧪 テスト方法

### 1. Bot起動テスト
```bash
python bot.py
```

起動時に以下が表示されることを確認：
```
✅ Supabase client initialized
Logged in as YourBot#1234
✅ System stats sent: CPU=45.2%, RAM=128.5MB, Ping=50ms
```

### 2. 機能テスト

#### Gemini API使用テスト
Discordで任意のコマンドを実行：
```
/chat こんにちは
```

コンソールに表示されることを確認：
```
✅ Gemini usage logged: 150 tokens
```

#### 音楽再生テスト
Discordで音楽を再生：
```
/play 曲名
```

コンソールに表示されることを確認：
```
✅ Music play logged: 曲名
✅ Active session updated: 曲名
```

### 3. ダッシュボードで確認

Webダッシュボードにアクセス：
```
https://your-dashboard.vercel.app/dashboard
```

以下が表示されることを確認：
- システム統計（CPU、RAM、Ping）
- アクティブセッション（再生中の曲）
- ライブコンソール（Botログ）

---

## 🔧 トラブルシューティング

### データが送信されない場合

1. **環境変数を確認**
```python
import os
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY')[:20]}...")
```

2. **Supabase接続をテスト**
```python
from supabase_client import supabase

result = supabase.table("system_stats").select("*").limit(1).execute()
print(f"Connection test: {result.data}")
```

3. **RLSを無効化（開発中）**
Supabaseダッシュボード → Database → Tables → 各テーブル → RLS disabled

4. **エラーログを確認**
```python
try:
    result = supabase.table("system_stats").insert(data).execute()
except Exception as e:
    print(f"Error details: {e}")
    import traceback
    traceback.print_exc()
```

---

## 📚 参考資料

- **Bot実装ガイド**: `bot-integration/BOT_IMPLEMENTATION_GUIDE.md`
- **サンプルコード**: `bot-integration/bot_example.py`
- **Supabaseクライアント**: `bot-integration/supabase_client.py`
- **データベーススキーマ**: `database.sql`

---

## 🎯 期待される結果

実装完了後、以下が自動的に動作します：

1. **5分ごと**: システム統計がダッシュボードに表示
2. **Gemini使用時**: 会話ログが記録され、Analyticsに反映
3. **音楽再生時**: 再生履歴が記録され、ランキングに反映
4. **リアルタイム**: ダッシュボードが10秒ごとに自動更新
5. **遠隔操作**: ダッシュボードから音楽を制御可能（オプション）

---

## ✅ 完成！

このプロンプトに従って実装すれば、BotとダッシュボードがSupabaseを通じて完全に連携します。

質問がある場合は、`bot-integration/BOT_IMPLEMENTATION_GUIDE.md`を参照してください。
