"use client";

import { motion } from "framer-motion";
import { Activity, Zap, MessageSquare, Hash, Sparkles } from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { Card, CardTitle, StatValue } from "@/components/Card";
import { TokenChart } from "@/components/TokenChart";
import { StatusBadge } from "@/components/StatusBadge";

// Mock data
const mockChannels = [
  { id: 1, name: "general", messages: 234 },
  { id: 2, name: "ai-chat", messages: 1892 },
  { id: 3, name: "support", messages: 456 },
];

export default function DashboardPage() {
  return (
    <div className="min-h-screen">
      {/* Background orbs */}
      <div className="osu-orb osu-orb-pink w-96 h-96 -top-48 -right-48" />
      <div className="osu-orb osu-orb-purple w-64 h-64 bottom-20 -left-32" />
      <div className="osu-orb osu-orb-cyan w-48 h-48 top-1/2 right-1/4" />

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
              <div className="w-16 h-16 rounded-2xl bg-gradient-cyan flex items-center justify-center">
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

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card delay={0.2}>
            <CardTitle icon={<Zap className="w-5 h-5" />}>トークン使用量</CardTitle>
            <StatValue value="12,450" label="今月の合計" />
          </Card>

          <Card delay={0.3} accent="cyan">
            <CardTitle icon={<MessageSquare className="w-5 h-5" />}>メッセージ数</CardTitle>
            <StatValue value="1,234" label="今月の合計" />
          </Card>

          <Card delay={0.4} accent="purple">
            <CardTitle icon={<Hash className="w-5 h-5" />}>アクティブチャンネル</CardTitle>
            <StatValue value="3" label="設定済み" />
          </Card>
        </div>

        {/* Charts and Channels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card delay={0.5} className="col-span-1">
            <CardTitle icon={<Zap className="w-5 h-5" />}>トークン使用推移</CardTitle>
            <TokenChart />
          </Card>

          <Card delay={0.6} accent="purple" className="col-span-1">
            <CardTitle icon={<Hash className="w-5 h-5" />}>チャットチャンネル</CardTitle>
            <div className="space-y-3">
              {mockChannels.map((channel, index) => (
                <motion.div
                  key={channel.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 + index * 0.1 }}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Hash className="w-4 h-4 text-osu-purple" />
                    <span className="text-white/80">{channel.name}</span>
                  </div>
                  <span className="text-sm text-white/50">{channel.messages} messages</span>
                </motion.div>
              ))}
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
