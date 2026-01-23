# 🔧 Bot側 Supabase データ送信修正プロンプト

## 🎯 問題

ダッシュボードはSupabaseからデータを受け取れているが、**0件**になっている。
Bot側がSupabaseにデータを送信していないか、スキーマが一致していない可能性があります。

---

## 📊 現在のBot実装の問題点

### 1. system_stats - 不足しているフィールド

**現在のBot側（`bot/supabase_client.py` 133行目）:**
```python
stats = {
    'cpu_usage': float(cpu_usage),
    'ram_rss': float(ram_rss),        # ❌ 間違い
    'ram_heap': float(ram_heap),      # ❌ 間違い
    'ping_gateway': int(ping_gateway),
    'ping_lavalink': int(ping_lavalink) if ping_lavalink else None
}
```

**問題:**
- ❌ `ram_usage` が不足（RAM使用率%）
- ❌ `memory_rss` ではなく `ram_rss`（カラム名が違う）
- ❌ `memory_heap` ではなく `ram_heap`（カラム名が違う）
- ❌ `server_count` が不足
- ❌ `guild_count` が不足
- ❌ `uptime` が不足
- ❌ `status` が不足

### 2. active_sessions - 不足しているフィールド

**現在のBot側（`bot/supabase_client.py` 331行目）:**
```python
session_data = {
    'guild_id': str(guild_id),
    'track_title': track_data.get('title'),
    'position_ms': int(track_data.get('position', 0)),
    'duration_ms': int(track_data.get('duration', 0)),
    'is_playing': bool(track_data.get('is_playing', False))
}
```

**問題:**
- ❌ `voice_members_count` が不足

### 3. music_history - 不足しているフィールド

**現在のBot側（`bot/supabase_client.py` 365行目）:**
```python
data = {
    "guild_id": str(guild_id),
    "track_title": str(track_title),
    "track_url": str(track_url),
    "duration_ms": int(duration_ms),
    "requested_by": str(requested_by)
}
```

**問題:**
- ❌ `requested_by_id` が不足

### 4. conversation_logs - recorded_at を手動設定

**現在のBot側（`bot/supabase_client.py` 391行目）:**
```python
self.client.table('conversation_logs').insert({
    'user_id': str(user_id),
    'user_name': user_name,
    'prompt': prompt,
    'response': response,
    'recorded_at': datetime.utcnow().isoformat()  # ⚠️ 不要（自動設定される）
}).execute()
```

**問題:**
- ⚠️ `recorded_at` は手動設定不要（Supabaseで自動設定）

---

## ✅ 修正版コード

### 修正1: system_stats の送信

**ファイル:** `bot/supabase_client.py`  
**行:** 95-145

```python
async def _send_system_stats(self):
    """システム統計をSupabaseに送信"""
    if not self.client or not self.is_running:
        return
    
    try:
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # システム全体のメモリ使用率
        memory = psutil.virtual_memory()
        ram_usage = memory.percent  # ✅ 追加: RAM使用率（%）
        
        # メモリ使用量（プロセス）
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_rss = memory_info.rss / 1024 / 1024  # MB (✅ 名前変更)
        memory_heap = memory_info.vms / 1024 / 1024  # MB (✅ 名前変更)
        
        # Discord Gateway Ping
        ping_gateway = round(self.bot.latency * 1000)  # ms
        
        # Lavalink Ping (音楽機能がある場合)
        ping_lavalink = 0  # デフォルト値
        try:
            if hasattr(self.bot, 'wavelink') and self.bot.wavelink:
                import wavelink
                nodes = wavelink.Pool.nodes
                if nodes:
                    node = list(nodes.values())[0]
                    ping_lavalink = round(node.latency * 1000) if node.latency else 0
        except Exception as e:
            logger.debug(f"Lavalink ping unavailable: {e}")
        
        # ✅ 正しいスキーマに合わせたデータ
        stats = {
            'cpu_usage': float(cpu_usage),
            'ram_usage': float(ram_usage),          # ✅ 追加
            'memory_rss': float(memory_rss),        # ✅ 名前変更
            'memory_heap': float(memory_heap),      # ✅ 名前変更
            'ping_gateway': float(ping_gateway),
            'ping_lavalink': float(ping_lavalink),
            'server_count': len(self.bot.guilds),   # ✅ 追加
            'guild_count': len(self.bot.guilds),    # ✅ 追加
            'uptime': int(time.time() - self.bot.start_time),  # ✅ 追加
            'status': 'online'                      # ✅ 追加
        }
        
        # INSERTでデータを追加（recorded_at, created_atは自動）
        self.client.table('system_stats').insert(stats).execute()
        
        logger.debug(f"📊 System stats sent: CPU={cpu_usage:.1f}%, RAM={ram_usage:.1f}%, Status=online")
        
    except Exception as e:
        logger.error(f"❌ Failed to send system stats: {e}")
        import traceback
        traceback.print_exc()
```

