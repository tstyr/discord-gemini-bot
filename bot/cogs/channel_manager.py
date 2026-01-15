import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class ChannelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="setup-public-chat", description="AI専用のパブリックチャンネルを作成します")
    async def setup_public_chat(self, interaction: discord.Interaction):
        """Create public AI chat channel"""
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ この機能を使用するには「チャンネル管理」権限が必要です。", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            
            # Create embed for progress
            embed = discord.Embed(
                title="🔧 チャンネルを構築中...",
                description="AI専用のパブリックチャンネルを作成しています",
                color=0xff66aa
            )
            embed.add_field(name="進行状況", value="⏳ カテゴリーを作成中...", inline=False)
            
            await interaction.followup.send(embed=embed)
            
            # Check if AI-CHAT category already exists
            ai_category = discord.utils.get(guild.categories, name="AI-CHAT")
            
            if not ai_category:
                # Create AI-CHAT category
                ai_category = await guild.create_category(
                    name="AI-CHAT",
                    reason="AI Bot専用カテゴリー"
                )
                logger.info(f"Created AI-CHAT category in {guild.name}")
            
            # Update progress
            embed.set_field_at(0, name="進行状況", value="⏳ チャンネルを作成中...", inline=False)
            await interaction.edit_original_response(embed=embed)
            
            # Check if gemini-public channel already exists
            existing_channel = discord.utils.get(guild.text_channels, name="gemini-public")
            
            if existing_channel:
                embed = discord.Embed(
                    title="⚠️ チャンネルが既に存在します",
                    description=f"<#{existing_channel.id}> は既に作成されています。",
                    color=0xffaa00
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            # Create gemini-public channel
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True
                )
            }
            
            channel = await ai_category.create_text_channel(
                name="gemini-public",
                topic="🤖 Gemini AIとの公開チャット - 誰でも参加できます！",
                overwrites=overwrites,
                reason="AI Bot専用パブリックチャンネル"
            )
            
            # Update progress
            embed.set_field_at(0, name="進行状況", value="⏳ データベースに登録中...", inline=False)
            await interaction.edit_original_response(embed=embed)
            
            # Add to database as chat channel
            success = await self.bot.database.add_chat_channel(guild.id, channel.id)
            
            # Save as public channel
            await self.bot.database.save_public_channel(guild.id, channel.id, interaction.user.id)
            
            if success:
                # Create success embed
                embed = discord.Embed(
                    title="✅ 準備完了！",
                    description="AI専用のパブリックチャンネルが正常に作成されました",
                    color=0x00ffcc
                )
                embed.add_field(
                    name="📺 作成されたチャンネル",
                    value=f"<#{channel.id}>",
                    inline=True
                )
                embed.add_field(
                    name="🎯 機能",
                    value="• AI自動応答\n• 全メンバーアクセス可能\n• 会話ログ記録",
                    inline=True
                )
                embed.add_field(
                    name="🚀 使い方",
                    value=f"<#{channel.id}> でメッセージを送信すると、AIが自動的に応答します！",
                    inline=False
                )
                
                # Add diagonal line decoration
                embed.set_footer(text="Powered by Gemini AI", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
                
                await interaction.edit_original_response(embed=embed)
                
                # Send welcome message to the new channel
                welcome_embed = discord.Embed(
                    title="🤖 Gemini AI チャットへようこそ！",
                    description="このチャンネルでは、Gemini AIと自由に会話できます。",
                    color=0xff66aa
                )
                welcome_embed.add_field(
                    name="💬 使い方",
                    value="メッセージを送信するだけで、AIが自動的に応答します！",
                    inline=False
                )
                welcome_embed.add_field(
                    name="🎛️ コマンド",
                    value="`/mode` - AIモードを変更\n`/clear` - 会話履歴をクリア",
                    inline=False
                )
                
                await channel.send(embed=welcome_embed)
                
                logger.info(f"Successfully created public AI channel in {guild.name}")
            else:
                raise Exception("データベースへの登録に失敗しました")
                
        except Exception as e:
            logger.error(f'Error creating public chat channel: {e}')
            
            error_embed = discord.Embed(
                title="❌ エラーが発生しました",
                description=f"チャンネルの作成中にエラーが発生しました: {str(e)}",
                color=0xff4444
            )
            await interaction.edit_original_response(embed=error_embed)
    
    @app_commands.command(name="setup-private-chat", description="あなた専用のプライベートAIチャンネルを作成します")
    async def setup_private_chat(self, interaction: discord.Interaction):
        """Create private AI chat channel for the user"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            user = interaction.user
            
            # Create embed for progress
            embed = discord.Embed(
                title="🔧 プライベートチャンネルを構築中...",
                description=f"{user.display_name}様専用のAIチャンネルを作成しています",
                color=0xaa66ff
            )
            embed.add_field(name="進行状況", value="⏳ カテゴリーを確認中...", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Get or create AI-CHAT category
            ai_category = discord.utils.get(guild.categories, name="AI-CHAT")
            
            if not ai_category:
                ai_category = await guild.create_category(
                    name="AI-CHAT",
                    reason="AI Bot専用カテゴリー"
                )
            
            # Update progress
            embed.set_field_at(0, name="進行状況", value="⏳ 権限を設定中...", inline=False)
            await interaction.edit_original_response(embed=embed)
            
            # Check if user already has a private channel
            channel_name = f"chat-with-{user.display_name.lower().replace(' ', '-')}"
            existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
            
            if existing_channel:
                embed = discord.Embed(
                    title="⚠️ プライベートチャンネルが既に存在します",
                    description=f"あなた専用のチャンネル <#{existing_channel.id}> は既に作成されています。",
                    color=0xffaa00
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            # Create permission overwrites
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False,
                    read_messages=False,
                    send_messages=False
                ),
                user: discord.PermissionOverwrite(
                    view_channel=True,
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True
                )
            }
            
            # Add permissions for administrators
            for role in guild.roles:
                if role.permissions.administrator:
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True,
                        read_messages=True,
                        send_messages=True,
                        read_message_history=True
                    )
            
            # Update progress
            embed.set_field_at(0, name="進行状況", value="⏳ チャンネルを作成中...", inline=False)
            await interaction.edit_original_response(embed=embed)
            
            # Create private channel
            channel = await ai_category.create_text_channel(
                name=channel_name,
                topic=f"🔒 {user.display_name}様専用のプライベートAIチャット",
                overwrites=overwrites,
                reason=f"{user.display_name}専用プライベートチャンネル"
            )
            
            # Update progress
            embed.set_field_at(0, name="進行状況", value="⏳ データベースに登録中...", inline=False)
            await interaction.edit_original_response(embed=embed)
            
            # Add to database as chat channel
            success = await self.bot.database.add_chat_channel(guild.id, channel.id)
            
            # Save as private channel
            await self.bot.database.save_private_channel(guild.id, channel.id, user.id)
            
            if success:
                # Create success embed
                embed = discord.Embed(
                    title="✅ 準備完了！",
                    description="あなた専用のプライベートAIチャンネルが作成されました",
                    color=0x00ffcc
                )
                embed.add_field(
                    name="🔒 プライベートチャンネル",
                    value=f"<#{channel.id}>",
                    inline=True
                )
                embed.add_field(
                    name="👤 アクセス権限",
                    value=f"• {user.mention}\n• サーバー管理者",
                    inline=True
                )
                embed.add_field(
                    name="🎯 機能",
                    value="• AI自動応答\n• 完全プライベート\n• 会話ログ記録",
                    inline=False
                )
                embed.add_field(
                    name="🚀 使い方",
                    value=f"<#{channel.id}> でAIとプライベートに会話できます！",
                    inline=False
                )
                
                embed.set_footer(text="あなただけの秘密の場所です", icon_url=user.avatar.url if user.avatar else None)
                
                await interaction.edit_original_response(embed=embed)
                
                # Send welcome message to the private channel
                welcome_embed = discord.Embed(
                    title=f"🔒 {user.display_name}様専用チャットへようこそ！",
                    description="このチャンネルはあなただけのプライベート空間です。",
                    color=0xaa66ff
                )
                welcome_embed.add_field(
                    name="🤖 プライベートAI",
                    value="ここでの会話は他の人には見えません。安心してAIと対話してください。",
                    inline=False
                )
                welcome_embed.add_field(
                    name="🎛️ 専用機能",
                    value="`/mode` - AIモードを変更\n`/clear` - 会話履歴をクリア\n`/stats` - あなたの使用統計",
                    inline=False
                )
                
                await channel.send(f"{user.mention}", embed=welcome_embed)
                
                logger.info(f"Successfully created private AI channel for {user.display_name} in {guild.name}")
            else:
                raise Exception("データベースへの登録に失敗しました")
                
        except Exception as e:
            logger.error(f'Error creating private chat channel: {e}')
            
            error_embed = discord.Embed(
                title="❌ エラーが発生しました",
                description=f"プライベートチャンネルの作成中にエラーが発生しました: {str(e)}",
                color=0xff4444
            )
            await interaction.edit_original_response(embed=error_embed)
    
    @app_commands.command(name="list-ai-channels", description="AI専用チャンネルの一覧を表示します")
    async def list_ai_channels(self, interaction: discord.Interaction):
        """List all AI channels in the guild"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ この機能を使用するには「サーバー管理」権限が必要です。", ephemeral=True)
            return
        
        try:
            guild_id = interaction.guild.id
            
            # Get all AI channels
            public_channels = await self.bot.database.get_public_channels(guild_id)
            private_channels = await self.bot.database.get_private_channels(guild_id)
            
            embed = discord.Embed(
                title="🤖 AI専用チャンネル一覧",
                description=f"{interaction.guild.name} のAI専用チャンネル",
                color=0xff66aa
            )
            
            # Public channels
            if public_channels:
                public_list = []
                for channel_data in public_channels:
                    channel = interaction.guild.get_channel(channel_data['channel_id'])
                    if channel:
                        public_list.append(f"• <#{channel.id}> ({channel.name})")
                    else:
                        public_list.append(f"• 削除済みチャンネル (ID: {channel_data['channel_id']})")
                
                embed.add_field(
                    name="📺 パブリックチャンネル",
                    value="\n".join(public_list) if public_list else "なし",
                    inline=False
                )
            
            # Private channels
            if private_channels:
                private_list = []
                for channel_data in private_channels:
                    channel = interaction.guild.get_channel(channel_data['channel_id'])
                    user = interaction.guild.get_member(channel_data['owner_id'])
                    
                    if channel and user:
                        private_list.append(f"• <#{channel.id}> - {user.display_name}")
                    elif channel:
                        private_list.append(f"• <#{channel.id}> - 不明なユーザー")
                    else:
                        private_list.append(f"• 削除済みチャンネル - {user.display_name if user else '不明'}")
                
                embed.add_field(
                    name="🔒 プライベートチャンネル",
                    value="\n".join(private_list) if private_list else "なし",
                    inline=False
                )
            
            if not public_channels and not private_channels:
                embed.add_field(
                    name="📝 チャンネルなし",
                    value="まだAI専用チャンネルが作成されていません。\n`/setup-public-chat` または `/setup-private-chat` で作成してください。",
                    inline=False
                )
            
            embed.set_footer(text=f"合計: {len(public_channels) + len(private_channels)} チャンネル")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f'Error listing AI channels: {e}')
            await interaction.response.send_message("❌ チャンネル一覧の取得に失敗しました。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChannelManager(bot))