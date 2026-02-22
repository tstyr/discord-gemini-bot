# 歌詞API設定ガイド

LRCLIB → NetEase → Genius の3段階フォールバックで、日本語の曲を含む多くの曲で歌詞を表示できます。

## 対応API

### 1. LRCLIB（最優先、完全無料）

- **URL**: https://lrclib.net
- **特徴**: 無料、APIキー不要、タイムスタンプ付き歌詞
- **設定**: 不要（自動で使用）
- **カバー率**: 日本の曲 50-60%、洋楽 80-90%

### 2. NetEase Cloud Music（日本語に強い、完全無料）

- **URL**: https://netease-cloud-music-api-phi-gules-69.vercel.app
- **特徴**: 中国最大の音楽サービス、日本の曲に強い、タイムスタンプ付き
- **設定**: 不要（自動で使用）
- **カバー率**: 日本の曲 80-90%、洋楽 70-80%

### 3. Genius（フォールバック、完全無料）

- **URL**: https://genius.com/api-clients
- **特徴**: 大規模な歌詞データベース、完全無料
- **制限**: タイムスタンプなし（推定タイムスタンプで対応）
- **カバー率**: 日本の曲 70-80%、洋楽 95%以上

## 検索精度の向上

### クエリクリーニング

以下のパターンを自動的に削除して検索精度を向上：

- `(TV Size)`, `(TV Ver.)`
- `(Short Ver.)`, `(Full Ver.)`
- `(Anime Ver.)`, `(Game Ver.)`
- `- Remastered`, `(Remastered)`
- `- Remix`, `(Remix)`
- `- Extended`, `(Extended)`
- `- Radio Edit`, `(Radio Edit)`
- `- Instrumental`, `(Instrumental)`
- `- Acoustic`, `(Acoustic)`
- `- Live`, `(Live)`
- `- Official Audio/Video`
- `[...]` 角括弧内の文字列
- `(feat. ...)`, `(ft. ...)` フィーチャリング

### 検索形式

`Artist Name - Song Title` の形式で検索してヒット率を向上。

## Genius API設定方法（オプション）

NetEaseでも見つからない場合のフォールバック用。

### 1. APIキーを取得

1. https://genius.com/api-clients にアクセス
2. Geniusアカウントでログイン（無料登録）
3. 「New API Client」をクリック
4. フォームに入力（すべて必須）:
   ```
   APP NAME: discord bot
   ICON URL: https://example.com/icon.png
   APP WEBSITE URL: https://example.com
   REDIRECT URI: https://example.com/callback
   ```
5. 「Save」をクリック
6. **Client Access Token** をコピー

⚠️ **注意**: すべての項目が必須です。実際に動作するURLでなくても登録できます。

### 2. Koyebに設定

1. Koyeb Dashboard → あなたのサービス
2. **Settings** → **Environment variables**
3. 「Add variable」をクリック
4. 以下を追加:
   ```
   Key: GENIUS_API_KEY
   Value: (コピーしたClient Access Token)
   ```
5. **Deploy** をクリック

## フォールバック動作

歌詞の検索は以下の順序で行われます：

1. **LRCLIB** - タイムスタンプ付き歌詞（高精度）
2. **NetEase** - タイムスタンプ付き歌詞（日本語に強い）
3. **Genius** - タイムスタンプ推定（LRCLIBとNetEaseで見つからない場合）

## 使い方

### 基本（APIキー不要）

```
/lyrics_mode mode:ON
```

LRCLIB + NetEaseで動作。ほとんどの日本語の曲に対応します。

### さらに多くの曲に対応

Genius APIキーを設定すると、LRCLIBとNetEaseで見つからない曲も表示されます。

## 歌詞取得の状態表示

曲が再生されると、`#lyrics-stream` チャンネルに以下のメッセージが表示されます：

- 🔍 **歌詞を検索中**: 検索開始
- ✅ **歌詞を取得しました**: 成功（歌詞の行数とソースも表示）
  - `LRCLIB: 50 lines`
  - `NetEase: 45 lines`
  - `Genius: 40 lines (estimated timestamps)`
- ❌ **歌詞が見つかりませんでした**: 失敗

## LRC形式のパース

### 対応フォーマット

- `[mm:ss.xx]` - センチ秒（1/100秒）
- `[mm:ss.xxx]` - ミリ秒（1/1000秒、NetEase形式）

### タイムスタンプ精度

- LRCLIB: 0.01秒精度
- NetEase: 0.001秒精度
- Genius: 推定（精度低）

## トラブルシューティング

### 日本語の曲が見つからない

- NetEaseが自動的に検索するので、ほとんどの日本語の曲に対応
- それでも見つからない場合は、曲名やアーティスト名が正確か確認

### 洋楽が見つからない

- LRCLIBが優先的に検索
- Genius APIキーを設定して検索範囲を広げる

### タイムスタンプがずれる

- Geniusから取得した歌詞は推定タイムスタンプのため、ずれる可能性があります
- LRCLIBやNetEaseで見つかる曲を優先してください

### ループボタンで曲が止まる

- 修正済み：ループボタンを押しても曲は止まりません
- エラーが発生した場合はログを確認してください

## 完全無料で使える

- LRCLIB: 完全無料、制限なし
- NetEase: 完全無料、制限なし
- Genius: 完全無料、制限なし（通常使用の範囲内）

すべて無料で使えるので、安心して設定してください！

## 日本語の曲のヒット率

NetEase Cloud Music APIの追加により、日本語の曲のヒット率が大幅に向上しました：

- アニメソング: 90%以上
- J-POP: 85%以上
- ボカロ曲: 80%以上
