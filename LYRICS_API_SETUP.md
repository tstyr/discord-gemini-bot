# 歌詞API設定ガイド

LRCLIB → Genius の2段階フォールバックで、より多くの曲で歌詞を表示できます。

## 対応API

### 1. LRCLIB（デフォルト、完全無料）

- **URL**: https://lrclib.net
- **特徴**: 無料、APIキー不要、タイムスタンプ付き歌詞
- **設定**: 不要（自動で使用）
- **カバー率**: 日本の曲 50-60%、洋楽 80-90%

### 2. Genius（フォールバック、完全無料）

- **URL**: https://genius.com/api-clients
- **特徴**: 大規模な歌詞データベース、完全無料
- **制限**: タイムスタンプなし（推定タイムスタンプで対応）
- **カバー率**: 日本の曲 70-80%、洋楽 95%以上

## Genius API設定方法

### 1. APIキーを取得

1. https://genius.com/api-clients にアクセス
2. Geniusアカウントでログイン（無料登録）
3. 「New API Client」をクリック
4. フォームに入力:
   - **APP NAME**: `discord bot`（任意）
   - **ICON URL**: 空欄でOK
   - **APP WEBSITE URL**: 空欄でOK
   - **REDIRECT URI**: 空欄でOK
5. 「Save」をクリック
6. **Client Access Token** をコピー

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
2. **Genius** - タイムスタンプ推定（LRCLIBで見つからない場合）

## 使い方

### 基本（APIキー不要）

```
/lyrics_mode mode:ON
```

LRCLIBのみ使用。そのまま使えます。

### より多くの曲に対応

Genius APIキーを設定すると、LRCLIBで見つからない曲も表示されます。

## タイムスタンプ推定について

Geniusから取得した歌詞はタイムスタンプがないため、以下の方法で推定します：

- 曲の長さを歌詞の行数で割って均等配置
- 精度は低いが、歌詞がないよりマシ

## トラブルシューティング

### 歌詞が見つからない

- 曲名やアーティスト名が正確か確認
- Genius APIキーを設定して検索範囲を広げる

### タイムスタンプがずれる

- Geniusから取得した歌詞は推定タイムスタンプのため、ずれる可能性があります
- LRCLIBで見つかる曲を優先してください

### API制限エラー

- Geniusは完全無料で制限なし（通常使用の範囲内）
- レート制限に達した場合は少し待ってから再試行

## 完全無料で使える

- LRCLIB: 完全無料、制限なし
- Genius: 完全無料、制限なし（通常使用の範囲内）

両方とも無料で使えるので、安心して設定してください！
