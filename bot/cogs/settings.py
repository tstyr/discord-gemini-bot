import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Settings(commands.Cog):
    """設定関連のコマンド（このCogは非推奨 - 他のCogに統合済み）"""
    def __init__(self, bot):
        self.bot = bot
        logger.warning("⚠️ Settings Cog is deprecated. Commands moved to other cogs.")

async def setup(bot):
    # このCogは読み込まない（コマンドは他のCogに統合済み）
    logger.info("ℹ️ Settings Cog skipped (commands integrated into other cogs)")
    pass