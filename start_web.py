#!/usr/bin/env python3
"""
Quick start script for the Web Dashboard
"""
import os
import sys
import subprocess
from pathlib import Path

def check_node():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js not found")
    print("Please install Node.js from: https://nodejs.org/")
    return False

def check_dependencies():
    """Check if npm dependencies are installed"""
    web_path = Path("web")
    node_modules = web_path / "node_modules"
    
    if node_modules.exists():
        print("✅ Web dependencies are installed")
        return True
    else:
        print("📦 Installing web dependencies...")
        os.chdir("web")
        try:
            subprocess.run(["npm", "install"], check=True, shell=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def start_web():
    """Start the web dashboard"""
    if not check_node():
        return False
    
    if not check_dependencies():
        return False
    
    print("🌐 Starting Web Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:3000")
    print("🔗 Make sure the Discord Bot is running on port 8000")
    print("\n" + "="*50)
    
    # Change to web directory and run
    if not os.getcwd().endswith("web"):
        os.chdir("web")
    
    try:
        subprocess.run(["npm", "run", "dev"], check=True, shell=True)
    except KeyboardInterrupt:
        print("\n🛑 Web dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Web dashboard failed to start: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🌐 Discord Bot Web Dashboard")
    print("=" * 50)
    start_web()