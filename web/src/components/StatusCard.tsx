"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface StatusCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  accent?: "pink" | "cyan";
  delay?: number;
}

export default function StatusCard({ icon: Icon, label, value, accent = "pink", delay = 0 }: StatusCardProps) {
  const accentColor = accent === "pink" ? "text-accent-pink" : "text-accent-cyan";
  const bgGradient = accent === "pink" 
    ? "from-accent-pink/20 to-transparent" 
    : "from-accent-cyan/20 to-transparent";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-dark-light/60 backdrop-blur-lg rounded-2xl border border-white/5 p-5 relative overflow-hidden"
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${bgGradient} opacity-30`} />
      <div className="relative">
        <Icon className={`${accentColor} mb-3`} size={24} />
        <p className="text-white/50 text-sm">{label}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
      </div>
    </motion.div>
  );
}
