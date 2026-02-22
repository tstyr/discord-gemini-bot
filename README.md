# Discord AI Bot + Web Dashboard

Discord BotとWebダッシュボードを統合したAIチャットシステムです。Gemini APIを使用した高度なAI機能と、osu!lazer風のモダンなWebインターフェースを提供します。

## 🚀 機能

### Discord Bot
- **スラッシュコマンド対応** (`/chat`, `/mode`, `/stats`, `/setchannel`, `/play`, `/skip`)
- **AI自動応答** - 指定チャンネルでの自動応答機能
- **AIモード切り替え** - Standard, Creative, Coder, Assistant, Music DJモード
- **会話履歴保持** - ユーザーごとのコンテキスト管理
- **使用統計記録** - トークン消費量とメッセージ数の追跡
- **音楽再生機能** - YouTube Music検索・再生、AI選曲システム、ハイブリッド再生
- **ハイブリッド再生** - Discord VC (低遅延) と Web Audio (高音質) の選択可能
- **チャンネル自動作成** - パブリック・プライベートAIチャンネル作成

### Web Dashboard
- **osu!lazer風UI** - モダンでスタイリッシュなデザイン
- **リアルタイム統計** - 使用量グラフとパフォーマンス分析
- **チャンネル管理** - AI自動応答の有効/無効設定
- **AIモード設定** - サーバーごとのAI動作モード変更
- **音楽プレイヤー** - osu!風の音楽制御UI、オーディオビジュアライザー、ハイブリッド再生
- **高音質Web再生** - Web Audio API、リアルタイムEQ、スペクトラムアナライザー
- **会話ログ表示** - リアルタイム会話履歴とフィルタリング
- **ネットワーク監視** - 通信状況のリアルタイム可視化
- **レスポンシブデザイン** - デスクトップ・モバイル対応

## 🛠 技術スタック

### Backend (Bot)
- **Python 3.8+**
- **discord.py** - Discord Bot API
- **google-generativeai** - Gemini API
- **FastAPI** - Web API サーバー
- **SQLite** - データベース
- **aiosqlite** - 非同期データベース操作
- **wavelink** - 音楽再生 (Lavalink)
- **yt-dlp** - YouTube音楽検索・高音質ストリーミング
- **PyNaCl** - 音声処理
- **python-socketio** - リアルタイム同期通信

### Frontend (Web)
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS** - スタイリング
- **Framer Motion** - アニメーション
- **Lucide React** - アイコン
- **Recharts** - グラフ・チャート
- **Socket.IO Client** - リアルタイム通信
- **Web Audio API** - 高音質音楽再生

## 📁 プロジェクト構成

```
├── bot/                    # Discord Bot
│   ├── main.py            # メインエントリーポイント
│   ├── gemini_client.py   # Gemini API クライアント
│   ├── database.py        # データベース操作
│   ├── api_server.py      # FastAPI サーバー
│   ├── cogs/              # Bot コマンド
│   │   ├── ai_commands.py # AI関連コマンド
│   │   └── settings.py    # 設定コマンド
│   └── requirements.txt   # Python依存関係
├── web/                   # Next.js Dashboard
│   ├── src/
│   │   ├── app/          # App Router ページ
│   │   ├── components/   # UIコンポーネント
│   │   └── lib/         # API クライアント
│   └── package.json     # Node.js依存関係
└── shared/               # 共有リソース
    ├── schema.sql       # データベーススキーマ
    └── config.json      # 設定ファイル
```

## 🚀 セットアップ

### 1. 環境変数の設定

**Bot側 (`bot/.env`)**
```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
DATABASE_PATH=../shared/bot.db
API_PORT=8000
API_HOST=0.0.0.0
```

**Web側 (`web/.env.local`)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BOT_NAME=AI Discord Bot
NEXT_PUBLIC_DASHBOARD_TITLE=AI Bot Dashboard
```

### 2. Lavalinkサーバーの起動

```bash
# Docker Composeでlavalinkサーバーを起動
docker-compose up -d lavalink
```

### 3. Bot のセットアップ

```bash
cd bot
pip install -r requirements.txt
python main.py
```

### 4. Web Dashboard のセットアップ

```bash
cd web
npm install
npm run dev
```

## 📋 使用方法

### Discord Bot コマンド

**基本コマンド:**
- `/chat <message>` - AIとチャット
- `/mode <standard|creative|coder|assistant|music_dj>` - AIモード変更
- `/stats` - 使用統計表示
- `/setchannel <enable>` - チャンネルの自動応答設定
- `/channels` - 設定済みチャンネル一覧
- `/clear` - 会話履歴クリア

**チャンネル管理:**
- `/setup-public-chat` - パブリックAIチャンネル作成
- `/setup-private-chat` - プライベートAIチャンネル作成
- `/list-ai-channels` - AI専用チャンネル一覧

**音楽機能:**
- `/play <曲名/URL>` - 音楽検索・再生
- `/skip` - 現在の曲をスキップ
- `/stop` - 再生停止・切断
- `/queue` - 再生キュー表示
- `/recommend` - AI推薦曲の再生

### Web Dashboard

1. `http://localhost:3000/dashboard` にアクセス
2. サイドバーから各機能にアクセス
   - **ダッシュボード** - 概要と統計
   - **統計** - 詳細な使用量分析
   - **チャンネル** - AI自動応答設定
   - **セットアップ** - チャンネル作成ガイド
   - **AIモード** - モード切り替え
   - **音楽プレイヤー** - 音楽制御とビジュアライザー
   - **会話ログ** - リアルタイム会話履歴
   - **ネットワーク** - 通信状況監視

## 🎨 UI デザイン

osu!lazer からインスパイアされたデザイン要素：
- **ダークテーマ** - `#111` ベース
- **アクセントカラー** - ピンク (`#ff66aa`)、シアン (`#00ffcc`)
- **斜めライン** - 背景装飾
- **滑らかなアニメーション** - Framer Motion
- **グラデーション** - カードとボタン

## 🔧 カスタマイズ

### AIモードの追加

`bot/gemini_client.py` の `modes` 辞書に新しいモードを追加：

```python
'custom_mode': {
    'system_instruction': "カスタム指示文",
    'temperature': 0.8,
    'max_tokens': 1500
}
```

### UIテーマの変更

`web/tailwind.config.ts` でカラーパレットを変更：

```typescript
colors: {
  'osu-pink': '#your-color',
  'osu-cyan': '#your-color',
  // ...
}
```

## 📊 API エンドポイント

- `GET /api/health` - ヘルスチェック
- `GET /api/stats` - 使用統計
- `GET /api/guilds` - サーバー一覧
- `GET /api/guilds/{id}/channels` - チャンネル一覧
- `POST /api/channels/toggle` - チャンネル設定変更
- `GET /api/guilds/{id}/mode` - AIモード取得
- `POST /api/mode` - AIモード変更

## 🤝 コントリビューション

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 🙏 謝辞

- [osu!lazer](https://github.com/ppy/osu) - UI デザインインスピレーション
- [Discord.py](https://github.com/Rapptz/discord.py) - Discord Bot ライブラリ
- [Google Gemini](https://ai.google.dev/) - AI API
- [Next.js](https://nextjs.org/) - React フレームワーク
