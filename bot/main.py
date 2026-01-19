import asyncio
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands
from gemini_client import GeminiClient
from database_pg import Database
from api_server import APIServer
from supabase_client import SupabaseClient
from supabase_log_handler import SupabaseLogHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check critical environment variables on startup
def check_critical_env():
    """Check critical environment variables"""
    missing = []
    
    if not os.getenv('DISCORD_TOKEN'):
        missing.append('DISCORD_TOKEN')
    if not os.getenv('GEMINI_API_KEY'):
        missing.append('GEMINI_API_KEY')
    if not os.getenv('DATABASE_URL'):
        missing.append('DATABASE_URL')
    
    if missing:
        logger.error("=" * 60)
        logger.error("❌ 必須環境変数が不足しています:")
        for var in missing:
            logger.error(f"   - {var}")
        logger.error("")
        logger.error("📝 設定方法:")
        logger.error("   1. .envファイルに環境変数を追加")
        logger.error("   2. またはKoyeb/Vercelのダッシュボードで設定")
        logger.error("")
        logger.error("詳細: KOYEB_VERCEL_DEPLOYMENT_FIX.md を参照")
        logger.error("=" * 60)
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    # Check Lavalink settings (warning only)
    lavalink_vars = ['LAVALINK_HOST', 'LAVALINK_PORT', 'LAVALINK_PASSWORD']
    missing_lavalink = [var for var in lavalink_vars if not os.getenv(var)]
    
    if missing_lavalink:
        logger.warning("=" * 60)
        logger.warning("⚠️  音楽機能の環境変数が不足しています:")
        for var in missing_lavalink:
            logger.warning(f"   - {var}")
        logger.warning("")
        logger.warning("音楽を再生するには以下を設定してください:")
        logger.warning("   LAVALINK_HOST=lavalinkv4.serenetia.com")
        logger.warning("   LAVALINK_PORT=443")
        logger.warning("   LAVALINK_PASSWORD=https://dsc.gg/ajidevserver")
        logger.warning("   LAVALINK_SECURE=true")
        logger.warning("=" * 60)
    else:
        logger.info("✅ すべての環境変数が設定されています")

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.gemini_client = GeminiClient()
        self.database = Database()
        self.supabase_client = SupabaseClient(self)
        self.api_server = None
        self.start_time = time.time()  # Track bot start time
        self.is_maintenance = False  # Maintenance mode flag
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        await self.database.initialize()
        
        # Initialize Supabase client
        supabase_initialized = await self.supabase_client.initialize()
        
        # Setup Supabase log handler if initialized
        if supabase_initialized:
            log_handler = SupabaseLogHandler(self.supabase_client)
            log_handler.setLevel(logging.INFO)
            log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logging.getLogger().addHandler(log_handler)
            
            # Start log flush loop
            asyncio.create_task(log_handler.start_flush_loop())
            logger.info("✅ Supabase log handler initialized")
        
        # Load cogs
        await self.load_extension('cogs.ai_commands')
        await self.load_extension('cogs.settings')
        await self.load_extension('cogs.channel_manager')
        
        # Try to load music player (optional, requires Lavalink)
        try:
            await self.load_extension('cogs.music_player')
            logger.info("Music player loaded successfully")
        except Exception as e:
            logger.warning(f"Music player not loaded (Lavalink may not be running): {e}")
        
        # Start API server
        self.api_server = APIServer(self)
        asyncio.create_task(self.api_server.start())
        
        logger.info("Bot setup completed")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Sync slash commands globally first
        try:
            synced = await self.tree.sync()
            logger.info(f'Synced {len(synced)} global commands')
        except Exception as e:
            logger.error(f'Failed to sync global commands: {e}')
        
        # Send restart notification to all chat channels
        for guild in self.guilds:
            chat_channels = await self.database.get_chat_channels(guild.id)
            for channel_id in chat_channels:
                channel = guild.get_channel(channel_id)
                if channel:
                    try:
                        await channel.send("🔄 Botが再起動しました。音楽機能が利用可能です。")
                    except:
                        pass
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild - sync commands"""
        logger.info(f'Joined new guild: {guild.name} ({guild.id})')
        try:
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(f'Synced {len(synced)} commands to new guild: {guild.name}')
        except Exception as e:
            logger.error(f'Failed to sync commands to {guild.name}: {e}')
    
    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author == self.user:
            return
        
        # Log message for debugging
        logger.debug(f"Message received from {message.author.name} in {message.channel.name}: {message.content[:50]}")
            
        # Check if this channel is set for auto-response
        is_chat_channel = await self.database.is_chat_channel(message.channel.id)
        logger.debug(f"Channel {message.channel.name} is_chat_channel: {is_chat_channel}")
        
        if is_chat_channel:
            # Process AI response in background
            logger.info(f"Processing AI response for message from {message.author.name}")
            asyncio.create_task(self.handle_ai_response(message))
        
        await self.process_commands(message)
    
    async def handle_ai_response(self, message):
        """Handle AI auto-response in chat channels"""
        try:
            # Check quota warnings before processing
            from utils.cost_optimizer import cost_optimizer
            if cost_optimizer.is_quota_warning_threshold():
                await self.send_quota_warning(message.guild)
            
            # Music control keywords - these always trigger music control
            control_keywords = [
                'スキップ', 'skip', '次の曲', 
                '停止', 'stop', 'ストップ', '止めて', 'とめて',
                '切断', 'disconnect', '退出', 'leave',
                '一時停止', 'pause', 'ポーズ',
                '再開', 'resume',
                'キュー', 'queue',
                '今の曲', '何の曲', 'なんの曲', 'nowplaying', 'np',
                'ループ', 'loop', 'リピート', 'repeat',
                '音量', 'volume', 'vol'
            ]
            
            content_lower = message.content.lower()
            
            # Check for music control commands first
            is_control = any(keyword in message.content or keyword in content_lower for keyword in control_keywords)
            if is_control:
                control_handled = await self.handle_music_control(message)
                if control_handled:
                    return
            
            # Music play keywords - MUST contain action words like 流して, かけて, 再生して
            music_action_keywords = [
                '流して', 'ながして', 'かけて', '再生して', 'プレイして', 
                '聞かせて', 'きかせて', '聴かせて',
                'play ', 'play　'  # play with space after
            ]
            
            # Check if message contains music action keywords
            is_music_request = any(keyword in message.content or keyword in content_lower for keyword in music_action_keywords)
            
            # Also check for explicit patterns like "〇〇を流して" or "〇〇かけて"
            import re
            music_pattern = re.search(r'.+(を|の|)(流して|かけて|再生して|プレイして|聞かせて|きかせて)', message.content)
            if music_pattern:
                is_music_request = True
            
            logger.info(f"Music request check: {is_music_request} for message: {message.content[:50]}")
            
            if is_music_request:
                # Try to handle music request - always return after attempting
                # to prevent AI from responding with "再生しますね"
                await self.handle_music_request(message)
                return  # Don't generate AI response for music requests
            
            start_time = time.time()
            async with message.channel.typing():
                # Get user's conversation history from database
                history = await self.database.get_user_history_from_db(message.author.id, limit=5)
                
                # Get AI mode for this guild
                mode = await self.database.get_ai_mode(message.guild.id)
                
                # Generate response
                response = await self.gemini_client.generate_response(
                    message.content,
                    history=history,
                    mode=mode
                )
                
                if response:
                    response_time = time.time() - start_time
                    
                    # Send response
                    await message.reply(response)
                    
                    # Save to Supabase conversation_logs
                    await self.supabase_client.save_conversation_log(
                        user_id=message.author.id,
                        user_name=message.author.display_name,
                        prompt=message.content,
                        response=response
                    )
                    
                    # Save detailed chat log
                    await self.database.save_chat_log(
                        user_id=message.author.id,
                        guild_id=message.guild.id,
                        channel_id=message.channel.id,
                        user_message=message.content,
                        ai_response=response,
                        username=message.author.display_name,
                        channel_name=message.channel.name,
                        guild_name=message.guild.name,
                        tokens_used=len(response.split()) * 1.3,
                        ai_mode=mode,
                        response_time=response_time
                    )
                    
                    # Log usage
                    await self.database.log_usage(
                        user_id=message.author.id,
                        guild_id=message.guild.id,
                        tokens_used=len(response.split()) * 1.3,
                        message_type='auto_response'
                    )
                    
                    # Update analytics
                    await self.database.increment_daily_stat(message.guild.id, 'message_count')
                    await self.database.increment_daily_stat(message.guild.id, 'user_count', message.author.id)
                    await self.database.increment_daily_stat(message.guild.id, 'token_count')
                    
                    # Update conversation history
                    self.database.update_user_history(
                        message.author.id,
                        message.content,
                        response
                    )
                    
                    # Broadcast to WebSocket clients
                    if self.api_server:
                        await self.api_server.broadcast_message_event({
                            'type': 'new_message',
                            'user_id': str(message.author.id),
                            'username': message.author.display_name,
                            'guild_id': str(message.guild.id),
                            'guild_name': message.guild.name,
                            'channel_id': str(message.channel.id),
                            'channel_name': message.channel.name,
                            'user_message': message.content,
                            'ai_response': response,
                            'tokens_used': len(response.split()) * 1.3,
                            'ai_mode': mode,
                            'response_time': response_time,
                            'timestamp': datetime.now().isoformat()
                        })
                    
        except Exception as e:
            logger.error(f'Error handling AI response: {e}')
    
    async def handle_music_request(self, message):
        """Handle music requests and actually play music"""
        try:
            logger.info(f"Handling music request: {message.content}")
            
            # Check if music player cog is loaded
            music_cog = self.get_cog('MusicPlayer')
            if not music_cog:
                logger.error("Music cog not loaded")
                await message.reply("❌ 音楽機能が利用できません。Lavalinkサーバーが起動していることを確認してください。")
                return False
            
            import wavelink
            import re
            
            # URL patterns
            YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+')
            SPOTIFY_REGEX = re.compile(r'(https?://)?(open\.)?spotify\.com/(track|album|playlist|artist)/([a-zA-Z0-9]+)')
            SOUNDCLOUD_REGEX = re.compile(r'(https?://)?(www\.)?soundcloud\.com/.+')
            
            content = message.content
            tracks = []
            is_playlist = False
            playlist_name = None
            source_type = "youtube"  # default
            
            # Extract URL from message
            url_match = re.search(r'https?://[^\s]+', content)
            
            if url_match:
                url = url_match.group(0)
                logger.info(f"Found URL in message: {url}")
                
                if SPOTIFY_REGEX.match(url):
                    source_type = "spotify"
                    logger.info("Detected Spotify URL")
                    try:
                        result = await wavelink.Playable.search(url)
                        if isinstance(result, wavelink.Playlist):
                            tracks = result.tracks
                            is_playlist = True
                            playlist_name = result.name
                        else:
                            tracks = result if result else []
                    except Exception as e:
                        logger.error(f"Spotify load failed: {e}")
                        
                elif YOUTUBE_REGEX.match(url):
                    source_type = "youtube"
                    logger.info("Detected YouTube URL")
                    try:
                        result = await wavelink.Playable.search(url)
                        if isinstance(result, wavelink.Playlist):
                            tracks = result.tracks
                            is_playlist = True
                            playlist_name = result.name
                        else:
                            tracks = result if result else []
                    except Exception as e:
                        logger.error(f"YouTube load failed: {e}")
                        
                elif SOUNDCLOUD_REGEX.match(url):
                    source_type = "soundcloud"
                    logger.info("Detected SoundCloud URL")
                    try:
                        tracks = await wavelink.Playable.search(url)
                    except Exception as e:
                        logger.error(f"SoundCloud load failed: {e}")
            
            # If no URL or URL failed, search by text
            if not tracks:
                # Check if user wants Spotify search
                use_spotify = any(word in content.lower() for word in ['spotify', 'スポティファイ', 'スポティ'])
                
                # Get search query
                recommendation_query = await music_cog.ai_music_recommendation(content)
                logger.info(f"Search query: {recommendation_query}")
                
                if use_spotify:
                    source_type = "spotify"
                    logger.info("Using Spotify search")
                    try:
                        tracks = await wavelink.Playable.search(f"spsearch:{recommendation_query}")
                    except Exception as e:
                        logger.error(f"Spotify search failed: {e}")
                
                # YouTube search - get multiple results for selection using wavelink
                if not tracks:
                    source_type = "youtube"
                    
                    try:
                        # Use wavelink ytsearch to get multiple results (15 tracks)
                        search_tracks = await wavelink.Playable.search(f"ytsearch15:{recommendation_query}")
                        
                        if search_tracks and len(search_tracks) > 1:
                            # Show selection UI with multiple results
                            embed = discord.Embed(
                                title="🎵 曲を選択してください",
                                description=f"検索: **{recommendation_query}**\n{len(search_tracks[:15])}件の結果",
                                color=0xff0000
                            )
                            
                            # Add thumbnail from first track
                            first_track = search_tracks[0]
                            if hasattr(first_track, 'artwork') and first_track.artwork:
                                embed.set_thumbnail(url=first_track.artwork)
                            
                            for i, track in enumerate(search_tracks[:15], 1):
                                duration_sec = track.length // 1000
                                duration_min = duration_sec // 60
                                duration_sec = duration_sec % 60
                                author = getattr(track, 'author', 'Unknown')
                                
                                # Truncate title and author for better display
                                title_display = track.title[:40] + '...' if len(track.title) > 40 else track.title
                                author_display = author[:18] + '...' if len(author) > 18 else author
                                
                                embed.add_field(
                                    name=f"{i}. {title_display}",
                                    value=f"⏱️ {duration_min}:{duration_sec:02d} | 📺 {author_display}",
                                    inline=False
                                )
                            
                            embed.set_footer(text="番号のボタンをクリックして選択 (60秒でタイムアウト)")
                            
                            # Create selection view with wavelink tracks (up to 15)
                            view = WavelinkTrackSelectionView(self, message, search_tracks[:15], music_cog)
                            selection_msg = await message.reply(embed=embed, view=view)
                            view.message = selection_msg
                            return True
                        elif search_tracks:
                            # Only one result, use it directly
                            tracks = search_tracks
                    except Exception as e:
                        logger.error(f"Wavelink ytsearch failed: {e}")
            
            if not tracks or len(tracks) == 0:
                await message.reply(f"❌ 曲が見つかりませんでした。別のキーワードで試してみてください。")
                return False
            
            # Create or get music channel
            try:
                music_channel = await music_cog.create_music_channel(message.guild, message.author)
                logger.info(f"Music channel: {music_channel.name}")
            except Exception as ch_err:
                logger.error(f"Failed to create music channel: {ch_err}")
                await message.reply("❌ 音楽チャンネルの作成に失敗しました。Botに必要な権限があるか確認してください。")
                return False
            try:
                if not message.guild.voice_client:
                    logger.info("Connecting to voice channel...")
                    vc = await music_channel.connect(cls=wavelink.Player)
                else:
                    vc = message.guild.voice_client
                logger.info(f"Voice client connected: {vc}")
            except Exception as vc_err:
                logger.error(f"Failed to connect to voice channel: {vc_err}")
                await message.reply("❌ ボイスチャンネルへの接続に失敗しました。")
                return False
            
            queue = music_cog.get_queue(message.guild.id)
            
            # Handle playlist
            if is_playlist and len(tracks) > 1:
                first_track = tracks[0]
                for track in tracks[1:]:
                    queue.add(track)
                
                if not vc.playing:
                    await vc.play(first_track)
                    queue.current = first_track
                else:
                    queue.add(first_track)
                
                # Source color
                color = 0x1DB954 if source_type == "spotify" else (0xFF5500 if source_type == "soundcloud" else 0xFF0000)
                
                embed = discord.Embed(
                    title="📋 プレイリストを追加しました",
                    description=f"**{playlist_name or 'プレイリスト'}**\n{len(tracks)}曲をキューに追加しました",
                    color=color
                )
                await message.reply(embed=embed)
                return True
            
            track = tracks[0]
            logger.info(f"Selected track: {track.title}")
            
            if not vc.playing:
                # Actually play the track
                try:
                    await vc.play(track)
                    queue.current = track
                    logger.info(f"Started playing: {track.title}")
                    
                    # Save to Supabase music_logs
                    await self.supabase_client.save_music_log(
                        guild_id=message.guild.id,
                        song_title=track.title,
                        requested_by=message.author.display_name,
                        requested_by_id=message.author.id
                    )
                except Exception as play_err:
                    logger.error(f"Failed to play track: {play_err}")
                    await message.reply(f"❌ 曲の再生に失敗しました: {str(play_err)}")
                    return False
                
                # Verify playback actually started
                await asyncio.sleep(0.5)
                if not vc.playing and not vc.paused:
                    logger.error("Playback did not start")
                    await message.reply("❌ 再生を開始できませんでした。Lavalinkサーバーの状態を確認してください。")
                    return False
                
                # Create player UI with buttons
                from music_ui import MusicPlayerView
                view = MusicPlayerView(self, message.guild.id)
                embed = view.create_embed()
                embed.add_field(name="リクエスト", value=message.content[:100], inline=False)
                
                player_message = await message.reply(embed=embed, view=view)
                view.message = player_message
                await view.start_update_loop()
                
                # Broadcast to WebSocket
                if self.api_server:
                    await self.api_server.broadcast_music_event({
                        'type': 'track_start',
                        'guild_id': message.guild.id,
                        'playback_mode': 'discord',
                        'track': {
                            'title': track.title,
                            'author': getattr(track, 'author', 'Unknown'),
                            'length': track.length,
                            'artwork': getattr(track, 'artwork', None),
                            'uri': track.uri
                        },
                        'requester': message.author.display_name
                    })
            else:
                queue.add(track)
                
                # Show queue with position
                queue_list = [f"{i}. {t.title[:40]}..." if len(t.title) > 40 else f"{i}. {t.title}" 
                             for i, t in enumerate(queue.queue[:5], 1)]
                
                embed = discord.Embed(
                    title="📝 キューに追加しました",
                    description=f"**{track.title}**",
                    color=0x00ffcc
                )
                embed.add_field(name="キュー位置", value=f"{len(queue.queue)}番目", inline=True)
                
                if len(queue.queue) > 1:
                    embed.add_field(name="📝 現在のキュー", value="\n".join(queue_list), inline=False)
                
                if hasattr(track, 'artwork') and track.artwork:
                    embed.set_thumbnail(url=track.artwork)
                
                await message.reply(embed=embed)
            
            return True
            
        except Exception as e:
            logger.error(f'Error handling music request: {e}')
            import traceback
            traceback.print_exc()
            await message.reply(f"❌ 音楽の再生中にエラーが発生しました: {str(e)}")
            return False
    
    async def handle_music_control(self, message):
        """Handle music control commands in chat"""
        content = message.content.lower()
        music_cog = self.get_cog('MusicPlayer')
        
        if not music_cog:
            return False
        
        vc = message.guild.voice_client
        queue = music_cog.get_queue(message.guild.id)
        
        # Skip command
        if any(cmd in content for cmd in ['スキップ', 'skip', '次', '次の曲', 'つぎ']):
            if vc and vc.playing:
                await vc.stop()
                await message.reply("⏭️ スキップしました")
                return True
            else:
                await message.reply("❌ 再生中の曲がありません")
                return True
        
        # Stop command
        if any(cmd in content for cmd in ['停止', 'stop', 'ストップ', '止めて', 'とめて']):
            if vc:
                queue.clear()
                await vc.disconnect()
                await message.reply("⏹️ 音楽を停止しました")
                return True
            else:
                await message.reply("❌ 再生中ではありません")
                return True
        
        # Disconnect command
        if any(cmd in content for cmd in ['切断', 'disconnect', '退出', '出て', 'leave', 'でて']):
            if vc:
                queue.clear()
                await vc.disconnect()
                await message.reply("👋 ボイスチャンネルから切断しました")
                return True
            else:
                await message.reply("❌ ボイスチャンネルに接続していません")
                return True
        
        # Pause command
        if any(cmd in content for cmd in ['一時停止', 'pause', 'ポーズ']):
            if vc and vc.playing:
                await vc.pause(True)
                await message.reply("⏸️ 一時停止しました")
                return True
        
        # Resume command
        if any(cmd in content for cmd in ['再開', 'resume', '続き', 'つづき']):
            if vc and vc.paused:
                await vc.pause(False)
                await message.reply("▶️ 再開しました")
                return True
        
        # Queue command
        if any(cmd in content for cmd in ['キュー', 'queue', '待ち', '次の曲は']):
            embed = discord.Embed(title="🎵 音楽キュー", color=0xaa66ff)
            
            if queue.current:
                embed.add_field(
                    name="🎵 現在再生中",
                    value=f"**{queue.current.title}**",
                    inline=False
                )
            
            if queue.queue:
                queue_list = [f"{i}. {t.title}" for i, t in enumerate(queue.queue[:10], 1)]
                embed.add_field(name="📝 次の曲", value="\n".join(queue_list), inline=False)
                if len(queue.queue) > 10:
                    embed.set_footer(text=f"他 {len(queue.queue) - 10} 曲")
            else:
                embed.add_field(name="📝 キュー", value="キューは空です", inline=False)
            
            await message.reply(embed=embed)
            return True
        
        # Now playing command
        if any(cmd in content for cmd in ['今の曲', '何の曲', 'なんの曲', 'nowplaying', 'np']):
            if queue.current and vc:
                # Get current position
                position = vc.position // 1000  # Convert to seconds
                duration = queue.current.length // 1000
                pos_min, pos_sec = divmod(position, 60)
                dur_min, dur_sec = divmod(duration, 60)
                
                # Progress bar
                progress = int((position / duration) * 20) if duration > 0 else 0
                bar = "▓" * progress + "░" * (20 - progress)
                
                embed = discord.Embed(
                    title="🎵 現在再生中",
                    description=f"**{queue.current.title}**\n{getattr(queue.current, 'author', 'Unknown')}",
                    color=0xff66aa
                )
                embed.add_field(
                    name="再生位置",
                    value=f"`{pos_min:02d}:{pos_sec:02d}` {bar} `{dur_min:02d}:{dur_sec:02d}`",
                    inline=False
                )
                if hasattr(queue.current, 'artwork') and queue.current.artwork:
                    embed.set_thumbnail(url=queue.current.artwork)
                await message.reply(embed=embed)
            else:
                await message.reply("❌ 現在再生中の曲はありません")
            return True
        
        # Loop command
        if any(cmd in content for cmd in ['ループ', 'loop', 'リピート', 'repeat']):
            if 'オフ' in content or 'off' in content:
                queue.loop_mode = "off"
                await message.reply("🔁 ループをオフにしました")
            elif '曲' in content or 'track' in content or '1曲' in content:
                queue.loop_mode = "track"
                await message.reply("🔂 現在の曲をループします")
            else:
                queue.loop_mode = "queue"
                await message.reply("🔁 キュー全体をループします")
            return True
        
        # Volume command
        if any(cmd in content for cmd in ['音量', 'volume', 'vol']):
            import re
            match = re.search(r'(\d+)', content)
            if match and vc:
                vol = min(100, max(0, int(match.group(1))))
                await vc.set_volume(vol)
                await message.reply(f"🔊 音量を {vol}% に設定しました")
                return True
        
        return False
    
    async def send_quota_warning(self, guild):
        """Send quota warning to guild administrators"""
        try:
            from utils.cost_optimizer import cost_optimizer
            usage_stats = cost_optimizer.get_usage_stats()
            
            # Find a suitable channel to send warning (preferably admin channel)
            warning_channel = None
            for channel in guild.text_channels:
                if any(keyword in channel.name.lower() for keyword in ['admin', 'bot', 'log', 'general']):
                    if channel.permissions_for(guild.me).send_messages:
                        warning_channel = channel
                        break
            
            if not warning_channel:
                # Fallback to first available channel
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        warning_channel = channel
                        break
            
            if warning_channel:
                embed = discord.Embed(
                    title="⚠️ API使用量警告",
                    description="Gemini APIの使用量が制限に近づいています。",
                    color=0xff9900
                )
                embed.add_field(
                    name="リクエスト使用量",
                    value=f"{usage_stats['daily_requests']}/{usage_stats['request_limit']} ({usage_stats['usage_percentage']['requests']:.1f}%)",
                    inline=True
                )
                embed.add_field(
                    name="トークン使用量", 
                    value=f"{usage_stats['daily_tokens']}/{usage_stats['token_limit']} ({usage_stats['usage_percentage']['tokens']:.1f}%)",
                    inline=True
                )
                embed.add_field(
                    name="対策",
                    value="• 簡単な質問は自動応答を使用\n• 長い会話は要約機能を活用\n• 複雑なタスクのみAIを使用",
                    inline=False
                )
                embed.set_footer(text="制限に達すると自動的にAI機能が無効になります")
                
                await warning_channel.send(embed=embed)
                logger.info(f"Sent quota warning to guild {guild.name}")
                
        except Exception as e:
            logger.error(f'Error sending quota warning: {e}')

async def run_api_server_standalone():
    """Run API server standalone for health checks"""
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"status": "starting", "message": "Bot is initializing..."}
    
    @app.get("/api/health")
    async def health():
        return {"status": "healthy", "bot_ready": False}
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('PORT', os.getenv('API_PORT', 8000)))
    
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    """Main function to run the bot with retry logic"""
    # Check critical environment variables first
    try:
        check_critical_env()
    except ValueError as e:
        logger.error(f"Environment check failed: {e}")
        return
    
    bot = DiscordBot()
    max_retries = 10
    retry_delay = 5  # seconds
    
    # Start a minimal API server first to satisfy Render's port binding
    api_task = None
    
    # Setup signal handlers for graceful shutdown
    import signal
    
    def signal_handler(sig, frame):
        logger.info("🔄 Received shutdown signal, cleaning up...")
        asyncio.create_task(shutdown(bot))
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Starting bot (attempt {attempt + 1}/{max_retries})...")
            await bot.start(os.getenv('DISCORD_TOKEN'))
            break  # If successful, exit loop
        except KeyboardInterrupt:
            logger.info('Bot shutdown requested')
            await shutdown(bot)
            break
        except OSError as e:
            if "Network is unreachable" in str(e) or e.errno == 101:
                logger.warning(f"Network unreachable, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                
                # Start standalone API server on first network failure
                if api_task is None:
                    logger.info("Starting standalone API server for health checks...")
                    api_task = asyncio.create_task(run_api_server_standalone())
                    await asyncio.sleep(2)  # Give server time to start
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 60)  # Cap at 60 seconds
                else:
                    logger.error("Max retries reached. Network still unreachable.")
            else:
                logger.error(f'Bot error: {e}')
                break
        except Exception as e:
            logger.error(f'Bot error: {e}')
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
            else:
                break
    
    # Cancel API task if running
    if api_task and not api_task.done():
        api_task.cancel()
    
    await shutdown(bot)


async def shutdown(bot):
    """Graceful shutdown"""
    logger.info("🔄 Starting graceful shutdown...")
    
    # Stop music in all guilds
    for guild in bot.guilds:
        if guild.voice_client:
            try:
                music_cog = bot.get_cog('MusicPlayer')
                if music_cog:
                    queue = music_cog.get_queue(guild.id)
                    queue.clear()
                await guild.voice_client.disconnect()
            except:
                pass
    
    # Shutdown Supabase client
    await bot.supabase_client.shutdown()
    
    # Close bot
    await bot.close()
    
    logger.info("✅ Shutdown complete")


class WavelinkTrackSelectionView(discord.ui.View):
    """View for selecting a track from wavelink search results"""
    def __init__(self, bot, message, tracks, music_cog):
        super().__init__(timeout=60)
        self.bot = bot
        self.original_message = message
        self.tracks = tracks  # wavelink tracks directly
        self.music_cog = music_cog
        self.message = None
        
        # Add buttons for each track (max 15, arranged in rows of 5)
        num_tracks = min(15, len(tracks))
        for i in range(num_tracks):
            button = discord.ui.Button(
                label=str(i + 1),
                style=discord.ButtonStyle.primary,
                custom_id=f"track_{i}",
                row=i // 5  # 5 buttons per row
            )
            button.callback = self.create_callback(i)
            self.add_item(button)
        
        # Add cancel button in the last row
        cancel_btn = discord.ui.Button(
            label="キャンセル",
            style=discord.ButtonStyle.danger,
            custom_id="cancel",
            row=4  # Always in the last row
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    def create_callback(self, index):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            await self.play_selected(interaction, index)
        return callback
    
    async def cancel_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(
            title="❌ キャンセルしました",
            color=0xff4444
        )
        await self.message.edit(embed=embed, view=None)
        self.stop()
    
    async def play_selected(self, interaction: discord.Interaction, index: int):
        """Play the selected track"""
        try:
            import wavelink
            
            track = self.tracks[index]
            
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            
            # Update embed to show loading
            embed = discord.Embed(
                title="🎵 読み込み中...",
                description=f"**{track.title}**",
                color=0xffaa00
            )
            await self.message.edit(embed=embed, view=self)
            
            # Create or get music channel
            music_channel = await self.music_cog.create_music_channel(
                self.original_message.guild, 
                self.original_message.author
            )
            
            # Connect to voice channel
            if not self.original_message.guild.voice_client:
                vc = await music_channel.connect(cls=wavelink.Player)
            else:
                vc = self.original_message.guild.voice_client
            
            queue = self.music_cog.get_queue(self.original_message.guild.id)
            
            if not vc.playing:
                await vc.play(track)
                queue.current = track
                
                # Save to Supabase music_logs
                await self.bot.supabase_client.save_music_log(
                    guild_id=self.original_message.guild.id,
                    song_title=track.title,
                    requested_by=self.original_message.author.display_name,
                    requested_by_id=self.original_message.author.id
                )
                
                # Create player UI
                from music_ui import MusicPlayerView
                view = MusicPlayerView(self.bot, self.original_message.guild.id)
                embed = view.create_embed()
                
                await self.message.edit(embed=embed, view=view)
                view.message = self.message
                await view.start_update_loop()
                
                # Broadcast to WebSocket
                if self.bot.api_server:
                    await self.bot.api_server.broadcast_music_event({
                        'type': 'track_start',
                        'guild_id': self.original_message.guild.id,
                        'track': {
                            'title': track.title,
                            'author': getattr(track, 'author', 'Unknown'),
                            'length': track.length,
                            'artwork': getattr(track, 'artwork', None),
                            'uri': track.uri
                        }
                    })
            else:
                queue.add(track)
                embed = discord.Embed(
                    title="📝 キューに追加しました",
                    description=f"**{track.title}**",
                    color=0x00ffcc
                )
                embed.add_field(name="キュー位置", value=f"{len(queue.queue)}番目", inline=True)
                await self.message.edit(embed=embed, view=None)
            
        except Exception as e:
            logger.error(f"Error playing selected track: {e}")
            embed = discord.Embed(
                title="❌ エラーが発生しました",
                description=str(e),
                color=0xff4444
            )
            await self.message.edit(embed=embed, view=None)
        
        self.stop()
    
    async def on_timeout(self):
        """Handle timeout"""
        embed = discord.Embed(
            title="⏰ タイムアウトしました",
            description="選択時間が過ぎました。もう一度お試しください。",
            color=0xff9900
        )
        try:
            await self.message.edit(embed=embed, view=None)
        except:
            pass


if __name__ == '__main__':
    asyncio.run(main())