'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ResourceMonitor } from '@/components/ResourceMonitor';
import { Activity, Zap, TrendingDown } from 'lucide-react';

export default function ResourcesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      {/* Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-4 mb-4">
            <div className="p-3 bg-gradient-to-r from-pink-500/20 to-cyan-500/20 rounded-xl border border-pink-500/30">
              <Activity className="w-8 h-8 text-pink-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">
                リソースモニター
              </h1>
              <p className="text-gray-400 mt-1">
                API使用量とコスト最適化の監視
              </p>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700/50"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">無料枠利用</p>
                  <p className="text-2xl font-bold text-green-400">100%</p>
                </div>
                <Zap className="w-8 h-8 text-green-400" />
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700/50"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">コスト削減</p>
                  <p className="text-2xl font-bold text-cyan-400">$0.00</p>
                </div>
                <TrendingDown className="w-8 h-8 text-cyan-400" />
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700/50"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">最適化率</p>
                  <p className="text-2xl font-bold text-purple-400">85%</p>
                </div>
                <Activity className="w-8 h-8 text-purple-400" />
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Resource Monitor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <ResourceMonitor />
        </motion.div>
      </div>
    </div>
  );
}