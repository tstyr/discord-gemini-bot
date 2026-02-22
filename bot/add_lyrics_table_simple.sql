-- 歌詞ログテーブルを作成（シンプル版）
-- エラーが出る場合はこちらを使用してください

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
