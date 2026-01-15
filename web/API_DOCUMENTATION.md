# Discord Bot Dashboard API Documentation

## 統計情報API エンドポイント

### GET /api/stats

Discord Botの統計情報を取得するためのAPIエンドポイントです。

#### パラメータ

| パラメータ | 型 | デフォルト | 説明 |
|-----------|---|-----------|------|
| `type` | string | `overview` | 取得する統計情報の種類 |
| `days` | number | `30` | 日別データの取得期間（日数） |
| `limit` | number | `10` | トップサーバーの取得件数 |

#### type パラメータの値

- `overview`: 基本統計情報（総サーバー数、総メッセージ数など）
- `messages-by-day`: 日別メッセージ数
- `top-guilds`: メッセージ数上位サーバー
- `all`: 全ての統計情報を一度に取得

#### レスポンス例

##### type=overview
```json
{
  "success": true,
  "data": {
    "totalGuilds": 15,
    "totalMessages": 12450,
    "totalUsers": 350,
    "messagesLast7Days": 890,
    "messagesLast30Days": 3200
  }
}
```

##### type=messages-by-day
```json
{
  "success": true,
  "data": [
    {
      "date": "2026-01-01",
      "count": 45
    },
    {
      "date": "2026-01-02",
      "count": 67
    }
  ]
}
```

##### type=top-guilds
```json
{
  "success": true,
  "data": [
    {
      "guild_id": "123456789",
      "name": "My Discord Server",
      "message_count": 1250
    },
    {
      "guild_id": "987654321",
      "name": "Another Server",
      "message_count": 890
    }
  ]
}
```

##### type=all
```json
{
  "success": true,
  "data": {
    "overview": {
      "totalGuilds": 15,
      "totalMessages": 12450,
      "totalUsers": 350,
      "messagesLast7Days": 890,
      "messagesLast30Days": 3200
    },
    "messagesByDay": [
      {
        "date": "2026-01-01",
        "count": 45
      }
    ],
    "topGuilds": [
      {
        "guild_id": "123456789",
        "name": "My Discord Server",
        "message_count": 1250
      }
    ]
  }
}
```

#### エラーレスポンス

```json
{
  "success": false,
  "error": "エラーメッセージ"
}
```

### 使用例

#### JavaScript/TypeScript
```typescript
// 基本統計情報を取得
const response = await fetch('/api/stats?type=overview');
const data = await response.json();

// 過去7日間の日別メッセージ数を取得
const messagesResponse = await fetch('/api/stats?type=messages-by-day&days=7');
const messagesData = await messagesResponse.json();

// トップ5サーバーを取得
const topGuildsResponse = await fetch('/api/stats?type=top-guilds&limit=5');
const topGuildsData = await topGuildsResponse.json();

// 全ての統計情報を一度に取得
const allStatsResponse = await fetch('/api/stats?type=all&days=30&limit=10');
const allStatsData = await allStatsResponse.json();
```

#### cURL
```bash
# 基本統計情報
curl "http://localhost:3000/api/stats?type=overview"

# 日別メッセージ数（過去7日間）
curl "http://localhost:3000/api/stats?type=messages-by-day&days=7"

# トップ5サーバー
curl "http://localhost:3000/api/stats?type=top-guilds&limit=5"

# 全ての統計情報
curl "http://localhost:3000/api/stats?type=all&days=30&limit=10"
```

## セットアップ

1. 依存関係をインストール:
```bash
cd web
npm install
```

2. 開発サーバーを起動:
```bash
npm run dev
```

3. ダッシュボードにアクセス:
```
http://localhost:3000/dashboard
```

## データベース要件

このAPIは以下のテーブル構造を前提としています：

- `guilds`: サーバー情報
- `messages`: メッセージログ

詳細は `shared/schema.sql` を参照してください。