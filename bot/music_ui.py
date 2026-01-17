import discord
from discord.ui import View, Button
import asyncio
import logging

logger = logging.getLogger(__name__)

class MusicPlayerView(View):
    def __init__(self, bot, guild_id, timeout=None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.guild_id = guild_id
        self.message = None
        self.update_task = None
    
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
        
        # Volume
        if vc:
            embed.add_field(name="音量", value=f"🔊 {vc.volume}%", inline=True)
        
        if hasattr(track, 'artwork') and track.artwork:
            embed.set_thumbnail(url=track.artwork)
        
        return embed
    
    async def start_update_loop(self):
        """Start the real-time update loop"""
        self.update_task = asyncio.create_task(self._update_loop())
    
    async def _update_loop(self):
        """Update embed every 5 seconds"""
        try:
            while True:
                await asyncio.sleep(5)
                if self.message:
                    vc = self.get_vc()
                    if not vc or not vc.playing:
                        # Stop updating if not playing
                        break
                    try:
                        await self.message.edit(embed=self.create_embed(), view=self)
                    except discord.NotFound:
                        break
                    except Exception as e:
                        logger.error(f"Error updating music embed: {e}")
                        break
        except asyncio.CancelledError:
            pass
    
    def stop_update(self):
        if self.update_task:
            self.update_task.cancel()
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def restart(self, interaction: discord.Interaction, button: Button):
        """Restart current track"""
        vc = self.get_vc()
        if vc:
            await vc.seek(0)
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary)
    async def pause_resume(self, interaction: discord.Interaction, button: Button):
        """Pause/Resume"""
        vc = self.get_vc()
        if vc:
            if vc.paused:
                await vc.pause(False)
                button.emoji = "⏸️"
            else:
                await vc.pause(True)
                button.emoji = "▶️"
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: Button):
        """Skip track"""
        vc = self.get_vc()
        if vc:
            await vc.stop()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: Button):
        """Stop and disconnect"""
        vc = self.get_vc()
        queue = self.get_queue()
        if vc:
            if queue:
                queue.clear()
            await vc.disconnect()
            self.stop_update()
            
            embed = discord.Embed(
                title="⏹️ 停止しました",
                description="ボイスチャンネルから切断しました",
                color=0xff4444
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary, row=1)
    async def loop(self, interaction: discord.Interaction, button: Button):
        """Toggle loop mode"""
        queue = self.get_queue()
        if queue:
            modes = ["off", "track", "queue"]
            current_idx = modes.index(queue.loop_mode) if queue.loop_mode in modes else 0
            queue.loop_mode = modes[(current_idx + 1) % 3]
            
            mode_text = {"off": "オフ", "track": "1曲リピート", "queue": "全曲リピート"}
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(emoji="🔉", style=discord.ButtonStyle.secondary, row=1)
    async def vol_down(self, interaction: discord.Interaction, button: Button):
        """Volume down"""
        try:
            vc = self.get_vc()
            if vc:
                current_vol = int(vc.volume * 100) if hasattr(vc, 'volume') else 100
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
                current_vol = int(vc.volume * 100) if hasattr(vc, 'volume') else 100
                new_vol = min(100, current_vol + 10)
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
