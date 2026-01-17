"use client";

import { motion } from "framer-motion";
import { Home, Settings, BarChart3, MessageSquare, Hash, Bot } from "lucide-react";
import Link from "next/link";

const navItems = [
  { icon: Home, label: "ダッシュボード", href: "/dashboard" },
  { icon: BarChart3, label: "統計", href: "/dashboard/stats" },
  { icon: Hash, label: "チャンネル", href: "/dashboard/channels" },
  { icon: MessageSquare, label: "ログ", href: "/dashboard/logs" },
  { icon: Settings, label: "設定", href: "/dashboard/settings" },
];

export function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -80, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed left-0 top-0 h-screen w-20 bg-osu-darker/80 backdrop-blur-lg border-r border-white/5 flex flex-col items-center py-6 z-50"
    >
      {/* Logo */}
      <div className="mb-8">
        <div className="w-12 h-12 rounded-xl bg-gradient-osu flex items-center justify-center">
          <Bot className="w-6 h-6 text-white" />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 flex flex-col gap-2">
        {navItems.map((item, index) => (
          <Link key={item.href} href={item.href}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="w-12 h-12 rounded-xl flex items-center justify-center text-white/50 hover:text-osu-pink hover:bg-white/5 transition-all cursor-pointer group relative"
            >
              <item.icon className="w-5 h-5" />
              {/* Tooltip */}
              <span className="absolute left-16 px-3 py-1 bg-osu-gray rounded-lg text-sm text-white opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                {item.label}
              </span>
            </motion.div>
          </Link>
        ))}
      </nav>
    </motion.aside>
  );
}
