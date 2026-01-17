"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, SkipForward, SkipBack, Volume2, VolumeX } from 'lucide-react';

interface Track {
  title: string;
  author: string;
  artwork: string | null;
  length: number;
  position: number;
  paused: boolean;
  volume: number;
}

interface SpotifyPlayerProps {
  track: Track | null;
  onControl: (action: string) => void;
}

export default function SpotifyPlayer({ track, onControl }: SpotifyPlayerProps) {
  const [currentPosition, setCurrentPosition] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    if (track && !track.paused && !isDragging) {
      setCurrentPosition(track.position);
      
      const interval = setInterval(() => {
        setCurrentPosition(prev => {
          const next = prev + 1000;
          return next <= track.length ? next : track.length;
        });
      }, 1000);

      return () => clearInterval(interval);
    } else if (track) {
      setCurrentPosition(track.position);
    }
  }, [track, isDragging]);

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPosition = parseInt(e.target.value);
    setCurrentPosition(newPosition);
  };

  const handleProgressMouseDown = () => {
    setIsDragging(true);
  };

  const handleProgressMouseUp = () => {
    setIsDragging(false);
    // TODO: Seek to position
  };

  if (!track) {
    return (
      <div className="bg-gradient-to-b from-gray-900 to-black rounded-2xl p-6 shadow-2xl">
        <div className="flex items-center justify-center h-32">
          <p className="text-gray-500">再生中の曲はありません</p>
        </div>
      </div>
    );
  }

  const progress = (currentPosition / track.length) * 100;

  return (
    <div className="bg-gradient-to-b from-gray-900 to-black rounded-2xl p-6 shadow-2xl border border-gray-800">
      <div className="flex items-center gap-6 mb-4">
        {/* Left: Album Art */}
        <motion.div
          animate={{
            y: track.paused ? 0 : [-2, 2, -2],
            boxShadow: track.paused 
              ? "0 10px 30px rgba(0, 0, 0, 0.3)"
              : "0 20px 40px rgba(94, 234, 212, 0.3)"
          }}
          transition={{
            y: {
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            },
            boxShadow: {
              duration: 0.3
            }
          }}
          className="flex-shrink-0"
        >
          {track.artwork ? (
            <img 
              src={track.artwork} 
              alt={track.title}
              className="w-24 h-24 rounded-lg object-cover"
            />
          ) : (
            <div className="w-24 h-24 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
              <Play className="w-12 h-12 text-white" />
            </div>
          )}
        </motion.div>

        {/* Center: Track Info & Controls */}
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-bold text-lg truncate mb-1">
            {track.title}
          </h3>
          <p className="text-gray-400 text-sm truncate mb-4">
            {track.author}
          </p>

          {/* Controls */}
          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onControl('previous')}
              className="text-gray-400 hover:text-white transition"
            >
              <SkipBack className="w-6 h-6" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onControl(track.paused ? 'resume' : 'pause')}
              className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center shadow-lg hover:shadow-cyan-500/50 transition"
            >
              {track.paused ? (
                <Play className="w-6 h-6 text-white ml-1" />
              ) : (
                <Pause className="w-6 h-6 text-white" />
              )}
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onControl('skip')}
              className="text-gray-400 hover:text-white transition"
            >
              <SkipForward className="w-6 h-6" />
            </motion.button>
          </div>
        </div>

        {/* Right: Volume */}
        <div className="flex items-center gap-3">
          {track.volume === 0 ? (
            <VolumeX className="w-5 h-5 text-gray-400" />
          ) : (
            <Volume2 className="w-5 h-5 text-gray-400" />
          )}
          <div className="w-24 h-1 bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-cyan-500 to-purple-600"
              style={{ width: `${track.volume}%` }}
            />
          </div>
          <span className="text-gray-400 text-sm w-10 text-right">
            {track.volume}%
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <span className="text-gray-400 text-xs w-12 text-right">
            {formatTime(currentPosition)}
          </span>
          <div className="flex-1 relative group">
            <input
              type="range"
              min="0"
              max={track.length}
              value={currentPosition}
              onChange={handleProgressChange}
              onMouseDown={handleProgressMouseDown}
              onMouseUp={handleProgressMouseUp}
              onTouchStart={handleProgressMouseDown}
              onTouchEnd={handleProgressMouseUp}
              className="w-full h-1 bg-gray-700 rounded-full appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-3
                [&::-webkit-slider-thumb]:h-3
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-white
                [&::-webkit-slider-thumb]:cursor-pointer
                [&::-webkit-slider-thumb]:opacity-0
                [&::-webkit-slider-thumb]:transition-opacity
                group-hover:[&::-webkit-slider-thumb]:opacity-100
                [&::-moz-range-thumb]:w-3
                [&::-moz-range-thumb]:h-3
                [&::-moz-range-thumb]:rounded-full
                [&::-moz-range-thumb]:bg-white
                [&::-moz-range-thumb]:border-0
                [&::-moz-range-thumb]:cursor-pointer
                [&::-moz-range-thumb]:opacity-0
                [&::-moz-range-thumb]:transition-opacity
                group-hover:[&::-moz-range-thumb]:opacity-100"
              style={{
                background: `linear-gradient(to right, 
                  rgb(6, 182, 212) 0%, 
                  rgb(168, 85, 247) ${progress}%, 
                  rgb(55, 65, 81) ${progress}%, 
                  rgb(55, 65, 81) 100%)`
              }}
            />
          </div>
          <span className="text-gray-400 text-xs w-12">
            {formatTime(track.length)}
          </span>
        </div>
      </div>
    </div>
  );
}