### 修正2: active_sessions の更新

**ファイル:** `bot/supabase_client.py`  
**行:** 320-345

```python
async def update_active_session(self, guild_id: int, track_data: Optional[Dict] = None):
    """アクティブセッション情報を更新"""
    if not self.client:
        return
    
    try:
        if track_data:
            # ✅ 正しいスキーマに合わせたデータ
            session_data = {
                'guild_id': str(guild_id),
                'track_title': track_data.get('title'),
                'position_ms': int(track_data.get('position', 0)),
                'duration_ms': int(track_data.get('duration', 0)),
                'is_playing': bool(track_data.get('is_playing', False)),
                'voice_members_count': int(track_data.get('members_count', 0))  # ✅ 追加
            }
            
            self.client.table('active_sessions').upsert(session_data).execute()
            logger.debug(f"📊 Active session updated for guild {guild_id}")
        else:
            # セッション終了
            self.client.table('active_sessions').delete().eq('guild_id', str(guild_id)).execute()
            logger.debug(f"📊 Active session cleared for guild {guild_id}")
            
    except Exception as e:
        logger.error(f"❌ Failed to update active session: {e}")
        import traceback
        traceback.print_exc()
```

### 修正3: music_history の記録

**ファイル:** `bot/supabase_client.py`  
**行:** 360-380

```python
async def log_music_play(self, guild_id: int, track_title: str, track_url: str,
                        duration_ms: int, requested_by: str, requested_by_id: int):
    """音楽再生ログをSupabaseに記録（music_history）"""
    if not self.client:
        return
    
    try:
        # ✅ 正しいスキーマに合わせたデータ
        data = {
            "guild_id": str(guild_id),
            "track_title": str(track_title),
            "track_url": str(track_url) if track_url else None,
            "duration_ms": int(duration_ms),
            "requested_by": str(requested_by),
            "requested_by_id": str(requested_by_id)  # ✅ 追加
        }
        
        self.client.table("music_history").insert(data).execute()
        logger.debug(f"🎵 Music history logged: {track_title}")
        
    except Exception as e:
        logger.error(f"❌ Failed to log music play: {e}")
        import traceback
        traceback.print_exc()
```

### 修正4: conversation_logs の記録

**ファイル:** `bot/supabase_client.py`  
**行:** 385-400

```python
async def save_conversation_log(self, user_id: int, user_name: str, prompt: str, response: str):
    """会話ログをSupabaseに保存"""
    if not self.client:
        return
    
    try:
        data = {
            'user_id': str(user_id),
            'user_name': user_name,
            'prompt': prompt,
            'response': response
            # ✅ recorded_at は削除（Supabaseで自動設定）
        }
        
        self.client.table('conversation_logs').insert(data).execute()
        logger.debug(f"💬 Conversation log saved for {user_name}")
    except Exception as e:
        logger.error(f"❌ Failed to save conversation log: {e}")
        import traceback
        traceback.print_exc()
```

### 修正5: music_logs の記録

**ファイル:** `bot/supabase_client.py`  
**行:** 402-420

```python
async def save_music_log(self, guild_id: int, song_title: str, requested_by: str, requested_by_id: int):
    """音楽ログをSupabaseに保存（music_logs）"""
    if not self.client:
        return
    
    try:
        data = {
            'guild_id': str(guild_id),
            'song_title': song_title,
            'requested_by': requested_by,
            'requested_by_id': str(requested_by_id)
            # ✅ recorded_at は削除（Supabaseで自動設定）
        }
        
        self.client.table('music_logs').insert(data).execute()
        logger.debug(f"🎵 Music log saved: {song_title} by {requested_by}")
    except Exception as e:
        logger.error(f"❌ Failed to save music log: {e}")
        import traceback
        traceback.print_exc()
```

---

## 🚀 実装手順

### ステップ1: bot/supabase_client.py を修正

上記の修正を適用してください。

### ステップ2: Botを再起動

```bash
# Koyebの場合
Koyeb Dashboard → Services → Redeploy

# ローカルの場合
python bot/main.py
```

### ステップ3: ログを確認

