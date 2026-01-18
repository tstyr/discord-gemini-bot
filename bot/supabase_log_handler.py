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
                'scope': scope,
                'timestamp': datetime.utcnow().isoformat()
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
                
        except Exception as e:
            print(f"Error flushing logs to Supabase: {e}")
            # エラーが発生した場合、ログを再度キューに戻す
            for log in reversed(logs_to_send):
                self.log_queue.appendleft(log)
    
    def stop(self):
        """ハンドラーを停止"""
        self.is_running = False
        if self.flush_task:
            self.flush_task.cancel()
    
    async def final_flush(self):
        """最終的なフラッシュ（シャットダウン時）"""
        await self.flush_logs()
