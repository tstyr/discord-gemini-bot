#!/usr/bin/env python3
"""
データベース接続テストスクリプト
"""
import asyncio
import os
from dotenv import load_dotenv
from database_pg import Database

load_dotenv()

async def test_database():
    """データベース接続をテスト"""
    print("🔍 データベース接続テスト開始...\n")
    
    # 環境変数チェック
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL: {database_url[:30]}...")
    else:
        print("⚠️  DATABASE_URL: 未設定（SQLiteを使用）")
    
    print("\n" + "="*60)
    
    # データベース初期化
    db = Database()
    try:
        await db.initialize()
        print("\n✅ データベース初期化成功")
    except Exception as e:
        print(f"\n❌ データベース初期化失敗: {e}")
        return
    
    print("\n" + "="*60)
    
    # テストデータ挿入
    print("\n📝 テストデータを挿入...")
    try:
        await db.save_chat_log(
            user_id=123456789,
            guild_id=987654321,
            channel_id=111222333,
            user_message="テストメッセージ",
            ai_response="テストレスポンス",
            username="TestUser",
            channel_name="test-channel",
            guild_name="Test Guild",
            tokens_used=100.0,
            ai_mode="standard",
            response_time=0.5
        )
        print("✅ テストデータ挿入成功")
    except Exception as e:
        print(f"❌ テストデータ挿入失敗: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*60)
    
    # データ取得テスト
    print("\n📖 データ取得テスト...")
    try:
        logs = await db.get_chat_logs(limit=5)
        print(f"✅ {len(logs)}件のログを取得")
        
        if logs:
            print("\n最新のログ:")
            for i, log in enumerate(logs[:3], 1):
                print(f"\n{i}. {log.get('username', 'Unknown')}")
                print(f"   メッセージ: {log.get('message', '')[:50]}...")
                print(f"   レスポンス: {log.get('response', '')[:50]}...")
                print(f"   トークン: {log.get('tokens_used', 0)}")
        else:
            print("⚠️  ログが見つかりません")
    except Exception as e:
        print(f"❌ データ取得失敗: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*60)
    
    # ユーザー一覧取得
    print("\n👥 ユーザー一覧取得...")
    try:
        users = await db.get_chat_users()
        print(f"✅ {len(users)}人のユーザーを取得")
        
        if users:
            print("\nユーザー一覧:")
            for i, user in enumerate(users[:5], 1):
                print(f"{i}. {user.get('username', 'Unknown')} - {user.get('message_count', 0)}件のメッセージ")
        else:
            print("⚠️  ユーザーが見つかりません")
    except Exception as e:
        print(f"❌ ユーザー取得失敗: {e}")
    
    print("\n" + "="*60)
    print("\n✅ すべてのテスト完了！")
    print("\n📝 次のステップ:")
    print("   1. Discordでメッセージを送信")
    print("   2. Botが返信することを確認")
    print("   3. このスクリプトを再実行してデータが増えているか確認")
    print("   4. Vercelダッシュボードでデータが表示されるか確認")

if __name__ == '__main__':
    asyncio.run(test_database())
