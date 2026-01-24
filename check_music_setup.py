#!/usr/bin/env python3
"""
音楽機能の設定チェックスクリプト
"""
import os
import sys
import socket
from pathlib import Path

def check_env_vars():
    """環境変数のチェック"""
    print("=" * 60)
    print("🔍 環境変数チェック")
    print("=" * 60)
    
    required_vars = {
        'LAVALINK_HOST': 'localhost',
        'LAVALINK_PORT': '2333',
        'LAVALINK_PASSWORD': 'youshallnotpass',
        'LAVALINK_SECURE': 'false'
    }
    
    env_file = Path('bot/.env')
    if not env_file.exists():
        print("❌ bot/.env ファイルが見つかりません")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    all_ok = True
    for var, default in required_vars.items():
        if var in env_content:
            # Extract value
            for line in env_content.split('\n'):
                if line.startswith(f'{var}='):
                    value = line.split('=', 1)[1].strip()
                    print(f"✅ {var}={value}")
                    break
        else:
            print(f"⚠️  {var} が設定されていません (デフォルト: {default})")
            all_ok = False
    
    return all_ok

def check_lavalink_files():
    """Lavalinkファイルのチェック"""
    print("\n" + "=" * 60)
    print("📁 Lavalinkファイルチェック")
    print("=" * 60)
    
    files = {
        'lavalink/Lavalink.jar': 'Lavalink本体',
        'lavalink/application.yml': '設定ファイル',
        'lavalink/plugins/youtube-plugin-1.11.5.jar': 'YouTubeプラグイン',
        'lavalink/plugins/lavasrc-plugin-4.0.1.jar': 'LavaSrcプラグイン'
    }
    
    all_ok = True
    for file_path, description in files.items():
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            size_mb = size / (1024 * 1024)
            print(f"✅ {description}: {file_path} ({size_mb:.1f} MB)")
        else:
            print(f"❌ {description}: {file_path} が見つかりません")
            all_ok = False
    
    return all_ok

def check_lavalink_config():
    """Lavalink設定のチェック"""
    print("\n" + "=" * 60)
    print("⚙️  Lavalink設定チェック")
    print("=" * 60)
    
    config_file = Path('lavalink/application.yml')
    if not config_file.exists():
        print("❌ application.yml が見つかりません")
        return False
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = f.read()
    
    checks = {
        'youtube: false': 'YouTube旧ソース無効化',
        'ANDROID_TESTSUITE': 'ANDROID_TESTSUITEクライアント',
        'youtube-plugin': 'YouTubeプラグイン設定'
    }
    
    all_ok = True
    for check, description in checks.items():
        if check in config:
            print(f"✅ {description}")
        else:
            print(f"⚠️  {description} が設定されていません")
            all_ok = False
    
    return all_ok

def check_lavalink_connection():
    """Lavalink接続チェック"""
    print("\n" + "=" * 60)
    print("🔌 Lavalink接続チェック")
    print("=" * 60)
    
    host = os.getenv('LAVALINK_HOST', 'localhost')
    port = int(os.getenv('LAVALINK_PORT', '2333'))
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Lavalinkに接続できました ({host}:{port})")
            return True
        else:
            print(f"❌ Lavalinkに接続できません ({host}:{port})")
            print(f"   Lavalinkが起動しているか確認してください")
            return False
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

def check_bot_dependencies():
    """Bot依存関係のチェック"""
    print("\n" + "=" * 60)
    print("📦 Bot依存関係チェック")
    print("=" * 60)
    
    try:
        import wavelink
        print(f"✅ wavelink: {wavelink.__version__}")
    except ImportError:
        print("❌ wavelink がインストールされていません")
        print("   pip install wavelink")
        return False
    
    try:
        import discord
        print(f"✅ discord.py: {discord.__version__}")
    except ImportError:
        print("❌ discord.py がインストールされていません")
        return False
    
    try:
        import yt_dlp
        print(f"✅ yt-dlp: インストール済み")
    except ImportError:
        print("⚠️  yt-dlp がインストールされていません (オプション)")
    
    return True

def main():
    """メイン処理"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "音楽機能セットアップチェック" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # チェック実行
    results.append(("環境変数", check_env_vars()))
    results.append(("Lavalinkファイル", check_lavalink_files()))
    results.append(("Lavalink設定", check_lavalink_config()))
    results.append(("Bot依存関係", check_bot_dependencies()))
    results.append(("Lavalink接続", check_lavalink_connection()))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 チェック結果サマリー")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ OK" if passed else "❌ NG"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 すべてのチェックに合格しました！")
        print("   音楽機能を使用できます。")
    else:
        print("⚠️  いくつかの問題が見つかりました。")
        print("   上記のエラーを修正してください。")
    print("=" * 60)
    
    # 次のステップ
    print("\n📝 次のステップ:")
    if not results[4][1]:  # Lavalink接続失敗
        print("   1. restart_lavalink.bat を実行してLavalinkを起動")
        print("   2. 'Lavalink is ready to accept connections.' を確認")
        print("   3. Botを起動")
    else:
        print("   1. Botを起動: python bot/main.py")
        print("   2. Discordで音楽を再生: 'オーイシマサヨシ流して'")
    
    print()

if __name__ == '__main__':
    main()
