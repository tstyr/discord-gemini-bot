"use client";

import { motion } from "framer-motion";
import { Terminal, CheckCircle, AlertCircle, Info } from "lucide-react";
import { useEffect, useState } from "react";

interface LogEntry {
  id: number;
  type: "success" | "error" | "info";
  message: string;
  timestamp: string;
}

export function BotLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([
    { id: 1, type: "success", message: "Bot connected to Discord", timestamp: "14:32:01" },
    { id: 2, type: "info", message: "Loaded 12 commands", timestamp: "14:32:02" },
    { id: 3, type: "success", message: "Database connection established", timestamp: "14:32:03" },
    { id: 4, type: "info", message: "AI handler initialized", timestamp: "14:32:04" },
    { id: 5, type: "success", message: "Music system ready", timestamp: "14:32:05" },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      const messages = [
        { type: "info" as const, message: "Processing user command..." },
        { type: "success" as const, message: "Message sent successfully" },
        { type: "info" as const, message: "Token usage: 150 tokens" },
        { type: "success" as const, message: "AI response generated" },
      ];
      const randomMsg = messages[Math.floor(Math.random() * messages.length)];
      const now = new Date();
      const timestamp = `${now.getHours()}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
      
      setLogs((prev) => [
        ...prev.slice(-4),
        { id: Date.now(), ...randomMsg, timestamp },
      ]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getIcon = (type: string) => {
    switch (type) {
      case "success":
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="relative overflow-hidden rounded-2xl bg-osu-darker/80 backdrop-blur-sm border border-white/10 p-6"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Terminal className="w-5 h-5 text-osu-cyan" />
        <h3 className="text-lg font-semibold text-white">Bot Logs</h3>
        <div className="ml-auto">
          <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-medium">
            Live
          </span>
        </div>
      </div>

      {/* Log entries */}
      <div className="space-y-2 font-mono text-sm max-h-48 overflow-y-auto">
        {logs.map((log, index) => (
          <motion.div
            key={log.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="flex items-start gap-3 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
          >
            {getIcon(log.type)}
            <span className="text-white/40 text-xs">{log.timestamp}</span>
            <span className="text-white/80 flex-1">{log.message}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
