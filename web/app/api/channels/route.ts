import { NextRequest, NextResponse } from "next/server";

// Mock data - replace with actual database connection
let chatChannels = [
  { id: "1", channelId: "123456789", name: "ai-chat", guildId: "111", guildName: "My Server", enabled: true },
  { id: "2", channelId: "987654321", name: "bot-testing", guildId: "222", guildName: "Dev Server", enabled: true },
];

export async function GET() {
  return NextResponse.json({ channels: chatChannels });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { channelId, guildId, name, guildName } = body;

    const newChannel = {
      id: String(Date.now()),
      channelId,
      guildId,
      name,
      guildName,
      enabled: true,
    };

    chatChannels.push(newChannel);
    return NextResponse.json({ success: true, channel: newChannel });
  } catch (error) {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const channelId = searchParams.get("channelId");

    if (!channelId) {
      return NextResponse.json({ error: "channelId required" }, { status: 400 });
    }

    chatChannels = chatChannels.filter((c) => c.channelId !== channelId);
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}
