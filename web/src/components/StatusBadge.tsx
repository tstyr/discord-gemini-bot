"use client";

import { motion } from "framer-motion";
import { Activity } from "lucide-react";

interface StatusBadgeProps {
  status: "online" | "offline" | "idle";
  botName?: string;
}

const statusConfig = {
  online: { color: "bg-osu-cyan", text: "オンライン", glow: "glow-cyan" },
  offline: { color: "bg-red-500", text: "オフライン", glow: "" },
  idle: { color: "bg-yellow-500", text: "アイドル", glow: "" },
};

export default function StatusBadge({
  status,
  botName = "AI Bot",
}: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`osu-card flex items-center gap-4 ${config.glow}`}
    >
      <div className="relative">
        <div className="w-14 h-14 rounded-2xl bg-osu-gradient flex items-center justify-center">
          <Activity className="w-7 h-7 text-white" />
        </div>
        <span
          className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full ${config.color} border-2 border-osu-surface`}
        />
      </div>
      <div>
        <h2 className="text-xl font-bold">{botName}</h2>
        <p className="text-sm text-gray-400 flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${config.color} animate-pulse`} />
          {config.text}
        </p>
      </div>
    </motion.div>
  );
}
