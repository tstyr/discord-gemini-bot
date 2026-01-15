'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Zap,
  TrendingUp,
  Server,
  Database
} from 'lucide-react';
import { Card } from './Card';

interface UsageStats {
  daily_requests: number;
  daily_tokens: number;
  request_limit: number;
  token_limit: number;
  requests_remaining: number;
  tokens_remaining: number;
  usage_percentage: {
    requests: number;
    tokens: number;
  };
  is_warning_threshold: boolean;
  is_quota_exceeded: boolean;
  last_reset: string;
}

interface ResourceMonitorProps {
  className?: string;
}

export const ResourceMonitor: React.FC<ResourceMonitorProps> = ({ className = '' }) => {
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsageStats = async () => {
      try {
        const response = await fetch('/api/cost/usage');
        const data = await response.json();
        
        if (data.success) {
          setUsageStats(data.data);
          setError(null);
        } else {
          setError('Failed to fetch usage statistics');
        }
      } catch (err) {
        setError('Network error');
        console.error('Error fetching usage stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUsageStats();
    const interval = setInterval(fetchUsageStats, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-400';
    if (percentage >= 80) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getStatusIcon = (percentage: number) => {
    if (percentage >= 90) return <AlertTriangle className="w-5 h-5 text-red-400" />;
    if (percentage >= 80) return <Clock className="w-5 h-5 text-yellow-400" />;
    return <CheckCircle className="w-5 h-5 text-green-400" />;
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (loading) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500"></div>
        </div>
      </Card>
    );
  }

  if (error || !usageStats) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="flex items-center justify-center h-48 text-red-400">
          <AlertTriangle className="w-6 h-6 mr-2" />
          {error || 'No data available'}
        </div>
      </Card>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Status Overview */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white flex items-center">
            <Activity className="w-6 h-6 mr-2 text-pink-500" />
            API使用量モニター
          </h3>
          <div className="flex items-center space-x-2">
            {usageStats.is_quota_exceeded ? (
              <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm font-medium">
                制限超過
              </span>
            ) : usageStats.is_warning_threshold ? (
              <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm font-medium">
                警告レベル
              </span>
            ) : (
              <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-medium">
                正常
              </span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Request Usage */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                <Server className="w-5 h-5 mr-2 text-cyan-400" />
                <span className="text-gray-300 font-medium">リクエスト使用量</span>
              </div>
              {getStatusIcon(usageStats.usage_percentage.requests)}
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">使用済み</span>
                <span className={getStatusColor(usageStats.usage_percentage.requests)}>
                  {formatNumber(usageStats.daily_requests)} / {formatNumber(usageStats.request_limit)}
                </span>
              </div>
              
              <div className="w-full bg-gray-700 rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${usageStats.usage_percentage.requests}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className={`h-2 rounded-full ${
                    usageStats.usage_percentage.requests >= 90 
                      ? 'bg-red-500' 
                      : usageStats.usage_percentage.requests >= 80 
                      ? 'bg-yellow-500' 
                      : 'bg-green-500'
                  }`}
                />
              </div>
              
              <div className="text-right">
                <span className="text-xs text-gray-400">
                  {usageStats.usage_percentage.requests.toFixed(1)}% 使用
                </span>
              </div>
            </div>
          </motion.div>

          {/* Token Usage */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                <Database className="w-5 h-5 mr-2 text-purple-400" />
                <span className="text-gray-300 font-medium">トークン使用量</span>
              </div>
              {getStatusIcon(usageStats.usage_percentage.tokens)}
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">使用済み</span>
                <span className={getStatusColor(usageStats.usage_percentage.tokens)}>
                  {formatNumber(usageStats.daily_tokens)} / {formatNumber(usageStats.token_limit)}
                </span>
              </div>
              
              <div className="w-full bg-gray-700 rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${usageStats.usage_percentage.tokens}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className={`h-2 rounded-full ${
                    usageStats.usage_percentage.tokens >= 90 
                      ? 'bg-red-500' 
                      : usageStats.usage_percentage.tokens >= 80 
                      ? 'bg-yellow-500' 
                      : 'bg-green-500'
                  }`}
                />
              </div>
              
              <div className="text-right">
                <span className="text-xs text-gray-400">
                  {usageStats.usage_percentage.tokens.toFixed(1)}% 使用
                </span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Remaining Quota */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30">
            <div className="flex items-center justify-between">
              <span className="text-gray-400 text-sm">残りリクエスト</span>
              <span className="text-green-400 font-bold">
                {formatNumber(usageStats.requests_remaining)}
              </span>
            </div>
          </div>
          
          <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30">
            <div className="flex items-center justify-between">
              <span className="text-gray-400 text-sm">残りトークン</span>
              <span className="text-green-400 font-bold">
                {formatNumber(usageStats.tokens_remaining)}
              </span>
            </div>
          </div>
        </div>

        {/* Reset Information */}
        <div className="mt-4 text-center">
          <span className="text-xs text-gray-500">
            制限リセット: {new Date(usageStats.last_reset).toLocaleDateString('ja-JP')} 00:00 JST
          </span>
        </div>
      </Card>

      {/* Optimization Tips */}
      <Card className="p-6">
        <h4 className="text-lg font-bold text-white mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
          コスト最適化のヒント
        </h4>
        
        <div className="space-y-3">
          <div className="flex items-start space-x-3">
            <Zap className="w-4 h-4 mt-1 text-yellow-400 flex-shrink-0" />
            <div>
              <p className="text-gray-300 text-sm">
                <strong>簡単な質問:</strong> 挨拶や基本的な質問は自動応答システムが処理し、APIを使用しません
              </p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <Zap className="w-4 h-4 mt-1 text-blue-400 flex-shrink-0" />
            <div>
              <p className="text-gray-300 text-sm">
                <strong>会話の要約:</strong> 長い会話は自動的に要約され、トークン使用量を削減します
              </p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <Zap className="w-4 h-4 mt-1 text-purple-400 flex-shrink-0" />
            <div>
              <p className="text-gray-300 text-sm">
                <strong>モデル選択:</strong> 簡単なタスクはFlashモデル、複雑なタスクはProモデルを自動選択
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};