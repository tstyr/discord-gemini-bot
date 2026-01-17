# 🔍 クイック診断ガイド

## 現在の状態

画像から確認できた情報:
- ✅ Botはオンライン
- ✅ サーバー数: 2
- ❌ Lavalink: 未接続
- ❌ Messages: 0（自動応答が動作していない）
- ❌ `/play` コマンドが応答しない

---

## 🚨 緊急修正手順

### 1. Koyebログを確認（最重要）

[Koyeb Dashboard](https://app.koyeb.com) → dying-nana-haklab-3e0dcb62 → Logs

#### 探すべきログ

```bash
# これが表示されていればOK
✅ Connected to Lavalink server successfully
✅ Music player loaded successfully

# これが表示されていたらNG
❌ Failed to connect to Lavalink
⚠️  Music player not loaded
```

### 2. 環境変数を確認

Koyeb → Settings → Environment variables

#### 必須チェック

```bash
GEMINI_API_KEY=（設定されているか？）
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

### 3. 不足している環境変数を追加

#### Lavalink環境変数が1つでも欠けている場合

Koyebで以下をすべて追加:

```
Name: LAVALINK_HOST
Value: lavalinkv4.serenetia.com

Name: LAVALINK_PORT
Value: 443

Name: LAVALINK_PASSWORD
Value: https://dsc.gg/ajidevserver

Name: LAVALINK_SECURE
Value: true
```

#### GEMINI_API_KEYが欠けている場合

```
Name: GEMINI_API_KEY
Value: あなたのGemini APIキー
```

[Google AI Studio](https://makersuite.google.com/app/apikey)で取得

### 4. Redeploy

Koyeb → 「Redeploy」ボタンをクリック

### 5. 1-2分待ってログを確認

```
✅ Connected to Lavalink server successfully
✅ Music player loaded successfully
✅ Bot setup completed
```

これらが表示されればOK！

---

## 🎵 音楽機能のテスト

### Discordで実行

```
/status
```

#### 期待される結果

```
🎵 Lavalink
Status: ✅ 接続中
Ping: ~XXms
VC: ❌ 未接続
```

#### 実際の結果が「❌ 未接続」の場合

→ Lavalink環境変数を設定してRedeploy

---

## 💬 AI自動応答のテスト

### 1. チャンネルを設定

```
/setchannel enable:True
```

### 2. メッセージを送信

```
こんにちは
```

#### Botが返信すればOK

#### 返信しない場合

→ GEMINI_API_KEYを設定してRedeploy

---

## 📊 現在の問題と解決策

### 問題1: Lavalinkが未接続

**原因**: Lavalink環境変数が設定されていない

**解決策**:
```bash
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

### 問題2: Messages: 0

**原因**: 
1. GEMINI_API_KEYが設定されていない
2. 自動応答チャンネルが設定されていない

**解決策**:
1. GEMINI_API_KEYを設定
2. `/setchannel enable:True` を実行
3. メッセージを送信

### 問題3: /playが応答しない

**原因**: Lavalinkが接続されていないため、タイムアウト

**解決策**:
1. Lavalink環境変数を設定
2. Redeploy
3. `/status` でLavalinkが接続されているか確認
4. `/play` を再実行

---

## ✅ 成功の確認

### `/status` コマンドの結果

```
🎵 Lavalink
Status: ✅ 接続中  ← これが重要！
```

### 自動応答チャンネル

```
あなた: こんにちは
Bot: こんにちは！何かお手伝いできることはありますか？
```

### 音楽再生

```
/play query:テスト曲
→ 曲の選択画面が表示される
```

---

## 🆘 それでも動かない場合

### Koyebログをコピーして確認

1. Koyeb → Logs
2. すべてのログをコピー
3. 以下を探す:
   - `Failed to connect to Lavalink`
   - `GEMINI_API_KEY not found`
   - `Error`

### 環境変数のスクリーンショット

1. Koyeb → Settings → Environment variables
2. スクリーンショットを撮る（トークンは隠す）
3. 以下が設定されているか確認:
   - GEMINI_API_KEY
   - LAVALINK_HOST
   - LAVALINK_PORT
   - LAVALINK_PASSWORD
   - LAVALINK_SECURE

---

## 💡 最も重要なポイント

### 音楽が動かない = Lavalink環境変数が未設定

```bash
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

**この4行がすべて設定されていないと、音楽機能は一切動作しません。**

### AI自動応答が動かない = GEMINI_API_KEYが未設定

```bash
GEMINI_API_KEY=あなたのAPIキー
```

**この1行が設定されていないと、AIは一切応答しません。**

---

## 📞 次のステップ

1. Koyebログを確認
2. 不足している環境変数を追加
3. Redeploy
4. `/status` で確認
5. `/play` と自動応答をテスト

詳細は `MUSIC_AND_AI_FIX.md` を参照してください。
