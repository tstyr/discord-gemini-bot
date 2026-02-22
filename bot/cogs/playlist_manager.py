"""プレイリスト管理機能"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional, List
import wavelink

logger = logging.getLogger(__name__)


class PlaylistManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_user_playlists(self, guild_id: int, user_id: int = None) -> List[dict]:
        """ユーザーまたはギルドのプレイリストを取得"""
        try:
            if not self.bot.supabase_client:
                logger.warning("Supabase client not available")
                return []
            
            # Try to get client, initialize if needed
            if not hasattr(self.bot.supabase_client, 'client') or not self.bot.supabase_client.client:
                logger.info("Initializing Supabase client...")
                await self.bot.supabase_client.initialize()
            
            if not self.bot.supabase_client.client:
                logger.error("Failed to initialize Supabase client")
                return []
            
            query = self.bot.supabase_client.client.table('playlists').select('*')
            
            if user_id:
                # ユーザーのプレイリストまたは公開プレイリスト
                query = query.eq('guild_id', str(guild_id)).or_(
                    f'creator_id.eq.{user_id},is_public.eq.true'
                )
            else:
                # ギルドの全プレイリスト
                query = query.eq('guild_id', str(guild_id))
            
            result = query.order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching playlists: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def create_playlist(self, guild_id: int, name: str, creator_id: int, 
                            creator_name: str, description: str = None, is_public: bool = True) -> Optional[str]:
        """プレイリストを作成"""
        try:
            if not self.bot.supabase_client:
                logger.error("Supabase client not available")
                return None
            
            # Try to get client, initialize if needed
            if not hasattr(self.bot.supabase_client, 'client') or not self.bot.supabase_client.client:
                logger.info("Initializing Supabase client...")
                await self.bot.supabase_client.initialize()
            
            if not self.bot.supabase_client.client:
                logger.error("Failed to initialize Supabase client")
                return None
            
            data = {
                'guild_id': str(guild_id),
                'name': name,
                'description': description,
                'creator_id': str(creator_id),
                'creator_name': creator_name,
                'is_public': is_public
            }
            
            logger.info(f"Creating playlist: {data}")
            result = self.bot.supabase_client.client.table('playlists').insert(data).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Playlist created successfully: {result.data[0]['id']}")
                return result.data[0]['id']
            
            logger.error("No data returned from playlist creation")
            return None
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def add_track_to_playlist(self, playlist_id: str, track_title: str, track_url: str,
                                   track_author: str, duration_ms: int, added_by: str, added_by_id: int) -> bool:
        """プレイリストに曲を追加"""
        try:
            if not self.bot.supabase_client:
                logger.error("Supabase client not available")
                return False
            
            # Try to get client, initialize if needed
            if not hasattr(self.bot.supabase_client, 'client') or not self.bot.supabase_client.client:
                logger.info("Initializing Supabase client...")
                await self.bot.supabase_client.initialize()
            
            if not self.bot.supabase_client.client:
                logger.error("Failed to initialize Supabase client")
                return False
            
            # 現在の曲数を取得してpositionを決定
            count_result = self.bot.supabase_client.client.table('playlist_tracks')\
                .select('id', count='exact')\
                .eq('playlist_id', playlist_id)\
                .execute()
            
            position = len(count_result.data) if count_result.data else 0
            
            data = {
                'playlist_id': playlist_id,
                'track_title': track_title,
                'track_url': track_url,
                'track_author': track_author,
                'duration_ms': duration_ms,
                'added_by': added_by,
                'added_by_id': str(added_by_id),
                'position': position
            }
            
            logger.info(f"Adding track to playlist: {track_title}")
            self.bot.supabase_client.client.table('playlist_tracks').insert(data).execute()
            logger.info("Track added successfully")
            return True
        except Exception as e:
            logger.error(f"Error adding track to playlist: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_playlist_tracks(self, playlist_id: str) -> List[dict]:
        """プレイリストの曲を取得"""
        try:
            if not self.bot.supabase_client:
                logger.warning("Supabase client not available")
                return []
            
            # Try to get client, initialize if needed
            if not hasattr(self.bot.supabase_client, 'client') or not self.bot.supabase_client.client:
                logger.info("Initializing Supabase client...")
                await self.bot.supabase_client.initialize()
            
            if not self.bot.supabase_client.client:
                logger.error("Failed to initialize Supabase client")
                return []
            
            result = self.bot.supabase_client.client.table('playlist_tracks')\
                .select('*')\
                .eq('playlist_id', playlist_id)\
                .order('position')\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching playlist tracks: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def delete_playlist(self, playlist_id: str) -> bool:
        """プレイリストを削除"""
        try:
            if not self.bot.supabase_client:
                logger.error("Supabase client not available")
                return False
            
            # Try to get client, initialize if needed
            if not hasattr(self.bot.supabase_client, 'client') or not self.bot.supabase_client.client:
                logger.info("Initializing Supabase client...")
                await self.bot.supabase_client.initialize()
            
            if not self.bot.supabase_client.client:
                logger.error("Failed to initialize Supabase client")
                return False
            
            self.bot.supabase_client.client.table('playlists').delete().eq('id', playlist_id).execute()
            logger.info(f"Playlist deleted: {playlist_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting playlist: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def delete_track_from_playlist(self, track_id: str) -> bool:
        """プレイリストから曲を削除"""
        try:
            if not self.bot.supabase_client:
                logger.error("Supabase client not available")
                return False
            
            # Try to get client, initialize if needed
            if not hasattr(self.bot.supabase_client, 'client') or not self.bot.supabase_client.client:
                logger.info("Initializing Supabase client...")
                await self.bot.supabase_client.initialize()
            
            if not self.bot.supabase_client.client:
                logger.error("Failed to initialize Supabase client")
                return False
            
            self.bot.supabase_client.client.table('playlist_tracks').delete().eq('id', track_id).execute()
            logger.info(f"Track deleted from playlist: {track_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting track: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @app_commands.command(name="playlist", description="プレイリスト管理")
    @app_commands.describe(
        action="実行するアクション",
        name="プレイリスト名（作成時）",
        description="プレイリストの説明（作成時・オプション）"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="作成 (create)", value="create"),
        app_commands.Choice(name="一覧 (list)", value="list"),
        app_commands.Choice(name="再生 (play)", value="play"),
        app_commands.Choice(name="削除 (delete)", value="delete"),
    ])
    async def playlist_command(self, interaction: discord.Interaction, action: str, 
                              name: Optional[str] = None, description: Optional[str] = None):
        """プレイリスト管理コマンド"""
        await interaction.response.defer()
        
        try:
            if action == "create":
                if not name:
                    await interaction.followup.send("❌ プレイリスト名を指定してください。", ephemeral=True)
                    return
                
                playlist_id = await self.create_playlist(
                    guild_id=interaction.guild.id,
                    name=name,
                    creator_id=interaction.user.id,
                    creator_name=interaction.user.display_name,
                    description=description
                )
                
                if playlist_id:
                    embed = discord.Embed(
                        title="✅ プレイリストを作成しました",
                        description=f"**{name}**",
                        color=0x00ff88
                    )
                    if description:
                        embed.add_field(name="説明", value=description, inline=False)
                    embed.add_field(name="作成者", value=interaction.user.display_name, inline=True)
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ プレイリストの作成に失敗しました。", ephemeral=True)
            
            elif action == "list":
                playlists = await self.get_user_playlists(interaction.guild.id)
                
                if not playlists:
                    await interaction.followup.send("📝 プレイリストがありません。", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title="📋 プレイリスト一覧",
                    description=f"{len(playlists)}個のプレイリスト",
                    color=0xaa66ff
                )
                
                for pl in playlists[:10]:  # 最大10個表示
                    # 曲数を取得
                    tracks = await self.get_playlist_tracks(pl['id'])
                    track_count = len(tracks)
                    
                    value = f"作成者: {pl['creator_name']}\n曲数: {track_count}曲"
                    if pl.get('description'):
                        value += f"\n{pl['description']}"
                    
                    embed.add_field(
                        name=f"🎵 {pl['name']}",
                        value=value,
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
            
            elif action == "play":
                playlists = await self.get_user_playlists(interaction.guild.id)
                
                if not playlists:
                    await interaction.followup.send("📝 プレイリストがありません。", ephemeral=True)
                    return
                
                # プレイリスト選択ビューを表示
                view = PlaylistSelectView(self, interaction, playlists, "play")
                
                embed = discord.Embed(
                    title="🎵 再生するプレイリストを選択",
                    description=f"{len(playlists)}個のプレイリスト",
                    color=0x00ffcc
                )
                
                await interaction.followup.send(embed=embed, view=view)
            
            elif action == "delete":
                playlists = await self.get_user_playlists(interaction.guild.id, interaction.user.id)
                
                # 自分が作成したプレイリストのみ
                my_playlists = [pl for pl in playlists if pl['creator_id'] == str(interaction.user.id)]
                
                if not my_playlists:
                    await interaction.followup.send("📝 削除できるプレイリストがありません。", ephemeral=True)
                    return
                
                # プレイリスト選択ビューを表示
                view = PlaylistSelectView(self, interaction, my_playlists, "delete")
                
                embed = discord.Embed(
                    title="🗑️ 削除するプレイリストを選択",
                    description=f"{len(my_playlists)}個のプレイリスト",
                    color=0xff4444
                )
                
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in playlist command: {e}")
            await interaction.followup.send("❌ エラーが発生しました。", ephemeral=True)


class PlaylistSelectView(discord.ui.View):
    """プレイリスト選択ビュー"""
    def __init__(self, playlist_manager, interaction, playlists, action):
        super().__init__(timeout=60)
        self.playlist_manager = playlist_manager
        self.interaction = interaction
        self.playlists = playlists
        self.action = action
        
        # セレクトメニューを追加
        options = []
        for pl in playlists[:25]:  # 最大25個
            options.append(discord.SelectOption(
                label=pl['name'][:100],
                description=f"作成者: {pl['creator_name']}"[:100],
                value=pl['id']
            ))
        
        select = discord.ui.Select(
            placeholder="プレイリストを選択...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        """プレイリスト選択時のコールバック"""
        await interaction.response.defer()
        
        playlist_id = interaction.data['values'][0]
        playlist = next((pl for pl in self.playlists if pl['id'] == playlist_id), None)
        
        if not playlist:
            await interaction.followup.send("❌ プレイリストが見つかりません。", ephemeral=True)
            return
        
        if self.action == "play":
            await self.play_playlist(interaction, playlist)
        elif self.action == "delete":
            await self.delete_playlist(interaction, playlist)
        
        self.stop()
    
    async def play_playlist(self, interaction: discord.Interaction, playlist: dict):
        """プレイリストを再生"""
        try:
            # 曲を取得
            tracks_data = await self.playlist_manager.get_playlist_tracks(playlist['id'])
            
            if not tracks_data:
                await interaction.followup.send("📝 プレイリストに曲がありません。", ephemeral=True)
                return
            
            # 音楽Cogを取得
            music_cog = self.playlist_manager.bot.get_cog('MusicPlayer')
            if not music_cog:
                await interaction.followup.send("❌ 音楽機能が利用できません。", ephemeral=True)
                return
            
            # ボイスチャンネルに接続
            if not interaction.user.voice:
                await interaction.followup.send("❌ ボイスチャンネルに参加してください。", ephemeral=True)
                return
            
            music_channel = await music_cog.create_music_channel(interaction.guild, interaction.user)
            
            if not interaction.guild.voice_client:
                vc = await music_channel.connect(cls=wavelink.Player)
            else:
                vc = interaction.guild.voice_client
            
            queue = music_cog.get_queue(interaction.guild.id)
            
            # 曲を検索してキューに追加
            added_count = 0
            for track_data in tracks_data:
                try:
                    # URLから曲を取得
                    tracks = await wavelink.Playable.search(track_data['track_url'])
                    if tracks:
                        track = tracks[0] if isinstance(tracks, list) else tracks
                        
                        # リクエスト情報を保存
                        track.extras.requester_name = interaction.user.display_name
                        track.extras.requester_id = interaction.user.id
                        
                        if not vc.playing and added_count == 0:
                            await vc.play(track)
                            queue.current = track
                        else:
                            queue.add(track)
                        
                        added_count += 1
                except Exception as e:
                    logger.error(f"Error loading track: {e}")
                    continue
            
            embed = discord.Embed(
                title="🎵 プレイリストを再生",
                description=f"**{playlist['name']}**\n{added_count}曲をキューに追加しました",
                color=0x00ff88
            )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error playing playlist: {e}")
            await interaction.followup.send("❌ 再生中にエラーが発生しました。", ephemeral=True)
    
    async def delete_playlist(self, interaction: discord.Interaction, playlist: dict):
        """プレイリストを削除"""
        try:
            success = await self.playlist_manager.delete_playlist(playlist['id'])
            
            if success:
                embed = discord.Embed(
                    title="✅ プレイリストを削除しました",
                    description=f"**{playlist['name']}**",
                    color=0xff4444
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("❌ 削除に失敗しました。", ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error deleting playlist: {e}")
            await interaction.followup.send("❌ エラーが発生しました。", ephemeral=True)


async def setup(bot):
    await bot.add_cog(PlaylistManager(bot))



class AddToPlaylistView(discord.ui.View):
    """プレイリストに曲を追加するビュー"""
    def __init__(self, playlist_manager, interaction, playlists, track):
        super().__init__(timeout=60)
        self.playlist_manager = playlist_manager
        self.interaction = interaction
        self.playlists = playlists
        self.track = track
        
        # セレクトメニューを追加
        options = []
        for pl in playlists[:25]:  # 最大25個
            options.append(discord.SelectOption(
                label=pl['name'][:100],
                description=f"作成者: {pl['creator_name']}"[:100],
                value=pl['id']
            ))
        
        select = discord.ui.Select(
            placeholder="プレイリストを選択...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        """プレイリスト選択時のコールバック"""
        await interaction.response.defer()
        
        playlist_id = interaction.data['values'][0]
        playlist = next((pl for pl in self.playlists if pl['id'] == playlist_id), None)
        
        if not playlist:
            await interaction.followup.send("❌ プレイリストが見つかりません。", ephemeral=True)
            return
        
        # 曲を追加
        success = await self.playlist_manager.add_track_to_playlist(
            playlist_id=playlist_id,
            track_title=self.track.title,
            track_url=self.track.uri if hasattr(self.track, 'uri') else '',
            track_author=getattr(self.track, 'author', 'Unknown'),
            duration_ms=self.track.length if hasattr(self.track, 'length') else 0,
            added_by=interaction.user.display_name,
            added_by_id=interaction.user.id
        )
        
        if success:
            embed = discord.Embed(
                title="✅ プレイリストに追加しました",
                description=f"**{self.track.title}**\n→ {playlist['name']}",
                color=0x00ff88
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ 追加に失敗しました。", ephemeral=True)
        
        self.stop()
