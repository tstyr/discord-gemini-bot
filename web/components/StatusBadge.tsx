"use client";

import { motion } from "framer-motion";

interface StatusBadgeProps {
  status: "online" | "offline" | "idle";
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const statusConfig = {
    online: { color: "bg-osu-cyan", text: "オンライン", pulse: true },
    offline: { color: "bg-red-500", text: "オフライン", pulse: false },
    idle: { color: "bg-yellow-500", text: "アイドル", pulse: false },
  };

  const config = statusConfig[status];

  return (
    <div className="flex items-center gap-2">
      <span className="relative flex h-3 w-3">
        {config.pulse && (
          <motion.span
            animate={{ scale: [1, 1.5, 1], opacity: [0.7, 0, 0.7] }}
            transition={{ duration: 2, repeat: Infinity }}
            className={`absolute inline-flex h-full w-full rounded-full ${config.color} opacity-75`}
          />
        )}
        <span className={`relative inline-flex rounded-full h-3 w-3 ${config.color}`} />
      </span>
      <span className="text-white/70 text-sm">{label || config.text}</span>
    </div>
  );
}
