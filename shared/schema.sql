-- Database Schema for Discord Bot + Web Dashboard

-- Guild settings
CREATE TABLE IF NOT EXISTS guilds (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    ai_mode TEXT DEFAULT 'standard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat channels (auto-response enabled)
CREATE TABLE IF NOT EXISTS chat_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    channel_id TEXT NOT NULL UNIQUE,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guild_id) REFERENCES guilds(id)
);

-- Enhanced usage statistics with more details
CREATE TABLE IF NOT EXISTS usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    channel_id TEXT,
    tokens_used INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 1,
    ai_mode TEXT DEFAULT 'standard',
    message_type TEXT DEFAULT 'auto_response', -- 'slash_command', 'auto_response'
    response_time REAL, -- in seconds
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guild_id) REFERENCES guilds(id)
);

-- Daily aggregated stats
CREATE TABLE IF NOT EXISTS daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    date DATE NOT NULL,
    total_tokens INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    avg_response_time REAL DEFAULT 0,
    UNIQUE(guild_id, date),
    FOREIGN KEY (guild_id) REFERENCES guilds(id)
);

-- Bot configuration settings
CREATE TABLE IF NOT EXISTS bot_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    setting_key TEXT NOT NULL,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(guild_id, setting_key),
    FOREIGN KEY (guild_id) REFERENCES guilds(id)
);

-- User preferences per guild
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, guild_id, preference_key),
    FOREIGN KEY (guild_id) REFERENCES guilds(id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_channels_guild ON chat_channels(guild_id);
CREATE INDEX IF NOT EXISTS idx_usage_stats_guild ON usage_stats(guild_id);
CREATE INDEX IF NOT EXISTS idx_usage_stats_user ON usage_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_stats_timestamp ON usage_stats(timestamp);
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date);
CREATE INDEX IF NOT EXISTS idx_bot_settings_guild ON bot_settings(guild_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_guild ON user_preferences(user_id, guild_id);
