"""One-time script to clear global commands and fix duplicates"""
import asyncio
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

async def clear_global_commands():
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        
        # Clear global commands
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        print('Cleared global commands')
        
        # List remaining commands per guild
        for guild in bot.guilds:
            commands = await bot.tree.fetch_commands(guild=guild)
            print(f'{guild.name}: {len(commands)} commands')
        
        await bot.close()
    
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(clear_global_commands())
