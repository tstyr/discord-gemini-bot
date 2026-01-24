"""管理者コマンド"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AdminCommands(commands.Cog):
    """管理者用コマンド"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="dbstats", description="データベースの統計情報を表示")
    async def dbstats(self, interaction: discord.Interaction):
        """データベースの統計情報を表示"""
        await interaction.response.defer()
        
        try:
            if not self.bot.supabase_client or not self.bot.supabase_client.client:
                await interaction.followup.send("❌ Supabaseに接続されていません。", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📊 Database Statistics",
                color=0x00ff88,
                timestamp=datetime.utcnow()
            )
            
            # bot_logs
            try:
                logs_count = self.bot.supabase_client.client.table('bot_logs')\
                    .select('id', count='exact')\
                    .execute()
                logs_total = logs_count.count if hasattr(logs_count, 'count') else len(logs_count.data)
                
                # 今日のログ数
                today = datetime.utcnow().date()
                logs_today = self.bot.supabase_client.client.table('bot_logs')\
                    .select('id', count='exact')\
                    .gte('created_at', today.isoformat())\
                    .execute()
                logs_today_count = logs_today.count if hasattr(logs_today, 'count') else len(logs_today.data)
                
                embed.add_field(
                    name="🗂️ Bot Logs",
                    value=f"Total: **{logs_total:,}** / 200,000\nToday: **{logs_today_count:,}**",
                    inline=True
                )
            except Exception as e:
                embed.add_field(name="🗂️ Bot Logs", value=f"Error: {str(e)[:50]}", inline=True)
            
            # lyrics_logs
            try:
                lyrics_count = self.bot.supabase_client.client.table('lyrics_logs')\
                    .select('id', count='exact')\
                    .execute()
                lyrics_total = lyrics_count.count if hasattr(lyrics_count, 'count') else len(lyrics_count.data)
                
                embed.add_field(
                    name="🎤 Lyrics Logs",
                    value=f"Total: **{lyrics_total:,}** / 100,000",
                    inline=True
                )
            except Exception as e:
                embed.add_field(name="🎤 Lyrics Logs", value=f"Error: {str(e)[:50]}", inline=True)
            
            # music_history
            try:
                music_count = self.bot.supabase_client.client.table('music_history')\
                    .select('id', count='exact')\
                    .execute()
                music_total = music_count.count if hasattr(music_count, 'count') else len(music_count.data)
                
                # 今日の再生数
                music_today = self.bot.supabase_client.client.table('music_history')\
                    .select('id', count='exact')\
                    .gte('played_at', today.isoformat())\
                    .execute()
                music_today_count = music_today.count if hasattr(music_today, 'count') else len(music_today.data)
                
                embed.add_field(
                    name="🎵 Music History",
                    value=f"Total: **{music_total:,}**\nToday: **{music_today_count:,}**",
                    inline=True
                )
            except Exception as e:
                embed.add_field(name="🎵 Music History", value=f"Error: {str(e)[:50]}", inline=True)
            
            # conversation_logs
            try:
                conv_count = self.bot.supabase_client.client.table('conversation_logs')\
                    .select('id', count='exact')\
                    .execute()
                conv_total = conv_count.count if hasattr(conv_count, 'count') else len(conv_count.data)
                
                # 今日の会話数
                conv_today = self.bot.supabase_client.client.table('conversation_logs')\
                    .select('id', count='exact')\
                    .gte('created_at', today.isoformat())\
                    .execute()
                conv_today_count = conv_today.count if hasattr(conv_today, 'count') else len(conv_today.data)
                
                embed.add_field(
                    name="💬 Conversations",
                    value=f"Total: **{conv_total:,}**\nToday: **{conv_today_count:,}**",
                    inline=True
                )
            except Exception as e:
                embed.add_field(name="💬 Conversations", value=f"Error: {str(e)[:50]}", inline=True)
            
            # gemini_usage
            try:
                gemini_count = self.bot.supabase_client.client.table('gemini_usage')\
                    .select('id', count='exact')\
                    .execute()
                gemini_total = gemini_count.count if hasattr(gemini_count, 'count') else len(gemini_count.data)
                
                # 今日のトークン使用量
                gemini_today = self.bot.supabase_client.client.table('gemini_usage')\
                    .select('total_tokens')\
                    .gte('created_at', today.isoformat())\
                    .execute()
                tokens_today = sum(row['total_tokens'] for row in gemini_today.data) if gemini_today.data else 0
                
                embed.add_field(
                    name="🤖 Gemini Usage",
                    value=f"Requests: **{gemini_total:,}**\nTokens Today: **{tokens_today:,}**",
                    inline=True
                )
            except Exception as e:
                embed.add_field(name="🤖 Gemini Usage", value=f"Error: {str(e)[:50]}", inline=True)
            
            # system_stats
            try:
                stats_count = self.bot.supabase_client.client.table('system_stats')\
                    .select('id', count='exact')\
                    .execute()
                stats_total = stats_count.count if hasattr(stats_count, 'count') else len(stats_count.data)
                
                embed.add_field(
                    name="📈 System Stats",
                    value=f"Total: **{stats_total:,}**",
                    inline=True
                )
            except Exception as e:
                embed.add_field(name="📈 System Stats", value=f"Error: {str(e)[:50]}", inline=True)
            
            embed.set_footer(text="Auto-cleanup: bot_logs (200k), lyrics_logs (100k)")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in dbstats command: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ エラーが発生しました: {str(e)}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
