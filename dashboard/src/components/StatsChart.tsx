"use client";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface StatsChartProps {
  data: { date: string; tokens: number; messages: number }[];
}

export default function StatsChart({ data }: StatsChartProps) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="tokenGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#ff66aa" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#ff66aa" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="msgGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#00ffcc" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#00ffcc" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date"
          stroke="#ffffff30"
          fontSize={12}
          tickLine={false}
        />
        <YAxis stroke="#ffffff30" fontSize={12} tickLine={false} />
        <Tooltip
          contentStyle={{
            background: "#1a1a1a",
            border: "1px solid #ff66aa30",
            borderRadius: "12px",
          }}
        />
        <Area
          type="monotone"
          dataKey="tokens"
          stroke="#ff66aa"
          fill="url(#tokenGradient)"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="messages"
          stroke="#00ffcc"
          fill="url(#msgGradient)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
