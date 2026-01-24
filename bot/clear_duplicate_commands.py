"""重複したスラッシュコマンドをクリアするスクリプト"""
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Botのセットアップ
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print(f'📊 Bot is in {len(bot.guilds)} guilds')
    
    # 1. グローバルコマンドをクリア
    print('\n🗑️ Clearing global commands...')
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    print('✅ Global commands cleared')
    
    # 2. 各ギルドのコマンドをクリア
    print('\n🗑️ Clearing guild-specific commands...')
    for guild in bot.guilds:
        print(f'  - Clearing commands for: {guild.name} ({guild.id})')
        bot.tree.clear_commands(guild=guild)
        try:
            await bot.tree.sync(guild=guild)
            print(f'    ✅ Cleared')
        except Exception as e:
            print(f'    ❌ Error: {e}')
    
    print('\n✅ All commands cleared!')
    print('ℹ️ Botを再起動してコマンドを再登録してください。')
    
    await bot.close()

async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN not found in .env')
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()

if __name__ == '__main__':
    asyncio.run(main())
