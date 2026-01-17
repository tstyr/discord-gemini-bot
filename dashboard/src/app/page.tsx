"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bot, MessageSquare, Activity, Music, 
  Users, Wifi, WifiOff, Play, Pause, SkipForward, 
  Square, Volume2, RefreshCw, Zap, ArrowLeft, Send
} from "lucide-react";

interface Guild {
  id: number;
  name: string;
  member_count: number;
  icon: string | null;
}

interface MusicStatus {
  playing: boolean;
  connected: boolean;
  paused: boolean;
  volume: number;
  current_track: {
    title: string;
    author: string;
    length: number;
    position: number;
    artwork: string | null;
    uri: string;
  } | null;
  queue: Array<{ title: string; author: string; length: number }>;
  loop_mode: string;
}

interface Stats {
  guilds: number;
  messages: number;
  uptime: string;
  apiUsage: number;
  apiLimit: number;
  totalTokens: number;
}

interface ChatLog {
  id: string;
  user_id: string;
  message: string;
  response: string;
  username: string;
  channel_name: string;
  tokens_used: number;
  timestamp: string;
}

interface ChatUser {
  user_id: string;
  username: string;
  avatar: string | null;
  message_count: number;
  total_tokens: number;
  last_message: string;
}

interface UserChatMessage {
  id: string;
  message: string;
  response: string;
  tokens_used: number;
  timestamp: string;
  channel_name: string;
  guild_name: string;
}

