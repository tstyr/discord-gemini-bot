# 🎉 セットアップ完了ガイド

## ✅ 現在の状態

Koyebログから確認:
- ✅ Bot起動成功
- ✅ PostgreSQL接続成功
- ✅ 環境変数設定完了
- ✅ 14個のコマンド同期完了
- ❌ 音楽プレイヤー未ロード（パッケージ不足）

---

## 🔧 残りの修正

### 1. 音楽機能の修正

**問題**: `ModuleNotFoundError: No module named 'youtubesearchpython'`

**解決策**: requirements.txtを更新してRedeploy

✅ **修正済み** - 次のデプロイで自動的に修正されます

---

## 🚀 使い方ガイド

### ステップ1: 自動応答チャンネルを設定

Discordで、AIに自動応答してほしいチャンネルで:

```
/setchannel enable:True
```

成功メッセージ:
```
✅ このチャンネルでAI自動応答を有効にしました
```

### ステップ2: AIと会話

設定したチャンネルで普通にメッセージを送信:

```
こんにちは
```

Botが自動的に返信します！

### ステップ3: 音楽を再生

#### 方法1: スラッシュコマンド

```
/play query:YOASOBI アイドル
```

#### 方法2: 自然言語（自動応答チャンネル）

```
YOASOBIのアイドル流して
```

---

## 📋 利用可能なコマンド

### AI関連

```
/chat message:質問内容
→ AIに質問（どのチャンネルでも使用可能）

/setchannel enable:True
→ 現在のチャンネルで自動応答を有効化

/setchannel enable:False
→ 現在のチャンネルで自動応答を無効化

/setmode mode:assistant
→ AIモードを変更（standard/assistant/creative/music_dj）

/status
→ Botの状態を確認
```

### 音楽関連

```
/play query:曲名
→ 音楽を再生

/skip
→ 現在の曲をスキップ

/stop
→ 音楽を停止してボットを切断

/queue
→ 現在のキューを表示

/recommend
→ AIが会話の流れから音楽を推薦
```

---

## 🎵 音楽の使い方

### 基本的な再生

```
/play query:YOASOBI アイドル
```

1. 曲の検索結果が表示される（最大5曲）
2. 番号ボタンをクリックして選択
3. 「Discord VC」または「Web高音質」を選択
4. 再生開始！

### 自然言語で再生（自動応答チャンネル）

```
YOASOBIのアイドル流して
米津玄師の曲かけて
リラックスできる曲流して
作業用BGM再生して
```

### URL直接再生

```
/play query:https://www.youtube.com/watch?v=xxxxx
/play query:https://open.spotify.com/track/xxxxx
```

### 音楽コントロール（自動応答チャンネル）

```
スキップ
停止
一時停止
再開
キュー見せて
今の曲は？
音量50
```

---

## 💬 AI自動応答の使い方

### 1. チャンネルを設定

```
/setchannel enable:True
```

### 2. 普通に会話

```
あなた: こんにちは
Bot: こんにちは！何かお手伝いできることはありますか？

あなた: 今日の天気は？
Bot: 申し訳ありませんが、リアルタイムの天気情報は取得できません...

あなた: Pythonでリストを反転する方法は？
Bot: Pythonでリストを反転する方法はいくつかあります...
```

### 3. AIモードを変更

```
/setmode mode:creative
→ より創造的な応答

/setmode mode:assistant
→ アシスタント的な応答

/setmode mode:standard
→ 標準的な応答
```

---

## 🔍 トラブルシューティング

### Q: AIが応答しない

**A**: チャンネルが自動応答に設定されているか確認

```
/setchannel enable:True
```

### Q: 音楽が再生できない

**A**: 次のデプロイ後に修正されます。Koyebが自動的にRedeployします。

確認方法:
```
/status
```

Lavalinkが「✅ 接続中」になっていればOK

### Q: コマンドが見つからない

**A**: Discordでコマンドを再同期

1. Discordを再起動
2. `/` を入力してコマンド一覧を確認
3. 表示されない場合は、Botを一度キックして再招待

---

## 📊 ダッシュボードの使い方

### Vercelダッシュボード

1. Vercelのダッシュボード URLを開く
2. 左側にユーザーアイコンが表示される
3. アイコンをクリックすると会話履歴が表示される
4. 統計情報やAPI使用量を確認できる

### 環境変数の確認

Vercel → Settings → Environment Variables

```
NEXT_PUBLIC_API_URL=https://dying-nana-haklab-3e0dcb62.koyeb.app
NEXT_PUBLIC_WS_URL=wss://dying-nana-haklab-3e0dcb62.koyeb.app/ws
```

---

## ✅ 次のステップ

### 1. GitHubにプッシュ

修正をプッシュすると、Koyebが自動的にRedeployします。

### 2. 音楽機能のテスト

Redeploy完了後（2-3分）:

```
/status
→ Lavalinkが「✅ 接続中」を確認

/play query:テスト曲
→ 曲が再生されることを確認
```

### 3. AI自動応答のテスト

```
/setchannel enable:True
→ チャンネルを設定

こんにちは
→ Botが返信することを確認
```

---

## 🎯 成功の確認

すべて正常に動作している場合:

1. ✅ `/status` でLavalinkが「✅ 接続中」
2. ✅ 自動応答チャンネルでBotが返信する
3. ✅ `/play` で曲が再生される
4. ✅ 「YOASOBIのアイドル流して」で曲が再生される
5. ✅ Vercelダッシュボードでデータが表示される

おめでとうございます！🎉

---

## 📞 サポート

問題が解決しない場合:

1. Koyebログを確認
2. `/status` コマンドを実行
3. エラーメッセージをコピー
4. 環境変数を確認

詳細なトラブルシューティング:
- `QUICK_DIAGNOSTIC.md` - クイック診断
- `MUSIC_AND_AI_FIX.md` - 音楽とAIの修正
- `DATABASE_FIX.md` - データベースの修正
