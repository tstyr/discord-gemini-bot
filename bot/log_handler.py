import logging
import asyncio
from typing import Optional

class SocketIOLogHandler(logging.Handler):
    """Socket.IOにログを送信するカスタムハンドラー"""
    
    def __init__(self, sio_manager=None):
        super().__init__()
        self.sio_manager = sio_manager
        self.loop = None
        
    def set_sio_manager(self, sio_manager):
        """Socket.IOマネージャーを設定"""
        self.sio_manager = sio_manager
        
    def emit(self, record):
        """ログレコードを処理してSocket.IOに送信"""
        try:
            if self.sio_manager is None:
                return
                
            log_entry = self.format(record)
            
            # ログレベルに応じた色分け
            level_colors = {
                'DEBUG': 'text-gray-500',
                'INFO': 'text-cyan-400',
                'WARNING': 'text-yellow-400',
                'ERROR': 'text-red-400',
                'CRITICAL': 'text-red-600'
            }
            
            log_data = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'message': record.getMessage(),
                'color': level_colors.get(record.levelname, 'text-white'),
                'module': record.module
            }
            
            # 非同期でSocket.IOに送信
            if self.loop is None:
                try:
                    self.loop = asyncio.get_event_loop()
                except RuntimeError:
                    self.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.loop)
            
            if self.loop and self.sio_manager:
                asyncio.create_task(self.sio_manager.broadcast_log(log_data))
                
        except Exception as e:
            # ログハンドラー内でエラーが発生しても、メインプログラムに影響を与えない
            print(f"Error in SocketIOLogHandler: {e}")
