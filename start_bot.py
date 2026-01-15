#!/usr/bin/env python3
"""
Quick start script for the Discord Bot
"""
import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import discord
        import google.generativeai as genai
        import fastapi
        import uvicorn
        import aiosqlite
        print("✅ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r bot/requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_path = Path("bot/.env")
    if env_path.exists():
        print("✅ Environment file found")
        return True
    else:
        print("❌ Environment file not found")
        print("Please create bot/.env with your Discord token and Gemini API key")
        return False

def start_bot():
    """Start the Discord bot"""
    if not check_requirements():
        return False
    
    if not check_env_file():
        return False
    
    print("🚀 Starting Discord Bot...")
    print("📊 Web Dashboard will be available at: http://localhost:8000")
    print("🎵 Music features require Lavalink server (optional)")
    print("💰 Cost optimization is enabled for free tier usage")
    print("\n" + "="*50)
    
    # Change to bot directory and run
    os.chdir("bot")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Bot failed to start: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🤖 Discord Bot with AI & Web Dashboard")
    print("=" * 50)
    start_bot()