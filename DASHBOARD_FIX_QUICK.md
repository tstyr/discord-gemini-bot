# 🚨 ダッシュボードが更新されない - 緊急修正

## 問題

- ✅ Botは動作している
- ✅ AIは反応する
- ❌ Vercelダッシュボードにデータが表示されない
- ❌ 会話記録がDBに保存されていない

---

## 🔥 5分で修正

### 1. DATABASE_URLを設定

**Koyeb** → あなたのサービス → Settings → Environment variables

```bash
DATABASE_URL=postgresql://postgres.xxxxx:パスワード@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

**まだデータベースを作成していない場合:**

1. [Supabase](https://supabase.com) にアクセス
2. 「New Project」→ プロジェクト名入力
3. パスワード設定（メモする！）
4. リージョン: Tokyo
5. 「Create new project」
6. Settings → Database → Connection string の URI をコピー
7. `[YOUR-PASSWORD]`を実際のパスワードに置き換え

### 2. VercelのAPI URLを修正

**Vercel** → あなたのプロジェクト → Settings → Environment Variables

```bash
# 必ず https:// を使用（http:// ではない）
NEXT_PUBLIC_API_URL=https://あなたのKoyebアプリ名.koyeb.app

# 必ず wss:// を使用（ws:// ではない）
NEXT_PUBLIC_WS_URL=wss://あなたのKoyebアプリ名.koyeb.app/ws
```

**重要**: 
- `http://` → `https://` に変更
- `ws://` → `wss://` に変更
- `あなたのKoyebアプリ名`を実際の名前に置き換え

### 3. Redeploy

1. **Koyeb**: 「Redeploy」をクリック
2. **Vercel**: 「Redeploy」をクリック

### 4. 確認

1. Discordでメッセージを送信
2. Botが返信する
3. Vercelダッシュボードを開く
4. 左側にユーザーアイコンが表示される

---

## 🔍 ログで確認

### Koyebログ

```
Koyeb → あなたのサービス → Logs
```

確認すべきログ:
```
✅ PostgreSQL database initialized successfully
✅ Database connection test: 1
✅ Chat log saved to PostgreSQL for ユーザー名
```

エラーログ:
```
❌ Failed to initialize PostgreSQL
❌ Error saving chat log
```

→ DATABASE_URLが間違っているか、データベースが起動していない

### Vercelログ

ブラウザでF12を押して、Consoleタブを確認:

```
✅ 正常: WebSocket connected
❌ エラー: Failed to fetch
❌ エラー: CORS error
```

→ API URLが間違っているか、`https://`を使用していない

---

## 🧪 ローカルでテスト

```bash
cd bot
python test_database.py
```

出力:
```
✅ DATABASE_URL: postgresql://...
✅ データベース初期化成功
✅ テストデータ挿入成功
✅ 5件のログを取得
```

エラーが出る場合:
- DATABASE_URLが設定されているか確認
- データベースが起動しているか確認

---

## ❌ よくあるエラー

### エラー1: "Failed to fetch"

**原因**: VercelのAPI URLが間違っている

**解決策**:
```bash
# Vercelの環境変数を確認
NEXT_PUBLIC_API_URL=https://あなたのKoyebアプリ名.koyeb.app
```

- `https://` で始まっているか確認
- Koyebのアプリ名が正しいか確認

### エラー2: "CORS error"

**原因**: KoyebのAPI_HOSTが正しく設定されていない

**解決策**:
```bash
# Koyebの環境変数を確認
API_HOST=0.0.0.0
API_PORT=8000
```

### エラー3: "WebSocket connection failed"

**原因**: WebSocket URLが間違っている

**解決策**:
```bash
# Vercelの環境変数を確認
NEXT_PUBLIC_WS_URL=wss://あなたのKoyebアプリ名.koyeb.app/ws
```

- `wss://` で始まっているか確認（`ws://` ではない）

### エラー4: "Database connection failed"

**原因**: DATABASE_URLが間違っている

**解決策**:
1. Supabaseの接続URLを再度コピー
2. パスワードが正しいか確認
3. Koyebで設定してRedeploy

---

## ✅ チェックリスト

デプロイ前に確認:

### Koyeb
- [ ] `DATABASE_URL` が設定されている
- [ ] `API_HOST=0.0.0.0` が設定されている
- [ ] `API_PORT=8000` が設定されている
- [ ] Redeployを実行した
- [ ] ログで `PostgreSQL database initialized` を確認

### Vercel
- [ ] `NEXT_PUBLIC_API_URL` が `https://` で始まる
- [ ] `NEXT_PUBLIC_WS_URL` が `wss://` で始まる
- [ ] Koyebのアプリ名が正しい
- [ ] Redeployを実行した

### 動作確認
- [ ] Discordでメッセージを送信
- [ ] Botが返信する
- [ ] Koyebログで `Chat log saved` を確認
- [ ] Vercelダッシュボードを開く
- [ ] ユーザーアイコンが表示される
- [ ] アイコンをクリックすると会話が表示される

---

## 💡 最重要ポイント

### データベースが動かない原因

```bash
DATABASE_URL=postgresql://...
```

この1行が設定されていないと、データは保存されません。

### ダッシュボードが動かない原因

```bash
# http:// ではなく https://
NEXT_PUBLIC_API_URL=https://あなたのKoyebアプリ名.koyeb.app

# ws:// ではなく wss://
NEXT_PUBLIC_WS_URL=wss://あなたのKoyebアプリ名.koyeb.app/ws
```

`http://` や `ws://` を使用すると、ブラウザがブロックします。

---

## 📞 詳細ガイド

詳しい手順は `DATABASE_FIX.md` を参照してください。
