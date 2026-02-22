# プレイリストスキーマ修正ガイド

## 問題

```
Error creating playlist: {'message': "Could not find the 'creator_id' column of 'playlists' in the schema cache", 'code': 'PGRST204'}
```

Supabaseのスキーマキャッシュが古く、`creator_id`カラムを認識していない。

## 解決方法

### 方法1: Supabase SQL Editorで修正（推奨）

1. **Supabaseダッシュボードにアクセス**
   - https://supabase.com/dashboard にログイン
   - プロジェクトを選択

2. **SQL Editorを開く**
   - 左メニューから「SQL Editor」をクリック
   - 「New query」をクリック

3. **修正SQLを実行**
   - `bot/fix_playlists_schema.sql` の内容をコピー
   - SQL Editorに貼り付け
   - 「Run」をクリック

4. **結果を確認**
   ```
   status: "Playlists tables recreated successfully!"
   ```

5. **Botを再起動**
   - Heroku/Koyeb/Renderなどでデプロイしている場合は再起動
   - ローカルの場合は `python bot/main.py` を再実行

### 方法2: スキーマキャッシュをリフレッシュ

Supabaseのスキーマキャッシュをリフレッシュする方法:

1. **Supabaseダッシュボード**
   - Settings → API → Schema cache
   - 「Refresh schema cache」をクリック

2. **または、テーブルを一度削除して再作成**
   ```sql
   -- Table Editorで playlists テーブルを削除
   -- その後、supabase_schema_clean.sql を再実行
   ```

### 方法3: 既存データを保持したまま修正

既にプレイリストデータがある場合:

```sql
-- 1. 既存データをバックアップ
CREATE TABLE playlists_backup AS SELECT * FROM playlists;
CREATE TABLE playlist_tracks_backup AS SELECT * FROM playlist_tracks;

-- 2. テーブルを削除
DROP TABLE IF EXISTS playlist_tracks CASCADE;
DROP TABLE IF EXISTS playlists CASCADE;

-- 3. 新しいスキーマで再作成（fix_playlists_schema.sql を実行）

-- 4. データを復元
INSERT INTO playlists SELECT * FROM playlists_backup;
INSERT INTO playlist_tracks SELECT * FROM playlist_tracks_backup;

-- 5. バックアップテーブルを削除
DROP TABLE playlists_backup;
DROP TABLE playlist_tracks_backup;
```

## 確認方法

### 1. Supabaseでテーブル構造を確認

```sql
-- playlists テーブルのカラムを確認
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'playlists';
```

期待される結果:
```
column_name     | data_type
----------------|------------------
id              | uuid
guild_id        | text
name            | text
description     | text
creator_id      | text  ← これが必要
creator_name    | text
is_public       | boolean
created_at      | timestamp with time zone
updated_at      | timestamp with time zone
```

### 2. Botでプレイリスト作成をテスト

Discordで:
```
/playlist create name:テストプレイリスト
```

成功すると:
```
✅ プレイリストを作成しました
テストプレイリスト
作成者: あなたの名前
```

## トラブルシューティング

### エラー: "relation 'playlists' does not exist"

→ テーブルが存在しません。`supabase_schema_clean.sql` を実行してください。

### エラー: "permission denied for table playlists"

→ RLSポリシーの問題です。以下を確認:
1. `SUPABASE_SERVICE_ROLE_KEY` を使用しているか（`SUPABASE_KEY`ではない）
2. ポリシーが正しく設定されているか

```sql
-- ポリシーを確認
SELECT * FROM pg_policies WHERE tablename = 'playlists';
```

### エラー: "Could not find the 'creator_id' column"（まだ出る場合）

1. **Supabaseプロジェクトを再起動**
   - Settings → General → Pause project
   - 数秒待つ
   - Resume project

2. **APIキーを再生成**
   - Settings → API → Reset service_role key
   - 新しいキーを `.env` に設定

3. **Botを完全に再起動**

## 予防策

今後同様の問題を防ぐために:

1. **スキーマ変更時は必ずSupabaseで実行**
   - ローカルのSQLファイルだけでなく、Supabaseでも実行

2. **マイグレーションスクリプトを使用**
   - スキーマ変更は段階的に実行
   - ALTER TABLE を使用して既存データを保持

3. **定期的にスキーマキャッシュをリフレッシュ**
   - 大きな変更後は必ずリフレッシュ

## 関連ファイル

- `bot/supabase_schema_clean.sql` - 完全なスキーマ定義
- `bot/fix_playlists_schema.sql` - プレイリストテーブル修正用
- `bot/cogs/playlist_manager.py` - プレイリスト管理コード

---

修正日: 2026-01-24
