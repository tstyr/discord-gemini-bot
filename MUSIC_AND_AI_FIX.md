# 🔧 音楽再生とAI自動応答の修正

## 問題

1. ❌ 音楽が再生できない（アプリケーションが応答しない）
2. ❌ 自動応答チャンネルでAIが応答しない
3. ❌ Lavalinkが未接続

---

## 🔍 原因の確認

### Koyebログを確認

1. [Koyeb Dashboard](https://app.koyeb.com) にアクセス
2. あなたのサービス（dying-nana-haklab-3e0dcb62）をクリック
3. 「Logs」タブをクリック

### 確認すべきログ

#### ✅ 正常な起動ログ

```
✅ すべての環境変数が設定されています
✅ PostgreSQL database initialized successfully
✅ Database connection test: 1
✅ Connecting to Lavalink: https://lavalinkv4.serenetia.com:443
✅ Connected to Lavalink server successfully
✅ Music player loaded successfully
✅ Bot setup completed
INFO - [あなたのBot名] has connected to Discord!
INFO - Synced X global commands
```

#### ❌ エラーログ

```
❌ GEMINI_API_KEY not found
❌ Failed to connect to Lavalink
❌ Music player not loaded (Lavalink may not be running)
❌ Error saving chat log
```

---

## 🚀 修正手順

### ステップ1: Koyeb環境変数を確認

Koyeb → dying-nana-haklab-3e0dcb62 → Settings → Environment variables

#### 必須環境変数チェックリスト

```bash
# Discord設定
✅ DISCORD_TOKEN=あなたのトークン
✅ DISCORD_CLIENT_ID=あなたのクライアントID

# Gemini AI設定（自動応答に必須）
✅ GEMINI_API_KEY=あなたのAPIキー

# データベース設定
✅ DATABASE_URL=postgresql://...

# API設定
✅ API_HOST=0.0.0.0
✅ API_PORT=8000

# Lavalink設定（音楽機能に必須）
✅ LAVALINK_HOST=lavalinkv4.serenetia.com
✅ LAVALINK_PORT=443
✅ LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
✅ LAVALINK_SECURE=true
```

### ステップ2: 不足している環境変数を追加

#### GEMINI_API_KEYが未設定の場合

1. [Google AI Studio](https://makersuite.google.com/app/apikey) でAPIキーを取得
2. Koyebで環境変数を追加:
   ```
   Name: GEMINI_API_KEY
   Value: あなたのAPIキー
   ```

#### Lavalink環境変数が未設定の場合

Koyebで以下を追加:

```bash
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

### ステップ3: Redeploy

1. Koyebで「Redeploy」をクリック
2. ログを確認（1-2分待つ）
3. 上記の「✅ 正常な起動ログ」が表示されるか確認

---

## 🎵 音楽機能のテスト

### 1. スラッシュコマンドでテスト

Discordで:
```
/play query:テスト曲
```

#### 成功の場合
- 曲の選択画面が表示される
- 「Discord VC」または「Web高音質」ボタンが表示される
- ボタンをクリックすると再生開始

#### 失敗の場合
- 「アプリケーションが応答しませんでした」
- → Lavalinkが接続されていない
- → Koyebログで `Failed to connect to Lavalink` を確認
- → Lavalink環境変数を設定してRedeploy

### 2. 自然言語でテスト

自動応答チャンネルで:
```
YOASOBIのアイドル流して
```

#### 成功の場合
- Botが曲を検索
- 自動的に再生開始

#### 失敗の場合
- 何も反応しない
- → 自動応答チャンネルが設定されていない
- → `/setchannel` コマンドで設定

---

## 💬 AI自動応答のテスト

### 1. チャンネルを設定

```
/setchannel enable:True
```

成功メッセージ:
```
✅ このチャンネルでAI自動応答を有効にしました
```

### 2. メッセージを送信

```
こんにちは
```

#### 成功の場合
- Botが返信する
- Koyebログに `Chat log saved to PostgreSQL` が表示される

#### 失敗の場合
- 何も反応しない
- → Koyebログを確認
- → `GEMINI_API_KEY not found` が表示されている
- → GEMINI_API_KEYを設定してRedeploy

---

## 🔍 トラブルシューティング

### 問題1: 音楽コマンドが応答しない

**症状**: `/play` を実行しても「アプリケーションが応答しませんでした」

**原因**: 
1. Lavalinkが接続されていない
2. Music cogがロードされていない

**解決策**:
1. Koyebログで確認:
   ```
   ❌ Failed to connect to Lavalink
   ⚠️  Music player not loaded
   ```
2. Lavalink環境変数を設定:
   ```bash
   LAVALINK_HOST=lavalinkv4.serenetia.com
   LAVALINK_PORT=443
   LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
   LAVALINK_SECURE=true
   ```
3. Redeploy
4. ログで確認:
   ```
   ✅ Connected to Lavalink server successfully
   ✅ Music player loaded successfully
   ```

### 問題2: AI自動応答が動作しない

**症状**: 自動応答チャンネルでメッセージを送っても反応しない

**原因**:
1. GEMINI_API_KEYが設定されていない
2. チャンネルが自動応答に設定されていない

**解決策**:
1. `/setchannel enable:True` を実行
2. Koyebログで確認:
   ```
   ❌ GEMINI_API_KEY not found
   ```
3. GEMINI_API_KEYを設定してRedeploy
4. もう一度メッセージを送信

### 問題3: Lavalinkに接続できない

**症状**: ログに `Failed to connect to Lavalink` が表示される

**原因**:
1. Lavalink環境変数が未設定
2. 外部Lavalinkサーバーがダウンしている

**解決策1**: 環境変数を確認
```bash
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

**解決策2**: 代替Lavalinkサーバーを使用
```bash
LAVALINK_HOST=lavalink.devz.cloud
LAVALINK_PORT=443
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SECURE=true
```

---

## 📋 完全チェックリスト

### Koyeb環境変数

- [ ] `DISCORD_TOKEN` が設定されている
- [ ] `GEMINI_API_KEY` が設定されている（**AI自動応答に必須**）
- [ ] `DATABASE_URL` が設定されている
- [ ] `LAVALINK_HOST` が設定されている（**音楽機能に必須**）
- [ ] `LAVALINK_PORT=443` が設定されている
- [ ] `LAVALINK_PASSWORD` が設定されている
- [ ] `LAVALINK_SECURE=true` が設定されている
- [ ] `API_HOST=0.0.0.0` が設定されている
- [ ] `API_PORT=8000` が設定されている

### デプロイ確認

- [ ] Koyebで「Redeploy」を実行した
- [ ] ログで `PostgreSQL database initialized` を確認
- [ ] ログで `Connected to Lavalink server successfully` を確認
- [ ] ログで `Music player loaded successfully` を確認
- [ ] ログで `Bot setup completed` を確認

### Discord確認

- [ ] `/status` コマンドでLavalinkが「✅ 接続中」
- [ ] `/setchannel enable:True` でチャンネルを設定
- [ ] 自動応答チャンネルでメッセージを送信してBotが返信
- [ ] `/play query:テスト曲` で曲が再生される

---

## ✅ 成功の確認

すべて正常に動作している場合:

1. ✅ `/status` でLavalinkが「✅ 接続中」
2. ✅ 自動応答チャンネルでBotが返信する
3. ✅ `/play` で曲が再生される
4. ✅ 「YOASOBIのアイドル流して」で曲が再生される
5. ✅ Koyebログにエラーがない

---

## 🆘 それでも動かない場合

### 確認すること

1. Koyebのログをすべてコピー
2. `/status` コマンドのスクリーンショット
3. 環境変数のスクリーンショット（トークンは隠す）

### よくある間違い

- `LAVALINK_PORT` を `"443"` (文字列) ではなく `443` (数値) で設定
- `LAVALINK_SECURE` を `"true"` (文字列) ではなく `true` (真偽値) で設定
- GEMINI_API_KEYにスペースや改行が含まれている
- DATABASE_URLが間違っている

---

## 💡 重要ポイント

### AI自動応答が動かない原因の99%

```bash
GEMINI_API_KEY=あなたのAPIキー
```

この1行が設定されていないと、AIは一切応答しません。

### 音楽が再生できない原因の99%

```bash
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

この4行がすべて正しく設定されている必要があります。
