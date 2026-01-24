# 歌詞API設定ガイド

複数の歌詞APIを使用して、より多くの曲で歌詞を表示できるようにします。

## 対応API

### 1. LRCLIB（デフォルト、無料）

- **URL**: https://lrclib.net
- **特徴**: 無料、APIキー不要、タイムスタンプ付き歌詞
- **設定**: 不要（自動で使用）

### 2. Musixmatch（フォールバック1）

- **URL**: https://developer.musixmatch.com/
- **特徴**: 大規模な歌詞データベース、タイムスタンプ付き
- **制限**: 無料プランは1日500リクエスト

#### 設定方法

1. https://developer.musixmatch.com/ にアクセス
2. アカウント作成
3. APIキーを取得
4. Koyebの環境変数に追加:
   ```
   MUSIXMATCH_API_KEY=your_api_key_here
   ```

### 3. Genius（フォールバック2）

- **URL**: https://genius.com/api-clients
- **特徴**: 歌詞の意味や解説も取得可能
- **制限**: タイムスタンプなし（推定タイムスタンプを使用）

#### 設定方法

1. https://genius.com/api-clients にアクセス
2. 「New API Client」を作成
3. Client Access Tokenを取得
4. Koyebの環境変数に追加:
   ```
   GENIUS_API_KEY=your_access_token_here
   ```

## フォールバック動作

歌詞の検索は以下の順序で行われます：

1. **LRCLIB** - 最優先（無料、高品質）
2. **Musixmatch** - LRCLIBで見つからない場合
3. **Genius** - Musixmatchでも見つからない場合

## Koyebでの設定

1. Koyeb Dashboard → あなたのサービス → **Settings** → **Environment variables**
2. 以下を追加（オプション）:
   - `MUSIXMATCH_API_KEY`
   - `GENIUS_API_KEY`
3. **Deploy** をクリック

## 注意事項

- APIキーを設定しない場合は、LRCLIBのみ使用されます
- 無料プランの制限に注意してください
- タイムスタンプなしの歌詞は推定タイムスタンプで表示されます

## トラブルシューティング

### 歌詞が見つからない

- 曲名やアーティスト名が正確か確認
- 複数のAPIキーを設定して検索範囲を広げる

### API制限エラー

- 無料プランの制限を超えた可能性
- 24時間待つか、有料プランにアップグレード

### タイムスタンプがずれる

- Geniusから取得した歌詞は推定タイムスタンプのため、ずれる可能性があります
- LRCLIBやMusixmatchで見つかる曲を優先してください
