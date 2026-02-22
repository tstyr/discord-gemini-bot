-- 歌詞ログテーブルのポリシーを作成
-- add_lyrics_table_simple.sql を実行した後に実行してください

-- 既存のポリシーを確認
SELECT policyname FROM pg_policies WHERE tablename = 'lyrics_logs';

-- ポリシーが存在する場合は削除
DROP POLICY IF EXISTS "Allow authenticated read access" ON lyrics_logs;
DROP POLICY IF EXISTS "Allow service role full access" ON lyrics_logs;

-- 読み取り専用ポリシー（認証済みユーザー）
CREATE POLICY "Allow authenticated read access" ON lyrics_logs 
    FOR SELECT TO authenticated USING (true);

-- Bot用の書き込みポリシー（service_roleキーを使用）
CREATE POLICY "Allow service role full access" ON lyrics_logs 
    FOR ALL TO service_role USING (true);

-- 確認
SELECT policyname, cmd FROM pg_policies WHERE tablename = 'lyrics_logs';

-- 完了
SELECT 'Policies created!' AS status;
