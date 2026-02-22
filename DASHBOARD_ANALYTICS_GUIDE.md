# 📊 ダッシュボード分析機能の実装ガイド

## 実装する機能

### 1. 音量調整ボタンの修正 ✅
- Wavelinkの音量取得方法を修正
- エラーハンドリングを追加

### 2. サーバー管理機能
- サーバーごとのメッセージ量
- アクティブユーザー数
- トークン使用量
- 音楽再生回数

### 3. 高画質グラフ
- **全期間**: すべてのデータ
- **月間**: 過去30日
- **週間**: 過去7日
- **日間**: 過去24時間

### 4. グラフの種類
- メッセージ数の推移
- ユーザー数の推移
- トークン使用量の推移
- 音楽再生回数の推移

### 5. インタラクティブ機能
- グラフをクリックで詳細表示
- 期間切り替え
- データのエクスポート

---

## 必要なパッケージ

```json
{
  "recharts": "^2.10.0"  // 高品質なグラフライブラリ
}
```

---

## API エンドポイント（追加が必要）

### 統計API

```python
@app.get("/api/guilds/{guild_id}/analytics")
async def get_guild_analytics(guild_id: int, period: str = "all"):
    """
    サーバーの分析データを取得
    period: all, month, week, day
    """
    pass

@app.get("/api/analytics/messages")
async def get_message_analytics(period: str = "all"):
    """メッセージ数の推移"""
    pass

@app.get("/api/analytics/users")
async def get_user_analytics(period: str = "all"):
    """ユーザー数の推移"""
    pass

@app.get("/api/analytics/tokens")
async def get_token_analytics(period: str = "all"):
    """トークン使用量の推移"""
    pass

@app.get("/api/analytics/music")
async def get_music_analytics(period: str = "all"):
    """音楽再生回数の推移"""
    pass
```

---

## データベーススキーマ（追加が必要）

### 日次統計テーブル

```sql
CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    date DATE NOT NULL,
    message_count INTEGER DEFAULT 0,
    user_count INTEGER DEFAULT 0,
    token_count INTEGER DEFAULT 0,
    music_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(guild_id, date)
);

CREATE INDEX idx_daily_stats_guild_date ON daily_stats(guild_id, date);
```

### 時間別統計テーブル

```sql
CREATE TABLE hourly_stats (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    hour TIMESTAMP NOT NULL,
    message_count INTEGER DEFAULT 0,
    user_count INTEGER DEFAULT 0,
    token_count INTEGER DEFAULT 0,
    music_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(guild_id, hour)
);

CREATE INDEX idx_hourly_stats_guild_hour ON hourly_stats(guild_id, hour);
```

---

## フロントエンド実装

### グラフコンポーネント

```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AnalyticsChartProps {
  data: Array<{ date: string; value: number }>;
  title: string;
  color: string;
}

const AnalyticsChart: React.FC<AnalyticsChartProps> = ({ data, title, color }) => {
  return (
    <div className="bg-discord-dark p-4 rounded-xl">
      <h3 className="text-white font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis dataKey="date" stroke="#888" />
          <YAxis stroke="#888" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#2f3136', border: 'none' }}
            labelStyle={{ color: '#fff' }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color} 
            strokeWidth={2}
            dot={{ fill: color, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
```

### 期間切り替え

```typescript
const [period, setPeriod] = useState<'all' | 'month' | 'week' | 'day'>('week');

<div className="flex gap-2 mb-4">
  <button onClick={() => setPeriod('all')} className={period === 'all' ? 'active' : ''}>
    全期間
  </button>
  <button onClick={() => setPeriod('month')} className={period === 'month' ? 'active' : ''}>
    月間
  </button>
  <button onClick={() => setPeriod('week')} className={period === 'week' ? 'active' : ''}>
    週間
  </button>
  <button onClick={() => setPeriod('day')} className={period === 'day' ? 'active' : ''}>
    日間
  </button>
</div>
```

---

## 実装手順

### ステップ1: データベースにテーブルを追加

```python
# bot/database_pg.py に追加

async def _create_tables_pg(self):
    # 既存のテーブル作成...
    
    # 日次統計テーブル
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            date DATE NOT NULL,
            message_count INTEGER DEFAULT 0,
            user_count INTEGER DEFAULT 0,
            token_count INTEGER DEFAULT 0,
            music_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, date)
        )
    ''')
    
    # 時間別統計テーブル
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS hourly_stats (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            hour TIMESTAMP NOT NULL,
            message_count INTEGER DEFAULT 0,
            user_count INTEGER DEFAULT 0,
            token_count INTEGER DEFAULT 0,
            music_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, hour)
        )
    ''')
```

### ステップ2: 統計収集機能を追加

