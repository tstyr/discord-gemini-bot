# 🔧 Koyeb + Vercel デプロイ修正ガイド

## 問題点

1. **AIが反応しない**: Gemini APIキーが環境変数に設定されていない
2. **音楽が再生できない**: Lavalinkサーバーの接続設定が不足
3. **環境変数の不足**: Koyebの環境変数設定が不完全

---

## ✅ 修正手順

### 1. Koyeb環境変数の設定

Koyebのダッシュボードで以下の環境変数を**すべて**追加してください:

#### 必須の環境変数

```bash
# Discord設定
DISCORD_TOKEN=あなたのDiscordトークン
DISCORD_CLIENT_ID=あなたのDiscordクライアントID

# Gemini AI設定（これが最重要！）
GEMINI_API_KEY=あなたのGemini APIキー

# API設定
API_HOST=0.0.0.0
API_PORT=8000

# データベース設定
DATABASE_URL=postgresql://ユーザー名:パスワード@ホスト:5432/データベース名

# Lavalink設定（音楽機能用）
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true

# Spotify設定（オプション）
SPOTIFY_CLIENT_ID=3ffed1b631aa436facaccc439098c732
SPOTIFY_CLIENT_SECRET=b27ddccaaa524dc5bfe3e41319578391

# コスト最適化
ENABLE_COST_OPTIMIZATION=true
DAILY_REQUEST_LIMIT=1500
DAILY_TOKEN_LIMIT=1000000
```

### 2. Vercel環境変数の設定

Vercelのダッシュボードで以下を設定:

```bash
NEXT_PUBLIC_API_URL=https://あなたのKoyebアプリ名.koyeb.app
NEXT_PUBLIC_WS_URL=wss://あなたのKoyebアプリ名.koyeb.app/ws
```

### 3. 設定確認方法

#### Koyebでの確認

1. Koyebダッシュボード → あなたのサービス
2. 「Settings」→「Environment variables」
3. 上記の環境変数がすべて設定されているか確認
4. 「Redeploy」をクリック

#### ログの確認

Koyebのログで以下を確認:

```
✅ 正常な起動ログ:
- "Connected to Lavalink server"
- "Bot setup completed"
- "has connected to Discord!"

❌ エラーログ:
- "GEMINI_API_KEY not found" → APIキーが未設定
- "Failed to connect to Lavalink" → Lavalink設定エラー
```

### 4. Discord Botの確認

Discordで以下をテスト:

```
# AIテスト
チャットチャンネルで: こんにちは

# 音楽テスト
/play query:テスト曲
```

---

## 🔍 トラブルシューティング

### AIが反応しない場合

**原因**: `GEMINI_API_KEY`が設定されていない

**解決策**:
1. [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーを取得
2. KoyebでGEMINI_API_KEYを設定
3. Redeployを実行

### 音楽が再生できない場合

**原因**: Lavalink接続エラー

**解決策**:
1. 環境変数を確認:
   - `LAVALINK_HOST=lavalinkv4.serenetia.com`
   - `LAVALINK_PORT=443`
   - `LAVALINK_PASSWORD=https://dsc.gg/ajidevserver`
   - `LAVALINK_SECURE=true`

2. Koyebログで確認:
   ```
   "Connected to Lavalink server" が表示されるか
   ```

3. 表示されない場合は、外部Lavalinkサーバーがダウンしている可能性
   - 代替サーバー: `lavalink.devz.cloud:443` (password: `youshallnotpass`)

### データベースエラー

**原因**: DATABASE_URLが未設定

**解決策**:
1. 無料PostgreSQLを使用:
   - [Supabase](https://supabase.com) (推奨)
   - [Neon](https://neon.tech)
   - [ElephantSQL](https://www.elephantsql.com)

2. 接続URLを取得してKoyebに設定

---

## 📝 チェックリスト

デプロイ前に確認:

- [ ] Koyebで`DISCORD_TOKEN`を設定
- [ ] Koyebで`GEMINI_API_KEY`を設定
- [ ] Koyebで`DATABASE_URL`を設定
- [ ] Koyebで`LAVALINK_HOST`を設定
- [ ] Koyebで`LAVALINK_PORT=443`を設定
- [ ] Koyebで`LAVALINK_PASSWORD`を設定
- [ ] Koyebで`LAVALINK_SECURE=true`を設定
- [ ] Vercelで`NEXT_PUBLIC_API_URL`を設定
- [ ] Vercelで`NEXT_PUBLIC_WS_URL`を設定
- [ ] Koyebで「Redeploy」を実行
- [ ] Vercelで「Redeploy」を実行
- [ ] Discordでテスト

---

## 🎯 最も重要な設定

**AIが反応しない問題の99%は以下が原因です:**

```bash
GEMINI_API_KEY=あなたのAPIキー
```

この1つの環境変数が設定されていないと、AIは一切反応しません。

**音楽が再生できない問題の99%は以下が原因です:**

```bash
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

これらの4つの環境変数がすべて正しく設定されている必要があります。

---

## 💡 ヒント

- 環境変数を変更したら必ず「Redeploy」を実行
- ログを確認して起動エラーがないかチェック
- 初回起動は30秒〜1分かかる場合があります
