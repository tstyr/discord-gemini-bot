import sqlite3 from 'sqlite3';
import { promisify } from 'util';
import path from 'path';

// データベースファイルのパス（botディレクトリのbot.dbを参照）
const DB_PATH = path.join(process.cwd(), '..', 'bot', 'bot.db');

export interface GuildStats {
  totalGuilds: number;
  totalMessages: number;
  totalUsers: number;
  messagesLast7Days: number;
  messagesLast30Days: number;
}

export interface MessagesByDay {
  date: string;
  count: number;
}

export interface TopGuilds {
  guild_id: string;
  name: string;
  message_count: number;
}

class Database {
  private db: sqlite3.Database;

  constructor() {
    this.db = new sqlite3.Database(DB_PATH);
  }

  private all = promisify(this.db.all.bind(this.db));
  private get = promisify(this.db.get.bind(this.db));

  async getStats(): Promise<GuildStats> {
    try {
      // 総ギルド数
      const guildCount = await this.get('SELECT COUNT(*) as count FROM guilds') as { count: number };
      
      // 総メッセージ数
      const messageCount = await this.get('SELECT COUNT(*) as count FROM messages') as { count: number };
      
      // 総ユーザー数（ユニーク）
      const userCount = await this.get('SELECT COUNT(DISTINCT user_id) as count FROM messages') as { count: number };
      
      // 過去7日間のメッセージ数
      const messages7Days = await this.get(`
        SELECT COUNT(*) as count FROM messages 
        WHERE created_at >= datetime('now', '-7 days')
      `) as { count: number };
      
      // 過去30日間のメッセージ数
      const messages30Days = await this.get(`
        SELECT COUNT(*) as count FROM messages 
        WHERE created_at >= datetime('now', '-30 days')
      `) as { count: number };

      return {
        totalGuilds: guildCount?.count || 0,
        totalMessages: messageCount?.count || 0,
        totalUsers: userCount?.count || 0,
        messagesLast7Days: messages7Days?.count || 0,
        messagesLast30Days: messages30Days?.count || 0,
      };
    } catch (error) {
      console.error('Database error:', error);
      return {
        totalGuilds: 0,
        totalMessages: 0,
        totalUsers: 0,
        messagesLast7Days: 0,
        messagesLast30Days: 0,
      };
    }
  }

  async getMessagesByDay(days: number = 30): Promise<MessagesByDay[]> {
    try {
      const result = await this.all(`
        SELECT 
          DATE(created_at) as date,
          COUNT(*) as count
        FROM messages 
        WHERE created_at >= datetime('now', '-${days} days')
        GROUP BY DATE(created_at)
        ORDER BY date ASC
      `) as MessagesByDay[];
      
      return result || [];
    } catch (error) {
      console.error('Database error:', error);
      return [];
    }
  }

  async getTopGuilds(limit: number = 10): Promise<TopGuilds[]> {
    try {
      const result = await this.all(`
        SELECT 
          m.guild_id,
          g.name,
          COUNT(m.id) as message_count
        FROM messages m
        LEFT JOIN guilds g ON m.guild_id = g.id
        GROUP BY m.guild_id
        ORDER BY message_count DESC
        LIMIT ${limit}
      `) as TopGuilds[];
      
      return result || [];
    } catch (error) {
      console.error('Database error:', error);
      return [];
    }
  }

  close() {
    this.db.close();
  }
}

export default Database;