# 🚀 Vercel環境変数設定ガイド

## あなたのKoyeb URL

```
https://dying-nana-haklab-3e0dcb62.koyeb.app
```

---

## ✅ Vercelで設定する環境変数

Vercel → あなたのプロジェクト → Settings → Environment Variables

### 環境変数1: API URL

```
Name: NEXT_PUBLIC_API_URL
Value: https://dying-nana-haklab-3e0dcb62.koyeb.app
```

### 環境変数2: WebSocket URL

```
Name: NEXT_PUBLIC_WS_URL
Value: wss://dying-nana-haklab-3e0dcb62.koyeb.app/ws
```

---

## 📝 設定手順

1. [Vercel Dashboard](https://vercel.com/dashboard) にアクセス
2. あなたのプロジェクトをクリック
3. 上部メニューの「Settings」をクリック
4. 左メニューの「Environment Variables」をクリック
5. 「Add New」をクリック

### 1つ目の環境変数

- **Name**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://dying-nana-haklab-3e0dcb62.koyeb.app`
- **Environment**: Production, Preview, Development すべてチェック
- 「Save」をクリック

### 2つ目の環境変数

- **Name**: `NEXT_PUBLIC_WS_URL`
- **Value**: `wss://dying-nana-haklab-3e0dcb62.koyeb.app/ws`
- **Environment**: Production, Preview, Development すべてチェック
- 「Save」をクリック

---

## 🔄 Redeploy

環境変数を設定したら:

1. Vercel Dashboard → あなたのプロジェクト
2. 「Deployments」タブをクリック
3. 最新のデプロイの右側の「...」メニューをクリック
4. 「Redeploy」をクリック
5. 「Redeploy」を再度クリックして確認

---

## ✅ 動作確認

### 1. Koyeb APIの確認

ブラウザで以下にアクセス:
```
https://dying-nana-haklab-3e0dcb62.koyeb.app/api/health
```

表示されるべき内容:
```json
{
  "status": "healthy",
  "bot_ready": true,
  "guilds": 1,
  "websocket_connections": 0
}
```

### 2. Vercelダッシュボードの確認

1. Vercelのデプロイが完了するまで待つ（1-2分）
2. Vercelのダッシュボード URLを開く
3. 右上に緑の点（接続中）が表示される
4. 左側にユーザーアイコンが表示される

---

## 🔍 トラブルシューティング

### ❌ "Failed to fetch" エラー

**原因**: 環境変数が反映されていない

**解決策**:
1. Vercel → Settings → Environment Variables で確認
2. 両方の環境変数が設定されているか確認
3. Redeployを実行

### ❌ WebSocketが接続できない（赤い点）

**原因**: WebSocket URLが間違っている

**解決策**:
1. `NEXT_PUBLIC_WS_URL` が `wss://` で始まっているか確認
2. `/ws` が末尾についているか確認
3. Redeployを実行

### ❌ CORSエラー

**原因**: KoyebのAPIサーバーが起動していない

**解決策**:
1. Koyeb → Logs を確認
2. `Starting API server on 0.0.0.0:8000` が表示されているか確認
3. Koyebで環境変数を確認してRedeploy

---

## 📋 チェックリスト

- [ ] Vercelで `NEXT_PUBLIC_API_URL` を設定
- [ ] Vercelで `NEXT_PUBLIC_WS_URL` を設定
- [ ] 両方の環境変数で Production, Preview, Development をチェック
- [ ] Vercelで Redeploy を実行
- [ ] デプロイ完了を待つ（1-2分）
- [ ] Koyeb API (`/api/health`) にアクセスして確認
- [ ] Vercelダッシュボードを開いて確認
- [ ] 右上に緑の点が表示される
- [ ] 左側にユーザーアイコンが表示される

---

## 🎯 成功の確認

すべて正常に動作している場合:

1. ✅ Koyeb API が `{"status": "healthy"}` を返す
2. ✅ Vercelダッシュボードが開く
3. ✅ 右上に緑の点（WebSocket接続中）
4. ✅ 左側にユーザーアイコンが表示される
5. ✅ アイコンをクリックすると会話履歴が表示される

おめでとうございます！🎉
