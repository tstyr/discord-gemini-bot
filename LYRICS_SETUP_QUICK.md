# 歌詞配信システム - クイックセットアップ 🎤

## エラー: relation "lyrics_logs" does not exist

このエラーは、Supabaseに`lyrics_logs`テーブルが作成されていないことを示しています。

## 解決方法（2つの方法）

### 方法1: シンプル版（推奨）

最もシンプルで確実な方法です。

#### ステップ1: テーブルを作成

Supabase SQL Editorで以下を実行：

```sql
-- テーブル作成
CREATE TABLE IF NOT EXISTS lyrics_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    lyrics_text TEXT NOT NULL,
    timestamp_sec REAL NOT NULL,
    track_title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_guild_id ON lyrics_logs(guild_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_created_at ON lyrics_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_track_title ON lyrics_logs(track_title);

-- RLS有効化
ALTER TABLE lyrics_logs ENABLE ROW LEVEL SECURITY;

-- 完了
SELECT 'Table created!' AS status;
```

#### ステップ2: ポリシーを作成

次に、以下を実行：

```sql
-- ポリシーが存在する場合は削除
DROP POLICY IF EXISTS "Allow authenticated read access" ON lyrics_logs;
DROP POLICY IF EXISTS "Allow service role full access" ON lyrics_logs;

-- 読み取り専用ポリシー
CREATE POLICY "Allow authenticated read access" ON lyrics_logs 
    FOR SELECT TO authenticated USING (true);

-- Bot用の書き込みポリシー
CREATE POLICY "Allow service role full access" ON lyrics_logs 
    FOR ALL TO service_role USING (true);

-- 完了
SELECT 'Policies created!' AS status;
```

### 方法2: 完全版（1回で実行）

### 方法2: 完全版（1回で実行）

#### Supabase SQL Editorで実行

```sql
-- 歌詞ログテーブルを作成
CREATE TABLE IF NOT EXISTS lyrics_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    lyrics_text TEXT NOT NULL,
    timestamp_sec REAL NOT NULL,
    track_title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_guild_id ON lyrics_logs(guild_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_created_at ON lyrics_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_track_title ON lyrics_logs(track_title);

-- RLS有効化
ALTER TABLE lyrics_logs ENABLE ROW LEVEL SECURITY;

-- ポリシー削除（エラーを無視）
DO $$ 
BEGIN
    DROP POLICY IF EXISTS "Allow authenticated read access" ON lyrics_logs;
    DROP POLICY IF EXISTS "Allow service role full access" ON lyrics_logs;
EXCEPTION
    WHEN undefined_table THEN NULL;
END $$;

-- ポリシー作成
CREATE POLICY "Allow authenticated read access" ON lyrics_logs 
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow service role full access" ON lyrics_logs 
    FOR ALL TO service_role USING (true);

-- 完了
SELECT 'Lyrics logs table created successfully!' AS status;
```

---

## 使用方法

テーブル作成後、Discordで：

```
/lyrics_mode on
```

→ `lyrics-stream`チャンネルが自動作成され、歌詞配信が開始されます。

## テーブルが正しく作成されたか確認

Supabase SQL Editorで：

```sql
-- テーブル構造を確認
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'lyrics_logs';
```

期待される結果：
```
column_name     | data_type
----------------|------------------
id              | uuid
guild_id        | text
lyrics_text     | text
timestamp_sec   | real
track_title     | text
created_at      | timestamp with time zone
```

## トラブルシューティング

### エラー: "permission denied for table lyrics_logs"

→ RLSポリシーの問題です。以下を確認：

1. **SUPABASE_KEY**が`service_role`キーか確認
   - `.env`ファイルを確認
   - `SUPABASE_KEY`は`service_role`キー（長いキー）を使用

2. **ポリシーを再作成**
   ```sql
   -- 既存のポリシーを削除
   DROP POLICY IF EXISTS "Allow service role full access" ON lyrics_logs;
   
   -- 再作成
   CREATE POLICY "Allow service role full access" ON lyrics_logs 
       FOR ALL TO service_role USING (true);
   ```

### エラー: "Could not find the 'lyrics_text' column"

→ スキーマキャッシュの問題です：

1. **Supabaseプロジェクトを再起動**
   - Settings → General → Pause project
   - 数秒待つ
   - Resume project

2. **Botを再起動**

### 歌詞が配信されない

1. **LRCLIB APIの確認**
   - ログに「No synced lyrics available」と表示される場合、その曲には歌詞がありません
   - 別の曲で試してください

2. **Webhookの確認**
   - `lyrics-stream`チャンネルが作成されているか
   - Botに`MANAGE_WEBHOOKS`権限があるか

## 完全なスキーマ（参考）

すべてのテーブルを一度に作成したい場合は、`bot/supabase_schema_clean.sql`を実行してください。

## 関連ファイル

- `bot/add_lyrics_table.sql` - 歌詞テーブルのみ作成
- `bot/supabase_schema_clean.sql` - 全テーブル作成
- `LYRICS_STREAMING_GUIDE.md` - 完全ガイド

---

セットアップ完了後、`/lyrics_mode on`で歌詞配信を開始できます！
