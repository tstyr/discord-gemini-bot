'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface TokenData {
  time: string;
  tokens: number;
}

interface TokenChartProps {
  data?: TokenData[];
  className?: string;
}

export default function TokenChart({ data = [], className = '' }: TokenChartProps) {
  // Mock data if none provided
  const mockData = [
    { time: '00:00', tokens: 120 },
    { time: '04:00', tokens: 80 },
    { time: '08:00', tokens: 200 },
    { time: '12:00', tokens: 350 },
    { time: '16:00', tokens: 280 },
    { time: '20:00', tokens: 150 },
  ];

  const chartData = data.length > 0 ? data : mockData;

  return (
    <div className={`h-64 ${className}`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis 
            dataKey="time" 
            stroke="#666" 
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            stroke="#666" 
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1a1a1a', 
              border: '1px solid #333',
              borderRadius: '8px',
              backdropFilter: 'blur(10px)'
            }}
            labelStyle={{ color: '#fff' }}
          />
          <Line
            type="monotone"
            dataKey="tokens"
            stroke="#ff66aa"
            strokeWidth={3}
            dot={{ fill: '#ff66aa', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#ff66aa', strokeWidth: 2 }}
            filter="drop-shadow(0 0 6px #ff66aa)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export { TokenChart };