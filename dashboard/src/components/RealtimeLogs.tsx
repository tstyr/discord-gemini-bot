"use client";

import { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, X, Maximize2, Minimize2 } from 'lucide-react';
import { io, Socket } from 'socket.io-client';

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  color: string;
  module: string;
}

interface RealtimeLogsProps {
  apiUrl: string;
}

export default function RealtimeLogs({ apiUrl }: RealtimeLogsProps) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Socket.IO connection
    const socketInstance = io(apiUrl, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10
    });

    socketInstance.on('connect', () => {
      console.log('Socket.IO connected');
      setIsConnected(true);
    });

    socketInstance.on('disconnect', () => {
      console.log('Socket.IO disconnected');
      setIsConnected(false);
    });

    socketInstance.on('log_event', (data: LogEntry) => {
      setLogs(prev => {
        const newLogs = [...prev, data];
        // Keep only last 100 logs
        return newLogs.slice(-100);
      });
    });

    setSocket(socketInstance);

    return () => {
      socketInstance.disconnect();
    };
  }, [apiUrl]);

  useEffect(() => {
    // Auto-scroll to bottom
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const clearLogs = () => {
    setLogs([]);
  };

  const getLevelBadge = (level: string) => {
    const badges = {
      'DEBUG': 'bg-gray-600',
      'INFO': 'bg-cyan-600',
      'WARNING': 'bg-yellow-600',
      'ERROR': 'bg-red-600',
      'CRITICAL': 'bg-red-800'
    };
    return badges[level as keyof typeof badges] || 'bg-gray-600';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-black rounded-xl border border-gray-800 overflow-hidden ${
        isExpanded ? 'fixed inset-4 z-50' : 'relative'
      }`}
    >
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Terminal className="w-5 h-5 text-cyan-400" />
          <h3 className="text-white font-semibold">リアルタイムログ</h3>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-gray-400">
              {isConnected ? '接続中' : '切断'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={clearLogs}
            className="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 rounded transition"
          >
            クリア
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 hover:bg-gray-800 rounded transition"
          >
            {isExpanded ? (
              <Minimize2 className="w-4 h-4 text-gray-400" />
            ) : (
              <Maximize2 className="w-4 h-4 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Logs Container */}
      <div
        ref={logsContainerRef}
        className={`bg-black p-4 overflow-y-auto font-mono text-xs ${
          isExpanded ? 'h-[calc(100vh-8rem)]' : 'h-96'
        }`}
      >
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-600">ログを待機中...</p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {logs.map((log, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="mb-1 flex items-start gap-2 hover:bg-gray-900/50 px-2 py-1 rounded"
              >
                <span className="text-gray-600 flex-shrink-0">
                  {log.timestamp}
                </span>
                <span className={`px-2 py-0.5 rounded text-xs font-bold flex-shrink-0 ${getLevelBadge(log.level)}`}>
                  {log.level}
                </span>
                <span className="text-gray-500 flex-shrink-0">
                  [{log.module}]
                </span>
                <span className={log.color || 'text-gray-300'}>
                  {log.message}
                </span>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Footer */}
      <div className="bg-gray-900 border-t border-gray-800 px-4 py-2 flex items-center justify-between text-xs text-gray-500">
        <span>{logs.length} ログエントリ</span>
        <span>最大100件まで表示</span>
      </div>
    </motion.div>
  );
}
