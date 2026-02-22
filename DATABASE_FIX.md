# 🔧 データベース問題の修正ガイド

## 問題

- ✅ Botは動作している
- ✅ AIは反応する
- ❌ ダッシュボードにデータが表示されない
- ❌ データベースに会話記録が保存されていない

---

## 原因

1. **DATABASE_URLが設定されていない**
2. **PostgreSQLデータベースが作成されていない**
3. **VercelとKoyebが異なるデータベースを参照している**

---

## 🚀 修正手順

### ステップ1: 無料PostgreSQLデータベースを作成

#### Supabase（推奨）

1. [Supabase](https://supabase.com) にアクセス
2. 「New Project」をクリック
3. プロジェクト名を入力（例: `discord-bot-db`）
4. データベースパスワードを設定（メモする！）
5. リージョン: **Tokyo** を選択
6. 「Create new project」をクリック
7. 作成完了まで1-2分待つ

#### 接続URLを取得

1. Supabaseダッシュボード → Settings → Database
2. 「Connection string」セクションの「URI」をコピー
3. `[YOUR-PASSWORD]`を実際のパスワードに置き換え

```
postgresql://postgres.xxxxx:パスワード@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

---

### ステップ2: Koyebに環境変数を設定

Koyeb → あなたのサービス → Settings → Environment variables

```bash
DATABASE_URL=postgresql://postgres.xxxxx:パスワード@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

**重要**: 上記のURLを実際のSupabaseのURLに置き換えてください！

---

### ステップ3: Vercelに環境変数を設定

Vercel → あなたのプロジェクト → Settings → Environment Variables

```bash
# KoyebのURL（必ず https:// で始まる）
NEXT_PUBLIC_API_URL=https://あなたのKoyebアプリ名.koyeb.app

# WebSocket URL（必ず wss:// で始まる）
NEXT_PUBLIC_WS_URL=wss://あなたのKoyebアプリ名.koyeb.app/ws
```

**重要**: 
- `http://` ではなく `https://` を使用
- `ws://` ではなく `wss://` を使用
- `あなたのKoyebアプリ名`を実際のアプリ名に置き換え

---

### ステップ4: Redeploy

#### Koyeb
1. Koyebダッシュボードで「Redeploy」をクリック
2. ログを確認:
   ```
   ✅ PostgreSQL database initialized
   ✅ Bot setup completed
   ```

#### Vercel
1. Vercelダッシュボードで「Redeploy」をクリック
2. デプロイ完了を待つ

---

### ステップ5: 動作確認

#### Botで会話する

Discordのチャットチャンネルで:
```
こんにちは
```

Botが返信したら成功！

#### ダッシュボードを確認

1. Vercelのダッシュボードを開く
2. 左側にユーザーアイコンが表示される
3. アイコンをクリックすると会話履歴が表示される

---

## 🔍 トラブルシューティング

### ❌ ダッシュボードに「データがありません」と表示される

**原因1**: DATABASE_URLが設定されていない

**解決策**:
1. Koyebのログを確認
2. `PostgreSQL database initialized` が表示されているか確認
3. 表示されていない場合、DATABASE_URLを設定してRedeploy

**原因2**: VercelのAPI URLが間違っている

**解決策**:
1. Vercelの環境変数を確認
2. `NEXT_PUBLIC_API_URL` が正しいKoyeb URLか確認
3. `https://` で始まっているか確認（`http://` ではない）
4. Redeployを実行

**原因3**: CORSエラー

**解決策**:
1. ブラウザの開発者ツール（F12）を開く
2. Consoleタブでエラーを確認
3. CORSエラーが表示されている場合:
   - KoyebのAPI_HOSTが`0.0.0.0`になっているか確認
   - Redeployを実行

### ❌ WebSocketが接続できない

**症状**: ダッシュボードの右上に赤い点が表示される

**解決策**:
1. Vercelの環境変数を確認
2. `NEXT_PUBLIC_WS_URL` が `wss://` で始まっているか確認
3. Koyebのアプリ名が正しいか確認
4. Redeployを実行

### ❌ データベース接続エラー

**症状**: Koyebログに `Failed to connect to database` が表示される

**解決策**:
1. DATABASE_URLが正しいか確認
2. パスワードが正しいか確認
3. Supabaseのプロジェクトが起動しているか確認
4. 接続URLを再度コピーして設定

---

## 📝 環境変数チェックリスト

### Koyeb

- [ ] `DISCORD_TOKEN` - Discordボットトークン
- [ ] `GEMINI_API_KEY` - Gemini APIキー
- [ ] `DATABASE_URL` - PostgreSQL接続URL（**最重要！**）
- [ ] `LAVALINK_HOST` - lavalinkv4.serenetia.com
- [ ] `LAVALINK_PORT` - 443
- [ ] `LAVALINK_PASSWORD` - https://dsc.gg/ajidevserver
- [ ] `LAVALINK_SECURE` - true
- [ ] `API_HOST` - 0.0.0.0
- [ ] `API_PORT` - 8000

### Vercel

- [ ] `NEXT_PUBLIC_API_URL` - https://あなたのKoyebアプリ名.koyeb.app
- [ ] `NEXT_PUBLIC_WS_URL` - wss://あなたのKoyebアプリ名.koyeb.app/ws

---

## 🎯 最重要ポイント

### データベースが動かない原因の99%

```bash
DATABASE_URL=postgresql://...
```

この1行が設定されていないと、データベースは動作しません。

### ダッシュボードが動かない原因の99%

```bash
# Vercelの環境変数
NEXT_PUBLIC_API_URL=https://あなたのKoyebアプリ名.koyeb.app
NEXT_PUBLIC_WS_URL=wss://あなたのKoyebアプリ名.koyeb.app/ws
```

- `https://` と `wss://` を使用（`http://` や `ws://` ではない）
- 実際のKoyebアプリ名に置き換える

---

## ✅ 成功の確認

すべて正常に動作している場合:

1. ✅ Discordでメッセージを送信
2. ✅ Botが返信する
3. ✅ Vercelダッシュボードを開く
4. ✅ 左側にユーザーアイコンが表示される
5. ✅ アイコンをクリックすると会話履歴が表示される
6. ✅ 統計情報が更新される

おめでとうございます！🎉

---

## 💡 デバッグ方法

### Koyebログの確認

```
Koyeb → あなたのサービス → Logs
```

確認すべきログ:
```
✅ PostgreSQL database initialized
✅ Saved chat log for ユーザー名
✅ Bot setup completed
```

### Vercelログの確認

```
Vercel → あなたのプロジェクト → Deployments → 最新のデプロイ → View Function Logs
```

### ブラウザ開発者ツール

1. ダッシュボードを開く
2. F12キーを押す
3. Consoleタブを確認
4. エラーメッセージを確認

---

## 📞 それでも動かない場合

1. Koyebのログをすべてコピー
2. Vercelのログをすべてコピー
3. ブラウザのConsoleエラーをコピー
4. 環境変数のスクリーンショットを撮る
5. DATABASE_URLが正しく設定されているか再確認
