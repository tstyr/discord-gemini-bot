# ネットワーク統計機能実装プロンプト

## 概要

Botのネットワーク送受信量を追跡し、リアルタイムで表示する機能を実装します。

## 実装内容

### 1. ネットワーク統計の追跡

#### 追跡対象
- **送信量 (TX)**: Botが送信したデータ量（MB）
- **受信量 (RX)**: Botが受信したデータ量（MB）
- **合計**: TX + RX
- **期間**: 今日、今週、今月、全期間

#### 追跡方法
```python
import psutil

# ネットワークI/O統計を取得
net_io = psutil.net_io_counters()
bytes_sent = net_io.bytes_sent  # 送信バイト数
bytes_recv = net_io.bytes_recv  # 受信バイト数
```

### 2. Supabaseテーブル設計

#### `network_stats` テーブル

```sql
CREATE TABLE IF NOT EXISTS network_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bytes_sent BIGINT NOT NULL,           -- 送信バイト数
    bytes_recv BIGINT NOT NULL,           -- 受信バイト数
    bytes_total BIGINT NOT NULL,          -- 合計バイト数
    mb_sent REAL NOT NULL,                -- 送信MB
    mb_recv REAL NOT NULL,                -- 受信MB
    mb_total REAL NOT NULL,               -- 合計MB
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_network_stats_recorded_at 
    ON network_stats(recorded_at DESC);

-- RLS設定
ALTER TABLE network_stats ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated read access" ON network_stats 
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow service role full access" ON network_stats 
    FOR ALL TO service_role USING (true);
```

### 3. データ収集

#### `supabase_client.py`に追加

```python
async def _send_network_stats(self):
    """ネットワーク統計をSupabaseに送信"""
    try:
        import psutil
        
        # 現在のネットワークI/O統計
        net_io = psutil.net_io_counters()
        
        # 前回の値との差分を計算（初回は0）
        if not hasattr(self, '_last_net_io'):
            self._last_net_io = net_io
            return
        
        bytes_sent = net_io.bytes_sent - self._last_net_io.bytes_sent
        bytes_recv = net_io.bytes_recv - self._last_net_io.bytes_recv
        bytes_total = bytes_sent + bytes_recv
        
        # MBに変換
        mb_sent = bytes_sent / 1024 / 1024
        mb_recv = bytes_recv / 1024 / 1024
        mb_total = bytes_total / 1024 / 1024
        
        stats = {
            'bytes_sent': int(bytes_sent),
            'bytes_recv': int(bytes_recv),
            'bytes_total': int(bytes_total),
            'mb_sent': float(mb_sent),
            'mb_recv': float(mb_recv),
            'mb_total': float(mb_total)
        }
        
        self.client.table('network_stats').insert(stats).execute()
        
        # 現在の値を保存
        self._last_net_io = net_io
        
        logger.debug(f"📊 Network stats: TX={mb_sent:.2f}MB, RX={mb_recv:.2f}MB")
        
    except Exception as e:
        logger.error(f"❌ Failed to send network stats: {e}")
```

#### `health_monitor_loop`に統合

```python
@tasks.loop(seconds=10)
async def health_monitor_loop(self):
    """10秒ごとにシステムメトリクスを送信"""
    try:
        await self._send_system_stats()
        await self._send_network_stats()  # ✅ 追加
    except Exception as e:
        logger.error(f"❌ Health monitor error: {e}")
```

### 4. `/netstats`コマンド

#### `admin_commands.py`に追加

