-- 歌詞ログテーブルを追加

-- 既存のテーブルとポリシーを削除（存在する場合）
DROP POLICY IF EXISTS "Allow authenticated read access" ON lyrics_logs;
DROP POLICY IF EXISTS "Allow service role full access" ON lyrics_logs;
DROP TABLE IF EXISTS lyrics_logs CASCADE;

-- 歌詞ログテーブル
CREATE TABLE lyrics_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    lyrics_text TEXT NOT NULL,
    timestamp_sec REAL NOT NULL,
    track_title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_lyrics_logs_guild_id ON lyrics_logs(guild_id, created_at DESC);
CREATE INDEX idx_lyrics_logs_created_at ON lyrics_logs(created_at DESC);
CREATE INDEX idx_lyrics_logs_track_title ON lyrics_logs(track_title);

-- Row Level Security (RLS) の設定
ALTER TABLE lyrics_logs ENABLE ROW LEVEL SECURITY;

-- 読み取り専用ポリシー（認証済みユーザー）
CREATE POLICY "Allow authenticated read access" ON lyrics_logs 
    FOR SELECT TO authenticated USING (true);

-- Bot用の書き込みポリシー（service_roleキーを使用）
CREATE POLICY "Allow service role full access" ON lyrics_logs 
    FOR ALL TO service_role USING (true);

-- 完了メッセージ
SELECT 'Lyrics logs table created successfully!' AS status;
