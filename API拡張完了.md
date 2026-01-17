# 🎯 統計・履歴データベースとAPI拡張完了

## 実装した機能

### ✅ 1. データベーススキーマの拡張

#### 新しいテーブル: `playback_history`
```sql
CREATE TABLE playback_history (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    track_title TEXT NOT NULL,
    track_author TEXT,
    track_artwork TEXT,
    track_uri TEXT,
    track_length INTEGER,
    requester_id BIGINT,
    requester_name TEXT,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_playback_history_guild 
ON playback_history(guild_id, played_at DESC);
```

**保存される情報**:
- 曲名（track_title）
- アーティスト名（track_author）
- サムネイル（track_artwork）
- 曲のURI（track_uri）
- 曲の長さ（track_length）
- リクエスト者ID（requester_id）
- リクエスト者名（requester_name）
- 再生時刻（played_at）

---

### ✅ 2. データベースメソッドの追加

#### `save_playback_history()`
```python
await database.save_playback_history(
    guild_id=guild_id,
    track_title="曲名",
    track_author="アーティスト",
    track_artwork="https://...",
    track_uri="https://...",
    track_length=180000,
    requester_id=user_id,
    requester_name="ユーザー名"
)
```

#### `get_playback_history()`
```python
# 特定サーバーの履歴
history = await database.get_playback_history(guild_id=123, limit=10)

# 全サーバーの履歴
history = await database.get_playback_history(limit=10)
```

#### `get_global_stats()`
```python
stats = await database.get_global_stats()
# {
#     'total_messages': 1234,
#     'unique_users': 56,
#     'total_tokens': 123456,
#     'total_music': 89
# }
```

---

### ✅ 3. 音楽再生時の自動保存

**4箇所で再生履歴を自動保存**:
1. プレイリスト再生時
2. AI推薦曲再生時
3. トラック選択ビュー（メッセージから）
4. トラック選択ビュー（スラッシュコマンドから）

**実装箇所**: `bot/cogs/music_player.py`

```python
# 曲を再生するたびに自動保存
await self.bot.database.save_playback_history(
    guild_id=interaction.guild.id,
    track_title=track.title,
    track_author=getattr(track, 'author', 'Unknown'),
    track_artwork=getattr(track, 'artwork', None),
    track_uri=track.uri,
    track_length=track.length,
    requester_id=interaction.user.id,
    requester_name=interaction.user.display_name
)
```

---

### ✅ 4. 新しいAPIエンドポイント

#### 1. `GET /api/stats` - グローバル統計

**説明**: サーバー数、ユーザー数、総メッセージ数を返す

**レスポンス**:
```json
{
  "success": true,
  "data": {
    "servers": 2,
    "total_messages": 1234,
    "unique_users": 56,
    "total_tokens": 123456,
    "total_music": 89
  }
}
```

**使用例**:
```bash
curl https://dying-nana-haklab-3e0dcb62.koyeb.app/api/stats
```

---

#### 2. `GET /api/history` - 再生履歴

**説明**: 最新の再生履歴を返す（デフォルト10件）

**パラメータ**:
- `guild_id` (optional): 特定サーバーの履歴のみ取得
- `limit` (optional): 取得件数（デフォルト: 10）

**レスポンス**:
```json
{
  "success": true,
  "data": [
    {
      "id": "123",
      "guild_id": "456",
      "track_title": "曲名",
      "track_author": "アーティスト",
      "track_artwork": "https://...",
      "track_uri": "https://...",
      "track_length": 180000,
      "requester_id": "789",
      "requester_name": "ユーザー名",
      "played_at": "2026-01-17T12:34:56"
    }
  ]
}
```

**使用例**:
```bash
# 全サーバーの履歴
curl https://dying-nana-haklab-3e0dcb62.koyeb.app/api/history

# 特定サーバーの履歴（20件）
curl https://dying-nana-haklab-3e0dcb62.koyeb.app/api/history?guild_id=123&limit=20
```

---

#### 3. `GET /api/now-playing` - 現在再生中の曲

**説明**: 現在の再生状況（曲名、プログレスバー用秒数）を返す

**パラメータ**:
- `guild_id` (optional): 特定サーバーの再生状況のみ取得

**レスポンス（特定サーバー）**:
```json
{
  "success": true,
  "data": {
    "guild_id": "123",
    "guild_name": "サーバー名",
    "track_title": "曲名",
    "track_author": "アーティスト",
    "track_artwork": "https://...",
    "track_length": 180000,
    "position": 45000,
    "paused": false,
    "volume": 80
  }
}
```

