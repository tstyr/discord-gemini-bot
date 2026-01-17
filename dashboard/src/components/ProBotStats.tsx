"use client";

import { motion } from 'framer-motion';
import { Users, Server, MessageSquare, Music } from 'lucide-react';
import CircularProgress from './CircularProgress';

interface ProBotStatsProps {
  servers: number;
  maxServers: number;
  users: number;
  maxUsers: number;
  messages: number;
  music: number;
}

export default function ProBotStats({ 
  servers, 
  maxServers, 
  users, 
  maxUsers,
  messages,
  music 
}: ProBotStatsProps) {
  return (
    <div className="bg-gradient-to-br from-gray-900 via-black to-gray-900 rounded-2xl p-8 border border-gray-800 shadow-2xl">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 text-center"
      >
        <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
          Bot Statistics
        </h2>
        <p className="text-gray-400 text-sm">リアルタイム統計ダッシュボード</p>
      </motion.div>

      {/* Circular Progress Bars */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
        <CircularProgress
          value={servers}
          max={maxServers}
          label="サーバー数"
          color="cyan"
          icon={<Server className="w-6 h-6" />}
        />
        <CircularProgress
          value={users}
          max={maxUsers}
          label="ユーザー数"
          color="magenta"
          icon={<Users className="w-6 h-6" />}
        />
        <CircularProgress
          value={messages}
          max={10000}
          label="メッセージ"
          color="green"
          icon={<MessageSquare className="w-6 h-6" />}
        />
        <CircularProgress
          value={music}
          max={1000}
          label="音楽再生"
          color="yellow"
          icon={<Music className="w-6 h-6" />}
        />
      </div>

      {/* Additional Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'アップタイム', value: '99.9%', color: 'text-green-400' },
          { label: 'レスポンス', value: '<50ms', color: 'text-cyan-400' },
          { label: 'コマンド', value: '19', color: 'text-purple-400' },
          { label: 'API呼び出し', value: '1.2k', color: 'text-pink-400' }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 + 1 }}
            className="bg-gray-900/50 rounded-xl p-4 border border-gray-800 hover:border-gray-700 transition"
          >
            <p className="text-gray-400 text-xs mb-1">{stat.label}</p>
            <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Neon Glow Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-pink-500/10 rounded-2xl blur-3xl -z-10" />
    </div>
  );
}
