"use client";

import { motion } from "framer-motion";
import { Play, Pause, SkipBack, SkipForward, Volume2, Music } from "lucide-react";
import { useState, useEffect } from "react";

export function MusicPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [volume, setVolume] = useState(70);

  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setProgress((prev) => (prev >= 100 ? 0 : prev + 0.5));
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isPlaying]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const currentTime = (progress / 100) * 180;
  const totalTime = 180;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.3 }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-osu-purple/20 to-osu-pink/20 backdrop-blur-sm border border-white/10 p-6"
    >
      {/* Glow effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-osu-purple/10 to-osu-pink/10 blur-xl" />
      
      <div className="relative z-10 flex items-center gap-6">
        {/* Album Art */}
        <motion.div
          animate={{ rotate: isPlaying ? 360 : 0 }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          className="w-24 h-24 rounded-xl bg-gradient-to-br from-osu-pink to-osu-purple flex items-center justify-center shadow-lg"
        >
          <Music className="w-12 h-12 text-white" />
        </motion.div>

        {/* Player Controls */}
        <div className="flex-1">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white">Now Playing</h3>
            <p className="text-sm text-white/60">AI Bot Background Music</p>
          </div>

          {/* Progress Bar */}
          <div className="mb-3">
            <div className="relative h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-osu-pink to-osu-purple"
                style={{ width: `${progress}%` }}
                transition={{ duration: 0.1 }}
              />
            </div>
            <div className="flex justify-between text-xs text-white/50 mt-1">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(totalTime)}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors">
                <SkipBack className="w-4 h-4 text-white" />
              </button>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="w-10 h-10 rounded-full bg-gradient-to-r from-osu-pink to-osu-purple hover:shadow-lg hover:shadow-osu-pink/50 flex items-center justify-center transition-all"
              >
                {isPlaying ? (
                  <Pause className="w-5 h-5 text-white" />
                ) : (
                  <Play className="w-5 h-5 text-white ml-0.5" />
                )}
              </button>
              <button className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors">
                <SkipForward className="w-4 h-4 text-white" />
              </button>
            </div>

            {/* Volume */}
            <div className="flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-white/60" />
              <input
                type="range"
                min="0"
                max="100"
                value={volume}
                onChange={(e) => setVolume(Number(e.target.value))}
                className="w-20 h-1 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-osu-cyan"
              />
              <span className="text-xs text-white/50 w-8">{volume}%</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