```bash
# Bot起動時のログ
✅ Supabase client initialized
✅ system_stats table exists
✅ conversation_logs table exists
✅ music_logs table exists
🔄 Health monitor started (10s interval)
📊 System stats sent: CPU=45.2%, RAM=60.5%, Status=online
```

### ステップ4: Supabaseでデータを確認

```sql
-- システム統計（最新1件）
SELECT * FROM system_stats ORDER BY recorded_at DESC LIMIT 1;

-- 会話ログ（最新5件）
SELECT * FROM conversation_logs ORDER BY recorded_at DESC LIMIT 5;

-- 音楽ログ（最新5件）
SELECT * FROM music_logs ORDER BY recorded_at DESC LIMIT 5;

-- Gemini使用統計（最新5件）
SELECT * FROM gemini_usage ORDER BY recorded_at DESC LIMIT 5;
```

### ステップ5: ダッシュボードで確認

1. ダッシュボードを開く
2. システム統計が表示される
3. 会話ログが表示される
4. 音楽ログが表示される

---

## 🔍 デバッグ方法

### 1. Bot側のログを確認

```python
# bot/supabase_client.py の各メソッドに以下を追加
logger.info(f"📤 Sending data: {data}")
```

### 2. Supabaseのログを確認

Supabase Dashboard → Logs → API Logs

### 3. エラーが出る場合

```python
# エラーの詳細を表示
except Exception as e:
    logger.error(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
```

### 4. データが送信されているか確認

```sql
-- 各テーブルの件数を確認
SELECT 
    'system_stats' as table_name, 
    COUNT(*) as count,
    MAX(recorded_at) as latest
FROM system_stats
UNION ALL
SELECT 'conversation_logs', COUNT(*), MAX(recorded_at) FROM conversation_logs
UNION ALL
SELECT 'music_logs', COUNT(*), MAX(recorded_at) FROM music_logs
UNION ALL
SELECT 'gemini_usage', COUNT(*), MAX(recorded_at) FROM gemini_usage;
```

---

## ✅ 確認チェックリスト

- [ ] `bot/supabase_client.py` を修正
- [ ] Botを再起動
- [ ] Bot起動ログで `✅ Supabase client initialized` を確認
- [ ] 10秒後に `📊 System stats sent` を確認
- [ ] Discordで会話してログを確認
- [ ] 音楽を再生してログを確認
- [ ] Supabaseでデータ件数を確認
- [ ] ダッシュボードでデータ表示を確認

---

## 🎯 重要なポイント

### カラム名の対応表

| 古いカラム名 | 新しいカラム名 | 説明 |
|------------|--------------|------|
| `ram_rss` | `memory_rss` | メモリRSS |
| `ram_heap` | `memory_heap` | メモリHeap |
| - | `ram_usage` | RAM使用率（新規） |
| - | `server_count` | サーバー数（新規） |
| - | `guild_count` | ギルド数（新規） |
| - | `uptime` | アップタイム（新規） |
| - | `status` | ステータス（新規） |
| - | `voice_members_count` | ボイスメンバー数（新規） |
| - | `requested_by_id` | リクエストユーザーID（新規） |

### recorded_at について

- ✅ Supabaseで自動設定される（`DEFAULT NOW()`）
- ❌ Bot側で手動設定する必要はない
- ✅ `created_at` も自動設定される

---

## 🔧 トラブルシューティング

### エラー: "column does not exist"

**原因**: カラム名が間違っている

**解決策**:
1. `bot/supabase_schema_clean.sql` を確認
2. カラム名を修正
3. Botを再起動

### エラー: "null value violates not-null constraint"

**原因**: 必須フィールドが送信されていない

**解決策**:
1. 全ての必須フィールドを送信
2. デフォルト値を設定

### データが0件のまま

**原因**: Bot側でエラーが発生している

**解決策**:
1. Bot側のログを確認
2. `traceback.print_exc()` でエラー詳細を表示
3. Supabase APIログを確認

### system_stats が送信されない

**原因**: `self.bot.start_time` が設定されていない

**解決策**:
```python
# bot/main.py の __init__ に追加
class DiscordBot(commands.Bot):
    def __init__(self):
        # ...
        self.start_time = time.time()  # ✅ 追加
```

---

## 🎉 完了！

これでBot側とダッシュボード側が完全に同期し、データが正しく表示されます。

**確認方法:**
1. Botでコマンドを実行
2. 10秒待つ（system_stats送信間隔）
3. ダッシュボードを確認
4. データが表示される

問題が解決しない場合は、Bot側のログとSupabaseのログを確認してください。
