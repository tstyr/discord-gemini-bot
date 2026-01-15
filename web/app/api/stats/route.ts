import { NextResponse } from "next/server";

// Mock data - replace with actual database connection
const mockStats = {
  totalTokens: 150000,
  totalMessages: 523,
  activeChannels: 3,
  servers: 5,
  dailyStats: [
    { date: "2026-01-09", tokens: 12000, messages: 45 },
    { date: "2026-01-10", tokens: 18000, messages: 62 },
    { date: "2026-01-11", tokens: 15000, messages: 51 },
    { date: "2026-01-12", tokens: 22000, messages: 78 },
    { date: "2026-01-13", tokens: 28000, messages: 95 },
    { date: "2026-01-14", tokens: 24000, messages: 82 },
    { date: "2026-01-15", tokens: 31000, messages: 110 },
  ],
};

export async function GET() {
  // TODO: Connect to actual database
  return NextResponse.json(mockStats);
}
