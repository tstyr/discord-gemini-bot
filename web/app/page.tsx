"use client";

import { motion } from "framer-motion";
import { Bot, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Background orbs */}
      <div className="osu-orb osu-orb-pink w-96 h-96 top-1/4 -left-48" />
      <div className="osu-orb osu-orb-purple w-80 h-80 bottom-1/4 -right-40" />
      <div className="osu-orb osu-orb-cyan w-64 h-64 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="text-center z-10"
      >
        <motion.div
          initial={{ y: -20 }}
          animate={{ y: 0 }}
          transition={{ delay: 0.2 }}
          className="w-24 h-24 mx-auto mb-8 rounded-3xl bg-gradient-osu flex items-center justify-center shadow-lg shadow-osu-pink/30"
        >
          <Bot className="w-12 h-12 text-white" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-5xl font-bold mb-4"
        >
          <span className="bg-gradient-osu bg-clip-text text-transparent">AI Bot</span>
          <span className="text-white"> Dashboard</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-white/50 text-lg mb-8 max-w-md mx-auto"
        >
          Discord BotとGemini AIを統合した管理ダッシュボード
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Link href="/dashboard">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 rounded-2xl bg-gradient-osu text-white font-semibold flex items-center gap-2 mx-auto shadow-lg shadow-osu-pink/30 hover:shadow-osu-pink/50 transition-shadow"
            >
              ダッシュボードへ
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          </Link>
        </motion.div>
      </motion.div>
    </div>
  );
}