**レスポンス（全サーバー）**:
```json
{
  "success": true,
  "data": [
    {
      "guild_id": "123",
      "guild_name": "サーバー1",
      "track_title": "曲名1",
      "track_author": "アーティスト1",
      "track_artwork": "https://...",
      "track_length": 180000,
      "position": 45000,
      "paused": false,
      "volume": 80
    },
    {
      "guild_id": "456",
      "guild_name": "サーバー2",
      "track_title": "曲名2",
      "track_author": "アーティスト2",
      "track_artwork": "https://...",
      "track_length": 240000,
      "position": 120000,
      "paused": false,
      "volume": 100
    }
  ]
}
```

**使用例**:
```bash
# 全サーバーの再生状況
curl https://dying-nana-haklab-3e0dcb62.koyeb.app/api/now-playing

# 特定サーバーの再生状況
curl https://dying-nana-haklab-3e0dcb62.koyeb.app/api/now-playing?guild_id=123
```

---

## データの流れ

### 1. 音楽再生時
```
ユーザーが /play コマンド実行
    ↓
曲を再生
    ↓
playback_history テーブルに保存
    ↓
daily_stats の music_count をインクリメント
```

### 2. 履歴取得時
```
ダッシュボードから /api/history にアクセス
    ↓
playback_history テーブルから取得
    ↓
JSON形式で返す
```

### 3. 現在再生中の曲取得時
```
ダッシュボードから /api/now-playing にアクセス
    ↓
Wavelinkから現在の再生状況を取得
    ↓
JSON形式で返す（position, length, paused など）
```

---

## プログレスバーの実装例

### フロントエンド（React/Next.js）
```typescript
interface NowPlaying {
  track_title: string;
  track_author: string;
  track_artwork: string;
  track_length: number;  // ミリ秒
  position: number;      // ミリ秒
  paused: boolean;
  volume: number;
}

function ProgressBar({ nowPlaying }: { nowPlaying: NowPlaying }) {
  const progress = (nowPlaying.position / nowPlaying.track_length) * 100;
  
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{formatTime(nowPlaying.position)}</span>
        <span>{formatTime(nowPlaying.track_length)}</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div 
          className="bg-discord-blurple h-2 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

function formatTime(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
```

---

## 使い方

### 1. Koyebにデプロイ
```bash
git push origin main
```

Koyebが自動的に再デプロイし、新しいテーブルが作成されます。

### 2. APIエンドポイントをテスト

#### グローバル統計
```bash
curl https://dying-nana-haklab-3e0dcb62.koyeb.app/api/stats
```

#### 再生履歴
```bash
curl https://dying-nana-haklab-3e0dcb62.koyeb.app/api/history?limit=5
```

#### 現在再生中
```bash
curl https://dying-nana-haklab-3e0dcb62.koyeb.app/api/now-playing
```

### 3. Discordで曲を再生
```
/play 曲名
```

再生履歴が自動的に保存されます。

### 4. ダッシュボードで確認
- 再生履歴が表示される
- 現在再生中の曲が表示される
- プログレスバーが動く

---

## データベーステーブル一覧

### 既存のテーブル
1. `chat_channels` - AI自動応答チャンネル
2. `ai_modes` - AIモード設定
3. `chat_logs` - チャットログ
4. `usage_logs` - 使用ログ
5. `music_channels` - 音楽チャンネル
6. `daily_stats` - 日次統計
7. `hourly_stats` - 時間別統計

### 新しいテーブル
8. `playback_history` - 再生履歴 ✨

---

## APIエンドポイント一覧

### 既存のエンドポイント
- `GET /api/health` - ヘルスチェック
- `GET /api/guilds` - サーバー一覧
- `GET /api/chat-logs` - チャットログ
- `GET /api/users` - ユーザー一覧
- `GET /api/guilds/{guild_id}/analytics` - サーバー分析
- `GET /api/guilds/{guild_id}/music/status` - 音楽ステータス
- `POST /api/guilds/{guild_id}/music/control` - 音楽コントロール

### 新しいエンドポイント
- `GET /api/stats` - グローバル統計 ✨
- `GET /api/history` - 再生履歴 ✨
- `GET /api/now-playing` - 現在再生中 ✨

---

## 完了した実装

✅ playback_history テーブルの追加
✅ 再生履歴の自動保存（4箇所）
✅ データベースメソッドの追加
✅ GET /api/stats エンドポイント
✅ GET /api/history エンドポイント
✅ GET /api/now-playing エンドポイント
✅ プログレスバー用のデータ提供

すべての機能が実装され、GitHubにプッシュされました！
Koyebが自動的に再デプロイします。
