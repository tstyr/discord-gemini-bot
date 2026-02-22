# スラッシュコマンド一覧

## 現在のコマンド

### AI関連 (ai_commands.py)
1. `/chat` - AIとチャットする
2. `/mode` - AIのモードを変更する
3. `/status` - Botのステータスを表示する
4. `/stats` - 使用統計を表示する
5. `/setchannel` - このチャンネルでAI自動応答を有効/無効にする
6. `/clear` - 会話履歴をクリアする
7. `/dashboard` - ダッシュボードのリンクを表示（管理者のみ）
8. `/invite` - Botの招待リンクを表示
9. `/restart` - Botを再起動する（管理者のみ）

### 音楽関連 (music_player.py)
10. `/play` - 音楽を再生します
11. `/skip` - 現在の曲をスキップします
12. `/stop` - 音楽を停止してボットを切断します
13. `/queue` - 現在のキューを表示します
14. `/recommend` - AIが会話の流れから音楽を推薦します

### プレイリスト関連 (playlist_manager.py)
15. `/playlist` - プレイリスト管理

### 歌詞関連 (lyrics_streamer.py)
16. `/lyrics_mode` - 歌詞配信のON/OFF

### チャンネル管理 (channel_manager.py)
17. `/setup-public-chat` - AI専用のパブリックチャンネルを作成します
18. `/setup-private-chat` - あなた専用のプライベートAIチャンネルを作成します
19. `/list-ai-channels` - AI専用チャンネルの一覧を表示します

### 設定関連 (settings.py)
20. `/channels` - AI自動応答が設定されているチャンネル一覧を表示
21. `/info` - Botの情報を表示

## 重複・統合の提案

### 重複コマンド
- `/channels` (settings.py) と `/list-ai-channels` (channel_manager.py) - 似た機能
- `/info` (settings.py) と `/status` (ai_commands.py) - 似た機能

### 統合案

#### 案1: チャンネル関連を統合
- `/channels` を削除
- `/list-ai-channels` に統一

#### 案2: 情報表示を統合
- `/info` を削除
- `/status` に統一

#### 案3: 設定コマンドを整理
- `/setchannel` → `/channel set`
- `/channels` → `/channel list`
- `/list-ai-channels` → `/channel list-ai`

## 推奨される整理後のコマンド構成

### AI関連
- `/chat` - AIとチャット
- `/mode` - AIモード変更
- `/clear` - 会話履歴クリア

### 音楽関連
- `/play` - 音楽再生
- `/skip` - スキップ
- `/stop` - 停止
- `/queue` - キュー表示
- `/recommend` - AI推薦
- `/lyrics_mode` - 歌詞配信ON/OFF

### プレイリスト関連
- `/playlist` - プレイリスト管理

### チャンネル管理
- `/setup-public-chat` - パブリックチャンネル作成
- `/setup-private-chat` - プライベートチャンネル作成
- `/channel list` - チャンネル一覧（統合）

### 情報・管理
- `/status` - ステータス表示（統合）
- `/stats` - 統計表示
- `/invite` - 招待リンク
- `/dashboard` - ダッシュボード（管理者）
- `/restart` - 再起動（管理者）

## 削除するコマンド

1. `/channels` (settings.py) - `/list-ai-channels`に統合
2. `/info` (settings.py) - `/status`に統合
