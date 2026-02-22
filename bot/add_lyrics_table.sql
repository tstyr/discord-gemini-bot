-- 歌詞ログテーブルを作成
-- Supabase SQL Editorで実行してください

-- 歌詞ログテーブル
CREATE TABLE IF NOT EXISTS lyrics_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    lyrics_text TEXT NOT NULL,
    timestamp_sec REAL NOT NULL,
    track_title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス（既に存在する場合はスキップ）
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_guild_id ON lyrics_logs(guild_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_created_at ON lyrics_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lyrics_logs_track_title ON lyrics_logs(track_title);

-- Row Level Security (RLS) の設定
ALTER TABLE lyrics_logs ENABLE ROW LEVEL SECURITY;

-- 既存のポリシーを削除（存在する場合のみ）
DO $$ 
BEGIN
    DROP POLICY IF EXISTS "Allow authenticated read access" ON lyrics_logs;
    DROP POLICY IF EXISTS "Allow service role full access" ON lyrics_logs;
EXCEPTION
    WHEN undefined_table THEN NULL;
END $$;

-- 読み取り専用ポリシー（認証済みユーザー）
CREATE POLICY "Allow authenticated read access" ON lyrics_logs 
    FOR SELECT TO authenticated USING (true);

-- Bot用の書き込みポリシー（service_roleキーを使用）
CREATE POLICY "Allow service role full access" ON lyrics_logs 
    FOR ALL TO service_role USING (true);

-- 完了メッセージ
SELECT 'Lyrics logs table created successfully!' AS status;
