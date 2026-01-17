import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from collections import deque
import asyncpg

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.pool = None
        self.user_histories = {}
        
    async def initialize(self):
        """Initialize database connection pool and tables"""
        if self.database_url:
            # PostgreSQL (Supabase/Railway)
            try:
                logger.info(f"🔌 Connecting to PostgreSQL database...")
                self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=10)
                await self._create_tables_pg()
                logger.info("✅ PostgreSQL database initialized successfully")
                
                # Test connection
                async with self.pool.acquire() as conn:
                    result = await conn.fetchval('SELECT 1')
                    logger.info(f"✅ Database connection test: {result}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize PostgreSQL: {e}")
                logger.warning("⚠️  Falling back to SQLite...")
                self.pool = None
                import aiosqlite
                self.db_path = os.getenv('DATABASE_PATH', 'bot.db')
                await self._create_tables_sqlite()
                logger.info("✅ SQLite database initialized (fallback)")
        else:
            logger.warning("⚠️  DATABASE_URL not set, using SQLite fallback")
            # Fallback to SQLite
            import aiosqlite
            self.db_path = os.getenv('DATABASE_PATH', 'bot.db')
            await self._create_tables_sqlite()
            logger.info("✅ SQLite database initialized")
    
    async def _create_tables_pg(self):
        """Create PostgreSQL tables"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_channels (
                    id SERIAL PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, channel_id)
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS ai_modes (
                    id SERIAL PRIMARY KEY,
                    guild_id BIGINT NOT NULL UNIQUE,
                    mode TEXT NOT NULL DEFAULT 'standard',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT,
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
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    tokens_used REAL NOT NULL,
                    message_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS music_channels (
                    id SERIAL PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL UNIQUE,
                    creator_id BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    async def _create_tables_sqlite(self):
        """Create SQLite tables (fallback)"""
        import aiosqlite
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS chat_channels (
                    id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, channel_id)
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ai_modes (
                    id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL UNIQUE,
                    mode TEXT NOT NULL DEFAULT 'standard',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER,
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
            await db.execute('''
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    tokens_used REAL NOT NULL,
                    message_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()
    
    async def _execute(self, query: str, *args):
        """Execute query with PostgreSQL or SQLite"""
        if self.pool:
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        else:
            import aiosqlite
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(query, args)
                await db.commit()
    
    async def _fetchone(self, query: str, *args):
        """Fetch one row"""
        if self.pool:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        else:
            import aiosqlite
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, args)
                return await cursor.fetchone()
    
    async def _fetchall(self, query: str, *args):
        """Fetch all rows"""
        if self.pool:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        else:
            import aiosqlite
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, args)
                return await cursor.fetchall()
    
    async def is_chat_channel(self, channel_id: int) -> bool:
        if self.pool:
            row = await self._fetchone('SELECT 1 FROM chat_channels WHERE channel_id = $1', channel_id)
        else:
            row = await self._fetchone('SELECT 1 FROM chat_channels WHERE channel_id = ?', channel_id)
        return row is not None
    
    async def add_chat_channel(self, guild_id: int, channel_id: int) -> bool:
        try:
            if self.pool:
                await self._execute(
                    'INSERT INTO chat_channels (guild_id, channel_id) VALUES ($1, $2) ON CONFLICT DO NOTHING',
                    guild_id, channel_id
                )
            else:
                await self._execute(
                    'INSERT OR IGNORE INTO chat_channels (guild_id, channel_id) VALUES (?, ?)',
                    guild_id, channel_id
                )
            return True
        except Exception as e:
            logger.error(f'Error adding chat channel: {e}')
            return False
    
    async def remove_chat_channel(self, guild_id: int, channel_id: int) -> bool:
        try:
            if self.pool:
                await self._execute('DELETE FROM chat_channels WHERE guild_id = $1 AND channel_id = $2', guild_id, channel_id)
            else:
                await self._execute('DELETE FROM chat_channels WHERE guild_id = ? AND channel_id = ?', guild_id, channel_id)
            return True
        except Exception as e:
            logger.error(f'Error removing chat channel: {e}')
            return False
    
    async def get_chat_channels(self, guild_id: int) -> List[int]:
        if self.pool:
            rows = await self._fetchall('SELECT channel_id FROM chat_channels WHERE guild_id = $1', guild_id)
            return [row['channel_id'] for row in rows]
        else:
            rows = await self._fetchall('SELECT channel_id FROM chat_channels WHERE guild_id = ?', guild_id)
            return [row[0] for row in rows]
    
    async def set_ai_mode(self, guild_id: int, mode: str) -> bool:
        try:
            if self.pool:
                await self._execute('''
                    INSERT INTO ai_modes (guild_id, mode, updated_at) VALUES ($1, $2, CURRENT_TIMESTAMP)
                    ON CONFLICT (guild_id) DO UPDATE SET mode = $2, updated_at = CURRENT_TIMESTAMP
                ''', guild_id, mode)
            else:
                await self._execute('''
                    INSERT OR REPLACE INTO ai_modes (guild_id, mode, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', guild_id, mode)
            return True
        except Exception as e:
            logger.error(f'Error setting AI mode: {e}')
            return False
    
    async def get_ai_mode(self, guild_id: int) -> str:
        if self.pool:
            row = await self._fetchone('SELECT mode FROM ai_modes WHERE guild_id = $1', guild_id)
            return row['mode'] if row else 'standard'
        else:
            row = await self._fetchone('SELECT mode FROM ai_modes WHERE guild_id = ?', guild_id)
            return row[0] if row else 'standard'
    
    async def log_usage(self, user_id: int, guild_id: int, tokens_used: float, message_type: str):
        try:
            if self.pool:
                await self._execute('''
                    INSERT INTO usage_logs (user_id, guild_id, tokens_used, message_type) VALUES ($1, $2, $3, $4)
                ''', user_id, guild_id, tokens_used, message_type)
            else:
                await self._execute('''
                    INSERT INTO usage_logs (user_id, guild_id, tokens_used, message_type) VALUES (?, ?, ?, ?)
                ''', user_id, guild_id, tokens_used, message_type)
        except Exception as e:
            logger.error(f'Error logging usage: {e}')
    
    async def get_usage_stats(self, guild_id: Optional[int] = None) -> Dict:
        try:
            if self.pool:
                if guild_id:
                    row = await self._fetchone('''
                        SELECT COUNT(*) as total, COALESCE(SUM(tokens_used), 0) as tokens, 
                               COALESCE(AVG(tokens_used), 0) as avg, COUNT(DISTINCT user_id) as users
                        FROM usage_logs WHERE guild_id = $1
                    ''', guild_id)
                else:
                    row = await self._fetchone('''
                        SELECT COUNT(*) as total, COALESCE(SUM(tokens_used), 0) as tokens,
                               COALESCE(AVG(tokens_used), 0) as avg, COUNT(DISTINCT user_id) as users
                        FROM usage_logs
                    ''')
                return {
                    'total_messages': row['total'] or 0,
                    'total_tokens': row['tokens'] or 0,
                    'avg_tokens': row['avg'] or 0,
                    'unique_users': row['users'] or 0
                }
            else:
                if guild_id:
                    row = await self._fetchone('''
                        SELECT COUNT(*), SUM(tokens_used), AVG(tokens_used), COUNT(DISTINCT user_id)
                        FROM usage_logs WHERE guild_id = ?
                    ''', guild_id)
                else:
                    row = await self._fetchone('''
                        SELECT COUNT(*), SUM(tokens_used), AVG(tokens_used), COUNT(DISTINCT user_id)
                        FROM usage_logs
                    ''')
                return {
                    'total_messages': row[0] or 0,
                    'total_tokens': row[1] or 0,
                    'avg_tokens': row[2] or 0,
                    'unique_users': row[3] or 0
                }
        except Exception as e:
            logger.error(f'Error getting usage stats: {e}')
            return {'total_messages': 0, 'total_tokens': 0, 'avg_tokens': 0, 'unique_users': 0}
    
    async def save_chat_log(self, user_id: int, guild_id: int, channel_id: int,
                           user_message: str, ai_response: str, username: str,
                           channel_name: str, guild_name: str, tokens_used: float,
                           ai_mode: str, response_time: float):
        try:
            logger.info(f"💾 Saving chat log for {username} (user_id: {user_id})")
            
            if self.pool:
                await self._execute('''
                    INSERT INTO chat_logs (user_id, guild_id, channel_id, user_message, ai_response,
                                          username, channel_name, guild_name, tokens_used, ai_mode, response_time)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ''', user_id, guild_id, channel_id, user_message, ai_response,
                     username, channel_name, guild_name, tokens_used, ai_mode, response_time)
                logger.info(f"✅ Chat log saved to PostgreSQL for {username}")
            else:
                await self._execute('''
                    INSERT INTO chat_logs (user_id, guild_id, channel_id, user_message, ai_response,
                                          username, channel_name, guild_name, tokens_used, ai_mode, response_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', user_id, guild_id, channel_id, user_message, ai_response,
                     username, channel_name, guild_name, tokens_used, ai_mode, response_time)
                logger.info(f"✅ Chat log saved to SQLite for {username}")
        except Exception as e:
            logger.error(f'❌ Error saving chat log for {username}: {e}')
            import traceback
            traceback.print_exc()
    
    async def get_chat_logs(self, guild_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        try:
            if self.pool:
                if guild_id:
                    rows = await self._fetchall('''
                        SELECT id, user_id, guild_id, channel_id, user_message, ai_response,
                               username, channel_name, guild_name, tokens_used, ai_mode, response_time, created_at
                        FROM chat_logs WHERE guild_id = $1 ORDER BY created_at DESC LIMIT $2
                    ''', guild_id, limit)
                else:
                    rows = await self._fetchall('''
                        SELECT id, user_id, guild_id, channel_id, user_message, ai_response,
                               username, channel_name, guild_name, tokens_used, ai_mode, response_time, created_at
                        FROM chat_logs ORDER BY created_at DESC LIMIT $1
                    ''', limit)
                return [{
                    'id': str(r['id']), 'user_id': str(r['user_id']), 'guild_id': str(r['guild_id']),
                    'channel_id': str(r['channel_id']) if r['channel_id'] else None,
                    'message': r['user_message'], 'response': r['ai_response'],
                    'username': r['username'], 'channel_name': r['channel_name'],
                    'guild_name': r['guild_name'], 'tokens_used': r['tokens_used'],
                    'ai_mode': r['ai_mode'], 'response_time': r['response_time'],
                    'timestamp': r['created_at'].isoformat() if r['created_at'] else None
                } for r in rows]
            else:
                if guild_id:
                    rows = await self._fetchall('''
                        SELECT id, user_id, guild_id, channel_id, user_message, ai_response,
                               username, channel_name, guild_name, tokens_used, ai_mode, response_time, created_at
                        FROM chat_logs WHERE guild_id = ? ORDER BY created_at DESC LIMIT ?
                    ''', guild_id, limit)
                else:
                    rows = await self._fetchall('''
                        SELECT id, user_id, guild_id, channel_id, user_message, ai_response,
                               username, channel_name, guild_name, tokens_used, ai_mode, response_time, created_at
                        FROM chat_logs ORDER BY created_at DESC LIMIT ?
                    ''', limit)
                return [{
                    'id': str(r[0]), 'user_id': str(r[1]), 'guild_id': str(r[2]),
                    'channel_id': str(r[3]) if r[3] else None,
                    'message': r[4], 'response': r[5], 'username': r[6],
                    'channel_name': r[7], 'guild_name': r[8], 'tokens_used': r[9],
                    'ai_mode': r[10], 'response_time': r[11], 'timestamp': r[12]
                } for r in rows]
        except Exception as e:
            logger.error(f'Error getting chat logs: {e}')
            return []
    
    async def get_chat_users(self) -> List[Dict]:
        try:
            if self.pool:
                rows = await self._fetchall('''
                    SELECT user_id, username, COUNT(*) as count, SUM(tokens_used) as tokens, MAX(created_at) as last
                    FROM chat_logs GROUP BY user_id, username ORDER BY last DESC
                ''')
                return [{'user_id': str(r['user_id']), 'username': r['username'], 
                        'message_count': r['count'], 'total_tokens': r['tokens'], 
                        'last_message': r['last'].isoformat() if r['last'] else None} for r in rows]
            else:
                rows = await self._fetchall('''
                    SELECT user_id, username, COUNT(*), SUM(tokens_used), MAX(created_at)
                    FROM chat_logs GROUP BY user_id ORDER BY MAX(created_at) DESC
                ''')
                return [{'user_id': str(r[0]), 'username': r[1], 'message_count': r[2],
                        'total_tokens': r[3], 'last_message': r[4]} for r in rows]
        except Exception as e:
            logger.error(f'Error getting chat users: {e}')
            return []
    
    async def get_user_chat_history(self, user_id: int, limit: int = 100) -> List[Dict]:
        try:
            if self.pool:
                rows = await self._fetchall('''
                    SELECT id, user_message, ai_response, tokens_used, channel_name, guild_name, created_at
                    FROM chat_logs WHERE user_id = $1 ORDER BY created_at ASC LIMIT $2
                ''', user_id, limit)
                return [{'id': str(r['id']), 'message': r['user_message'], 'response': r['ai_response'],
                        'tokens_used': r['tokens_used'], 'channel_name': r['channel_name'],
                        'guild_name': r['guild_name'], 
                        'timestamp': r['created_at'].isoformat() if r['created_at'] else None} for r in rows]
            else:
                rows = await self._fetchall('''
                    SELECT id, user_message, ai_response, tokens_used, channel_name, guild_name, created_at
                    FROM chat_logs WHERE user_id = ? ORDER BY created_at ASC LIMIT ?
                ''', user_id, limit)
                return [{'id': str(r[0]), 'message': r[1], 'response': r[2], 'tokens_used': r[3],
                        'channel_name': r[4], 'guild_name': r[5], 'timestamp': r[6]} for r in rows]
        except Exception as e:
            logger.error(f'Error getting user chat history: {e}')
            return []
    
    async def get_user_history_from_db(self, user_id: int, limit: int = 5) -> List[Dict]:
        try:
            if self.pool:
                rows = await self._fetchall('''
                    SELECT user_message, ai_response, created_at FROM chat_logs
                    WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2
                ''', user_id, limit)
                return [{'user_message': r['user_message'], 'ai_response': r['ai_response'],
                        'timestamp': r['created_at'].isoformat() if r['created_at'] else None} 
                       for r in reversed(rows)]
            else:
                rows = await self._fetchall('''
                    SELECT user_message, ai_response, created_at FROM chat_logs
                    WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
                ''', user_id, limit)
                return [{'user_message': r[0], 'ai_response': r[1], 'timestamp': r[2]} 
                       for r in reversed(rows)]
        except Exception as e:
            logger.error(f'Error getting user history: {e}')
            return []
    
    def get_user_history(self, user_id: int) -> List[Dict]:
        if user_id not in self.user_histories:
            self.user_histories[user_id] = deque(maxlen=20)
        return list(self.user_histories[user_id])
    
    def update_user_history(self, user_id: int, user_message: str, ai_response: str):
        if user_id not in self.user_histories:
            self.user_histories[user_id] = deque(maxlen=20)
        self.user_histories[user_id].append({
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
    
    async def save_music_channel(self, guild_id: int, channel_id: int, creator_id: int) -> bool:
        try:
            if self.pool:
                await self._execute('''
                    INSERT INTO music_channels (guild_id, channel_id, creator_id) VALUES ($1, $2, $3)
                    ON CONFLICT (channel_id) DO UPDATE SET guild_id = $1, creator_id = $3
                ''', guild_id, channel_id, creator_id)
            else:
                await self._execute('''
                    INSERT OR REPLACE INTO music_channels (guild_id, channel_id, creator_id) VALUES (?, ?, ?)
                ''', guild_id, channel_id, creator_id)
            return True
        except Exception as e:
            logger.error(f'Error saving music channel: {e}')
            return False
    
    async def remove_music_channel(self, guild_id: int) -> bool:
        try:
            if self.pool:
                await self._execute('DELETE FROM music_channels WHERE guild_id = $1', guild_id)
            else:
                await self._execute('DELETE FROM music_channels WHERE guild_id = ?', guild_id)
            return True
        except Exception as e:
            logger.error(f'Error removing music channel: {e}')
            return False
