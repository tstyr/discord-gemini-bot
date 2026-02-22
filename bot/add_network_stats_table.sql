-- ネットワーク統計テーブルを作成
-- Supabase SQL Editorで実行してください

-- ネットワーク統計テーブル
CREATE TABLE IF NOT EXISTS network_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bytes_sent BIGINT NOT NULL,           -- 送信バイト数
    bytes_recv BIGINT NOT NULL,           -- 受信バイト数
    bytes_total BIGINT NOT NULL,          -- 合計バイト数
    mb_sent REAL NOT NULL,                -- 送信MB
    mb_recv REAL NOT NULL,                -- 受信MB
    mb_total REAL NOT NULL,               -- 合計MB
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_network_stats_recorded_at 
    ON network_stats(recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_network_stats_created_at 
    ON network_stats(created_at DESC);

-- RLS設定
ALTER TABLE network_stats ENABLE ROW LEVEL SECURITY;

-- 既存のポリシーを削除（存在する場合のみ）
DO $$ 
BEGIN
    DROP POLICY IF EXISTS "Allow authenticated read access" ON network_stats;
    DROP POLICY IF EXISTS "Allow service role full access" ON network_stats;
EXCEPTION
    WHEN undefined_table THEN NULL;
END $$;

-- 読み取り専用ポリシー（認証済みユーザー）
CREATE POLICY "Allow authenticated read access" ON network_stats 
    FOR SELECT TO authenticated USING (true);

-- Bot用の書き込みポリシー（service_roleキーを使用）
CREATE POLICY "Allow service role full access" ON network_stats 
    FOR ALL TO service_role USING (true);

-- 完了メッセージ
SELECT 'Network stats table created successfully!' AS status;
