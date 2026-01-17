# Vercel デプロイメントガイド

## 問題: UIが更新されない

### 原因
Vercelには2種類のURLがあります：

1. **Production URL（本番URL）**
   - 例: `discord-gemini-bot-rjdl.vercel.app`
   - 短くてシンプル
   - `main`ブランチのデプロイ先

2. **Preview URL（プレビューURL）**
   - 例: `discord-gemini-bot-rjdl-2wfigtp2b-...vercel.app`
   - 非常に長い
   - 特定のコミット専用
   - 古いキャッシュが残りやすい

### 解決方法

#### 1. Production URLを確認する

1. [Vercelダッシュボード](https://vercel.com/dashboard)にアクセス
2. プロジェクト `discord-gemini-bot-rjdl` を選択
3. 「Domains」タブで本番URLを確認
4. **本番URL**を直接開いてください（プレビューURLではなく）

#### 2. キャッシュをクリアする

ブラウザで以下を試してください：

- **Chrome/Edge**: `Ctrl + Shift + R` (Windows) / `Cmd + Shift + R` (Mac)
- **Firefox**: `Ctrl + F5` (Windows) / `Cmd + Shift + R` (Mac)
- **Safari**: `Cmd + Option + R`

または：

1. ブラウザの設定を開く
2. 「閲覧履歴データの削除」
3. 「キャッシュされた画像とファイル」を選択
4. 削除を実行

#### 3. Vercelで再デプロイする

1. Vercelダッシュボードでプロジェクトを開く
2. 「Deployments」タブを選択
3. 最新のデプロイメントの右側にある「...」メニューをクリック
4. 「Redeploy」を選択
5. 「Redeploy」ボタンをクリック

#### 4. 環境変数を確認する

Vercelの「Settings」→「Environment Variables」で以下を確認：

```
NEXT_PUBLIC_API_URL=https://your-bot-api.com
NEXT_PUBLIC_WS_URL=wss://your-bot-api.com/ws
```

環境変数を変更した場合は、必ず再デプロイが必要です。

## ナビゲーション改善完了

### 実装内容

左サイドバーのBotアイコンに以下の機能を追加しました：

1. **ホームボタンとして機能**
   - クリックするとダッシュボードに戻る
   - どの画面からでもアクセス可能

2. **視覚的なフィードバック**
   - ダッシュボード表示中: 白いリングでハイライト
   - チャット表示中: ホバーで角丸に変化
   - アニメーション効果（拡大/縮小）

3. **一貫性のある動作**
   - ヘッダーの「戻る」ボタンと同じ動作
   - 右サイドバーの「ダッシュボードに戻る」ボタンと同じ動作

### 使い方

- **ダッシュボードに戻る**: 左上のBotアイコンをクリック
- **ユーザーとチャット**: 左サイドバーのユーザーアイコンをクリック
- **現在の位置を確認**: Botアイコンが白いリングで囲まれている = ダッシュボード

## トラブルシューティング

### UIが更新されない場合のチェックリスト

- [ ] 本番URL（短いURL）を使用している
- [ ] ブラウザのキャッシュをクリアした
- [ ] Vercelで最新のデプロイメントが成功している
- [ ] 環境変数が正しく設定されている
- [ ] GitHubに最新のコードがプッシュされている

### デプロイメントが失敗する場合

1. Vercelのデプロイメントログを確認
2. ビルドエラーがないか確認
3. `package.json`の依存関係を確認
4. Node.jsのバージョンを確認（`package.json`の`engines`フィールド）

### 接続エラーが出る場合

1. API URLが正しいか確認
2. WebSocket URLが正しいか確認（`wss://`で始まる）
3. Botサーバーが起動しているか確認
4. CORSの設定を確認

## 参考リンク

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
