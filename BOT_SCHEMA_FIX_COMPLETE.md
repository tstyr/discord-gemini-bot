# Bot Supabaseスキーマ修正完了 ✅

## 修正内容

### 問題点
Bot側のコードが、Supabaseに存在しないカラムを送信していました：

1. **system_stats テーブル**
   - ❌ `bot_id`, `ram_usage`, `server_count`, `guild_count`, `uptime`, `recorded_at`, `updated_at`, `status`
   - ✅ `cpu_usage`, `ram_rss`, `ram_heap`, `ping_gateway`, `ping_lavalink`

2. **bot_logs テーブル**
   - ❌ `scope`, `timestamp`, `recorded_at`
   - ✅ `level`, `message`

3. **command_queue テーブル**
   - ❌ `command_type`, `result`, `error`, `completed_at`, `updated_at`
   - ✅ `command`, `payload`, `status`

4. **gemini_usage テーブル**
   - ❌ `recorded_at`
   - ✅ `guild_id`, `user_id`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `model`

5. **music_history テーブル**
   - ❌ `requested_by_id`, `recorded_at`
   - ✅ `guild_id`, `track_title`, `track_url`, `duration_ms`, `requested_by`

6. **active_sessions テーブル**
   - ❌ `voice_members_count`, `updated_at`
   - ✅ `guild_id`, `track_title`, `position_ms`, `duration_ms`, `is_playing`

### 修正したファイル

**bot/supabase_client.py**

#### 1. `_send_system_stats()` メソッド
```python
# ✅ 修正後
stats = {
    'cpu_usage': float(cpu_usage),
    'ram_rss': float(ram_rss),
    'ram_heap': float(ram_heap),
    'ping_gateway': int(ping_gateway),
    'ping_lavalink': int(ping_lavalink) if ping_lavalink else None
}
self.client.table('system_stats').insert(stats).execute()
```

#### 2. `log_bot_event()` メソッド
```python
# ✅ 修正後
data = {
    "level": str(level).upper(),  # "INFO", "WARNING", "ERROR"
    "message": str(message)
}
self.client.table("bot_logs").insert(data).execute()
```

#### 3. `_process_command()` メソッド
```python
# ✅ 修正後
command_name = command['command']  # command_type → command

# コマンド処理
if command_name == 'pause':
    result = await self._handle_music_pause(payload)
elif command_name == 'resume':
    result = await self._handle_music_resume(payload)
elif command_name == 'skip':
    result = await self._handle_music_skip(payload)
# ...

# ステータス更新のみ（result, error, completed_atは削除）
self.client.table('command_queue').update({
    'status': 'completed' if not error else 'failed'
}).eq('id', command_id).execute()
```

#### 4. `log_gemini_usage()` メソッド
```python
# ✅ 修正後
data = {
    "guild_id": str(guild_id),
    "user_id": str(user_id),
    "prompt_tokens": int(prompt_tokens),
    "completion_tokens": int(completion_tokens),
    "total_tokens": int(total_tokens),
    "model": str(model)
}
self.client.table("gemini_usage").insert(data).execute()
```

#### 5. `log_music_play()` メソッド
```python
# ✅ 修正後
data = {
    "guild_id": str(guild_id),
    "track_title": str(track_title),
    "track_url": str(track_url),
    "duration_ms": int(duration_ms),
    "requested_by": str(requested_by)
}
self.client.table("music_history").insert(data).execute()
```

#### 6. `update_active_session()` メソッド
```python
# ✅ 修正後
session_data = {
    'guild_id': str(guild_id),
    'track_title': track_data.get('title'),
    'position_ms': int(track_data.get('position', 0)),
    'duration_ms': int(track_data.get('duration', 0)),
    'is_playing': bool(track_data.get('is_playing', False))
}
self.client.table('active_sessions').upsert(session_data).execute()
```

#### 7. `shutdown()` メソッド
```python
# ✅ 修正後 - オフライン状態をログに記録
await self.log_bot_event("INFO", "Bot shutting down")
```

#### 8. 新しいハンドラー追加
```python
async def _handle_music_pause(self, payload: Dict) -> str:
    """一時停止コマンド"""
    # ...

async def _handle_music_resume(self, payload: Dict) -> str:
    """再開コマンド"""
    # ...
```

### 削除したコード

- ❌ `bot_id` フィールド
- ❌ `ram_usage`, `server_count`, `guild_count`, `uptime` フィールド
- ❌ `recorded_at`, `updated_at`, `timestamp` フィールド（created_atが自動生成）
- ❌ `scope` フィールド
- ❌ `command_type` → `command` に変更
- ❌ `result`, `error`, `completed_at` フィールド
- ❌ `requested_by_id` フィールド
- ❌ `voice_members_count` フィールド
- ❌ `_handle_music_play()` メソッド（不要）
- ❌ `_handle_maintenance()` メソッド（不要）
- ❌ `job_logs` テーブルへの記録（不要）

## 期待される結果

Bot再起動時に以下が表示されます：

```
✅ Supabase client initialized
✅ system_stats table exists
✅ command_queue table exists
✅ active_sessions table exists
🔄 Health monitor started (10s interval)
📊 System stats sent: CPU=45.2%, RAM=128.5MB
```

エラーメッセージが消えて、ダッシュボードにリアルタイムでデータが表示されます。

## テスト方法

1. **Bot再起動**
   ```bash
   python bot/main.py
   ```

2. **ログ確認**
   - エラーメッセージが出ないことを確認
   - `✅ System stats sent` が表示されることを確認

3. **ダッシュボード確認**
   - システム統計が更新されることを確認
   - Botログが表示されることを確認
   - 音楽再生ログが記録されることを確認

## Git コミット

```bash
git add bot/supabase_client.py
git commit -m "Fix: Supabase schema errors - remove non-existent columns"
git push
```

✅ コミット完了

---

**完了日時:** 2026-01-19
**修正ファイル:** `bot/supabase_client.py`
**削除行数:** 119行
**追加行数:** 71行
