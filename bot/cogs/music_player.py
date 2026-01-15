import discord
from discord.ext import commands
from discord import app_commands
import wavelink
import asyncio
import logging
from typing import Optional, List, Dict
import re
from youtubesearchpython import VideosSearch
import json

logger = logging.getLogger(__name__)

# URL patterns
YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+')
SPOTIFY_REGEX = re.compile(r'(https?://)?(open\.)?spotify\.com/(track|album|playlist|artist)/([a-zA-Z0-9]+)')
SOUNDCLOUD_REGEX = re.compile(r'(https?://)?(www\.)?soundcloud\.com/.+')

class MusicQueue:
    def __init__(self):
        self.queue: List[wavelink.Playable] = []
        self.history: List[wavelink.Playable] = []
        self.current: Optional[wavelink.Playable] = None
        self.loop_mode = "off"  # off, track, queue
    
    def add(self, track: wavelink.Playable):
        self.queue.append(track)
    
    def get_next(self) -> Optional[wavelink.Playable]:
        if self.loop_mode == "track" and self.current:
            return self.current
        
        if not self.queue:
            if self.loop_mode == "queue" and self.history:
                self.queue.extend(self.history)
                self.history.clear()
        
        if self.queue:
            track = self.queue.pop(0)
            if self.current:
                self.history.append(self.current)
            self.current = track
            return track
        
        return None
    
    def clear(self):
        self.queue.clear()
        self.history.clear()
        self.current = None

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queues: Dict[int, MusicQueue] = {}
        self.music_channels: Dict[int, int] = {}  # guild_id -> voice_channel_id
        
    async def cog_load(self):
        """Initialize Wavelink when cog loads"""
        try:
            # Connect to Lavalink server (using external hosted server)
            nodes = [wavelink.Node(uri="https://lavalinkv4.serenetia.com:443", password="https://dsc.gg/ajidevserver")]
            await wavelink.Pool.connect(nodes=nodes, client=self.bot)
            logger.info("Connected to Lavalink server")
        except Exception as e:
            logger.error(f"Failed to connect to Lavalink: {e}")
    
    def get_queue(self, guild_id: int) -> MusicQueue:
        """Get or create music queue for guild"""
        if guild_id not in self.music_queues:
            self.music_queues[guild_id] = MusicQueue()
        return self.music_queues[guild_id]
    
    async def create_music_channel(self, guild: discord.Guild, user: discord.Member) -> discord.VoiceChannel:
        """Create dedicated music voice channel"""
        try:
            # Check if music channel already exists
            existing_channel = discord.utils.get(guild.voice_channels, name="🎵｜Music-Space")
            if existing_channel:
                return existing_channel
            
            # Create new music channel
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    connect=True,
                    speak=True,
                    view_channel=True
                )
            }
            
            channel = await guild.create_voice_channel(
                name="🎵｜Music-Space",
                overwrites=overwrites,
                reason="AI Music Bot専用チャンネル"
            )
            
            # Save to database
            await self.bot.database.save_music_channel(guild.id, channel.id, user.id)
            self.music_channels[guild.id] = channel.id
            
            logger.info(f"Created music channel in {guild.name}")
            return channel
            
        except Exception as e:
            logger.error(f"Error creating music channel: {e}")
            raise
    
    async def search_youtube(self, query: str, limit: int = 1) -> List[Dict]:
        """Search YouTube for tracks"""
        try:
            videos_search = VideosSearch(query, limit=limit)
            results = videos_search.result()
            
            tracks = []
            for video in results['result']:
                tracks.append({
                    'title': video['title'],
                    'url': video['link'],
                    'duration': video['duration'],
                    'thumbnail': video['thumbnails'][0]['url'] if video['thumbnails'] else None,
                    'channel': video['channel']['name']
                })
            
            return tracks
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    async def ai_music_recommendation(self, user_message: str, conversation_context: str = "") -> str:
        """Extract search query from user message"""
        try:
            # まず、メッセージから直接曲名/アーティスト名を抽出
            # 「流して」「かけて」「再生して」などを除去
            clean_message = user_message
            remove_words = ['流して', 'ながして', 'かけて', '再生して', '聞きたい', '聴きたい', 
                           '聞かせて', 'きかせて', 'プレイして', 'play', '曲', 'の曲', '音楽']
            for word in remove_words:
                clean_message = clean_message.replace(word, '')
            clean_message = clean_message.strip()
            
            # クリーンなメッセージがあればそれを使う
            if clean_message and len(clean_message) > 2:
                logger.info(f"Using cleaned query: {clean_message}")
                return clean_message
            
            # AIで検索クエリを生成
            prompt = f"""あなたはYouTube検索クエリ生成器です。
ユーザーの入力から、YouTube Music検索に最適な検索クエリを生成してください。

入力: "{user_message}"

ルール:
1. 検索クエリのみを出力（説明や絵文字は不要）
2. アーティスト名と曲名が含まれていればそのまま使用
3. 「流して」「再生して」などの指示語は除去
4. 曖昧な場合は一般的な検索語を生成

出力例:
- 入力「YOASOBIのアイドル流して」→ 出力「YOASOBI アイドル」
- 入力「リラックスできる曲」→ 出力「relaxing music chill」
- 入力「作業用BGM」→ 出力「lo-fi study beats」

検索クエリ:"""
            
            response = await self.bot.gemini_client.generate_response(
                prompt,
                mode='assistant'
            )
            
            if response:
                # 余計な文字を除去
                result = response.strip()
                result = result.replace('🎵', '').replace('音楽を再生しますね', '').strip()
                if result and len(result) > 2 and '再生' not in result:
                    logger.info(f"AI generated query: {result}")
                    return result
            
            # フォールバック: クリーンなメッセージを返す
            return clean_message if clean_message else user_message
            
        except Exception as e:
            logger.error(f"Error getting AI music recommendation: {e}")
            return user_message
    
    @app_commands.command(name="play", description="音楽を再生します")
    @app_commands.describe(
        query="曲名、アーティスト名、またはURL (YouTube/Spotify/SoundCloud)",
        source="検索ソース"
    )
    @app_commands.choices(source=[
        app_commands.Choice(name="YouTube", value="youtube"),
        app_commands.Choice(name="Spotify", value="spotify"),
        app_commands.Choice(name="SoundCloud", value="soundcloud"),
        app_commands.Choice(name="自動検出", value="auto"),
    ])
    async def play(self, interaction: discord.Interaction, query: str, source: str = "auto"):
        """Play music command with source selection"""
        await interaction.response.defer()
        
        try:
            # Check if user is in voice channel
            if not interaction.user.voice:
                await interaction.followup.send("❌ ボイスチャンネルに参加してから使用してください。", ephemeral=True)
                return
            
            tracks = []
            is_playlist = False
            playlist_name = None
            
            # Detect URL type or use specified source
            if SPOTIFY_REGEX.match(query):
                # Spotify URL
                tracks, is_playlist, playlist_name = await self.search_spotify(query)
            elif YOUTUBE_REGEX.match(query):
                # YouTube URL
                tracks = await wavelink.Playable.search(query)
                if isinstance(tracks, wavelink.Playlist):
                    is_playlist = True
                    playlist_name = tracks.name
                    tracks = tracks.tracks
            elif SOUNDCLOUD_REGEX.match(query):
                # SoundCloud URL
                tracks = await wavelink.Playable.search(query)
            elif query.startswith(('http://', 'https://')):
                # Other URL
                tracks = await wavelink.Playable.search(query)
            else:
                # Search by source
                if source == "spotify" or (source == "auto" and any(word in query.lower() for word in ['spotify', 'スポティファイ'])):
                    tracks, _, _ = await self.search_spotify(query, search_mode=True)
                elif source == "soundcloud":
                    tracks = await wavelink.Playable.search(f"scsearch:{query}")
                else:
                    # Default: YouTube search
                    if any(word in query.lower() for word in ['リラックス', '作業', '盛り上がる', 'bgm', 'chill', '高音質']):
                        ai_query = await self.ai_music_recommendation(query)
                        tracks = await wavelink.Playable.search(f"ytsearch:{ai_query}")
                    else:
                        tracks = await wavelink.Playable.search(f"ytsearch:{query}")
            
            if not tracks:
                await interaction.followup.send("❌ 曲が見つかりませんでした。", ephemeral=True)
                return
            
            # Handle playlist
            if is_playlist and len(tracks) > 1:
                # Add all tracks to queue
                music_channel = await self.create_music_channel(interaction.guild, interaction.user)
                
                if not interaction.guild.voice_client:
                    vc = await music_channel.connect(cls=wavelink.Player)
                else:
                    vc = interaction.guild.voice_client
                
                queue = self.get_queue(interaction.guild.id)
                
                first_track = tracks[0]
                for track in tracks[1:]:
                    queue.add(track)
                
                if not vc.playing:
                    await vc.play(first_track)
                    queue.current = first_track
                else:
                    queue.add(first_track)
                
                embed = discord.Embed(
                    title="📋 プレイリストを追加しました",
                    description=f"**{playlist_name or 'プレイリスト'}**\n{len(tracks)}曲をキューに追加しました",
                    color=0x1DB954 if 'spotify' in query.lower() else 0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            track = tracks[0] if isinstance(tracks, list) else tracks
            
            # Create playback mode selection view
            view = PlaybackModeView(self, interaction, track)
            
            # Detect source for embed color
            if SPOTIFY_REGEX.match(query) or source == "spotify":
                color = 0x1DB954  # Spotify green
                source_icon = "🟢"
            elif SOUNDCLOUD_REGEX.match(query) or source == "soundcloud":
                color = 0xFF5500  # SoundCloud orange
                source_icon = "🟠"
            else:
                color = 0xFF0000  # YouTube red
                source_icon = "🔴"
            
            embed = discord.Embed(
                title="🎵 再生方法を選択してください",
                description=f"{source_icon} **{track.title}**\n{getattr(track, 'author', 'Unknown Artist')}",
                color=color
            )
            embed.add_field(
                name="📻 Discord VC",
                value="• 低遅延\n• 64-96kbps\n• 全員が同時に聞ける",
                inline=True
            )
            embed.add_field(
                name="🎧 Web高音質",
                value="• 最高音質 (256kbps)\n• Web Audio API\n• 個人専用再生",
                inline=True
            )
            
            if hasattr(track, 'artwork') and track.artwork:
                embed.set_thumbnail(url=track.artwork)
            elif hasattr(track, 'thumb') and track.thumb:
                embed.set_thumbnail(url=track.thumb)
            
            await interaction.followup.send(embed=embed, view=view)
                
        except Exception as e:
            logger.error(f"Error in play command: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ 再生中にエラーが発生しました: {str(e)}", ephemeral=True)
    
    async def search_spotify(self, query: str, search_mode: bool = False) -> tuple:
        """Search or load from Spotify"""
        try:
            is_playlist = False
            playlist_name = None
            
            if search_mode:
                # Search mode: use spsearch
                tracks = await wavelink.Playable.search(f"spsearch:{query}")
                return (tracks if tracks else [], False, None)
            
            # URL mode: detect type
            match = SPOTIFY_REGEX.match(query)
            if match:
                content_type = match.group(3)  # track, album, playlist, artist
                
                if content_type in ['album', 'playlist']:
                    is_playlist = True
                
                # Load via wavelink (LavaSrc handles Spotify)
                result = await wavelink.Playable.search(query)
                
                if isinstance(result, wavelink.Playlist):
                    playlist_name = result.name
                    return (result.tracks, True, playlist_name)
                
                return (result if result else [], is_playlist, playlist_name)
            
            return ([], False, None)
            
        except Exception as e:
            logger.error(f"Error searching Spotify: {e}")
            return ([], False, None)
    
    @app_commands.command(name="skip", description="現在の曲をスキップします")
    async def skip(self, interaction: discord.Interaction):
        """Skip current track"""
        vc = interaction.guild.voice_client
        
        if not vc or not vc.playing:
            await interaction.response.send_message("❌ 再生中の曲がありません。", ephemeral=True)
            return
        
        await vc.stop()
        
        embed = discord.Embed(
            title="⏭️ スキップしました",
            color=0xffaa00
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stop", description="音楽を停止してボットを切断します")
    async def stop(self, interaction: discord.Interaction):
        """Stop music and disconnect"""
        vc = interaction.guild.voice_client
        
        if not vc:
            await interaction.response.send_message("❌ ボイスチャンネルに接続していません。", ephemeral=True)
            return
        
        queue = self.get_queue(interaction.guild.id)
        queue.clear()
        
        await vc.disconnect()
        
        embed = discord.Embed(
            title="⏹️ 音楽を停止しました",
            description="ボイスチャンネルから切断しました",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed)
        
        # Broadcast stop event
        if self.bot.api_server:
            await self.bot.api_server.broadcast_music_event({
                'type': 'music_stopped',
                'guild_id': interaction.guild.id
            })
    
    @app_commands.command(name="queue", description="現在のキューを表示します")
    async def queue_command(self, interaction: discord.Interaction):
        """Show current queue"""
        queue = self.get_queue(interaction.guild.id)
        
        embed = discord.Embed(
            title="🎵 音楽キュー",
            color=0xaa66ff
        )
        
        if queue.current:
            embed.add_field(
                name="🎵 現在再生中",
                value=f"**{queue.current.title}**",
                inline=False
            )
        
        if queue.queue:
            queue_list = []
            for i, track in enumerate(queue.queue[:10], 1):
                queue_list.append(f"{i}. {track.title}")
            
            embed.add_field(
                name="📝 次の曲",
                value="\n".join(queue_list),
                inline=False
            )
            
            if len(queue.queue) > 10:
                embed.add_field(
                    name="📊 統計",
                    value=f"他 {len(queue.queue) - 10} 曲",
                    inline=True
                )
        else:
            embed.add_field(
                name="📝 キュー",
                value="キューは空です",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="recommend", description="AIが会話の流れから音楽を推薦します")
    async def recommend(self, interaction: discord.Interaction):
        """AI music recommendation based on conversation context"""
        await interaction.response.defer()
        
        try:
            # Get recent conversation context
            messages = []
            async for message in interaction.channel.history(limit=10):
                if not message.author.bot:
                    messages.append(f"{message.author.display_name}: {message.content}")
            
            context = "\n".join(reversed(messages))
            
            # Get AI recommendation
            recommendation_query = await self.ai_music_recommendation(
                "会話の流れに合う音楽を推薦して",
                context
            )
            
            # Search and play
            tracks = await wavelink.Playable.search(recommendation_query)
            
            if not tracks:
                await interaction.followup.send("❌ 推薦曲が見つかりませんでした。", ephemeral=True)
                return
            
            # Get or create music channel
            music_channel = await self.create_music_channel(interaction.guild, interaction.user)
            
            # Connect to voice channel
            if not interaction.guild.voice_client:
                vc = await music_channel.connect(cls=wavelink.Player)
            else:
                vc = interaction.guild.voice_client
            
            track = tracks[0]
            queue = self.get_queue(interaction.guild.id)
            
            if not vc.playing:
                await vc.play(track)
                queue.current = track
                
                embed = discord.Embed(
                    title="🤖 AI推薦曲を再生",
                    description=f"**{track.title}**",
                    color=0xff66aa
                )
                embed.add_field(name="推薦理由", value="会話の流れから選曲しました", inline=False)
                embed.add_field(name="検索クエリ", value=recommendation_query, inline=True)
                
                await interaction.followup.send(embed=embed)
            else:
                queue.add(track)
                
                embed = discord.Embed(
                    title="🤖 AI推薦曲をキューに追加",
                    description=f"**{track.title}**",
                    color=0x00ffcc
                )
                embed.add_field(name="推薦理由", value="会話の流れから選曲しました", inline=False)
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in recommend command: {e}")
            await interaction.followup.send("❌ 推薦中にエラーが発生しました。", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """Handle track end event"""
        try:
            player = payload.player
            
            # Ignore if track failed to load or was replaced
            # Only handle FINISHED (normal end) and STOPPED (skip)
            if hasattr(payload, 'reason'):
                reason = str(payload.reason).upper()
                logger.info(f"Track end reason: {reason}")
                if reason in ['LOAD_FAILED', 'CLEANUP', 'REPLACED']:
                    logger.warning(f"Track ended with reason: {reason}, not processing")
                    return
            
            # Check if player is still connected
            if not player or not player.connected:
                return
            
            queue = self.get_queue(player.guild.id)
            
            # Get next track
            next_track = queue.get_next()
            
            if next_track:
                await player.play(next_track)
                
                # Broadcast next track event
                if self.bot.api_server:
                    await self.bot.api_server.broadcast_music_event({
                        'type': 'track_start',
                        'guild_id': player.guild.id,
                        'track': {
                            'title': next_track.title,
                            'author': getattr(next_track, 'author', 'Unknown'),
                            'length': next_track.length,
                            'artwork': getattr(next_track, 'artwork', None),
                            'uri': next_track.uri
                        }
                    })
            else:
                # Queue is empty, wait a bit before disconnecting
                # to avoid disconnecting during track loading
                await asyncio.sleep(2)
                
                # Check again if something is playing
                if player.playing or player.paused:
                    return
                
                logger.info(f"Queue empty, disconnecting from {player.guild.name}")
                await player.disconnect()
                queue.clear()
                
                # Broadcast disconnect event
                if self.bot.api_server:
                    await self.bot.api_server.broadcast_music_event({
                        'type': 'queue_empty_disconnect',
                        'guild_id': player.guild.id
                    })
        
        except Exception as e:
            logger.error(f"Error handling track end: {e}")
    
    async def cleanup_music_channel(self, guild_id: int):
        """Clean up empty music channel"""
        try:
            if guild_id in self.music_channels:
                guild = self.bot.get_guild(guild_id)
                if guild:
                    channel = guild.get_channel(self.music_channels[guild_id])
                    if channel and len(channel.members) <= 1:  # Only bot
                        await channel.delete(reason="Music session ended")
                        await self.bot.database.remove_music_channel(guild_id)
                        del self.music_channels[guild_id]
                        logger.info(f"Cleaned up music channel in {guild.name}")
        except Exception as e:
            logger.error(f"Error cleaning up music channel: {e}")
    
    # Note: Natural language music requests are handled in main.py handle_ai_response
    # to avoid duplicate processing

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))

class PlaybackModeView(discord.ui.View):
    def __init__(self, music_cog, interaction, track):
        super().__init__(timeout=60)
        self.music_cog = music_cog
        self.interaction = interaction
        self.track = track
    
    @discord.ui.button(label="Discord VC", style=discord.ButtonStyle.secondary, emoji="📻")
    async def discord_playback(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Play in Discord VC"""
        await interaction.response.defer()
        
        try:
            # Get or create music channel
            music_channel = await self.music_cog.create_music_channel(interaction.guild, interaction.user)
            
            # Connect to voice channel
            if not interaction.guild.voice_client:
                vc = await music_channel.connect(cls=wavelink.Player)
            else:
                vc = interaction.guild.voice_client
            
            queue = self.music_cog.get_queue(interaction.guild.id)
            
            if not vc.playing:
                await vc.play(self.track)
                queue.current = self.track
                
                embed = discord.Embed(
                    title="📻 Discord VCで再生開始",
                    description=f"**{self.track.title}**",
                    color=0xaa66ff
                )
                embed.add_field(name="音質", value="64-96kbps (低遅延)", inline=True)
                embed.add_field(name="チャンネル", value=f"<#{music_channel.id}>", inline=True)
                
                await interaction.followup.send(embed=embed)
                
                # Broadcast to WebSocket
                if self.music_cog.bot.api_server:
                    await self.music_cog.bot.api_server.broadcast_music_event({
                        'type': 'track_start',
                        'guild_id': interaction.guild.id,
                        'playback_mode': 'discord',
                        'track': {
                            'title': self.track.title,
                            'author': getattr(self.track, 'author', 'Unknown'),
                            'length': self.track.length,
                            'artwork': getattr(self.track, 'artwork', None),
                            'uri': self.track.uri
                        },
                        'requester': interaction.user.display_name
                    })
            else:
                queue.add(self.track)
                embed = discord.Embed(
                    title="📝 Discord VCキューに追加",
                    description=f"**{self.track.title}**",
                    color=0x00ffcc
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in Discord playback: {e}")
            await interaction.followup.send("❌ Discord再生でエラーが発生しました。", ephemeral=True)
        
        self.stop()
    
    @discord.ui.button(label="Web高音質", style=discord.ButtonStyle.primary, emoji="🎧")
    async def web_playback(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Play in Web with high quality"""
        await interaction.response.defer()
        
        try:
            # Get high-quality stream URL
            stream_url = await self.music_cog.get_high_quality_stream(self.track.uri)
            
            if not stream_url:
                await interaction.followup.send("❌ 高音質ストリームの取得に失敗しました。", ephemeral=True)
                return
            
            # Generate AI lyrics if requested
            lyrics = None
            if any(word in self.track.title.lower() for word in ['歌', 'song', 'vocal']):
                lyrics = await self.music_cog.generate_ai_lyrics(self.track.title, self.track.author)
            
            embed = discord.Embed(
                title="🎧 Web高音質再生を開始",
                description=f"**{self.track.title}**\n\nWebダッシュボードで高音質再生が開始されました。",
                color=0x00ffcc
            )
            embed.add_field(name="音質", value="256kbps AAC (最高音質)", inline=True)
            embed.add_field(name="機能", value="• Web Audio API\n• リアルタイムEQ\n• ビジュアライザー", inline=True)
            embed.add_field(name="アクセス", value="[Webダッシュボードを開く](http://localhost:3000/dashboard/music)", inline=False)
            
            await interaction.followup.send(embed=embed)
            
            # Update Discord status
            activity = discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{self.track.title} (Web高音質)"
            )
            await self.music_cog.bot.change_presence(activity=activity)
            
            # Broadcast to WebSocket with stream URL
            if self.music_cog.bot.api_server:
                await self.music_cog.bot.api_server.broadcast_music_event({
                    'type': 'web_playback_start',
                    'guild_id': interaction.guild.id,
                    'playback_mode': 'web',
                    'track': {
                        'title': self.track.title,
                        'author': getattr(self.track, 'author', 'Unknown'),
                        'length': self.track.length,
                        'artwork': getattr(self.track, 'artwork', None),
                        'uri': self.track.uri,
                        'stream_url': stream_url,
                        'lyrics': lyrics
                    },
                    'requester': interaction.user.display_name
                })
                
        except Exception as e:
            logger.error(f"Error in Web playback: {e}")
            await interaction.followup.send("❌ Web再生でエラーが発生しました。", ephemeral=True)
        
        self.stop()
    
    async def on_timeout(self):
        """Handle timeout"""
        for item in self.children:
            item.disabled = True
        
        try:
            await self.interaction.edit_original_response(view=self)
        except:
            pass

# Add methods to MusicPlayer class
async def get_high_quality_stream(self, uri: str) -> Optional[str]:
    """Get high-quality stream URL for web playback"""
    try:
        import yt_dlp
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(uri, download=False)
            if info and 'url' in info:
                return info['url']
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting high-quality stream: {e}")
        return None

async def generate_ai_lyrics(self, title: str, artist: str) -> Optional[List[str]]:
    """Generate AI-predicted lyrics"""
    try:
        prompt = f"""
        曲名: "{title}"
        アーティスト: "{artist}"
        
        上記の楽曲の歌詞を推測して生成してください。
        実際の歌詞ではなく、曲名とアーティストから推測される内容で構いません。
        
        以下の形式で出力してください:
        - 各行を改行で区切る
        - 8-12行程度
        - 日本語の楽曲の場合は日本語で、英語の楽曲の場合は英語で
        """
        
        response = await self.bot.gemini_client.generate_response(
            prompt,
            mode='creative'
        )
        
        if response:
            lyrics = [line.strip() for line in response.split('\n') if line.strip()]
            return lyrics[:12]  # Limit to 12 lines
        
        return None
        
    except Exception as e:
        logger.error(f"Error generating AI lyrics: {e}")
        return None

# Add these methods to the MusicPlayer class
MusicPlayer.get_high_quality_stream = get_high_quality_stream
MusicPlayer.generate_ai_lyrics = generate_ai_lyrics