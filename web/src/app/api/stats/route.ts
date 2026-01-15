import { NextRequest, NextResponse } from 'next/server';
import Database from '@/lib/database';

export async function GET(request: NextRequest) {
  const db = new Database();
  
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type') || 'overview';
    const days = parseInt(searchParams.get('days') || '30');
    const limit = parseInt(searchParams.get('limit') || '10');

    switch (type) {
      case 'overview':
        const stats = await db.getStats();
        return NextResponse.json({
          success: true,
          data: stats
        });

      case 'messages-by-day':
        const messagesByDay = await db.getMessagesByDay(days);
        return NextResponse.json({
          success: true,
          data: messagesByDay
        });

      case 'top-guilds':
        const topGuilds = await db.getTopGuilds(limit);
        return NextResponse.json({
          success: true,
          data: topGuilds
        });

      case 'all':
        const [overviewStats, messagesData, guildsData] = await Promise.all([
          db.getStats(),
          db.getMessagesByDay(days),
          db.getTopGuilds(limit)
        ]);
        
        return NextResponse.json({
          success: true,
          data: {
            overview: overviewStats,
            messagesByDay: messagesData,
            topGuilds: guildsData
          }
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid type parameter. Use: overview, messages-by-day, top-guilds, or all'
        }, { status: 400 });
    }
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  } finally {
    db.close();
  }
}