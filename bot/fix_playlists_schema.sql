-- プレイリストテーブルのスキーマ修正
-- Supabaseのスキーマキャッシュをリフレッシュするため、テーブルを再作成

-- 既存のプレイリストテーブルを削除（データも削除されます）
DROP TABLE IF EXISTS playlist_tracks CASCADE;
DROP TABLE IF EXISTS playlists CASCADE;

-- プレイリストテーブルを再作成
CREATE TABLE playlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    creator_id TEXT NOT NULL,
    creator_name TEXT NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_playlists_guild_id ON playlists(guild_id, created_at DESC);
CREATE INDEX idx_playlists_creator_id ON playlists(creator_id);

-- プレイリスト曲テーブルを再作成
CREATE TABLE playlist_tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    playlist_id UUID NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    track_title TEXT NOT NULL,
    track_url TEXT NOT NULL,
    track_author TEXT,
    duration_ms INTEGER DEFAULT 0,
    added_by TEXT NOT NULL,
    added_by_id TEXT NOT NULL,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_playlist_tracks_playlist_id ON playlist_tracks(playlist_id, position);
CREATE INDEX idx_playlist_tracks_added_by ON playlist_tracks(added_by_id);

-- Row Level Security (RLS) の設定
ALTER TABLE playlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE playlist_tracks ENABLE ROW LEVEL SECURITY;

-- 読み取り専用ポリシー（認証済みユーザー）
CREATE POLICY "Allow authenticated read access" ON playlists FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON playlist_tracks FOR SELECT TO authenticated USING (true);

-- Bot用の書き込みポリシー（service_roleキーを使用）
CREATE POLICY "Allow service role full access" ON playlists FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON playlist_tracks FOR ALL TO service_role USING (true);

-- 完了メッセージ
SELECT 'Playlists tables recreated successfully!' AS status;
