"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface CircularChartProps {
  value: number;
  max: number;
  label: string;
  color: "pink" | "cyan" | "purple";
}

export function CircularChart({ value, max, label, color }: CircularChartProps) {
  const [progress, setProgress] = useState(0);
  const percentage = (value / max) * 100;
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  const colors = {
    pink: { gradient: "from-osu-pink to-pink-400", glow: "osu-pink", stroke: "#ff66aa" },
    cyan: { gradient: "from-osu-cyan to-cyan-400", glow: "osu-cyan", stroke: "#00ffcc" },
    purple: { gradient: "from-osu-purple to-purple-400", glow: "osu-purple", stroke: "#aa66ff" },
  };

  useEffect(() => {
    const timer = setTimeout(() => setProgress(percentage), 100);
    return () => clearTimeout(timer);
  }, [percentage]);

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg className="transform -rotate-90 w-32 h-32">
          {/* Background circle */}
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-white/10"
          />
          {/* Progress circle */}
          <motion.circle
            cx="64"
            cy="64"
            r="45"
            stroke={colors[color].stroke}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{
              filter: `drop-shadow(0 0 8px ${colors[color].stroke})`,
            }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-2xl font-bold bg-gradient-to-br ${colors[color].gradient} bg-clip-text text-transparent`}>
            {value.toLocaleString()}
          </span>
        </div>
      </div>
      <p className="text-sm text-white/60 mt-3">{label}</p>
    </div>
  );
}
