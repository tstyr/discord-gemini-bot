"""Supabase統合クライアント"""
import os
import logging
import asyncio
import psutil
import time
from datetime import datetime
from typing import Dict, Optional, Any
from discord.ext import tasks
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabaseとの統合を管理するクライアント"""
    
    def __init__(self, bot):
        self.bot = bot
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.client: Optional[Client] = None
        self.realtime_channel = None
        self.is_running = False
        self._last_net_io = None  # ✅ ネットワークI/O統計の前回値
        
    async def initialize(self):
        """Supabaseクライアントを初期化"""
        if not self.supabase_url or not self.supabase_key:
            logger.warning("⚠️  Supabase credentials not found. Remote control disabled.")
            return False
        
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized")
            
            # テーブルの存在確認
            await self._ensure_tables()
            
            # Realtime監視を開始
            await self.start_realtime_listener()
            
            # tasks.loopでヘルスモニターを開始
            self.is_running = True
            if not self.health_monitor_loop.is_running():
                self.health_monitor_loop.start()
            
            logger.info("✅ Supabase integration fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
            return False
    
    async def _ensure_tables(self):
        """必要なテーブルが存在することを確認"""
        try:
            # system_stats テーブルの確認
            result = self.client.table('system_stats').select('*').limit(1).execute()
            logger.info("✅ system_stats table exists")
        except Exception as e:
            logger.warning(f"⚠️  system_stats table check failed: {e}")
        
        try:
            # command_queue テーブルの確認
            result = self.client.table('command_queue').select('*').limit(1).execute()
            logger.info("✅ command_queue table exists")
        except Exception as e:
            logger.warning(f"⚠️  command_queue table check failed: {e}")
        
        try:
            # active_sessions テーブルの確認
            result = self.client.table('active_sessions').select('*').limit(1).execute()
            logger.info("✅ active_sessions table exists")
        except Exception as e:
            logger.warning(f"⚠️  active_sessions table check failed: {e}")
    
    @tasks.loop(seconds=10)
    async def health_monitor_loop(self):
        """10秒ごとにシステムメトリクスを送信（tasks.loop使用）"""
        try:
            await self._send_system_stats()
            await self._send_network_stats()  # ✅ ネットワーク統計を追加
        except Exception as e:
            logger.error(f"❌ Health monitor error: {e}")
    
    @health_monitor_loop.before_loop
    async def before_health_monitor(self):
        """ヘルスモニター開始前の待機"""
        await self.bot.wait_until_ready()
        logger.info("🔄 Health monitor started (10s interval)")
    
    async def _send_system_stats(self):
        """システム統計をSupabaseに送信"""
        if not self.client or not self.is_running:
            return
        
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # システム全体のメモリ使用率
            memory = psutil.virtual_memory()
            ram_usage = memory.percent  # ✅ 追加: RAM使用率（%）
            
            # メモリ使用量（プロセス）
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_rss = memory_info.rss / 1024 / 1024  # MB (✅ 名前変更)
            memory_heap = memory_info.vms / 1024 / 1024  # MB (✅ 名前変更)
            
            # Discord Gateway Ping
            ping_gateway = round(self.bot.latency * 1000)  # ms
            
            # Lavalink Ping (音楽機能がある場合)
            ping_lavalink = 0  # デフォルト値
            try:
                import wavelink
                nodes = wavelink.Pool.nodes
                if nodes:
                    node = list(nodes.values())[0]
                    ping_lavalink = round(node.latency * 1000) if node.latency else 0
            except Exception as e:
                logger.debug(f"Lavalink ping unavailable: {e}")
            
            # ✅ 正しいスキーマに合わせたデータ
            stats = {
                'cpu_usage': float(cpu_usage),
                'ram_usage': float(ram_usage),          # ✅ 追加
                'memory_rss': float(memory_rss),        # ✅ 名前変更
                'memory_heap': float(memory_heap),      # ✅ 名前変更
                'ping_gateway': float(ping_gateway),
                'ping_lavalink': float(ping_lavalink),
                'server_count': len(self.bot.guilds),   # ✅ 追加
                'guild_count': len(self.bot.guilds),    # ✅ 追加
                'uptime': int(time.time() - self.bot.start_time),  # ✅ 追加
                'status': 'online'                      # ✅ 追加
            }
            
            # INSERTでデータを追加（recorded_at, created_atは自動）
            self.client.table('system_stats').insert(stats).execute()
            
            logger.info(f"📊 System stats sent: CPU={cpu_usage:.1f}%, RAM={ram_usage:.1f}%, Status=online")
            
        except Exception as e:
            logger.error(f"❌ Failed to send system stats: {e}")
            import traceback
            traceback.print_exc()
    
    async def _send_network_stats(self):
        """ネットワーク統計をSupabaseに送信"""
        if not self.client or not self.is_running:
            return
        
        try:
            # 現在のネットワークI/O統計
            net_io = psutil.net_io_counters()
            
            # 前回の値との差分を計算（初回は0）
            if self._last_net_io is None:
                self._last_net_io = net_io
                logger.debug("📊 Network stats initialized")
                return
            
            bytes_sent = net_io.bytes_sent - self._last_net_io.bytes_sent
            bytes_recv = net_io.bytes_recv - self._last_net_io.bytes_recv
            bytes_total = bytes_sent + bytes_recv
            
            # MBに変換
            mb_sent = bytes_sent / 1024 / 1024
            mb_recv = bytes_recv / 1024 / 1024
            mb_total = bytes_total / 1024 / 1024
            
            stats = {
                'bytes_sent': int(bytes_sent),
                'bytes_recv': int(bytes_recv),
                'bytes_total': int(bytes_total),
                'mb_sent': float(mb_sent),
                'mb_recv': float(mb_recv),
                'mb_total': float(mb_total)
            }
            
            self.client.table('network_stats').insert(stats).execute()
            
            # 現在の値を保存
            self._last_net_io = net_io
            
            logger.debug(f"📊 Network stats: TX={mb_sent:.2f}MB, RX={mb_recv:.2f}MB")
            
        except Exception as e:
            # テーブルが存在しない場合は警告のみ
            if 'does not exist' in str(e) or 'PGRST204' in str(e):
                logger.warning(f"⚠️ network_stats table does not exist. Please run add_network_stats_table.sql in Supabase.")
            else:
                logger.error(f"❌ Failed to send network stats: {e}")
    
    async def start_realtime_listener(self):
        """Realtimeチャンネルでコマンドキューを監視"""
        if not self.client:
            return
        
        try:
            logger.info("🔄 Starting Realtime listener for command_queue...")
            
            # Supabase Realtimeの購読
            # Note: Python SDKのRealtime機能は限定的なため、ポーリングで実装
            asyncio.create_task(self._poll_command_queue())
            
            logger.info("✅ Realtime listener started (polling mode)")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Realtime listener: {e}")
    
    async def _poll_command_queue(self):
        """コマンドキューをポーリング"""
        logger.info("🔄 Command queue polling started")
        
        while self.is_running:
            try:
                # pending状態のコマンドを取得
                result = self.client.table('command_queue')\
                    .select('*')\
                    .eq('status', 'pending')\
                    .order('created_at', desc=False)\
                    .limit(10)\
                    .execute()
                
                if result.data:
                    for command in result.data:
                        await self._process_command(command)
                
                await asyncio.sleep(1)  # 1秒ごとにポーリング
                
            except Exception as e:
                logger.error(f"❌ Command queue polling error: {e}")
                await asyncio.sleep(5)
    
    async def _process_command(self, command: Dict[str, Any]):
        """コマンドを処理"""
        command_id = command['id']
        command_name = command['command']  # ✅ 正しいカラム名
        payload = command.get('payload', {})
        
        logger.info(f"📥 Processing command: {command_name} (ID: {command_id})")
        
        try:
            # コマンドを処理中に更新
            self.client.table('command_queue').update({
                'status': 'processing'
            }).eq('id', command_id).execute()
            
            result = None
            error = None
            
            # コマンド名に応じて処理
            if command_name == 'pause':
                result = await self._handle_music_pause(payload)
            elif command_name == 'resume':
                result = await self._handle_music_resume(payload)
            elif command_name == 'skip':
                result = await self._handle_music_skip(payload)
            elif command_name == 'stop':
                result = await self._handle_music_stop(payload)
            elif command_name == 'volume':
                result = await self._handle_music_volume(payload)
            elif command_name == 'seek':
                result = await self._handle_music_seek(payload)
            else:
                error = f"Unknown command: {command_name}"
            
            # 完了状態に更新
            self.client.table('command_queue').update({
                'status': 'completed' if not error else 'failed'
            }).eq('id', command_id).execute()
            
            logger.info(f"✅ Command completed: {command_name}")
            
        except Exception as e:
            logger.error(f"❌ Command processing failed: {e}")
            
            # 失敗状態に更新
            self.client.table('command_queue').update({
                'status': 'failed'
            }).eq('id', command_id).execute()
    
    async def _handle_music_pause(self, payload: Dict) -> str:
        """一時停止コマンド"""
        guild_id = payload.get('guild_id')
        
        if not guild_id:
            raise ValueError("Missing guild_id")
        
        guild = self.bot.get_guild(int(guild_id))
        if not guild or not guild.voice_client:
            raise ValueError("Not playing music")
        
        await guild.voice_client.pause()
        return "Paused"
    
    async def _handle_music_resume(self, payload: Dict) -> str:
        """再開コマンド"""
        guild_id = payload.get('guild_id')
        
        if not guild_id:
            raise ValueError("Missing guild_id")
        
        guild = self.bot.get_guild(int(guild_id))
        if not guild or not guild.voice_client:
            raise ValueError("Not playing music")
        
        await guild.voice_client.resume()
        return "Resumed"
    
    async def _handle_music_skip(self, payload: Dict) -> str:
        """スキップコマンド"""
        guild_id = payload.get('guild_id')
        
        if not guild_id:
            raise ValueError("Missing guild_id")
        
        guild = self.bot.get_guild(int(guild_id))
        if not guild or not guild.voice_client:
            raise ValueError("Not playing music")
        
        await guild.voice_client.stop()
        return "Skipped"
    
    async def _handle_music_stop(self, payload: Dict) -> str:
        """停止コマンド"""
        guild_id = payload.get('guild_id')
        
        if not guild_id:
            raise ValueError("Missing guild_id")
        
        guild = self.bot.get_guild(int(guild_id))
        if not guild or not guild.voice_client:
            raise ValueError("Not connected to voice")
        
        music_cog = self.bot.get_cog('MusicPlayer')
        if music_cog:
            queue = music_cog.get_queue(int(guild_id))
            queue.clear()
        
        await guild.voice_client.disconnect()
        return "Stopped"
    
    async def _handle_music_volume(self, payload: Dict) -> str:
        """音量調整コマンド"""
        guild_id = payload.get('guild_id')
        volume = payload.get('volume', 100)
        
        if not guild_id:
            raise ValueError("Missing guild_id")
        
        guild = self.bot.get_guild(int(guild_id))
        if not guild or not guild.voice_client:
            raise ValueError("Not playing music")
        
        await guild.voice_client.set_volume(volume)
        return f"Volume set to {volume}%"
    
    async def _handle_music_seek(self, payload: Dict) -> str:
        """シークコマンド"""
        guild_id = payload.get('guild_id')
        position = payload.get('position', 0)
        
        if not guild_id:
            raise ValueError("Missing guild_id")
        
        guild = self.bot.get_guild(int(guild_id))
        if not guild or not guild.voice_client:
            raise ValueError("Not playing music")
        
        await guild.voice_client.seek(position)
        return f"Seeked to {position}ms"
    
    async def update_active_session(self, guild_id: int, track_data: Optional[Dict] = None):
        """アクティブセッション情報を更新"""
        if not self.client:
            return
        
        try:
            if track_data:
                # ✅ 正しいスキーマに合わせたデータ
                session_data = {
                    'guild_id': str(guild_id),
                    'track_title': track_data.get('title'),
                    'position_ms': int(track_data.get('position', 0)),
                    'duration_ms': int(track_data.get('duration', 0)),
                    'is_playing': bool(track_data.get('is_playing', False)),
                    'voice_members_count': int(track_data.get('members_count', 0))  # ✅ 追加
                }
                
                self.client.table('active_sessions').upsert(session_data).execute()
                logger.debug(f"📊 Active session updated for guild {guild_id}")
            else:
                # セッション終了
                self.client.table('active_sessions').delete().eq('guild_id', str(guild_id)).execute()
                logger.debug(f"📊 Active session cleared for guild {guild_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update active session: {e}")
            import traceback
            traceback.print_exc()
    
    async def log_gemini_usage(self, guild_id: int, user_id: int, prompt_tokens: int, 
                              completion_tokens: int, total_tokens: int, model: str = "gemini-pro"):
        """Gemini API使用ログをSupabaseに記録"""
        if not self.client:
            return
        
        try:
            # ✅ 正しいスキーマに合わせたデータ
            data = {
                "guild_id": str(guild_id),
                "user_id": str(user_id),
                "prompt_tokens": int(prompt_tokens),
                "completion_tokens": int(completion_tokens),
                "total_tokens": int(total_tokens),
                "model": str(model)
            }
            
            self.client.table("gemini_usage").insert(data).execute()
            logger.debug(f"📊 Gemini usage logged: {total_tokens} tokens")
            
        except Exception as e:
            logger.error(f"❌ Failed to log Gemini usage: {e}")
    
    async def log_music_play(self, guild_id: int, track_title: str, track_url: str,
                            duration_ms: int, requested_by: str, requested_by_id: int):
        """音楽再生ログをSupabaseに記録（music_history）"""
        if not self.client:
            return
        
        try:
            # ✅ 正しいスキーマに合わせたデータ
            data = {
                "guild_id": str(guild_id),
                "track_title": str(track_title),
                "track_url": str(track_url) if track_url else None,
                "duration_ms": int(duration_ms),
                "requested_by": str(requested_by),
                "requested_by_id": str(requested_by_id)  # ✅ 追加
            }
            
            self.client.table("music_history").insert(data).execute()
            logger.debug(f"🎵 Music history logged: {track_title}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log music play: {e}")
            import traceback
            traceback.print_exc()
    
    async def log_bot_event(self, level: str, message: str):
        """BotイベントログをSupabaseに送信"""
        if not self.client:
            return
        
        try:
            # ✅ 正しいスキーマ: level, message のみ（created_atは自動）
            data = {
                "level": str(level).upper(),  # "INFO", "WARNING", "ERROR"
                "message": str(message)
            }
            
            self.client.table("bot_logs").insert(data).execute()
            
        except Exception as e:
            logger.error(f"❌ Failed to log bot event: {e}")
    
    async def save_conversation_log(self, user_id: int, user_name: str, prompt: str, response: str):
        """会話ログをSupabaseに保存"""
        if not self.client:
            return
        
        try:
            data = {
                'user_id': str(user_id),
                'user_name': user_name,
                'prompt': prompt,
                'response': response
                # ✅ recorded_at は削除（Supabaseで自動設定）
            }
            
            self.client.table('conversation_logs').insert(data).execute()
            logger.info(f"💬 Conversation log saved for {user_name}")
        except Exception as e:
            logger.error(f"❌ Failed to save conversation log: {e}")
            import traceback
            traceback.print_exc()
    
    async def save_music_log(self, guild_id: int, song_title: str, requested_by: str, requested_by_id: int):
        """音楽ログをSupabaseに保存（music_logs）"""
        if not self.client:
            return
        
        try:
            data = {
                'guild_id': str(guild_id),
                'song_title': song_title,
                'requested_by': requested_by,
                'requested_by_id': str(requested_by_id)
                # ✅ recorded_at は削除（Supabaseで自動設定）
            }
            
            self.client.table('music_logs').insert(data).execute()
            logger.info(f"🎵 Music log saved: {song_title} by {requested_by}")
        except Exception as e:
            logger.error(f"❌ Failed to save music log: {e}")
            import traceback
            traceback.print_exc()
    
    async def shutdown(self):
        """シャットダウン処理"""
        logger.info("🔄 Shutting down Supabase client...")
        self.is_running = False
        
        # tasks.loopを停止
        if self.health_monitor_loop.is_running():
            self.health_monitor_loop.cancel()
        
        # オフライン状態をログに記録
        if self.client:
            try:
                await self.log_bot_event("INFO", "Bot shutting down")
            except Exception as e:
                logger.error(f"Failed to record offline status: {e}")
        
        logger.info("✅ Supabase client shutdown complete")
