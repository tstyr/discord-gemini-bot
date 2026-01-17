"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  accent?: "pink" | "cyan" | "purple";
}

export function Card({ children, className = "", delay = 0, accent = "pink" }: CardProps) {
  const accentColors = {
    pink: "from-osu-pink/20 to-transparent border-osu-pink/30",
    cyan: "from-osu-cyan/20 to-transparent border-osu-cyan/30",
    purple: "from-osu-purple/20 to-transparent border-osu-purple/30",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      className={`
        relative overflow-hidden rounded-2xl
        bg-gradient-to-br ${accentColors[accent]}
        bg-osu-gray/50 backdrop-blur-sm
        border border-white/5
        p-6 ${className}
      `}
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}

export function CardTitle({ children, icon }: { children: ReactNode; icon?: ReactNode }) {
  return (
    <h3 className="flex items-center gap-2 text-lg font-semibold text-white/90 mb-4">
      {icon && <span className="text-osu-pink">{icon}</span>}
      {children}
    </h3>
  );
}

export function StatValue({ value, label, trend }: { value: string | number; label: string; trend?: "up" | "down" }) {
  return (
    <div className="text-center">
      <div className="text-3xl font-bold bg-gradient-osu bg-clip-text text-transparent">
        {value}
      </div>
      <div className="text-sm text-white/50 mt-1">{label}</div>
    </div>
  );
}
