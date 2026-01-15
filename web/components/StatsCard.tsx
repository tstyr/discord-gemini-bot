"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  icon: LucideIcon;
  title: string;
  value: string;
  delay?: number;
}

export default function StatsCard({ icon: Icon, title, value, delay = 0 }: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="bg-discord-dark rounded-xl p-6 hover:bg-discord-dark/80 transition-colors"
    >
      <div className="flex items-center gap-4">
        <div className="p-3 bg-discord-blurple/20 rounded-lg">
          <Icon className="w-6 h-6 text-discord-blurple" />
        </div>
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </div>
    </motion.div>
  );
}
