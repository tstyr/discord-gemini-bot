"use client";

import { motion } from "framer-motion";
import { Hash, Trash2 } from "lucide-react";

const mockChannels = [
  { id: 1, name: "general-chat", guild: "My Server" },
  { id: 2, name: "ai-playground", guild: "My Server" },
  { id: 3, name: "bot-testing", guild: "Dev Server" },
];

export default function ChannelList() {
  return (
    <div className="space-y-2">
      {mockChannels.map((channel, i) => (
        <motion.div
          key={channel.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 * i }}
          className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors group"
        >
          <div className="flex items-center gap-3">
            <Hash size={18} className="text-accent-cyan" />
            <div>
              <p className="font-medium">{channel.name}</p>
              <p className="text-xs text-white/40">{channel.guild}</p>
            </div>
          </div>
          <button className="opacity-0 group-hover:opacity-100 transition-opacity text-white/40 hover:text-red-400">
            <Trash2 size={16} />
          </button>
        </motion.div>
      ))}
    </div>
  );
}
