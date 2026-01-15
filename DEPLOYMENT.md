# 🚀 デプロイメントガイド（完全無料）

Render + UptimeRobot + Vercel + Supabase で24時間無料運用する方法です。

## 📋 必要なもの

- GitHubアカウント
- [Render](https://render.com) アカウント
- [UptimeRobot](https://uptimerobot.com) アカウント
- [Vercel](https://vercel.com) アカウント
- [Supabase](https://supabase.com) アカウント

---

## 1️⃣ Supabase (データベース)

### 1.1 プロジェクト作成
1. [Supabase](https://supabase.com) にログイン
2. 「New Project」→ プロジェクト名入力
3. パスワード設定（メモする）
4. リージョン: Tokyo
5. 「Create new project」

### 1.2 接続URL取得
1. Settings → Database
2. Connection string の URI をコピー
3. `[YOUR-PASSWORD]` を置き換え

```
postgresql://postgres:パスワード@db.xxxxx.supabase.co:5432/postgres
```

---

## 2️⃣ Render (Bot)

### 2.1 Web Service作成
1. [Render](https://render.com) にログイン
2. 「New」→「Web Service」
3. GitHubリポジトリを接続
4. 設定:
   - Name: `discord-bot`
   - Root Directory: `bot`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
   - Instance Type: **Free**

### 2.2 環境変数
「Environment」タブで追加:

| Key | Value |
|-----|-------|
| `DISCORD_TOKEN` | Discordトークン |
| `GEMINI_API_KEY` | Gemini APIキー |
| `DATABASE_URL` | SupabaseのURL |
| `API_HOST` | `0.0.0.0` |
| `API_PORT` | `10000` |
| `DASHBOARD_URL` | （後で設定） |
| `LAVALINK_HOST` | `lavalinkv4.serenetia.com` |
| `LAVALINK_PORT` | `443` |
| `LAVALINK_PASSWORD` | `https://dsc.gg/ajidevserver` |
| `LAVALINK_SECURE` | `true` |

### 2.3 デプロイ
「Create Web Service」→ デプロイ完了を待つ

URLをメモ: `https://discord-bot-xxxx.onrender.com`

---

## 3️⃣ UptimeRobot（スリープ防止）

Render無料プランは15分無アクセスでスリープするため、UptimeRobotで定期的にアクセスします。

### 3.1 モニター作成
1. [UptimeRobot](https://uptimerobot.com) にログイン
2. 「Add New Monitor」
3. 設定:
   - Monitor Type: **HTTP(s)**
   - Friendly Name: `Discord Bot`
   - URL: `https://discord-bot-xxxx.onrender.com/api/health`
   - Monitoring Interval: **5 minutes**

4. 「Create Monitor」

これでBotが24時間起動し続けます！

---

## 4️⃣ Vercel (ダッシュボード)

### 4.1 プロジェクト作成
1. [Vercel](https://vercel.com) にログイン
2. 「Add New」→「Project」
3. GitHubリポジトリをインポート
4. Root Directory: `dashboard`

### 4.2 環境変数
| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://discord-bot-xxxx.onrender.com` |
| `NEXT_PUBLIC_WS_URL` | `wss://discord-bot-xxxx.onrender.com/ws` |

### 4.3 デプロイ
「Deploy」→ URLをメモ

### 4.4 RenderのDASHBOARD_URL更新
RenderでDASHBOARD_URLをVercelのURLに更新

---

## 5️⃣ 動作確認

```bash
# ヘルスチェック
curl https://discord-bot-xxxx.onrender.com/api/health
```

Discordで `/status` コマンドを実行

---

## � コスト: 完全無料

| サービス | 無料枠 |
|----------|--------|
| Render | 750時間/月（1サービスなら24時間OK） |
| UptimeRobot | 50モニター |
| Vercel | 無制限 |
| Supabase | 500MB DB |

---

## ⚠️ 注意点

### Renderの制限
- 無料プランは月750時間（1サービスなら十分）
- 初回起動に30秒〜1分かかる場合あり
- スリープ後の復帰に数秒かかる

### 対策
- UptimeRobotで5分間隔でping
- `/api/health`エンドポイントを軽量に保つ

---

## 🔄 更新方法

GitHubにpushすると自動デプロイ:
```bash
git add .
git commit -m "Update"
git push
```
