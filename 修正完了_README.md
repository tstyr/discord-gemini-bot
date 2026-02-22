# ✅ Koyeb + Vercel デプロイ問題 - 修正完了

## 🎯 問題

- ❌ AIが反応しない
- ❌ 音楽が再生できない

## 🔧 原因

**環境変数が設定されていませんでした**

---

## 📦 修正内容

### 1. 新規作成ファイル

| ファイル | 説明 |
|---------|------|
| `KOYEB_VERCEL_QUICK_FIX.md` | 🚨 5分で修正する緊急ガイド |
| `KOYEB_VERCEL_DEPLOYMENT_FIX.md` | 📖 詳細な修正ガイド |
| `KOYEB_VERCEL_CHECKLIST.md` | ✅ デプロイチェックリスト |
| `bot/check_env.py` | 🔍 環境変数チェックツール |
| `bot/.env.koyeb.example` | 📝 Koyeb用環境変数テンプレート |

### 2. 修正ファイル

| ファイル | 変更内容 |
|---------|---------|
| `bot/main.py` | 起動時に環境変数チェックを追加 |
| `bot/cogs/music_player.py` | Lavalink接続を環境変数から読み込むように修正 |
| `bot/koyeb.yaml` | 環境変数の説明を追加 |
| `bot/.env.production.example` | Koyeb用に更新 |
| `dashboard/vercel.json` | Koyeb URLに更新 |

---

## 🚀 今すぐ修正する方法

### ステップ1: 環境変数を設定

**Koyebダッシュボード** → あなたのサービス → Settings → Environment variables

以下を追加:

```bash
# 必須
DISCORD_TOKEN=あなたのDiscordトークン
GEMINI_API_KEY=あなたのGemini APIキー
DATABASE_URL=あなたのPostgreSQL URL

# 音楽用
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true

# 基本設定
API_HOST=0.0.0.0
API_PORT=8000
```

### ステップ2: Redeploy

Koyebで「Redeploy」をクリック

### ステップ3: 確認

Discordで:
```
こんにちは
```

Botが返信すれば成功！🎉

---

## 📚 ドキュメント

### 緊急時

→ **`KOYEB_VERCEL_QUICK_FIX.md`** を読む

### 詳細な手順

→ **`KOYEB_VERCEL_DEPLOYMENT_FIX.md`** を読む

### チェックリスト

→ **`KOYEB_VERCEL_CHECKLIST.md`** を使う

### 環境変数チェック

```bash
python bot/check_env.py
```

---

## 🔍 トラブルシューティング

### AIが反応しない

**原因**: `GEMINI_API_KEY`が未設定

**解決策**:
1. [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーを取得
2. Koyebで設定
3. Redeploy

### 音楽が再生できない

**原因**: Lavalink環境変数が未設定

**解決策**:
1. 上記の4つのLavalink環境変数を設定
2. Redeploy
3. ログで`Connected to Lavalink server successfully`を確認

---

## ✅ 成功の確認

すべて正常に動作している場合:

- ✅ Botがオンライン
- ✅ チャットでAIが返信する
- ✅ `/play`で音楽が再生される
- ✅ Koyebログにエラーがない

---

## 💡 重要ポイント

### 最も重要な環境変数

```bash
GEMINI_API_KEY=あなたのAPIキー
```

**この1行がないと、AIは一切反応しません！**

### 音楽機能に必要な環境変数

```bash
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

**この4行がすべて必要です！**

---

## 📞 次のステップ

1. ✅ 環境変数を設定
2. ✅ Redeployを実行
3. ✅ Discordでテスト
4. ✅ 動作確認

問題が解決しない場合は、`KOYEB_VERCEL_DEPLOYMENT_FIX.md`の
トラブルシューティングセクションを参照してください。

---

## 🎉 完了！

すべての修正が完了しました。
環境変数を設定してRedeployすれば、
AIも音楽も正常に動作するはずです！

頑張ってください！🚀
