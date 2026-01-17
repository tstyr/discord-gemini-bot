"use client";

import { motion } from 'framer-motion';

interface CircularProgressProps {
  value: number;
  max: number;
  label: string;
  color: 'cyan' | 'magenta' | 'green' | 'yellow';
  icon?: React.ReactNode;
}

export default function CircularProgress({ value, max, label, color, icon }: CircularProgressProps) {
  const percentage = Math.min((value / max) * 100, 100);
  const circumference = 2 * Math.PI * 45; // radius = 45
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const colorClasses = {
    cyan: {
      gradient: 'from-cyan-500 to-cyan-600',
      glow: 'shadow-cyan-500/50',
      text: 'text-cyan-400',
      stroke: 'stroke-cyan-500'
    },
    magenta: {
      gradient: 'from-fuchsia-500 to-pink-600',
      glow: 'shadow-fuchsia-500/50',
      text: 'text-fuchsia-400',
      stroke: 'stroke-fuchsia-500'
    },
    green: {
      gradient: 'from-green-500 to-emerald-600',
      glow: 'shadow-green-500/50',
      text: 'text-green-400',
      stroke: 'stroke-green-500'
    },
    yellow: {
      gradient: 'from-yellow-500 to-orange-600',
      glow: 'shadow-yellow-500/50',
      text: 'text-yellow-400',
      stroke: 'stroke-yellow-500'
    }
  };

  const colors = colorClasses[color];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="relative"
    >
      <div className={`relative w-32 h-32 rounded-full bg-gradient-to-br ${colors.gradient} p-1 shadow-2xl ${colors.glow}`}>
        <div className="w-full h-full rounded-full bg-gray-900 flex items-center justify-center">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth="8"
            />
            {/* Progress circle */}
            <motion.circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              className={colors.stroke}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1, ease: "easeOut" }}
              style={{
                filter: `drop-shadow(0 0 8px currentColor)`
              }}
            />
          </svg>
          
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {icon && (
              <div className={`mb-1 ${colors.text}`}>
                {icon}
              </div>
            )}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="text-center"
            >
              <div className="text-2xl font-bold text-white">
                {value.toLocaleString()}
              </div>
              <div className="text-xs text-gray-400">
                / {max.toLocaleString()}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
      
      {/* Label */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="mt-3 text-center"
      >
        <p className="text-sm font-semibold text-white">{label}</p>
        <p className={`text-xs ${colors.text}`}>
          {percentage.toFixed(1)}%
        </p>
      </motion.div>
    </motion.div>
  );
}
