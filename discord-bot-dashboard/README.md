# Discord Bot with Gemini AI

Discord BotとGemini AIを統合したプロジェクト。

## セットアップ

1. 依存関係のインストール:
```bash
cd bot
pip install -r requirements.txt
```

2. `.env.example`を`.env`にコピーして環境変数を設定:
```bash
cp .env.example .env
```

3. Botの起動:
```bash
python bot/main.py
```

## コマンド

- `!ask <質問>` - Gemini AIに質問
- `!ping` - Bot応答確認