```python
# bot/database_pg.py に追加

async def increment_daily_stat(self, guild_id: int, stat_type: str):
    """日次統計をインクリメント"""
    today = datetime.now().date()
    
    if self.pool:
        await self.pool.execute(f'''
            INSERT INTO daily_stats (guild_id, date, {stat_type})
            VALUES ($1, $2, 1)
            ON CONFLICT (guild_id, date)
            DO UPDATE SET {stat_type} = daily_stats.{stat_type} + 1
        ''', guild_id, today)

async def get_analytics_data(self, guild_id: int, period: str = "week"):
    """分析データを取得"""
    if period == "day":
        # 過去24時間
        query = '''
            SELECT hour, message_count, user_count, token_count, music_count
            FROM hourly_stats
            WHERE guild_id = $1 AND hour >= NOW() - INTERVAL '24 hours'
            ORDER BY hour
        '''
    elif period == "week":
        # 過去7日
        query = '''
            SELECT date, message_count, user_count, token_count, music_count
            FROM daily_stats
            WHERE guild_id = $1 AND date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY date
        '''
    elif period == "month":
        # 過去30日
        query = '''
            SELECT date, message_count, user_count, token_count, music_count
            FROM daily_stats
            WHERE guild_id = $1 AND date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY date
        '''
    else:  # all
        # 全期間
        query = '''
            SELECT date, message_count, user_count, token_count, music_count
            FROM daily_stats
            WHERE guild_id = $1
            ORDER BY date
        '''
    
    rows = await self._fetchall(query, guild_id)
    return rows
```

### ステップ3: APIエンドポイントを追加

```python
# bot/api_server.py に追加

@self.app.get("/api/guilds/{guild_id}/analytics")
async def get_guild_analytics(guild_id: int, period: str = "week"):
    """サーバーの分析データを取得"""
    try:
        data = await self.bot.database.get_analytics_data(guild_id, period)
        
        return {
            "success": True,
            "data": {
                "period": period,
                "stats": data
            }
        }
    except Exception as e:
        logger.error(f'Error getting analytics: {e}')
        raise HTTPException(status_code=500, detail="Failed to get analytics")
```

### ステップ4: フロントエンドにグラフを追加

```typescript
// dashboard/src/app/page.tsx に追加

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// ステート追加
const [analyticsData, setAnalyticsData] = useState<any>(null);
const [analyticsPeriod, setAnalyticsPeriod] = useState<'all' | 'month' | 'week' | 'day'>('week');

// データ取得
const fetchAnalytics = async (period: string) => {
  if (!selectedGuild) return;
  
  try {
    const res = await fetch(`${API_URL}/api/guilds/${selectedGuild.id}/analytics?period=${period}`);
    if (res.ok) {
      const data = await res.json();
      setAnalyticsData(data.data);
    }
  } catch (e) {
    console.error('Failed to fetch analytics:', e);
  }
};

// グラフ表示
<section className="bg-discord-dark p-4 rounded-xl">
  <div className="flex items-center justify-between mb-4">
    <h2 className="text-lg font-semibold text-white">📊 統計グラフ</h2>
    <div className="flex gap-2">
      {['day', 'week', 'month', 'all'].map(p => (
        <button
          key={p}
          onClick={() => { setAnalyticsPeriod(p as any); fetchAnalytics(p); }}
          className={`px-3 py-1 rounded ${analyticsPeriod === p ? 'bg-discord-blurple' : 'bg-discord-darker'}`}
        >
          {p === 'day' ? '日間' : p === 'week' ? '週間' : p === 'month' ? '月間' : '全期間'}
        </button>
      ))}
    </div>
  </div>
  
  {analyticsData && (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={analyticsData.stats}>
        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
        <XAxis dataKey="date" stroke="#888" />
        <YAxis stroke="#888" />
        <Tooltip 
          contentStyle={{ backgroundColor: '#2f3136', border: 'none', borderRadius: '8px' }}
          labelStyle={{ color: '#fff' }}
        />
        <Legend />
        <Line type="monotone" dataKey="message_count" stroke="#5865f2" name="メッセージ" strokeWidth={2} />
        <Line type="monotone" dataKey="user_count" stroke="#57f287" name="ユーザー" strokeWidth={2} />
        <Line type="monotone" dataKey="music_count" stroke="#eb459e" name="音楽" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  )}
</section>
```

---

## 完成イメージ

### ダッシュボード画面

```
┌─────────────────────────────────────────────────┐
│ 📊 統計グラフ          [日間][週間][月間][全期間] │
├─────────────────────────────────────────────────┤
│                                                 │
│  メッセージ数                                    │
│  ↗️ 📈                                          │
│                                                 │
│  [グラフ表示エリア]                              │
│                                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 📊 サーバー統計                                  │
├─────────────────────────────────────────────────┤
│ メッセージ: 1,234件                              │
│ アクティブユーザー: 56人                         │
│ トークン使用: 123,456                            │
│ 音楽再生: 89回                                   │
└─────────────────────────────────────────────────┘
```

---

## 次のステップ

1. ✅ 音量調整ボタンを修正（完了）
2. ⏳ データベースにテーブルを追加
3. ⏳ 統計収集機能を実装
4. ⏳ APIエンドポイントを追加
5. ⏳ フロントエンドにグラフを追加
6. ⏳ インタラクティブ機能を追加

---

## 注意事項

- グラフライブラリ（recharts）のインストールが必要
- データベースのマイグレーションが必要
- 統計データの収集は非同期で行う
- パフォーマンスを考慮してキャッシュを使用

---

この実装には時間がかかるため、段階的に実装することをお勧めします。
