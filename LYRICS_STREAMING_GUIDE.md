# リアルタイム歌詞配信システム 🎤

## 概要

LRCLIBから取得したタイムスタンプ付き歌詞を、Lavalinkの再生位置に合わせて0.1秒精度でリアルタイム配信するシステムです。

## 主な機能

### 1. 高精度歌詞配信
- **0.1秒間隔**で再生位置を監視
- **0.5秒のオフセット**で少し早めに送信
- Wavelinkの`player.position`を直接参照（Supabaseの5秒ラグを回避）

### 2. Supabaseレコード数管理
- 歌詞ログを自動的にSupabaseに保存
- **10万件を超えないよう自動削除**
- 100回の更新ごとにクリーンアップ実行
- 古い順（created_at）に削除

### 3. Webhook配信
- 曲名をWebhookの`username`に設定
- ジャケット画像を`avatar_url`に設定
- 専用チャンネル`lyrics-stream`に配信

### 4. スラッシュコマンド
- `/lyrics_mode on` - 歌詞配信を有効化
- `/lyrics_mode off` - 歌詞配信を無効化

## セットアップ

### 1. Supabaseテーブルの作成

Supabase SQL Editorで`bot/add_lyrics_table.sql`を実行：

```sql
-- 歌詞ログテーブル
CREATE TABLE lyrics_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    lyrics_text TEXT NOT NULL,
    timestamp_sec REAL NOT NULL,
    track_title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. Botの起動

Cogは自動的に読み込まれます：

```python
# bot/main.py で自動読み込み
await bot.load_extension('cogs.lyrics_streamer')
```

## 使用方法

### 1. 歌詞配信を有効化

Discordで：
```
/lyrics_mode on
```

→ `lyrics-stream`チャンネルが自動作成されます

### 2. 音楽を再生

通常通り音楽を再生：
```
/play query:YOASOBI アイドル
```

→ 歌詞が自動的に`lyrics-stream`に配信されます

### 3. 歌詞配信を無効化

```
/lyrics_mode off
```

## 技術仕様

### LRC形式のパース

```python
# [mm:ss.xx] text の形式
pattern = re.compile(r'\[(\d+):(\d+)\.(\d+)\](.+)')

# 例: [00:15.50]歌詞のテキスト
# → timestamp: 15.5秒
```

### 配信タイミング

```python
# 0.1秒ごとにチェック
@tasks.loop(seconds=0.1)
async def lyrics_stream_loop(self):
    position = vc.position / 1000.0  # ミリ秒→秒
    
    # 0.5秒早めに送信
    if position >= (line.timestamp - OFFSET):
        await send_lyrics_line(line)
```

### レコード数管理

```python
# 100回の更新ごとにクリーンアップ
self.update_counter += 1

if self.update_counter >= 100:
    # レコード数をチェック
    if total_count > 100000:
        delete_count = total_count - 100000
        
        # 古い順に削除
        old_records = client.table('lyrics_logs')\
            .select('id')\
            .order('created_at', desc=False)\
            .limit(delete_count)\
            .execute()
        
        # バッチ削除（1000件ずつ）
        for batch in batches(ids_to_delete, 1000):
            client.table('lyrics_logs')\
                .delete()\
                .in_('id', batch)\
                .execute()
```

## ファイル構成

```
bot/
├── cogs/
│   ├── lyrics_streamer.py      # 歌詞配信システム
│   └── music_player.py         # 音楽プレイヤー（統合済み）
├── add_lyrics_table.sql        # Supabaseテーブル定義
└── supabase_client.py          # Supabaseクライアント
```

## クラス構造

### LyricsLine
```python
class LyricsLine:
    timestamp: float  # 秒数
    text: str         # 歌詞テキスト
    sent: bool        # 送信済みフラグ
```

### LyricsStreamer (Cog)
```python
class LyricsStreamer(commands.Cog):
    # 状態管理
    lyrics_enabled: Dict[int, bool]              # guild_id -> enabled
    lyrics_channels: Dict[int, int]              # guild_id -> channel_id
    lyrics_webhooks: Dict[int, Webhook]          # guild_id -> webhook
    current_lyrics: Dict[int, List[LyricsLine]]  # guild_id -> lyrics
    current_track_info: Dict[int, Dict]          # guild_id -> track info
    lyrics_index: Dict[int, int]                 # guild_id -> current index
    
    # メソッド
    async def fetch_lyrics(track, artist, duration) -> List[LyricsLine]
    async def start_lyrics_for_track(guild_id, track)
    async def stop_lyrics_for_guild(guild_id)
    async def _cleanup_old_records()
```

## LRCLIB API

### エンドポイント
```
GET https://lrclib.net/api/get
```

### パラメータ
```python
params = {
    'track_name': 'アイドル',
    'artist_name': 'YOASOBI',
    'duration': 210  # 秒
}
```

### レスポンス
```json
{
  "syncedLyrics": "[00:15.50]歌詞のテキスト\n[00:20.30]次の行\n...",
  "plainLyrics": "歌詞のテキスト\n次の行\n..."
}
```

## パフォーマンス

### メモリ使用量
- 1曲あたり約10-50KB（歌詞の長さによる）
- 100ギルドで同時再生しても5MB以下

### CPU使用量
- 0.1秒ループは軽量（1%未満）
- 歌詞送信時のみWebhook API呼び出し

### データベース
- 100回の更新ごとにクリーンアップ
- バッチ削除で効率化（1000件ずつ）
- インデックスで高速検索

## トラブルシューティング

### 歌詞が表示されない

1. **LRCLIB APIの確認**
   ```python
   # ログを確認
   # "No synced lyrics available" → 歌詞が存在しない
   # "LRCLIB returned 404" → 曲が見つからない
   ```

2. **Webhook の確認**
   ```python
   # Webhookが作成されているか確認
   webhooks = await channel.webhooks()
   ```

3. **再生位置の確認**
   ```python
   # player.position が正しく取得できているか
   logger.info(f"Position: {vc.position}ms")
   ```

### レコード数が増え続ける

1. **クリーンアップの確認**
   ```python
   # ログを確認
   # "Cleaning up X old lyrics records..." が表示されるか
   ```

2. **手動クリーンアップ**
   ```sql
   -- Supabase SQL Editorで実行
   DELETE FROM lyrics_logs 
   WHERE created_at < NOW() - INTERVAL '7 days';
   ```

### Webhook エラー

1. **権限の確認**
   - Botに`MANAGE_WEBHOOKS`権限があるか
   - チャンネルに`SEND_MESSAGES`権限があるか

2. **レート制限**
   - Webhookは1秒に5回まで
   - 0.1秒ループでも歌詞は数秒に1回なので問題なし

## 今後の改善案

1. **歌詞の翻訳**
   - Gemini APIで自動翻訳
   - 日本語⇔英語

2. **カラオケモード**
   - 現在の行をハイライト
   - 次の行をプレビュー

3. **歌詞の編集**
   - ユーザーが歌詞を修正
   - コミュニティで共有

4. **統計情報**
   - 最も再生された曲
   - 歌詞の人気ランキング

## 関連ファイル

- `bot/cogs/lyrics_streamer.py` - 歌詞配信システム
- `bot/cogs/music_player.py` - 音楽プレイヤー統合
- `bot/add_lyrics_table.sql` - Supabaseテーブル定義
- `bot/supabase_client.py` - Supabaseクライアント

---

実装日: 2026-01-24
