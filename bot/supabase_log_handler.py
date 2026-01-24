"""Supabaseへログを送信するカスタムログハンドラー"""
import logging
import asyncio
from datetime import datetime
from typing import Optional
from collections import deque


class SupabaseLogHandler(logging.Handler):
    """ログをSupabaseに非同期で送信するハンドラー"""
    
    def __init__(self, supabase_client, level=logging.INFO):
        super().__init__(level)
        self.supabase_client = supabase_client
        self.log_queue = deque(maxlen=1000)  # 最大1000件のログをバッファ
        self.is_running = False
        self.flush_task = None
        self.cleanup_counter = 0  # ✅ クリーンアップカウンター
        self.cleanup_interval = 100  # ✅ 100回のフラッシュごとにクリーンアップ
        
    def emit(self, record: logging.LogRecord):
        """ログレコードを受信してキューに追加"""
        try:
            log_entry = self.format(record)
            
            # ログレベルを文字列に変換
            level_name = record.levelname.lower()
            
            # スコープを決定（ロガー名から）
            scope = 'general'
            if 'music' in record.name.lower():
                scope = 'music'
            elif 'ai' in record.name.lower() or 'gemini' in record.name.lower():
                scope = 'ai'
            elif 'database' in record.name.lower():
                scope = 'database'
            elif 'api' in record.name.lower():
                scope = 'api'
            
            # キューに追加
            self.log_queue.append({
                'level': level_name,
                'message': log_entry,
                'scope': scope
                # ✅ recorded_at は削除（Supabaseで自動生成）
            })
            
        except Exception as e:
            # ログハンドラー内でエラーが発生しても、メインプログラムに影響を与えない
            print(f"Error in SupabaseLogHandler: {e}")
    
    async def start_flush_loop(self):
        """定期的にログをSupabaseにフラッシュ"""
        self.is_running = True
        
        while self.is_running:
            try:
                await self.flush_logs()
                await asyncio.sleep(10)  # 10秒ごとにフラッシュ
            except Exception as e:
                print(f"Error in flush loop: {e}")
                await asyncio.sleep(10)
    
    async def flush_logs(self):
        """キューに溜まったログをSupabaseに送信"""
        if not self.log_queue or not self.supabase_client.client:
            return
        
        try:
            # キューから最大100件取得
            logs_to_send = []
            for _ in range(min(100, len(self.log_queue))):
                if self.log_queue:
                    logs_to_send.append(self.log_queue.popleft())
            
            if logs_to_send:
                # バッチでSupabaseに送信
                self.supabase_client.client.table('bot_logs').insert(logs_to_send).execute()
                
                # ✅ クリーンアップカウンターを増やす
                self.cleanup_counter += 1
                
                # ✅ 一定回数ごとにクリーンアップ
                if self.cleanup_counter >= self.cleanup_interval:
                    await self._cleanup_old_logs()
                    self.cleanup_counter = 0
                
        except Exception as e:
            print(f"Error flushing logs to Supabase: {e}")
            # エラーが発生した場合、ログを再度キューに戻す
            for log in reversed(logs_to_send):
                self.log_queue.appendleft(log)
    
    async def _cleanup_old_logs(self):
        """古いログを削除して20万件以下に保つ"""
        try:
            if not self.supabase_client.client:
                return
            
            # レコード数を取得
            count_result = self.supabase_client.client.table('bot_logs')\
                .select('id', count='exact')\
                .execute()
            
            total_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            
            if total_count > 200000:
                # 削除する件数
                delete_count = total_count - 200000
                
                print(f"🗑️ Cleaning up {delete_count} old bot_logs records...")
                
                # 古い順にIDを取得
                old_records = self.supabase_client.client.table('bot_logs')\
                    .select('id')\
                    .order('created_at', desc=False)\
                    .limit(delete_count)\
                    .execute()
                
                if old_records.data:
                    # IDのリストを作成
                    ids_to_delete = [record['id'] for record in old_records.data]
                    
                    # バッチ削除（1000件ずつ）
                    batch_size = 1000
                    for i in range(0, len(ids_to_delete), batch_size):
                        batch = ids_to_delete[i:i + batch_size]
                        self.supabase_client.client.table('bot_logs')\
                            .delete()\
                            .in_('id', batch)\
                            .execute()
                    
                    print(f"✅ Deleted {len(ids_to_delete)} old bot_logs records")
            
        except Exception as e:
            print(f"❌ Failed to cleanup old logs: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """ハンドラーを停止"""
        self.is_running = False
        if self.flush_task:
            self.flush_task.cancel()
    
    async def final_flush(self):
        """最終的なフラッシュ（シャットダウン時）"""
        await self.flush_logs()
