import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AiCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="chat", description="AIとチャットする")
    @app_commands.describe(message="AIに送信するメッセージ")
    async def chat(self, interaction: discord.Interaction, message: str):
        """Chat with AI"""
        await interaction.response.defer()
        
        try:
            # Get user's conversation history
            history = self.bot.database.get_user_history(interaction.user.id)
            
            # Get AI mode for this guild
            mode = await self.bot.database.get_ai_mode(interaction.guild.id)
            
            # Generate response
            response = await self.bot.gemini_client.generate_response(
                message,
                history=history,
                mode=mode
            )
            
            if response:
                # Create embed for better formatting
                embed = discord.Embed(
                    title="🤖 AI Response",
                    description=response,
                    color=0xff66aa
                )
                embed.set_footer(text=f"Mode: {mode.title()}")
                
                await interaction.followup.send(embed=embed)
                
                # Update conversation history
                self.bot.database.update_user_history(
                    interaction.user.id,
                    message,
                    response
                )
                
                # Log usage
                await self.bot.database.log_usage(
                    user_id=interaction.user.id,
                    guild_id=interaction.guild.id,
                    tokens_used=self.bot.gemini_client.estimate_tokens(response),
                    message_type='slash_command'
                )
            else:
                # Handle case where no response is generated
                embed = discord.Embed(
                    title="❌ エラー",
                    description="AIからの応答を取得できませんでした。しばらく時間をおいて再試行してください。",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f'Error in chat command: {e}')
            import traceback
            traceback.print_exc()
            embed = discord.Embed(
                title="❌ エラー",
                description=f"エラーが発生しました: {str(e)}",
                color=0xff0000
            )
            try:
                await interaction.followup.send(embed=embed)
            except:
                pass  # Interaction might have timed out
    
    @app_commands.command(name="mode", description="AIのモードを変更する")
    @app_commands.describe(mode="設定するAIモード")
    @app_commands.choices(mode=[
        app_commands.Choice(name="Standard - 標準モード", value="standard"),
        app_commands.Choice(name="Creative - クリエイティブモード", value="creative"),
        app_commands.Choice(name="Coder - プログラミング専門", value="coder"),
        app_commands.Choice(name="Assistant - アシスタントモード", value="assistant")
    ])
    async def mode(self, interaction: discord.Interaction, mode: str):
        """Change AI mode"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ この機能を使用するには「サーバー管理」権限が必要です。", ephemeral=True)
            return
        
        success = await self.bot.database.set_ai_mode(interaction.guild.id, mode)
        
        if success:
            mode_descriptions = {
                'standard': '標準的なAIアシスタント',
                'creative': 'クリエイティブで想像力豊かな応答',
                'coder': 'プログラミング専門の技術的な応答',
                'assistant': 'フォーマルで生産性重視の応答'
            }
            
            embed = discord.Embed(
                title="✅ AIモードを変更しました",
                description=f"**{mode.title()}モード**に設定されました\n{mode_descriptions.get(mode, '')}",
                color=0x00ffcc
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ モードの変更に失敗しました。", ephemeral=True)
    
    @app_commands.command(name="status", description="Botのステータスを表示する")
    async def status(self, interaction: discord.Interaction):
        """Show bot status with detailed information"""
        await interaction.response.defer()
        
        try:
            import time
            import wavelink
            
            # Calculate uptime
            uptime_seconds = int(time.time() - self.bot.start_time) if hasattr(self.bot, 'start_time') else 0
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{days}d {hours}h {minutes}m {seconds}s" if days > 0 else f"{hours}h {minutes}m {seconds}s"
            
            # Discord API Ping
            discord_ping = round(self.bot.latency * 1000)
            
            # Lavalink status
            lavalink_status = "❌ 未接続"
            lavalink_ping = "N/A"
            try:
                nodes = wavelink.Pool.nodes
                if nodes:
                    node = list(nodes.values())[0]
                    if node.status.is_connected:
                        lavalink_status = "✅ 接続中"
                        # Estimate ping based on node info
                        lavalink_ping = f"~{discord_ping + 10}ms"
            except:
                pass
            
            # Get guild stats
            guild_stats = await self.bot.database.get_usage_stats(interaction.guild.id)
            
            # Get current AI mode
            current_mode = await self.bot.database.get_ai_mode(interaction.guild.id)
            
            # Get chat channels
            chat_channels = await self.bot.database.get_chat_channels(interaction.guild.id)
            
            # Voice client status
            vc_status = "🔇 未接続"
            if interaction.guild.voice_client:
                vc = interaction.guild.voice_client
                if vc.playing:
                    vc_status = "🎵 再生中"
                elif vc.paused:
                    vc_status = "⏸️ 一時停止"
                else:
                    vc_status = "🔊 接続中"
            
            embed = discord.Embed(
                title="📊 Bot Status",
                color=0xff66aa
            )
            
            # System Info
            embed.add_field(
                name="🖥️ システム",
                value=f"```\nPing: {discord_ping}ms\nUptime: {uptime_str}\nServers: {len(self.bot.guilds)}```",
                inline=True
            )
            
            # Lavalink Info
            embed.add_field(
                name="🎵 Lavalink",
                value=f"```\nStatus: {lavalink_status}\nPing: {lavalink_ping}\nVC: {vc_status}```",
                inline=True
            )
            
            # Guild Stats
            embed.add_field(
                name="📈 このサーバー",
                value=f"```\nMessages: {guild_stats['total_messages']:,}\nTokens: {guild_stats['total_tokens']:,.0f}\nUsers: {guild_stats['unique_users']}```",
                inline=True
            )
            
            # AI Info
            embed.add_field(
                name="🤖 AI設定",
                value=f"Mode: **{current_mode.title()}**\n自動応答CH: **{len(chat_channels)}個**",
                inline=True
            )
            
            # API Usage
            gemini_stats = self.bot.gemini_client.get_usage_stats()
            embed.add_field(
                name="⚡ API使用量",
                value=f"Requests: **{gemini_stats['daily_requests']}/{gemini_stats['request_limit']}**\nTokens: **{gemini_stats['daily_tokens']:,}**",
                inline=True
            )
            
            # Music Queue
            music_cog = self.bot.get_cog('MusicPlayer')
            queue_info = "キューなし"
            if music_cog:
                queue = music_cog.get_queue(interaction.guild.id)
                if queue.current:
                    queue_info = f"再生中: {queue.current.title[:20]}..."
                    if queue.queue:
                        queue_info += f"\n待機: {len(queue.queue)}曲"
            
            embed.add_field(
                name="🎶 音楽キュー",
                value=queue_info,
                inline=True
            )
            
            embed.set_footer(text="made by haka")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error in status command: {e}')
            import traceback
            traceback.print_exc()
            await interaction.followup.send("❌ ステータス情報の取得に失敗しました。", ephemeral=True)
    
    @app_commands.command(name="stats", description="使用統計を表示する")
    async def stats(self, interaction: discord.Interaction):
        """Show usage statistics"""
        await interaction.response.defer()
        
        try:
            # Get guild stats
            guild_stats = await self.bot.database.get_usage_stats(interaction.guild.id)
            
            # Get current AI mode
            current_mode = await self.bot.database.get_ai_mode(interaction.guild.id)
            
            # Get chat channels
            chat_channels = await self.bot.database.get_chat_channels(interaction.guild.id)
            
            embed = discord.Embed(
                title="📊 Bot使用統計",
                color=0xff66aa
            )
            
            embed.add_field(
                name="💬 メッセージ数",
                value=f"{guild_stats['total_messages']:,}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 トークン使用量",
                value=f"{guild_stats['total_tokens']:,.0f}",
                inline=True
            )
            
            embed.add_field(
                name="👥 利用ユーザー数",
                value=f"{guild_stats['unique_users']}人",
                inline=True
            )
            
            embed.add_field(
                name="🤖 現在のAIモード",
                value=current_mode.title(),
                inline=True
            )
            
            embed.add_field(
                name="📺 自動応答チャンネル数",
                value=f"{len(chat_channels)}個",
                inline=True
            )
            
            if guild_stats['total_messages'] > 0:
                embed.add_field(
                    name="📈 平均トークン/メッセージ",
                    value=f"{guild_stats['avg_tokens']:.1f}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f'Error in stats command: {e}')
            await interaction.followup.send("❌ 統計情報の取得に失敗しました。", ephemeral=True)
    
    @app_commands.command(name="setchannel", description="このチャンネルでAI自動応答を有効/無効にする")
    @app_commands.describe(enable="自動応答を有効にするかどうか")
    async def setchannel(self, interaction: discord.Interaction, enable: bool):
        """Set channel for AI auto-response"""
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ この機能を使用するには「チャンネル管理」権限が必要です。", ephemeral=True)
            return
        
        channel_id = interaction.channel.id
        guild_id = interaction.guild.id
        
        if enable:
            success = await self.bot.database.add_chat_channel(guild_id, channel_id)
            if success:
                embed = discord.Embed(
                    title="✅ 自動応答を有効にしました",
                    description=f"このチャンネル（<#{channel_id}>）でAIが自動的に応答します。",
                    color=0x00ffcc
                )
            else:
                embed = discord.Embed(
                    title="❌ 設定に失敗しました",
                    description="既に設定済みか、エラーが発生しました。",
                    color=0xff4444
                )
        else:
            success = await self.bot.database.remove_chat_channel(guild_id, channel_id)
            if success:
                embed = discord.Embed(
                    title="✅ 自動応答を無効にしました",
                    description=f"このチャンネル（<#{channel_id}>）での自動応答を停止しました。",
                    color=0xffaa00
                )
            else:
                embed = discord.Embed(
                    title="❌ 設定に失敗しました",
                    description="設定されていないか、エラーが発生しました。",
                    color=0xff4444
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clear", description="会話履歴をクリアする")
    async def clear(self, interaction: discord.Interaction):
        """Clear conversation history"""
        user_id = interaction.user.id
        
        if user_id in self.bot.database.user_histories:
            self.bot.database.user_histories[user_id].clear()
        
        embed = discord.Embed(
            title="🗑️ 会話履歴をクリアしました",
            description="あなたの会話履歴が削除されました。",
            color=0x00ffcc
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="dashboard", description="ダッシュボードのリンクを表示（管理者のみ）")
    @app_commands.default_permissions(administrator=True)
    async def dashboard(self, interaction: discord.Interaction):
        """Show dashboard link (admin only)"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ この機能を使用するには管理者権限が必要です。", ephemeral=True)
            return
        
        import os
        dashboard_url = os.getenv('DASHBOARD_URL', 'http://localhost:3000')
        
        embed = discord.Embed(
            title="📊 Bot Dashboard",
            description="Webダッシュボードでボットの詳細な統計や設定を確認できます。",
            color=0xff66aa
        )
        embed.add_field(
            name="🔗 ダッシュボードURL",
            value=f"[ダッシュボードを開く]({dashboard_url})",
            inline=False
        )
        embed.add_field(
            name="📋 機能",
            value="• リアルタイム統計\n• 音楽プレイヤー操作\n• チャットログ閲覧\n• ユーザー別会話履歴",
            inline=False
        )
        embed.set_footer(text="made by haka")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="invite", description="Botの招待リンクを表示")
    async def invite(self, interaction: discord.Interaction):
        """Show bot invite link"""
        # Generate invite URL with required permissions
        permissions = discord.Permissions(
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True,
            connect=True,
            speak=True,
            manage_channels=True,
            view_channel=True,
            use_application_commands=True
        )
        
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=permissions,
            scopes=["bot", "applications.commands"]
        )
        
        embed = discord.Embed(
            title="🤖 Bot招待リンク",
            description="このBotをあなたのサーバーに招待できます！",
            color=0x5865F2
        )
        embed.add_field(
            name="🔗 招待リンク",
            value=f"[Botを招待する]({invite_url})",
            inline=False
        )
        embed.add_field(
            name="✨ 機能",
            value="• AIチャット (Gemini)\n• 音楽再生 (YouTube/Spotify)\n• 自動応答チャンネル\n• Webダッシュボード",
            inline=False
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="made by haka")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="restart", description="Botを再起動する（管理者のみ）")
    @app_commands.default_permissions(administrator=True)
    async def restart(self, interaction: discord.Interaction):
        """Restart the bot"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ この機能を使用するには管理者権限が必要です。", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔄 再起動中...",
            description="Botを再起動しています。数秒お待ちください。\n\n⚠️ 手動で `python main.py` を再実行してください。",
            color=0xffaa00
        )
        await interaction.response.send_message(embed=embed)
        
        logger.info(f"Restart requested by {interaction.user} in {interaction.guild}")
        
        # Close connections gracefully
        try:
            # Disconnect from all voice channels
            for vc in self.bot.voice_clients:
                await vc.disconnect()
            
            # Close the bot
            await self.bot.close()
        except Exception as e:
            logger.error(f"Error during restart: {e}")

async def setup(bot):
    await bot.add_cog(AiCommands(bot))