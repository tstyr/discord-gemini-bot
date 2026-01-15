"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface StatsCardProps {
  icon: ReactNode;
  title: string;
  value: string;
  trend: string;
}

export default function StatsCard({ icon, title, value, trend }: StatsCardProps) {
  const isPositive = trend.startsWith("+") || trend.startsWith("-0");

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-dark-200 rounded-2xl p-6 border border-dark-100"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center text-primary-400">
          {icon}
        </div>
        <span
          className={`text-sm px-2 py-1 rounded-full ${
            isPositive
              ? "bg-green-500/20 text-green-400"
              : "bg-red-500/20 text-red-400"
          }`}
        >
          {trend}
        </span>
      </div>
      <h3 className="text-gray-400 text-sm mb-1">{title}</h3>
      <p className="text-2xl font-bold text-white">{value}</p>
    </motion.div>
  );
}
