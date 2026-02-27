import discord
from discord.ui import View, Button
import asyncio
import logging
import wavelink

logger = logging.getLogger(__name__)

class MusicPlayerView(View):
    def __init__(self, bot, guild_id, timeout=None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.guild_id = guild_id
        self.message = None
        self.update_task = None
        
        # Note: ボタンの初期状態は __init__ 後に設定される
        # _update_lyrics_button_state() は後で呼ぶ
    
    def _update_lyrics_button_state(self):
        """歌詞ボタンの状態を更新"""
        try:
            lyrics_cog = self.bot.get_cog('LyricsStreamer')
            if lyrics_cog:
                is_enabled = lyrics_cog.lyrics_enabled.get(self.guild_id, False)
                
                # 歌詞ボタンを探して更新
                for item in self.children:
                    if hasattr(item, 'callback') and item.callback.__name__ == 'toggle_lyrics':
                        if is_enabled:
                            item.style = discord.ButtonStyle.success
                            item.label = "歌詞 ON"
                        else:
                            item.style = discord.ButtonStyle.secondary
                            item.label = "歌詞"
                        break
        except Exception as e:
            logger.error(f"Error updating lyrics button state: {e}")
    
    def get_music_cog(self):
        return self.bot.get_cog('MusicPlayer')
    
    def get_vc(self):
        guild = self.bot.get_guild(self.guild_id)
        return guild.voice_client if guild else None
    
    def get_queue(self):
        music_cog = self.get_music_cog()
        return music_cog.get_queue(self.guild_id) if music_cog else None
    
    def create_embed(self):
        queue = self.get_queue()
        vc = self.get_vc()
        
        if not queue or not queue.current:
            embed = discord.Embed(
                title="🎵 音楽プレイヤー",
                description="再生中の曲はありません",
                color=0x666666
            )
            return embed
        
        track = queue.current
        
        # Get position
        position = (vc.position // 1000) if vc else 0
        duration = track.length // 1000
        pos_min, pos_sec = divmod(position, 60)
        dur_min, dur_sec = divmod(duration, 60)
        
        # Progress bar
        progress = int((position / duration) * 20) if duration > 0 else 0
        bar = "▓" * progress + "░" * (20 - progress)
        
        # Status
        if vc and vc.paused:
            status = "⏸️ 一時停止中"
            color = 0xffaa00
        elif vc and vc.playing:
            status = "▶️ 再生中"
            color = 0x00ff88
        else:
            status = "⏹️ 停止"
            color = 0xff4444
        
        embed = discord.Embed(
            title=f"{status}",
            description=f"**{track.title}**\n{getattr(track, 'author', 'Unknown Artist')}",
            color=color
        )
        
        embed.add_field(
            name="再生位置",
            value=f"`{pos_min:02d}:{pos_sec:02d}` {bar} `{dur_min:02d}:{dur_sec:02d}`",
            inline=False
        )
        
        # Queue info
        if queue.queue:
            next_tracks = [f"{i}. {t.title[:30]}..." if len(t.title) > 30 else f"{i}. {t.title}" 
                         for i, t in enumerate(queue.queue[:5], 1)]
            queue_text = "\n".join(next_tracks)
            if len(queue.queue) > 5:
                queue_text += f"\n... 他 {len(queue.queue) - 5} 曲"
            embed.add_field(name=f"📝 キュー ({len(queue.queue)}曲)", value=queue_text, inline=False)
        
        # Loop mode
        loop_icons = {"off": "➡️", "track": "🔂", "queue": "🔁"}
        embed.add_field(name="ループ", value=loop_icons.get(queue.loop_mode, "➡️"), inline=True)
        
        # Volume (Wavelinkは0-1000なので10で割る)
        if vc:
            volume_percent = int(vc.volume / 10)
            embed.add_field(name="音量", value=f"🔊 {volume_percent}%", inline=True)
        
        if hasattr(track, 'artwork') and track.artwork:
            embed.set_thumbnail(url=track.artwork)
        
        return embed
    
    async def start_update_loop(self):
        """Start the real-time update loop"""
        self.update_task = asyncio.create_task(self._update_loop())
    
    async def _update_loop(self):
        """Update embed every 5 seconds and sync with Supabase"""
        try:
            while True:
                await asyncio.sleep(5)
                if self.message:
                    vc = self.get_vc()
                    queue = self.get_queue()
                    
                    # Continue loop if playing OR paused
                    if not vc or not (vc.playing or vc.paused):
                        logger.info("Stopping update loop: not playing or paused")
                        break
                    
                    try:
                        # Update Discord embed
                        await self.message.edit(embed=self.create_embed(), view=self)
                        
                        # ✅ Update Supabase active_sessions with current position
                        if queue and queue.current and hasattr(self.bot, 'supabase_client'):
                            voice_channel = vc.channel
                            members_count = len(voice_channel.members) - 1 if voice_channel else 0
                            
                            track_data = {
                                'title': queue.current.title,
                                'author': getattr(queue.current, 'author', 'Unknown'),
                                'duration': queue.current.length,
                                'position': vc.position,  # ✅ 現在の再生位置（ミリ秒）
                                'is_playing': vc.playing and not vc.paused,
                                'members_count': members_count
                            }
                            
                            await self.bot.supabase_client.update_active_session(
                                self.guild_id,
                                track_data
                            )
                            logger.debug(f"📊 Updated position: {vc.position}ms for guild {self.guild_id}")
                            
                    except discord.NotFound:
                        logger.info("Message not found, stopping update loop")
                        break
                    except discord.HTTPException as e:
                        logger.warning(f"HTTP error updating music embed: {e}")
                        # Don't break on HTTP errors, continue trying
                    except Exception as e:
                        logger.error(f"Error updating music embed: {e}")
                        break
        except asyncio.CancelledError:
            logger.info("Update loop cancelled")
            pass
    
    def stop_update(self):
        if self.update_task:
            self.update_task.cancel()
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def restart(self, interaction: discord.Interaction, button: Button):
        """Restart current track"""
        try:
            vc = self.get_vc()
            if vc and (vc.playing or vc.paused):
                await vc.seek(0)
                try:
                    await interaction.response.edit_message(embed=self.create_embed(), view=self)
                except discord.InteractionResponded:
                    await interaction.followup.send("⏮️ 最初から再生します", ephemeral=True)
            else:
                await interaction.response.send_message("❌ 再生中の曲がありません", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in restart button: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ エラーが発生しました", ephemeral=True)
                else:
                    await interaction.followup.send("❌ エラーが発生しました", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary)
    async def pause_resume(self, interaction: discord.Interaction, button: Button):
        """Pause/Resume"""
        try:
            vc = self.get_vc()
            if vc and (vc.playing or vc.paused):
                if vc.paused:
                    await vc.pause(False)
                    button.emoji = "⏸️"
                else:
                    await vc.pause(True)
                    button.emoji = "▶️"
                try:
                    await interaction.response.edit_message(embed=self.create_embed(), view=self)
                except discord.InteractionResponded:
                    status = "再開" if not vc.paused else "一時停止"
                    await interaction.followup.send(f"⏸️ {status}しました", ephemeral=True)
            else:
                await interaction.response.send_message("❌ 再生中の曲がありません", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in pause_resume button: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ エラーが発生しました", ephemeral=True)
                else:
                    await interaction.followup.send("❌ エラーが発生しました", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: Button):
        """Skip track - force skip even in loop mode"""
        try:
            vc = self.get_vc()
            queue = self.get_queue()
            
            if not vc or not (vc.playing or vc.paused):
                await interaction.response.send_message("❌ 再生中の曲がありません", ephemeral=True)
                return
            
            # Acknowledge the interaction first
            await interaction.response.defer()
            
            # Get next track with force_skip=True to bypass loop mode
            next_track = queue.get_next(force_skip=True)
            
            if next_track:
                # Play next track with error handling
                try:
                    await vc.play(next_track)
                    logger.info(f"Skipped to: {next_track.title}")
                except wavelink.exceptions.LavalinkException as e:
                    logger.error(f"Lavalink error during skip: {e}")
                    if "404" in str(e) or "session" in str(e).lower():
                        logger.warning("Lavalink session lost during skip, attempting to reconnect...")
                        try:
                            # Get music channel
                            music_cog = self.bot.get_cog('MusicPlayer')
                            if music_cog and vc.channel:
                                await vc.disconnect(force=True)
                                await asyncio.sleep(1)
                                vc = await vc.channel.connect(cls=wavelink.Player, timeout=15.0)
                                logger.info("Reconnected to voice channel")
                                await vc.play(next_track)
                                logger.info(f"Skipped to: {next_track.title} after reconnect")
                            else:
                                raise Exception("Could not reconnect to voice channel")
                        except Exception as reconnect_error:
                            logger.error(f"Failed to reconnect: {reconnect_error}")
                            await interaction.followup.send("❌ Lavalinkサーバーとの接続が切れました。もう一度お試しください。", ephemeral=True)
                            return
                    else:
                        raise
                
                # Wait a bit for the track to start
                await asyncio.sleep(0.3)
                
                # Update the message
                try:
                    await interaction.edit_original_response(embed=self.create_embed(), view=self)
                except Exception as e:
                    logger.warning(f"Could not update message after skip: {e}")
            else:
                # No more tracks, stop playback
                await vc.stop()
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="⏹️ キューが空です",
                        description="再生を停止しました",
                        color=0xff4444
                    ),
                    view=None
                )
                
        except Exception as e:
            logger.error(f"Error in skip button: {e}")
            import traceback
            logger.error(traceback.format_exc())
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ スキップ中にエラーが発生しました", ephemeral=True)
                else:
                    await interaction.followup.send("❌ スキップ中にエラーが発生しました", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: Button):
        """Stop and disconnect"""
        try:
            vc = self.get_vc()
            queue = self.get_queue()
            
            if not vc:
                await interaction.response.send_message("❌ ボイスチャンネルに接続していません", ephemeral=True)
                return
            
            if queue:
                queue.clear()
            await vc.disconnect()
            self.stop_update()
            
            embed = discord.Embed(
                title="⏹️ 停止しました",
                description="ボイスチャンネルから切断しました",
                color=0xff4444
            )
            try:
                await interaction.response.edit_message(embed=embed, view=None)
            except discord.InteractionResponded:
                await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in stop button: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ エラーが発生しました", ephemeral=True)
                else:
                    await interaction.followup.send("❌ エラーが発生しました", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary, row=1)
    async def loop(self, interaction: discord.Interaction, button: Button):
        """Toggle loop mode"""
        try:
            queue = self.get_queue()
            vc = self.get_vc()
            
            if not queue:
                await interaction.response.send_message("❌ キューが見つかりません", ephemeral=True)
                return
            
            if not vc or not vc.playing:
                await interaction.response.send_message("❌ 再生中の曲がありません", ephemeral=True)
                return
            
            # ループモードを切り替え
            modes = ["off", "track", "queue"]
            current_idx = modes.index(queue.loop_mode) if queue.loop_mode in modes else 0
            queue.loop_mode = modes[(current_idx + 1) % 3]
            
            mode_text = {"off": "➡️ オフ", "track": "🔂 1曲リピート", "queue": "🔁 全曲リピート"}
            
            # Embedを更新
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
            
            # ループモード変更を通知
            await interaction.followup.send(
                f"ループモード: {mode_text.get(queue.loop_mode, '➡️ オフ')}",
                ephemeral=True
            )
            
            logger.info(f"Loop mode changed to: {queue.loop_mode}")
            
        except Exception as e:
            logger.error(f"Error in loop button: {e}")
            import traceback
            traceback.print_exc()
            try:
                await interaction.response.send_message("❌ エラーが発生しました", ephemeral=True)
            except:
                await interaction.followup.send("❌ エラーが発生しました", ephemeral=True)
    
    @discord.ui.button(emoji="🔉", style=discord.ButtonStyle.secondary, row=1)
    async def vol_down(self, interaction: discord.Interaction, button: Button):
        """Volume down"""
        try:
            vc = self.get_vc()
            if vc:
                # Wavelinkのvolumeは0-1000の範囲
                current_vol = vc.volume if hasattr(vc, 'volume') else 100
                new_vol = max(0, current_vol - 10)
                await vc.set_volume(new_vol)
                await interaction.response.edit_message(embed=self.create_embed(), view=self)
            else:
                await interaction.response.send_message("❌ ボイスチャンネルに接続していません", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in vol_down: {e}")
            await interaction.response.defer()
    
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.secondary, row=1)
    async def vol_up(self, interaction: discord.Interaction, button: Button):
        """Volume up"""
        try:
            vc = self.get_vc()
            if vc:
                # Wavelinkのvolumeは0-1000の範囲
                current_vol = vc.volume if hasattr(vc, 'volume') else 100
                new_vol = min(1000, current_vol + 10)
                await vc.set_volume(new_vol)
                await interaction.response.edit_message(embed=self.create_embed(), view=self)
            else:
                await interaction.response.send_message("❌ ボイスチャンネルに接続していません", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in vol_up: {e}")
            await interaction.response.defer()
    
    @discord.ui.button(emoji="🔄", style=discord.ButtonStyle.secondary, row=1)
    async def refresh(self, interaction: discord.Interaction, button: Button):
        """Refresh display"""
        await interaction.response.edit_message(embed=self.create_embed(), view=self)
    
    @discord.ui.button(emoji="➕", label="プレイリストへ追加", style=discord.ButtonStyle.success, row=2)
    async def add_to_playlist(self, interaction: discord.Interaction, button: Button):
        """現在の曲をプレイリストに追加"""
        try:
            queue = self.get_queue()
            if not queue or not queue.current:
                await interaction.response.send_message("❌ 再生中の曲がありません", ephemeral=True)
                return
            
            # プレイリスト管理Cogを取得
            playlist_manager = self.bot.get_cog('PlaylistManager')
            if not playlist_manager:
                await interaction.response.send_message("❌ プレイリスト機能が利用できません", ephemeral=True)
                return
            
            # プレイリスト一覧を取得
            playlists = await playlist_manager.get_user_playlists(self.guild_id, interaction.user.id)
            
            if not playlists:
                # プレイリストがない場合は作成を促す
                await interaction.response.send_message(
                    "📝 プレイリストがありません。\n`/playlist create` で作成してください。",
                    ephemeral=True
                )
                return
            
            # プレイリスト選択ビューを表示
            from cogs.playlist_manager import AddToPlaylistView
            view = AddToPlaylistView(playlist_manager, interaction, playlists, queue.current)
            
            embed = discord.Embed(
                title="➕ プレイリストに追加",
                description=f"**{queue.current.title}**\n追加先のプレイリストを選択してください",
                color=0x00ff88
            )
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in add_to_playlist: {e}")
            await interaction.response.send_message("❌ エラーが発生しました", ephemeral=True)
    
    @discord.ui.button(emoji="🎤", label="歌詞", style=discord.ButtonStyle.secondary, row=2)
    async def toggle_lyrics(self, interaction: discord.Interaction, button: Button):
        """歌詞配信のON/OFF切り替え"""
        try:
            # 歌詞配信Cogを取得
            lyrics_cog = self.bot.get_cog('LyricsStreamer')
            if not lyrics_cog:
                await interaction.response.send_message("❌ 歌詞機能が利用できません", ephemeral=True)
                return
            
            # 現在の状態を取得
            is_enabled = lyrics_cog.lyrics_enabled.get(self.guild_id, False)
            
            if is_enabled:
                # OFFにする
                lyrics_cog.lyrics_enabled[self.guild_id] = False
                await lyrics_cog.stop_lyrics_for_guild(self.guild_id)
                
                embed = discord.Embed(
                    title="⏹️ 歌詞配信を無効化しました",
                    color=0xff4444
                )
                button.style = discord.ButtonStyle.secondary
                button.label = "歌詞"
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await interaction.message.edit(view=self)
            else:
                # ONにする
                await interaction.response.defer(ephemeral=True)
                
                # チャンネルを作成または取得
                guild = self.bot.get_guild(self.guild_id)
                channel = await lyrics_cog.get_or_create_lyrics_channel(guild)
                if not channel:
                    await interaction.followup.send("❌ 歌詞チャンネルの作成に失敗しました。", ephemeral=True)
                    return
                
                # Webhookを作成または取得
                webhook = await lyrics_cog.get_or_create_webhook(guild, channel)
                if not webhook:
                    await interaction.followup.send("❌ Webhookの作成に失敗しました。", ephemeral=True)
                    return
                
                # 有効化
                lyrics_cog.lyrics_enabled[self.guild_id] = True
                
                # 現在再生中の曲の歌詞を開始
                queue = self.get_queue()
                if queue and queue.current:
                    await lyrics_cog.start_lyrics_for_track(self.guild_id, queue.current)
                
                embed = discord.Embed(
                    title="✅ 歌詞配信を有効化しました",
                    description=f"歌詞は {channel.mention} にリアルタイムで配信されます。",
                    color=0x00ff88
                )
                embed.add_field(name="精度", value="0.1秒間隔", inline=True)
                embed.add_field(name="オフセット", value="0.5秒早め", inline=True)
                
                button.style = discord.ButtonStyle.success
                button.label = "歌詞 ON"
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                await interaction.message.edit(view=self)
        
        except Exception as e:
            logger.error(f"Error in toggle_lyrics: {e}")
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send("❌ エラーが発生しました", ephemeral=True)
            except:
                await interaction.response.send_message("❌ エラーが発生しました", ephemeral=True)
