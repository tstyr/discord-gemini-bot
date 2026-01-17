#!/usr/bin/env python3
"""
環境変数チェックスクリプト
デプロイ前に必要な環境変数が設定されているか確認します
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_env():
    """環境変数をチェック"""
    print("🔍 環境変数チェック開始...\n")
    
    required_vars = {
        'DISCORD_TOKEN': 'Discordボットトークン',
        'GEMINI_API_KEY': 'Gemini APIキー（AI機能に必須）',
        'DATABASE_URL': 'データベース接続URL',
    }
    
    optional_vars = {
        'LAVALINK_HOST': 'Lavalinkホスト（音楽機能用）',
        'LAVALINK_PORT': 'Lavalinkポート（音楽機能用）',
        'LAVALINK_PASSWORD': 'Lavalinkパスワード（音楽機能用）',
        'LAVALINK_SECURE': 'Lavalink SSL設定（音楽機能用）',
        'SPOTIFY_CLIENT_ID': 'Spotify APIクライアントID（オプション）',
        'SPOTIFY_CLIENT_SECRET': 'Spotify APIシークレット（オプション）',
        'API_HOST': 'APIサーバーホスト',
        'API_PORT': 'APIサーバーポート',
    }
    
    all_ok = True
    
    # 必須環境変数のチェック
    print("📋 必須環境変数:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # トークンは一部のみ表示
            if 'TOKEN' in var or 'KEY' in var or 'SECRET' in var:
                display_value = value[:10] + '...' if len(value) > 10 else value
            else:
                display_value = value[:30] + '...' if len(value) > 30 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: 未設定 - {description}")
            all_ok = False
    
    print("\n📋 オプション環境変数:")
    music_vars_ok = True
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = value[:10] + '...' if len(value) > 10 else value
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ⚠️  {var}: 未設定 - {description}")
            if 'LAVALINK' in var:
                music_vars_ok = False
    
    # 音楽機能の警告
    if not music_vars_ok:
        print("\n⚠️  音楽機能の環境変数が不足しています。")
        print("   音楽を再生するには以下を設定してください:")
        print("   - LAVALINK_HOST=lavalinkv4.serenetia.com")
        print("   - LAVALINK_PORT=443")
        print("   - LAVALINK_PASSWORD=https://dsc.gg/ajidevserver")
        print("   - LAVALINK_SECURE=true")
    
    print("\n" + "="*60)
    if all_ok:
        print("✅ すべての必須環境変数が設定されています！")
        if music_vars_ok:
            print("✅ 音楽機能も利用可能です！")
        else:
            print("⚠️  音楽機能は利用できません（オプション）")
        print("\n🚀 デプロイ準備完了！")
    else:
        print("❌ 必須環境変数が不足しています。")
        print("\n📝 設定方法:")
        print("   1. .envファイルに環境変数を追加")
        print("   2. またはKoyeb/Vercelのダッシュボードで設定")
        print("\n詳細: KOYEB_VERCEL_DEPLOYMENT_FIX.md を参照")
    print("="*60)
    
    return all_ok

if __name__ == '__main__':
    check_env()