```python
@app_commands.command(name="netstats", description="ネットワーク統計を表示")
@app_commands.describe(period="期間")
@app_commands.choices(period=[
    app_commands.Choice(name="今日", value="today"),
    app_commands.Choice(name="今週", value="week"),
    app_commands.Choice(name="今月", value="month"),
    app_commands.Choice(name="全期間", value="all"),
])
async def netstats(self, interaction: discord.Interaction, period: str = "today"):
    """ネットワーク統計を表示"""
    await interaction.response.defer()
    
    try:
        if not self.bot.supabase_client or not self.bot.supabase_client.client:
            await interaction.followup.send("❌ Supabaseに接続されていません。", ephemeral=True)
            return
        
        # 期間の開始日時を計算
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            title = "📊 Network Stats - Today"
        elif period == "week":
            start_date = now - timedelta(days=7)
            title = "📊 Network Stats - Last 7 Days"
        elif period == "month":
            start_date = now - timedelta(days=30)
            title = "📊 Network Stats - Last 30 Days"
        else:  # all
            start_date = datetime(2020, 1, 1)
            title = "📊 Network Stats - All Time"
        
        # データを取得
        result = self.bot.supabase_client.client.table('network_stats')\
            .select('mb_sent, mb_recv, mb_total')\
            .gte('recorded_at', start_date.isoformat())\
            .execute()
        
        if not result.data:
            await interaction.followup.send("📊 データがありません。", ephemeral=True)
            return
        
        # 合計を計算
        total_sent = sum(row['mb_sent'] for row in result.data)
        total_recv = sum(row['mb_recv'] for row in result.data)
        total = total_sent + total_recv
        
        # GBに変換（1GB以上の場合）
        if total >= 1024:
            sent_str = f"{total_sent / 1024:.2f} GB"
            recv_str = f"{total_recv / 1024:.2f} GB"
            total_str = f"{total / 1024:.2f} GB"
        else:
            sent_str = f"{total_sent:.2f} MB"
            recv_str = f"{total_recv / 1024:.2f} MB"
            total_str = f"{total:.2f} MB"
        
        embed = discord.Embed(
            title=title,
            color=0x00ff88,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📤 Sent", value=sent_str, inline=True)
        embed.add_field(name="📥 Received", value=recv_str, inline=True)
        embed.add_field(name="📊 Total", value=total_str, inline=True)
        
        # データポイント数
        embed.add_field(name="📈 Data Points", value=f"{len(result.data):,}", inline=True)
        
        # 平均（10秒ごとのデータなので）
        if len(result.data) > 0:
            avg_per_10s = total / len(result.data)
            embed.add_field(name="⚡ Avg/10s", value=f"{avg_per_10s:.2f} MB", inline=True)
        
        embed.set_footer(text="Updated every 10 seconds")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in netstats command: {e}")
        import traceback
        traceback.print_exc()
        await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}", ephemeral=True)
```

### 5. Webダッシュボード対応

#### フロントエンド（Next.js）

```typescript
// app/network/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { Line } from 'react-chartjs-2'

interface NetworkStat {
  id: string
  mb_sent: number
  mb_recv: number
  mb_total: number
  recorded_at: string
}

export default function NetworkStatsPage() {
  const [stats, setStats] = useState<NetworkStat[]>([])
  const [totalSent, setTotalSent] = useState(0)
  const [totalRecv, setTotalRecv] = useState(0)
  const supabase = createClient()

  useEffect(() => {
    // 初期データ取得
    fetchStats()

    // リアルタイム更新
    const channel = supabase
      .channel('network_stats_changes')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'network_stats'
        },
        (payload) => {
          const newStat = payload.new as NetworkStat
          setStats(prev => [...prev.slice(-100), newStat]) // 最新100件
          setTotalSent(prev => prev + newStat.mb_sent)
          setTotalRecv(prev => prev + newStat.mb_recv)
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  const fetchStats = async () => {
    const { data, error } = await supabase
      .from('network_stats')
      .select('*')
      .order('recorded_at', { ascending: false })
      .limit(100)

    if (data) {
      setStats(data.reverse())
      setTotalSent(data.reduce((sum, s) => sum + s.mb_sent, 0))
      setTotalRecv(data.reduce((sum, s) => sum + s.mb_recv, 0))
    }
  }

  const chartData = {
    labels: stats.map(s => new Date(s.recorded_at).toLocaleTimeString()),
    datasets: [
      {
        label: 'Sent (MB)',
        data: stats.map(s => s.mb_sent),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Received (MB)',
        data: stats.map(s => s.mb_recv),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      }
    ]
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Network Statistics</h1>
      
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Total Sent</h3>
          <p className="text-2xl font-bold">{totalSent.toFixed(2)} MB</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Total Received</h3>
          <p className="text-2xl font-bold">{totalRecv.toFixed(2)} MB</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Total</h3>
          <p className="text-2xl font-bold">{(totalSent + totalRecv).toFixed(2)} MB</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Real-time Traffic</h2>
        <Line data={chartData} />
      </div>
    </div>
  )
}
```

## 実装手順

1. **Supabaseテーブル作成**
   - SQL Editorで`network_stats`テーブルを作成

2. **Bot側実装**
   - `supabase_client.py`に`_send_network_stats()`を追加
   - `health_monitor_loop`に統合
   - `admin_commands.py`に`/netstats`コマンドを追加

3. **Webダッシュボード実装**
   - Next.jsプロジェクトに`app/network/page.tsx`を追加
   - Chart.jsをインストール: `npm install react-chartjs-2 chart.js`
   - Supabase Realtimeで自動更新

4. **テスト**
   - `/netstats today`でデータ確認
   - Webダッシュボードでリアルタイム表示確認

## 注意事項

- ネットワーク統計は差分で記録（10秒ごとの増加量）
- 初回起動時は前回の値がないため、2回目から正確なデータ
- Supabase Realtimeは無料プランで制限あり（同時接続数）
- データ量が多い場合は定期的にクリーンアップ推奨

## クリーンアップ

古いデータを削除する場合：

```sql
-- 30日以上前のデータを削除
DELETE FROM network_stats 
WHERE recorded_at < NOW() - INTERVAL '30 days';
```

または、`supabase_log_handler.py`と同様に自動クリーンアップを実装。
