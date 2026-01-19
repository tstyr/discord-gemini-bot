-- Supabase テーブル定義
-- このSQLをSupabaseのSQL Editorで実行してください

-- 1. システム統計テーブル（10秒間隔で履歴保存）
CREATE TABLE IF NOT EXISTS system_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id TEXT DEFAULT 'primary',
    cpu_usage REAL DEFAULT 0,
    ram_usage REAL DEFAULT 0,
    memory_rss REAL DEFAULT 0,
    memory_heap REAL DEFAULT 0,
    ping_gateway REAL DEFAULT 0,
    ping_lavalink REAL DEFAULT 0,
    server_count INTEGER DEFAULT 0,
    guild_count INTEGER DEFAULT 0,
    uptime INTEGER DEFAULT 0,
    status TEXT DEFAULT 'online',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_system_stats_timestamp ON system_stats(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_stats_bot_id ON system_stats(bot_id, timestamp DESC);

-- 2. 会話ログテーブル
CREATE TABLE IF NOT EXISTS conversation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_conversation_logs_user_id ON conversation_logs(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_logs_timestamp ON conversation_logs(timestamp DESC);

-- 3. 音楽ログテーブル
CREATE TABLE IF NOT EXISTS music_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    song_title TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    requested_by_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_music_logs_guild_id ON music_logs(guild_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_music_logs_timestamp ON music_logs(timestamp DESC);

-- 4. 音楽再生履歴テーブル（詳細版）
CREATE TABLE IF NOT EXISTS music_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    track_title TEXT NOT NULL,
    track_url TEXT,
    duration_ms INTEGER DEFAULT 0,
    requested_by TEXT NOT NULL,
    requested_by_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_music_history_guild_id ON music_history(guild_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_music_history_timestamp ON music_history(timestamp DESC);

-- 5. Gemini使用ログテーブル
CREATE TABLE IF NOT EXISTS gemini_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guild_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    model TEXT DEFAULT 'gemini-pro',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_gemini_usage_guild_id ON gemini_usage(guild_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_gemini_usage_user_id ON gemini_usage(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_gemini_usage_timestamp ON gemini_usage(timestamp DESC);

-- 4. コマンドキューテーブル（Realtime対応）
CREATE TABLE IF NOT EXISTS command_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    command_type TEXT NOT NULL,
    payload JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    result TEXT,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Realtimeを有効化
ALTER PUBLICATION supabase_realtime ADD TABLE command_queue;

-- インデックス
CREATE INDEX IF NOT EXISTS idx_command_queue_status ON command_queue(status, created_at);

-- 5. アクティブセッションテーブル
CREATE TABLE IF NOT EXISTS active_sessions (
    guild_id TEXT PRIMARY KEY,
    track_title TEXT,
    position_ms INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    is_playing BOOLEAN DEFAULT FALSE,
    voice_members_count INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. ジョブログテーブル
CREATE TABLE IF NOT EXISTS job_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    command_id UUID REFERENCES command_queue(id),
    command_type TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_job_logs_command_id ON job_logs(command_id);
CREATE INDEX IF NOT EXISTS idx_job_logs_created_at ON job_logs(created_at DESC);

-- 7. Botログテーブル
CREATE TABLE IF NOT EXISTS bot_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level TEXT NOT NULL CHECK (level IN ('debug', 'info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    scope TEXT DEFAULT 'general',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_bot_logs_level ON bot_logs(level, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bot_logs_scope ON bot_logs(scope, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bot_logs_created_at ON bot_logs(created_at DESC);

-- 古いログを自動削除する関数（オプション）
CREATE OR REPLACE FUNCTION delete_old_logs()
RETURNS void AS $$
BEGIN
    -- 30日以上前のログを削除
    DELETE FROM bot_logs WHERE created_at < NOW() - INTERVAL '30 days';
    DELETE FROM job_logs WHERE created_at < NOW() - INTERVAL '30 days';
    DELETE FROM conversation_logs WHERE created_at < NOW() - INTERVAL '90 days';
    DELETE FROM music_logs WHERE created_at < NOW() - INTERVAL '90 days';
    DELETE FROM music_history WHERE created_at < NOW() - INTERVAL '90 days';
    DELETE FROM gemini_usage WHERE created_at < NOW() - INTERVAL '90 days';
    -- システム統計は7日以上前を削除（データ量が多いため）
    DELETE FROM system_stats WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- 定期実行（毎日午前3時）
-- SELECT cron.schedule('delete-old-logs', '0 3 * * *', 'SELECT delete_old_logs()');

-- Row Level Security (RLS) の設定
ALTER TABLE system_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE music_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE music_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE gemini_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE command_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE active_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_logs ENABLE ROW LEVEL SECURITY;

-- 読み取り専用ポリシー（認証済みユーザー）
CREATE POLICY "Allow authenticated read access" ON system_stats FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON conversation_logs FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON music_logs FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON music_history FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON gemini_usage FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON command_queue FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON active_sessions FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON job_logs FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated read access" ON bot_logs FOR SELECT TO authenticated USING (true);

-- Bot用の書き込みポリシー（service_roleキーを使用）
CREATE POLICY "Allow service role full access" ON system_stats FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON conversation_logs FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON music_logs FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON music_history FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON gemini_usage FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON command_queue FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON active_sessions FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON job_logs FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role full access" ON bot_logs FOR ALL TO service_role USING (true);

-- ダッシュボード用のコマンド挿入ポリシー
CREATE POLICY "Allow authenticated insert commands" ON command_queue FOR INSERT TO authenticated WITH CHECK (true);

-- 完了
SELECT 'Supabase schema created successfully!' AS status;
