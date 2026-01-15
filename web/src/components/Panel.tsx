"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface PanelProps {
  title: string;
  children: ReactNode;
  delay?: number;
  className?: string;
}

export default function Panel({ title, children, delay = 0, className = "" }: PanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`bg-dark-light/60 backdrop-blur-lg rounded-2xl border border-white/5 p-6 ${className}`}
    >
      <h2 className="text-lg font-semibold mb-4 text-white/90">{title}</h2>
      {children}
    </motion.div>
  );
}
