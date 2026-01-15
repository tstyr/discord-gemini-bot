import aiosqlite
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json
from collections import deque

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_PATH', '../shared/bot.db')
        self.user_histories = {}  # In-memory conversation history
        
    async def initialize(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Chat channels table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS chat_channels (
                    id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, channel_id)
                )
            ''')
            
            # AI modes table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ai_modes (
                    id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL UNIQUE,
                    mode TEXT NOT NULL DEFAULT 'standard',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Usage logs table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER,
                    tokens_used REAL NOT NULL,
                    message_type TEXT NOT NULL,
                    ai_mode TEXT DEFAULT 'standard',
                    response_time REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Chat logs table for detailed history
            await db.execute('''
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    username TEXT,
                    channel_name TEXT,
                    guild_name TEXT,
                    tokens_used REAL DEFAULT 0,
                    ai_mode TEXT DEFAULT 'standard',
                    response_time REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    setting_key TEXT NOT NULL,
                    setting_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, setting_key)
                )
            ''')
            
            # Public/Private channels table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS public_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL UNIQUE,
                    creator_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS private_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL UNIQUE,
                    owner_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Music channels table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS music_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL UNIQUE,
                    creator_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def is_chat_channel(self, channel_id: int) -> bool:
        """Check if channel is set for AI auto-response"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT 1 FROM chat_channels WHERE channel_id = ?',
                (channel_id,)
            )
            result = await cursor.fetchone()
            return result is not None
    
    async def add_chat_channel(self, guild_id: int, channel_id: int) -> bool:
        """Add channel for AI auto-response"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT OR IGNORE INTO chat_channels (guild_id, channel_id) VALUES (?, ?)',
                    (guild_id, channel_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error adding chat channel: {e}')
            return False
    
    async def remove_chat_channel(self, guild_id: int, channel_id: int) -> bool:
        """Remove channel from AI auto-response"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'DELETE FROM chat_channels WHERE guild_id = ? AND channel_id = ?',
                    (guild_id, channel_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error removing chat channel: {e}')
            return False
    
    async def get_chat_channels(self, guild_id: int) -> List[int]:
        """Get all chat channels for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT channel_id FROM chat_channels WHERE guild_id = ?',
                (guild_id,)
            )
            results = await cursor.fetchall()
            return [row[0] for row in results]
    
    async def set_ai_mode(self, guild_id: int, mode: str) -> bool:
        """Set AI mode for a guild"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO ai_modes (guild_id, mode, updated_at) 
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (guild_id, mode))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error setting AI mode: {e}')
            return False
    
    async def get_ai_mode(self, guild_id: int) -> str:
        """Get AI mode for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT mode FROM ai_modes WHERE guild_id = ?',
                (guild_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else 'standard'
    
    async def log_usage(self, user_id: int, guild_id: int, tokens_used: float, message_type: str):
        """Log token usage"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO usage_logs (user_id, guild_id, tokens_used, message_type) 
                    VALUES (?, ?, ?, ?)
                ''', (user_id, guild_id, tokens_used, message_type))
                await db.commit()
        except Exception as e:
            logger.error(f'Error logging usage: {e}')
    
    async def get_usage_stats(self, guild_id: Optional[int] = None) -> Dict:
        """Get usage statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            if guild_id:
                # Guild-specific stats
                cursor = await db.execute('''
                    SELECT 
                        COUNT(*) as total_messages,
                        SUM(tokens_used) as total_tokens,
                        AVG(tokens_used) as avg_tokens,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM usage_logs 
                    WHERE guild_id = ?
                ''', (guild_id,))
            else:
                # Global stats
                cursor = await db.execute('''
                    SELECT 
                        COUNT(*) as total_messages,
                        SUM(tokens_used) as total_tokens,
                        AVG(tokens_used) as avg_tokens,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM usage_logs
                ''')
            
            result = await cursor.fetchone()
            return {
                'total_messages': result[0] or 0,
                'total_tokens': result[1] or 0,
                'avg_tokens': result[2] or 0,
                'unique_users': result[3] or 0
            }
    
    async def get_chat_logs(self, guild_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """Get chat logs with detailed information"""
        async with aiosqlite.connect(self.db_path) as db:
            if guild_id:
                cursor = await db.execute('''
                    SELECT 
                        id, user_id, guild_id, channel_id, user_message, ai_response,
                        username, channel_name, guild_name, tokens_used, ai_mode,
                        response_time, created_at
                    FROM chat_logs
                    WHERE guild_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (guild_id, limit))
            else:
                cursor = await db.execute('''
                    SELECT 
                        id, user_id, guild_id, channel_id, user_message, ai_response,
                        username, channel_name, guild_name, tokens_used, ai_mode,
                        response_time, created_at
                    FROM chat_logs
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
            
            results = await cursor.fetchall()
            
            logs = []
            for row in results:
                logs.append({
                    'id': str(row[0]),
                    'user_id': str(row[1]),
                    'guild_id': str(row[2]),
                    'channel_id': str(row[3]) if row[3] else None,
                    'message': row[4] or '',
                    'response': row[5] or '',
                    'username': row[6] or 'Unknown',
                    'channel_name': row[7] or 'unknown',
                    'guild_name': row[8] or 'Unknown',
                    'tokens_used': row[9] or 0,
                    'ai_mode': row[10] or 'standard',
                    'response_time': row[11] or 0,
                    'timestamp': row[12]
                })
            
            return logs

    async def save_chat_log(self, user_id: int, guild_id: int, channel_id: int, 
                           user_message: str, ai_response: str, username: str, 
                           channel_name: str, guild_name: str, tokens_used: float, 
                           ai_mode: str, response_time: float):
        """Save detailed chat log"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO chat_logs (user_id, guild_id, channel_id, user_message, 
                                          ai_response, username, channel_name, guild_name,
                                          tokens_used, ai_mode, response_time) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, guild_id, channel_id, user_message, ai_response, 
                      username, channel_name, guild_name, tokens_used, ai_mode, response_time))
                await db.commit()
                logger.info(f"Saved chat log for user {username} in {guild_name}")
        except Exception as e:
            logger.error(f'Error saving chat log: {e}')

    async def get_chat_users(self) -> List[Dict]:
        """Get all users who have chatted with the bot"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT 
                    user_id,
                    username,
                    COUNT(*) as message_count,
                    SUM(tokens_used) as total_tokens,
                    MAX(created_at) as last_message
                FROM chat_logs
                GROUP BY user_id
                ORDER BY last_message DESC
            ''')
            
            results = await cursor.fetchall()
            
            users = []
            for row in results:
                users.append({
                    'user_id': str(row[0]),
                    'username': row[1] or 'Unknown',
                    'message_count': row[2] or 0,
                    'total_tokens': row[3] or 0,
                    'last_message': row[4]
                })
            
            return users

    async def get_user_chat_history(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get chat history for a specific user"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT 
                    id, user_id, guild_id, channel_id, user_message, ai_response,
                    username, channel_name, guild_name, tokens_used, ai_mode,
                    response_time, created_at
                FROM chat_logs
                WHERE user_id = ?
                ORDER BY created_at ASC
                LIMIT ?
            ''', (user_id, limit))
            
            results = await cursor.fetchall()
            
            messages = []
            for row in results:
                messages.append({
                    'id': str(row[0]),
                    'user_id': str(row[1]),
                    'guild_id': str(row[2]),
                    'channel_id': str(row[3]) if row[3] else None,
                    'message': row[4] or '',
                    'response': row[5] or '',
                    'username': row[6] or 'Unknown',
                    'channel_name': row[7] or 'unknown',
                    'guild_name': row[8] or 'Unknown',
                    'tokens_used': row[9] or 0,
                    'ai_mode': row[10] or 'standard',
                    'response_time': row[11] or 0,
                    'timestamp': row[12]
                })
            
            return messages

    def get_user_history(self, user_id: int) -> List[Dict]:
        """Get user conversation history from memory"""
        if user_id not in self.user_histories:
            self.user_histories[user_id] = deque(maxlen=20)
        return list(self.user_histories[user_id])
    
    async def get_user_history_from_db(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get user conversation history from database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT user_message, ai_response, created_at
                FROM chat_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = await cursor.fetchall()
            
            # Return in chronological order (oldest first)
            history = []
            for row in reversed(results):
                history.append({
                    'user_message': row[0],
                    'ai_response': row[1],
                    'timestamp': row[2]
                })
            
            return history
    
    def update_user_history(self, user_id: int, user_message: str, ai_response: str):
        """Update user conversation history in memory"""
        if user_id not in self.user_histories:
            self.user_histories[user_id] = deque(maxlen=20)
        
        self.user_histories[user_id].append({
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
    async def save_public_channel(self, guild_id: int, channel_id: int, creator_id: int) -> bool:
        """Save public AI channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT OR IGNORE INTO public_channels (guild_id, channel_id, creator_id) VALUES (?, ?, ?)',
                    (guild_id, channel_id, creator_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error saving public channel: {e}')
            return False
    
    async def save_private_channel(self, guild_id: int, channel_id: int, owner_id: int) -> bool:
        """Save private AI channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT OR IGNORE INTO private_channels (guild_id, channel_id, owner_id) VALUES (?, ?, ?)',
                    (guild_id, channel_id, owner_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error saving private channel: {e}')
            return False
    
    async def get_public_channels(self, guild_id: int) -> List[Dict]:
        """Get all public AI channels for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT channel_id, creator_id, created_at FROM public_channels WHERE guild_id = ?',
                (guild_id,)
            )
            results = await cursor.fetchall()
            return [
                {
                    'channel_id': row[0],
                    'creator_id': row[1],
                    'created_at': row[2]
                }
                for row in results
            ]
    
    async def get_private_channels(self, guild_id: int) -> List[Dict]:
        """Get all private AI channels for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT channel_id, owner_id, created_at FROM private_channels WHERE guild_id = ?',
                (guild_id,)
            )
            results = await cursor.fetchall()
            return [
                {
                    'channel_id': row[0],
                    'owner_id': row[1],
                    'created_at': row[2]
                }
                for row in results
            ]
    
    async def remove_public_channel(self, guild_id: int, channel_id: int) -> bool:
        """Remove public AI channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'DELETE FROM public_channels WHERE guild_id = ? AND channel_id = ?',
                    (guild_id, channel_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error removing public channel: {e}')
            return False
    
    async def remove_private_channel(self, guild_id: int, channel_id: int) -> bool:
        """Remove private AI channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'DELETE FROM private_channels WHERE guild_id = ? AND channel_id = ?',
                    (guild_id, channel_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error removing private channel: {e}')
            return False
    
    async def is_private_channel(self, channel_id: int) -> bool:
        """Check if channel is a private AI channel"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT 1 FROM private_channels WHERE channel_id = ?',
                (channel_id,)
            )
            result = await cursor.fetchone()
            return result is not None
    
    async def get_channel_activity(self, guild_id: int) -> List[Dict]:
        """Get channel activity for heatmap"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT 
                    channel_id,
                    COUNT(*) as message_count,
                    MAX(created_at) as last_activity,
                    AVG(tokens_used) as avg_tokens
                FROM usage_logs 
                WHERE guild_id = ? AND created_at > datetime('now', '-24 hours')
                GROUP BY channel_id
                ORDER BY message_count DESC
            ''', (guild_id,))
            
            results = await cursor.fetchall()
            return [
                {
                    'channel_id': row[0],
                    'message_count': row[1],
                    'last_activity': row[2],
                    'avg_tokens': row[3] or 0
                }
                for row in results
            ]
    async def save_music_channel(self, guild_id: int, channel_id: int, creator_id: int) -> bool:
        """Save music channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT OR REPLACE INTO music_channels (guild_id, channel_id, creator_id) VALUES (?, ?, ?)',
                    (guild_id, channel_id, creator_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error saving music channel: {e}')
            return False
    
    async def remove_music_channel(self, guild_id: int) -> bool:
        """Remove music channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'DELETE FROM music_channels WHERE guild_id = ?',
                    (guild_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f'Error removing music channel: {e}')
            return False
    
    async def get_music_channel(self, guild_id: int) -> Optional[int]:
        """Get music channel for guild"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT channel_id FROM music_channels WHERE guild_id = ?',
                (guild_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else None