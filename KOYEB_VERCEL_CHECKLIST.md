# ✅ Koyeb + Vercel デプロイチェックリスト

## 🎯 問題: AIが反応しない & 音楽が再生できない

### 原因
1. **GEMINI_API_KEY**が設定されていない → AIが反応しない
2. **Lavalink環境変数**が設定されていない → 音楽が再生できない

---

## 📝 デプロイ前チェックリスト

### ステップ1: 環境変数チェック（ローカル）

```bash
cd bot
python check_env.py
```

すべて✅になるまで`.env`ファイルを編集してください。

---

### ステップ2: Koyeb設定

#### 2.1 必須環境変数（Koyebダッシュボード）

Koyeb → あなたのサービス → Settings → Environment variables

```bash
# 🔴 必須（これがないとAIが動きません）
DISCORD_TOKEN=あなたのDiscordトークン
GEMINI_API_KEY=あなたのGemini APIキー
DATABASE_URL=あなたのPostgreSQL URL

# 🟡 音楽機能用（これがないと音楽が再生できません）
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true

# 🟢 基本設定
API_HOST=0.0.0.0
API_PORT=8000

# 🔵 オプション（Spotify音楽用）
SPOTIFY_CLIENT_ID=3ffed1b631aa436facaccc439098c732
SPOTIFY_CLIENT_SECRET=b27ddccaaa524dc5bfe3e41319578391
```

#### 2.2 Redeploy

環境変数を設定したら:
1. Koyebダッシュボードで「Redeploy」をクリック
2. ログを確認:
   - ✅ `Connected to Lavalink server successfully`
   - ✅ `Bot setup completed`
   - ✅ `has connected to Discord!`

---

### ステップ3: Vercel設定

#### 3.1 環境変数（Vercelダッシュボード）

Vercel → あなたのプロジェクト → Settings → Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://あなたのKoyebアプリ名.koyeb.app
NEXT_PUBLIC_WS_URL=wss://あなたのKoyebアプリ名.koyeb.app/ws
```

**重要**: `あなたのKoyebアプリ名`を実際のアプリ名に置き換えてください！

#### 3.2 Redeploy

1. Vercelダッシュボードで「Redeploy」
2. デプロイ完了を待つ

---

### ステップ4: 動作確認

#### 4.1 Koyebログ確認

Koyeb → Logs で以下を確認:

```
✅ 正常:
INFO - Connected to Lavalink server successfully
INFO - Bot setup completed
INFO - [あなたのBot名] has connected to Discord!

❌ エラー:
ERROR - GEMINI_API_KEY not found
ERROR - Failed to connect to Lavalink
```

#### 4.2 Discord動作テスト

```
# AIテスト
チャットチャンネルで: こんにちは
→ Botが返信すればOK

# 音楽テスト
/play query:テスト曲
→ 曲が再生されればOK
```

---

## 🔧 トラブルシューティング

### ❌ AIが反応しない

**症状**: Botはオンラインだが、メッセージに反応しない

**原因**: `GEMINI_API_KEY`が未設定

**解決策**:
1. [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーを取得
2. Koyebで`GEMINI_API_KEY`を設定
3. Redeployを実行

### ❌ 音楽が再生できない

**症状**: `/play`コマンドを実行してもエラーが出る

**原因**: Lavalink環境変数が未設定

**解決策**:
1. Koyebで以下を設定:
   ```
   LAVALINK_HOST=lavalinkv4.serenetia.com
   LAVALINK_PORT=443
   LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
   LAVALINK_SECURE=true
   ```
2. Redeployを実行
3. ログで`Connected to Lavalink server successfully`を確認

### ❌ データベースエラー

**症状**: `database connection failed`

**原因**: `DATABASE_URL`が未設定または無効

**解決策**:
1. 無料PostgreSQLを取得:
   - [Supabase](https://supabase.com) (推奨)
   - [Neon](https://neon.tech)
2. 接続URLをコピー
3. Koyebで`DATABASE_URL`を設定
4. Redeployを実行

---

## 🎯 最重要ポイント

### AIが動かない場合

```bash
GEMINI_API_KEY=あなたのAPIキー
```

この1行が設定されていないと、AIは一切反応しません。

### 音楽が動かない場合

```bash
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

この4行がすべて正しく設定されている必要があります。

---

## 📞 サポート

それでも動かない場合:

1. Koyebのログをすべてコピー
2. エラーメッセージを確認
3. `check_env.py`の出力を確認
4. 環境変数のスクリーンショットを撮る

---

## ✅ 成功の確認

すべて正常に動作している場合:

- ✅ Botがオンライン
- ✅ チャットでAIが返信する
- ✅ `/play`で音楽が再生される
- ✅ Webダッシュボードが表示される
- ✅ ログにエラーがない

おめでとうございます！🎉
