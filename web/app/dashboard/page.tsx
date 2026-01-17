"use client";

import { motion } from "framer-motion";
import { Activity, Sparkles, Users, MessageSquare } from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { Card } from "@/components/Card";
import { StatusBadge } from "@/components/StatusBadge";
import { CircularChart } from "@/components/CircularChart";
import { MusicPlayer } from "@/components/MusicPlayer";
import { BotLogs } from "@/components/BotLogs";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-osu-darker">
      {/* Background orbs */}
      <div className="fixed w-96 h-96 -top-48 -right-48 bg-osu-pink/20 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed w-64 h-64 bottom-20 -left-32 bg-osu-purple/20 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed w-48 h-48 top-1/2 right-1/4 bg-osu-cyan/20 rounded-full blur-3xl pointer-events-none" />

      <Sidebar />

      <main className="ml-20 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-white mb-2">ダッシュボード</h1>
          <p className="text-white/50">AI Botの稼働状況を確認</p>
        </motion.div>

        {/* Status Card */}
        <Card className="mb-6" delay={0.1} accent="cyan">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-osu-cyan to-osu-purple flex items-center justify-center shadow-lg shadow-osu-cyan/50">
                <Activity className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">Bot Status</h2>
                <StatusBadge status="online" />
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-osu-cyan/20 border border-osu-cyan/30">
              <Sparkles className="w-4 h-4 text-osu-cyan" />
              <span className="text-osu-cyan text-sm font-medium">Standard Mode</span>
            </div>
          </div>
        </Card>

        {/* Circular Charts - ProBot Style */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6"
        >
          <Card accent="pink">
            <div className="flex justify-around items-center py-4">
              <CircularChart value={1234} max={2000} label="メッセージ数" color="pink" />
              <CircularChart value={8} max={10} label="参加サーバー数" color="cyan" />
            </div>
          </Card>

          <Card accent="purple">
            <div className="flex justify-around items-center py-4">
              <CircularChart value={12450} max={20000} label="トークン使用量" color="purple" />
              <CircularChart value={156} max={200} label="アクティブユーザー" color="pink" />
            </div>
          </Card>
        </motion.div>

        {/* Spotify-Style Music Player */}
        <div className="mb-6">
          <MusicPlayer />
        </div>

        {/* Bot Logs - Terminal Style */}
        <BotLogs />
      </main>
    </div>
  );
}
