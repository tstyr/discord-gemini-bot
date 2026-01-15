"""Discord Bot with Gemini AI integration."""
import os
import discord
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} is now running!")


@bot.command(name="ask")
async def ask_gemini(ctx, *, question: str):
    """Ask Gemini AI a question."""
    async with ctx.typing():
        try:
            response = model.generate_content(question)
            # Discord message limit is 2000 chars
            answer = response.text[:1900] if len(response.text) > 1900 else response.text
            await ctx.send(answer)
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")


@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency."""
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
