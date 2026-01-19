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
            
            # RAM使用率（システム全体）
            ram = psutil.virtual_memory()
            ram_usage = ram.percent
            
            # メモリ使用量（プロセス）
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_rss = memory_info.rss / 1024 / 1024  # MB
            memory_heap = memory_info.vms / 1024 / 1024  # MB
            
            # Discord Gateway Ping
            ping_gateway = round(self.bot.latency * 1000, 2)  # ms
            
            # Lavalink Ping (音楽機能がある場合)
            ping_lavalink = 0
            try:
                if hasattr(self.bot, 'wavelink') and self.bot.wavelink:
                    # Wavelinkのノード情報を取得
                    nodes = self.bot.wavelink.nodes
                    if nodes:
                        ping_lavalink = round(nodes[0].latency * 1000, 2)
            except:
                pass
            
            # サーバー数（ギルド数）
            server_count = len(self.bot.guilds)
            
            # 稼働時間
            uptime = int(time.time() - self.bot.start_time)
            
            stats = {
                'cpu_usage': cpu_usage,
                'ram_usage': ram_usage,
                'memory_rss': memory_rss,
                'memory_heap': memory_heap,
                'ping_gateway': ping_gateway,
                'ping_lavalink': ping_lavalink,
                'server_count': server_count,
                'guild_count': server_count,  # 互換性のため
                'uptime': uptime,
                'timestamp': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # INSERTでデータを追加（履歴として保存）
            self.client.table('system_stats').insert({
                'bot_id': 'primary',
                **stats
            }).execute()
            
            logger.debug(f"📊 System stats sent: CPU={cpu_usage}%, RAM={ram_usage}%, Servers={server_count}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send system stats: {e}")
    
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
        command_type = command['command_type']
        payload = command.get('payload', {})
        
        logger.info(f"📥 Processing command: {command_type} (ID: {command_id})")
        
        try:
            # コマンドを処理中に更新
            self.client.table('command_queue').update({
                'status': 'processing',
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', command_id).execute()
            
            result = None
            error = None
            
            # コマンドタイプに応じて処理
            if command_type == 'MUSIC_PLAY':
                result = await self._handle_music_play(payload)
            elif command_type == 'MUSIC_SKIP':
                result = await self._handle_music_skip(payload)
            elif command_type == 'MUSIC_STOP':
                result = await self._handle_music_stop(payload)
            elif command_type == 'MUSIC_VOLUME':
                result = await self._handle_music_volume(payload)
            elif command_type == 'MUSIC_SEEK':
                result = await self._handle_music_seek(payload)
            elif command_type == 'SYS_MAINTENANCE':
                result = await self._handle_maintenance(payload)
            else:
                error = f"Unknown command type: {command_type}"
            
            # 完了状態に更新
            self.client.table('command_queue').update({
                'status': 'completed' if not error else 'failed',
                'result': result,
                'error': error,
                'completed_at': datetime.utcnow().isoformat()
            }).eq('id', command_id).execute()
            
            # ジョブログに記録
            self.client.table('job_logs').insert({
                'command_id': command_id,
                'command_type': command_type,
                'status': 'completed' if not error else 'failed',
                'result': result,
                'error': error,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            logger.info(f"✅ Command completed: {command_type}")
            
        except Exception as e:
            logger.error(f"❌ Command processing failed: {e}")
            
            # 失敗状態に更新
            self.client.table('command_queue').update({
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.utcnow().isoformat()
            }).eq('id', command_id).execute()
    
    async def _handle_music_play(self, payload: Dict) -> str:
        """音楽再生コマンド"""
        url = payload.get('url')
        guild_id = payload.get('guild_id')
        
        if not url or not guild_id:
            raise ValueError("Missing url or guild_id")
        
        # 音楽Cogを取得
        music_cog = self.bot.get_cog('MusicPlayer')
        if not music_cog:
            raise ValueError("Music player not available")
        
        # ギルドを取得
        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            raise ValueError(f"Guild not found: {guild_id}")
        
        # 音楽を再生（実装は既存のロジックを使用）
        # TODO: 実際の再生ロジックを実装
        
        return f"Playing: {url}"
    
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
    
    async def _handle_maintenance(self, payload: Dict) -> str:
        """メンテナンスモード切り替え"""
        enabled = payload.get('enabled', False)
        
        # グローバル変数でメンテナンスモードを管理
        self.bot.is_maintenance = enabled
        
        return f"Maintenance mode: {'enabled' if enabled else 'disabled'}"
    
    async def update_active_session(self, guild_id: int, track_data: Optional[Dict] = None):
        """アクティブセッション情報を更新"""
        if not self.client:
            return
        
        try:
            if track_data:
                session_data = {
                    'guild_id': str(guild_id),
                    'track_title': track_data.get('title'),
                    'position_ms': track_data.get('position', 0),
                    'duration_ms': track_data.get('duration', 0),
                    'is_playing': track_data.get('is_playing', False),
                    'voice_members_count': track_data.get('members_count', 0),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                self.client.table('active_sessions').upsert(session_data).execute()
            else:
                # セッション終了
                self.client.table('active_sessions').delete().eq('guild_id', str(guild_id)).execute()
                
        except Exception as e:
            logger.error(f"❌ Failed to update active session: {e}")
    
    async def log_to_supabase(self, level: str, message: str, scope: str = 'general'):
        """ログをSupabaseに送信"""
        if not self.client:
            return
        
        try:
            self.client.table('bot_logs').insert({
                'level': level,
                'message': message,
                'scope': scope,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"❌ Failed to log to Supabase: {e}")
    
    async def save_conversation_log(self, user_id: int, user_name: str, prompt: str, response: str):
        """会話ログをSupabaseに保存"""
        if not self.client:
            return
        
        try:
            self.client.table('conversation_logs').insert({
                'user_id': str(user_id),
                'user_name': user_name,
                'prompt': prompt,
                'response': response,
                'timestamp': datetime.utcnow().isoformat()
            }).execute()
            logger.debug(f"💬 Conversation log saved for {user_name}")
        except Exception as e:
            logger.error(f"❌ Failed to save conversation log: {e}")
    
    async def save_music_log(self, guild_id: int, song_title: str, requested_by: str, requested_by_id: int):
        """音楽ログをSupabaseに保存"""
        if not self.client:
            return
        
        try:
            self.client.table('music_logs').insert({
                'guild_id': str(guild_id),
                'song_title': song_title,
                'requested_by': requested_by,
                'requested_by_id': str(requested_by_id),
                'timestamp': datetime.utcnow().isoformat()
            }).execute()
            logger.debug(f"🎵 Music log saved: {song_title} by {requested_by}")
        except Exception as e:
            logger.error(f"❌ Failed to save music log: {e}")
    
    async def shutdown(self):
        """シャットダウン処理"""
        logger.info("🔄 Shutting down Supabase client...")
        self.is_running = False
        
        # tasks.loopを停止
        if self.health_monitor_loop.is_running():
            self.health_monitor_loop.cancel()
        
        # オフライン状態を記録
        if self.client:
            try:
                self.client.table('system_stats').insert({
                    'bot_id': 'primary',
                    'status': 'offline',
                    'cpu_usage': 0,
                    'ram_usage': 0,
                    'server_count': 0,
                    'timestamp': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }).execute()
            except Exception as e:
                logger.error(f"Failed to record offline status: {e}")
        
        logger.info("✅ Supabase client shutdown complete")
