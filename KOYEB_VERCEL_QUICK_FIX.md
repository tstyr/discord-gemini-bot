# 🚨 緊急修正: AIが反応しない & 音楽が再生できない

## 問題

- ✅ Botはオンライン
- ❌ AIが反応しない
- ❌ 音楽が再生できない

## 原因

**環境変数が設定されていません！**

---

## 🔥 5分で修正する方法

### 1. Koyebで環境変数を設定

Koyeb → あなたのサービス → Settings → Environment variables

以下をコピペして追加:

```bash
# 🔴 必須（AIが動くために必要）
GEMINI_API_KEY=あなたのGemini APIキー

# 🟡 音楽用（音楽が動くために必要）
LAVALINK_HOST=lavalinkv4.serenetia.com
LAVALINK_PORT=443
LAVALINK_PASSWORD=https://dsc.gg/ajidevserver
LAVALINK_SECURE=true
```

**重要**: `あなたのGemini APIキー`を実際のAPIキーに置き換えてください！

### 2. Redeploy

Koyebダッシュボードで「Redeploy」ボタンをクリック

### 3. 確認

1分後、Discordで:
```
こんにちは
```

Botが返信すれば成功！🎉

---

## 📝 詳細な手順

### Gemini APIキーの取得方法

1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. 「Create API Key」をクリック
3. APIキーをコピー
4. Koyebの`GEMINI_API_KEY`に貼り付け

### 環境変数の設定場所

```
Koyebダッシュボード
  → あなたのサービス名をクリック
  → 左メニュー「Settings」
  → 「Environment variables」セクション
  → 「Add variable」をクリック
  → Key と Value を入力
  → 「Save」
```

### 必須環境変数リスト

| Key | Value | 説明 |
|-----|-------|------|
| `DISCORD_TOKEN` | あなたのトークン | Discordボット |
| `GEMINI_API_KEY` | あなたのAPIキー | **AI機能に必須** |
| `DATABASE_URL` | PostgreSQL URL | データベース |
| `LAVALINK_HOST` | lavalinkv4.serenetia.com | **音楽に必須** |
| `LAVALINK_PORT` | 443 | **音楽に必須** |
| `LAVALINK_PASSWORD` | https://dsc.gg/ajidevserver | **音楽に必須** |
| `LAVALINK_SECURE` | true | **音楽に必須** |
| `API_HOST` | 0.0.0.0 | API設定 |
| `API_PORT` | 8000 | API設定 |

---

## ✅ 動作確認

### AIテスト

Discordのチャットチャンネルで:
```
こんにちは
```

Botが返信すれば成功！

### 音楽テスト

Discordで:
```
/play query:テスト曲
```

曲が再生されれば成功！

---

## 🔍 トラブルシューティング

### それでもAIが反応しない

1. Koyeb → Logs を確認
2. `GEMINI_API_KEY not found` が表示されていないか確認
3. 環境変数が正しく設定されているか再確認
4. Redeployを実行

### それでも音楽が再生できない

1. Koyeb → Logs を確認
2. `Connected to Lavalink server successfully` が表示されているか確認
3. Lavalink環境変数が4つすべて設定されているか確認
4. Redeployを実行

---

## 📞 さらに詳しい情報

- `KOYEB_VERCEL_DEPLOYMENT_FIX.md` - 詳細な修正ガイド
- `KOYEB_VERCEL_CHECKLIST.md` - 完全なチェックリスト
- `bot/check_env.py` - 環境変数チェックツール

---

## 💡 ワンポイント

**最も重要な環境変数**:

```bash
GEMINI_API_KEY=あなたのAPIキー
```

この1行がないと、AIは一切反応しません。
必ず設定してください！
