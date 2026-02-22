"""データベース操作モジュール"""
import aiosqlite
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "bot_data.db"

async def init_db():
    """データベース初期化"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                chat_channel_id INTEGER,
                ai_mode TEXT DEFAULT 'standard'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                tokens_used INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def get_guild_settings(guild_id: int) -> dict | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def set_chat_channel(guild_id: int, channel_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO guild_settings (guild_id, chat_channel_id)
            VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET chat_channel_id = ?
        """, (guild_id, channel_id, channel_id))
        await db.commit()

async def set_ai_mode(guild_id: int, mode: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO guild_settings (guild_id, ai_mode)
            VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET ai_mode = ?
        """, (guild_id, mode, mode))
        await db.commit()

async def log_usage(guild_id: int, user_id: int, tokens: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO usage_stats (guild_id, user_id, tokens_used) VALUES (?, ?, ?)",
            (guild_id, user_id, tokens)
        )
        await db.commit()

async def get_stats(guild_id: int) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT SUM(tokens_used) as total_tokens, COUNT(*) as message_count FROM usage_stats WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return {"total_tokens": row[0] or 0, "message_count": row[1] or 0}