interface MusicHistory {
  id: string;
  track_title: string;
  track_author: string;
  track_artwork: string | null;
  requester: string;
  played_at: string;
  guild_name: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001/ws";

export default function Dashboard() {
  const [connected, setConnected] = useState(false);
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [selectedGuild, setSelectedGuild] = useState<Guild | null>(null);
  const [musicStatus, setMusicStatus] = useState<MusicStatus | null>(null);
  const [stats, setStats] = useState<Stats>({ guilds: 0, messages: 0, uptime: "0%", apiUsage: 0, apiLimit: 1500, totalTokens: 0 });
  const [chatLogs, setChatLogs] = useState<ChatLog[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [networkStats, setNetworkStats] = useState({ latency: 0 });
  const [loading, setLoading] = useState(true);
  
  // ユーザーチャット関連
  const [chatUsers, setChatUsers] = useState<ChatUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<ChatUser | null>(null);
  const [userMessages, setUserMessages] = useState<UserChatMessage[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 音楽履歴
  const [musicHistory, setMusicHistory] = useState<MusicHistory[]>([]);
  
  // リアルタイムログ
  const [realtimeLogs, setRealtimeLogs] = useState<string[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // WebSocket接続
  useEffect(() => {
    const connectWebSocket = () => {
      const websocket = new WebSocket(WS_URL);
      websocket.onopen = () => { setConnected(true); };
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (e) {}
      };
      websocket.onclose = () => {
        setConnected(false);
        setTimeout(connectWebSocket, 3000);
      };
      setWs(websocket);
    };
    connectWebSocket();
    return () => { ws?.close(); };
  }, []);

  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.type) {
      case "network_stats":
        setNetworkStats({ latency: Math.round(data.data.latency) });
        break;
      case "music_event":
        const eventData = data.data;
        if (eventData.type === "track_start") {
          setMusicStatus(prev => ({ 
            ...prev!, 
            playing: true, 
            connected: true, 
            current_track: eventData.track 
          }));
          
          // 音楽履歴に追加
          const historyEntry: MusicHistory = {
            id: Date.now().toString(),
            track_title: eventData.track.title,
            track_author: eventData.track.author,
            track_artwork: eventData.track.artwork,
            requester: eventData.requester || 'Unknown',
            played_at: new Date().toISOString(),
            guild_name: 'Discord'
          };
          setMusicHistory(prev => [historyEntry, ...prev].slice(0, 50));
          
          // リアルタイムログに追加
          addLog(`🎵 再生開始: ${eventData.track.title} - ${eventData.track.author}`);
        } else if (eventData.type === "music_stopped" || eventData.type === "queue_empty_disconnect") {
          setMusicStatus({ 
            playing: false, 
            connected: false, 
            paused: false, 
            volume: 1, 
            current_track: null, 
            queue: [], 
            loop_mode: "off" 
          });
          addLog(`⏹️ 音楽停止`);
        }
        break;
      case "new_message":
        setChatLogs(prev => [data.data, ...prev].slice(0, 50));
        addLog(`💬 ${data.data.username}: ${data.data.user_message.substring(0, 30)}...`);
        // ユーザーリストも更新
        fetchChatUsers();
        break;
    }
  }, []);
  
  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString('ja-JP');
    setRealtimeLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 100));
  };

  useEffect(() => { fetchInitialData(); }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [guildsRes, statsRes, costRes, logsRes, healthRes, usersRes] = await Promise.all([
        fetch(`${API_URL}/api/guilds`),
        fetch(`${API_URL}/api/stats`),
        fetch(`${API_URL}/api/cost/usage`),
        fetch(`${API_URL}/api/chat-logs?limit=20`),
        fetch(`${API_URL}/api/health`),
        fetch(`${API_URL}/api/users`)
      ]);

      if (guildsRes.ok) {
        const data = await guildsRes.json();
        setGuilds(data.data || []);
        if (data.data?.length > 0) setSelectedGuild(data.data[0]);
      }
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(prev => ({ ...prev, messages: data.data?.total_messages || 0, totalTokens: data.data?.total_tokens || 0 }));
      }
      if (costRes.ok) {
        const data = await costRes.json();
        setStats(prev => ({ ...prev, apiUsage: data.data?.requests_today || 0, apiLimit: data.data?.daily_limit || 1500 }));
      }
      if (logsRes.ok) {
        const data = await logsRes.json();
        setChatLogs(data.data || []);
      }
      if (healthRes.ok) {
        const data = await healthRes.json();
        setStats(prev => ({ ...prev, guilds: data.guilds || 0, uptime: data.bot_ready ? "Online" : "Offline" }));
      }
      if (usersRes.ok) {
        const data = await usersRes.json();
        setChatUsers(data.data || []);
      }
    } catch (error) {
      console.error("Failed to fetch initial data:", error);
    }
    setLoading(false);
  };

  const fetchChatUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/api/users`);
      if (res.ok) {
        const data = await res.json();
        setChatUsers(data.data || []);
      }
    } catch (e) {}
  };

  const fetchUserMessages = async (userId: string) => {
    setLoadingMessages(true);
    try {
      const res = await fetch(`${API_URL}/api/users/${userId}/chat-history?limit=100`);
      if (res.ok) {
        const data = await res.json();
        setUserMessages(data.data?.messages || []);
      }
    } catch (e) {}
    setLoadingMessages(false);
  };

  const selectUser = (user: ChatUser) => {
    setSelectedUser(user);
    fetchUserMessages(user.user_id);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [userMessages]);
  
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [realtimeLogs]);

  useEffect(() => {
    if (selectedGuild) {
      fetch(`${API_URL}/api/guilds/${selectedGuild.id}/music/status`)
        .then(res => res.ok ? res.json() : null)
        .then(data => data && setMusicStatus(data.data));
    }
  }, [selectedGuild]);

  const controlMusic = async (action: string) => {
    if (!selectedGuild) return;
    await fetch(`${API_URL}/api/guilds/${selectedGuild.id}/music/control?action=${action}`, { method: "POST" });
  };

  const formatDuration = (ms: number) => {
    const mins = Math.floor(ms / 60000);
    const secs = Math.floor((ms % 60000) / 1000);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const formatTime = (timestamp: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString("ja-JP", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-discord-darker flex items-center justify-center">
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}>
          <RefreshCw className="w-8 h-8 text-discord-blurple" />
        </motion.div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-discord-darker flex">
      {/* 左サイドバー - ユーザーアイコン一覧 */}
      <aside className="w-20 bg-discord-dark flex flex-col items-center py-4 gap-2 border-r border-gray-800">
        <div className="w-12 h-12 bg-discord-blurple rounded-full flex items-center justify-center mb-4">
          <Bot className="w-7 h-7 text-white" />
        </div>
        <div className="w-8 h-0.5 bg-gray-700 rounded mb-2" />
        
        {/* ユーザーアイコン一覧 */}
        <div className="flex-1 overflow-y-auto space-y-2 w-full px-2">
          {chatUsers.map((user) => (
            <motion.button
              key={user.user_id}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => selectUser(user)}
              className={`w-12 h-12 mx-auto rounded-full overflow-hidden transition-all ${
                selectedUser?.user_id === user.user_id 
                  ? "ring-2 ring-discord-blurple ring-offset-2 ring-offset-discord-dark" 
                  : "hover:rounded-2xl"
              }`}
              title={user.username}
            >
              {user.avatar ? (
                <img src={user.avatar} alt={user.username} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-discord-blurple flex items-center justify-center text-white font-bold">
                  {user.username?.charAt(0).toUpperCase() || '?'}
                </div>
              )}
            </motion.button>
          ))}
        </div>
        
        {/* 接続状態 */}
        <div className={`w-3 h-3 rounded-full ${connected ? "bg-discord-green" : "bg-discord-red"}`} title={connected ? "接続中" : "切断"} />
      </aside>

      {/* メインコンテンツ */}
      <div className="flex-1 flex">
        {/* 中央 - チャットエリア */}
        <div className="flex-1 flex flex-col">
          {selectedUser ? (
            <>
              {/* チャットヘッダー */}
              <header className="h-14 bg-discord-dark border-b border-gray-800 flex items-center px-4 gap-3">
                <button 
                  onClick={() => setSelectedUser(null)} 
                  className="p-2 hover:bg-gray-700 rounded transition"
                  title="ダッシュボードに戻る"
                >
                  <ArrowLeft className="w-5 h-5 text-gray-400" />
                </button>
                {selectedUser.avatar ? (
                  <img src={selectedUser.avatar} alt="" className="w-8 h-8 rounded-full" />
                ) : (
                  <div className="w-8 h-8 bg-discord-blurple rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {selectedUser.username?.charAt(0).toUpperCase()}
                  </div>
                )}
                <div className="flex-1">
                  <h2 className="text-white font-semibold">{selectedUser.username}</h2>
                  <p className="text-gray-400 text-xs">{selectedUser.message_count}件のメッセージ • {selectedUser.total_tokens?.toLocaleString()} tokens</p>
                </div>
              </header>

              {/* メッセージエリア */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {loadingMessages ? (
                  <div className="flex justify-center py-8">
                    <RefreshCw className="w-6 h-6 text-gray-500 animate-spin" />
                  </div>
                ) : (
                  <AnimatePresence>
                    {userMessages.map((msg, i) => (
                      <motion.div
                        key={msg.id || i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-3"
                      >
                        {/* ユーザーメッセージ */}
                        <div className="flex items-start gap-3">
                          {selectedUser.avatar ? (
                            <img src={selectedUser.avatar} alt="" className="w-10 h-10 rounded-full flex-shrink-0" />
                          ) : (
                            <div className="w-10 h-10 bg-discord-blurple rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                              {selectedUser.username?.charAt(0).toUpperCase()}
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-baseline gap-2">
                              <span className="text-white font-medium">{selectedUser.username}</span>
                              <span className="text-gray-500 text-xs">{formatTime(msg.timestamp)}</span>
                            </div>
                            <p className="text-gray-300 mt-1 break-words">{msg.message}</p>
                          </div>
                        </div>

                        {/* Botレスポンス */}
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 bg-discord-green rounded-full flex items-center justify-center flex-shrink-0">
                            <Bot className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-baseline gap-2">
                              <span className="text-discord-green font-medium">AI Bot</span>
                              <span className="text-gray-500 text-xs">{msg.tokens_used?.toFixed(0)} tokens</span>
                            </div>
                            <p className="text-gray-300 mt-1 break-words whitespace-pre-wrap">{msg.response}</p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* 入力エリア（表示のみ） */}
              <div className="p-4 border-t border-gray-800">
                <div className="bg-discord-dark rounded-lg px-4 py-3 flex items-center gap-2 text-gray-500">
                  <Send className="w-5 h-5" />
                  <span className="text-sm">閲覧専用モード</span>
                </div>
              </div>
            </>
          ) : (
            /* ダッシュボード表示 */
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="max-w-4xl mx-auto space-y-6">
                {/* ヘッダー */}
                <header className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Bot className="w-10 h-10 text-discord-blurple" />
                    <div>
                      <h1 className="text-2xl font-bold text-white">AI Bot Dashboard</h1>
                      <p className="text-gray-400 text-sm">左のアイコンをクリックして会話を表示</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {connected ? <Wifi className="w-4 h-4 text-discord-green" /> : <WifiOff className="w-4 h-4 text-discord-red" />}
                    <span className="text-gray-400 text-sm">{networkStats.latency}ms</span>
                  </div>
                </header>

                {/* 統計カード */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {[
                    { label: "サーバー", value: stats.guilds, icon: Users, color: "text-discord-blurple" },
                    { label: "メッセージ", value: stats.messages, icon: MessageSquare, color: "text-discord-green" },
                    { label: "トークン", value: stats.totalTokens.toLocaleString(), icon: Zap, color: "text-discord-yellow" },
                    { label: "API", value: `${stats.apiUsage}/${stats.apiLimit}`, icon: Activity, color: "text-discord-fuchsia" },
                    { label: "状態", value: stats.uptime, icon: Wifi, color: "text-discord-green" },
                  ].map((stat, i) => (
                    <div key={stat.label} className="bg-discord-dark p-3 rounded-xl">
                      <div className="flex items-center gap-2 mb-1">
                        <stat.icon className={`w-4 h-4 ${stat.color}`} />
                        <span className="text-gray-400 text-xs">{stat.label}</span>
                      </div>
                      <p className="text-xl font-bold text-white">{stat.value}</p>
                    </div>
                  ))}
                </div>

                {/* 音楽プレイヤー */}
                <section className="bg-discord-dark p-4 rounded-xl">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Music className="w-5 h-5 text-discord-fuchsia" />
                    音楽プレイヤー
                  </h2>
                  {musicStatus?.connected && musicStatus.current_track ? (
                    <div className="space-y-4">
                      <div className="flex items-center gap-4">
                        {musicStatus.current_track.artwork && (
                          <img src={musicStatus.current_track.artwork} alt="" className="w-16 h-16 rounded-lg" />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-medium truncate">{musicStatus.current_track.title}</p>
                          <p className="text-gray-400 text-sm">{musicStatus.current_track.author}</p>
                          <p className="text-gray-500 text-xs">{formatDuration(musicStatus.current_track.position || 0)} / {formatDuration(musicStatus.current_track.length)}</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-center gap-4">
                        <button onClick={() => controlMusic(musicStatus.paused ? "resume" : "pause")} className="p-3 bg-discord-blurple rounded-full">
                          {musicStatus.paused ? <Play className="w-6 h-6 text-white" /> : <Pause className="w-6 h-6 text-white" />}
                        </button>
                        <button onClick={() => controlMusic("skip")} className="p-2 bg-discord-darker rounded-full"><SkipForward className="w-5 h-5 text-white" /></button>
                        <button onClick={() => controlMusic("stop")} className="p-2 bg-discord-darker rounded-full"><Square className="w-5 h-5 text-white" /></button>
                        <div className="flex items-center gap-2 ml-4">
                          <Volume2 className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-400 text-sm">{Math.round((musicStatus.volume || 1) * 100)}%</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-6">
                      <Music className="w-10 h-10 text-gray-600 mx-auto mb-2" />
                      <p className="text-gray-500">再生中の曲はありません</p>
                    </div>
                  )}
                </section>

                {/* 最近のチャット */}
                <section className="bg-discord-dark p-4 rounded-xl">
                  <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-discord-green" />
                    最近のチャット
                  </h2>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {chatLogs.slice(0, 10).map((log, i) => (
                      <div key={log.id || i} className="bg-discord-darker p-3 rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-discord-blurple text-xs font-medium">{log.username}</span>
                          <span className="text-gray-600 text-xs">{formatTime(log.timestamp)}</span>
                        </div>
                        <p className="text-gray-300 text-sm truncate">{log.message}</p>
                        <p className="text-gray-500 text-xs mt-1 truncate">→ {log.response}</p>
                      </div>
                    ))}
                    {chatLogs.length === 0 && <p className="text-gray-500 text-center py-4">チャットログがありません</p>}
                  </div>
                </section>

                {/* 音楽履歴 */}
                <section className="bg-discord-dark p-4 rounded-xl">
                  <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Music className="w-5 h-5 text-discord-fuchsia" />
                    音楽履歴
                  </h2>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {musicHistory.length > 0 ? (
                      musicHistory.map((track, i) => (
                        <div key={track.id || i} className="bg-discord-darker p-3 rounded-lg flex items-center gap-3">
                          {track.track_artwork ? (
                            <img src={track.track_artwork} alt="" className="w-12 h-12 rounded object-cover flex-shrink-0" />
                          ) : (
                            <div className="w-12 h-12 bg-gray-700 rounded flex items-center justify-center flex-shrink-0">
                              <Music className="w-6 h-6 text-gray-500" />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-white text-sm font-medium truncate">{track.track_title}</p>
                            <p className="text-gray-400 text-xs truncate">{track.track_author}</p>
                            <p className="text-gray-600 text-xs">{track.requester} • {formatTime(track.played_at)}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 text-center py-4">音楽履歴がありません</p>
                    )}
                  </div>
                </section>

                {/* リアルタイムログ */}
                <section className="bg-discord-dark p-4 rounded-xl">
                  <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-discord-green" />
                    リアルタイムログ
                  </h2>
                  <div className="bg-discord-darker rounded-lg p-3 font-mono text-xs max-h-64 overflow-y-auto">
                    {realtimeLogs.length > 0 ? (
                      <>
                        {realtimeLogs.map((log, i) => (
                          <div key={i} className="text-gray-300 py-0.5">
                            {log}
                          </div>
                        ))}
                        <div ref={logsEndRef} />
                      </>
                    ) : (
                      <p className="text-gray-500 text-center py-4">ログがありません</p>
                    )}
                  </div>
                </section>
              </div>
            </div>
          )}
        </div>

        {/* 右サイドバー - ユーザーリスト */}
        <aside className="w-60 bg-discord-dark border-l border-gray-800 hidden lg:block">
          <div className="p-4">
            <h3 className="text-gray-400 text-xs font-semibold uppercase mb-3">ユーザー — {chatUsers.length}</h3>
            <div className="space-y-1">
              {chatUsers.map((user) => (
                <button
                  key={user.user_id}
                  onClick={() => selectUser(user)}
                  className={`w-full flex items-center gap-3 p-2 rounded-lg transition ${
                    selectedUser?.user_id === user.user_id ? "bg-discord-blurple/20" : "hover:bg-gray-800"
                  }`}
                >
                  {user.avatar ? (
                    <img src={user.avatar} alt="" className="w-8 h-8 rounded-full" />
                  ) : (
                    <div className="w-8 h-8 bg-discord-blurple rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {user.username?.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div className="flex-1 min-w-0 text-left">
                    <p className="text-white text-sm truncate">{user.username}</p>
                    <p className="text-gray-500 text-xs">{user.message_count}件</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}
