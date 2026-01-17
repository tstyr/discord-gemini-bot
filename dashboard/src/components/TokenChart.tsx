"use client";

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

// Mock data - replace with real API data
const data = [
  { date: "1/1", tokens: 1200 },
  { date: "1/2", tokens: 1800 },
  { date: "1/3", tokens: 2400 },
  { date: "1/4", tokens: 1600 },
  { date: "1/5", tokens: 3200 },
  { date: "1/6", tokens: 2800 },
  { date: "1/7", tokens: 3600 },
];

export function TokenChart() {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="tokenGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ff66aa" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#ff66aa" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis 
          dataKey="date" 
          axisLine={false} 
          tickLine={false} 
          tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} 
        />
        <YAxis 
          axisLine={false} 
          tickLine={false} 
          tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 12 }} 
        />
        <Tooltip
          contentStyle={{
            background: "#222",
            border: "1px solid rgba(255,102,170,0.3)",
            borderRadius: "8px",
            color: "white",
          }}
        />
        <Area
          type="monotone"
          dataKey="tokens"
          stroke="#ff66aa"
          strokeWidth={2}
          fill="url(#tokenGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
