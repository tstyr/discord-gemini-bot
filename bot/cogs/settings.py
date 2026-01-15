import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="channels", description="AI自動応答が設定されているチャンネル一覧を表示")
    async def channels(self, interaction: discord.Interaction):
        """List channels with AI auto-response enabled"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ この機能を使用するには「サーバー管理」権限が必要です。", ephemeral=True)
            return
        
        try:
            chat_channels = await self.bot.database.get_chat_channels(interaction.guild.id)
            
            if not chat_channels:
                embed = discord.Embed(
                    title="📺 AI自動応答チャンネル",
                    description="現在、AI自動応答が設定されているチャンネルはありません。",
                    color=0xffaa00
                )
            else:
                channel_list = []
                for channel_id in chat_channels:
                    channel = interaction.guild.get_channel(channel_id)
                    if channel:
                        channel_list.append(f"• <#{channel_id}> ({channel.name})")
                    else:
                        channel_list.append(f"• <#{channel_id}> (削除済み)")
                
                embed = discord.Embed(
                    title="📺 AI自動応答チャンネル",
                    description="\n".join(channel_list),
                    color=0x00ffcc
                )
                embed.set_footer(text=f"合計: {len(chat_channels)}個のチャンネル")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f'Error in channels command: {e}')
            await interaction.response.send_message("❌ チャンネル一覧の取得に失敗しました。", ephemeral=True)
    
    @app_commands.command(name="info", description="Botの情報を表示")
    async def info(self, interaction: discord.Interaction):
        """Show bot information"""
        embed = discord.Embed(
            title="🤖 Discord AI Bot",
            description="Gemini APIを使用したAIチャットボット",
            color=0xff66aa
        )
        
        embed.add_field(
            name="📋 利用可能なコマンド",
            value=(
                "`/chat` - AIとチャット\n"
                "`/mode` - AIモード変更\n"
                "`/stats` - 使用統計\n"
                "`/setchannel` - 自動応答設定\n"
                "`/channels` - 設定済みチャンネル一覧\n"
                "`/clear` - 会話履歴クリア"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎯 AIモード",
            value=(
                "**Standard** - 標準的な応答\n"
                "**Creative** - クリエイティブな応答\n"
                "**Coder** - プログラミング専門\n"
                "**Assistant** - フォーマルなアシスタント"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚡ 機能",
            value=(
                "• スラッシュコマンド対応\n"
                "• チャンネル別自動応答\n"
                "• 会話履歴の保持\n"
                "• 使用統計の記録\n"
                "• Webダッシュボード連携"
            ),
            inline=False
        )
        
        embed.set_footer(text="Powered by Google Gemini API")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Settings(bot))