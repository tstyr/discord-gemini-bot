# 🚀 クイックスタートガイド

## ⚠️ セキュリティ重要事項
**提供されたトークンは公開されているため、以下の手順で新しいトークンを生成してください：**

1. **Discord Token**: [Discord Developer Portal](https://discord.com/developers/applications) → あなたのアプリ → Bot → Reset Token
2. **Gemini API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey) → Create API Key

## 📋 必要な環境

### Python 3.8+
```bash
python --version
```

### Node.js 16+
```bash
node --version
npm --version
```

## 🔧 セットアップ手順

### 1. Python依存関係のインストール
```bash
cd bot
pip install -r requirements.txt
```

### 2. Web依存関係のインストール
```bash
cd web
npm install
```

### 3. 環境変数の設定
環境ファイルは既に作成済みです：
- `bot/.env` - Discord BotとGemini API設定
- `web/.env.local` - Web Dashboard設定

**新しいトークンで更新してください！**

## 🚀 起動方法

### オプション1: 自動起動スクリプト

#### Discord Bot起動
```bash
python start_bot.py
```

#### Web Dashboard起動 (別ターミナル)
```bash
python start_web.py
```

### オプション2: 手動起動

#### Discord Bot
```bash
cd bot
python main.py
```

#### Web Dashboard
```bash
cd web
npm run dev
```

## 🌐 アクセス先

- **Web Dashboard**: http://localhost:3000
- **Bot API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/api/health

## 🎯 初回テスト手順

### 1. Bot動作確認
1. Discordサーバーにボットを招待
2. `/chat` コマンドでAI応答テスト
3. `/setup-public-chat` でチャンネル作成テスト

### 2. Web Dashboard確認
1. http://localhost:3000 にアクセス
2. ダッシュボードが表示されることを確認
3. リソース監視ページで使用量確認

### 3. 連携テスト
1. Discordでメッセージ送信
2. Web Dashboardの会話ログに表示確認
3. ネットワーク統計の更新確認

## 🎵 音楽機能 (オプション)

### Lavalink サーバー起動
```bash
# Docker使用の場合
docker-compose up lavalink

# または手動でLavalinkサーバーを起動
# lavalink/application.yml の設定を確認
```

### 音楽コマンドテスト
```
/play 曲名
/music-setup (音楽チャンネル作成)
```

## 💰 コスト最適化機能

### 自動機能
- ✅ 簡単な挨拶は無料応答
- ✅ 長い会話は自動要約
- ✅ 使用量80%で自動警告
- ✅ 制限到達で自動停止

### 監視方法
- Web Dashboard → リソース監視
- Discord → 自動警告メッセージ
- API: `GET /api/cost/usage`

## 🔧 トラブルシューティング

### Bot起動エラー
```bash
# 依存関係確認
pip list | grep discord
pip list | grep google-generativeai

# 環境変数確認
cat bot/.env
```

### Web Dashboard エラー
```bash
# 依存関係確認
cd web
npm list

# ビルドテスト
npm run build
```

### API接続エラー
```bash
# ヘルスチェック
curl http://localhost:8000/api/health

# CORS設定確認
# web/next.config.js の rewrites 設定
```

## 📊 機能一覧

### Discord Bot機能
- ✅ AI チャット (Gemini API)
- ✅ スラッシュコマンド
- ✅ チャンネル自動作成
- ✅ 音楽再生 (Lavalink)
- ✅ コスト最適化
- ✅ 使用量監視

### Web Dashboard機能
- ✅ リアルタイム監視
- ✅ 会話ログ表示
- ✅ ネットワーク統計
- ✅ リソース使用量
- ✅ osu!lazer風UI
- ✅ レスポンシブデザイン

## 🎨 UI/UX特徴

### osu!lazer スタイル
- 🎨 ダークテーマ
- 💖 ピンク/シアンアクセント
- ✨ 滑らかなアニメーション
- 🌟 ブラー効果
- 📱 完全レスポンシブ

## 🔄 次のステップ

### 開発継続
1. 新機能の追加
2. カスタマイズ
3. 本番デプロイ準備

### 本番デプロイ
1. `DEPLOYMENT.md` を参照
2. Vercel + Railway 無料デプロイ
3. Supabase データベース設定

## 📞 サポート

問題が発生した場合：
1. ログを確認
2. 環境変数を再確認
3. 依存関係を再インストール
4. GitHub Issues で報告

---

**🎉 セットアップ完了後、完全に動作するDiscord Bot + Web Dashboardをお楽しみください！**