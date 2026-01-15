"use client";

import { motion } from "framer-motion";
import { Sparkles, Code, Lightbulb, MessageCircle } from "lucide-react";
import { useState } from "react";

const modes = [
  { id: "standard", name: "Standard", icon: MessageCircle, color: "from-blue-500 to-blue-700" },
  { id: "assistant", name: "Assistant", icon: Lightbulb, color: "from-green-500 to-green-700" },
  { id: "creative", name: "Creative", icon: Sparkles, color: "from-purple-500 to-purple-700" },
  { id: "code_expert", name: "Code Expert", icon: Code, color: "from-orange-500 to-orange-700" },
];

export default function ModeSelector() {
  const [selected, setSelected] = useState("standard");

  return (
    <div className="bg-dark-200 rounded-2xl p-6 border border-dark-100">
      <h2 className="text-xl font-semibold mb-4 text-white">AI Mode</h2>
      <div className="grid grid-cols-2 gap-3">
        {modes.map((mode) => (
          <motion.button
            key={mode.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setSelected(mode.id)}
            className={`p-4 rounded-xl border-2 transition-all ${
              selected === mode.id
                ? "border-primary-500 bg-primary-500/10"
                : "border-dark-100 hover:border-dark-100/50"
            }`}
          >
            <div
              className={`w-10 h-10 rounded-lg bg-gradient-to-br ${mode.color} flex items-center justify-center mb-2`}
            >
              <mode.icon className="w-5 h-5 text-white" />
            </div>
            <span className="text-sm font-medium text-white">{mode.name}</span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
