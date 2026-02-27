-- Supabaseで実行するSQL: 古いログを削除する関数
-- この関数を作成してから、Pythonコードから呼び出します

CREATE OR REPLACE FUNCTION delete_old_logs(delete_count INTEGER)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  DELETE FROM bot_logs
  WHERE id IN (
    SELECT id
    FROM bot_logs
    ORDER BY created_at ASC
    LIMIT delete_count
  );
END;
$$;

-- 使用例:
-- SELECT delete_old_logs(10000); -- 古い順に10000件削除
