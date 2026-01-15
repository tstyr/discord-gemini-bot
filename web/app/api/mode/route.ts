import { NextRequest, NextResponse } from "next/server";

// Mock data - replace with actual database connection
const guildModes: Record<string, string> = {
  "111": "standard",
  "222": "coder",
};

const validModes = ["standard", "assistant", "creative", "coder"];

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const guildId = searchParams.get("guildId");

  if (!guildId) {
    return NextResponse.json({ error: "guildId required" }, { status: 400 });
  }

  const mode = guildModes[guildId] || "standard";
  return NextResponse.json({ guildId, mode });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { guildId, mode } = body;

    if (!guildId || !mode) {
      return NextResponse.json({ error: "guildId and mode required" }, { status: 400 });
    }

    if (!validModes.includes(mode)) {
      return NextResponse.json({ error: `Invalid mode. Valid: ${validModes.join(", ")}` }, { status: 400 });
    }

    guildModes[guildId] = mode;
    return NextResponse.json({ success: true, guildId, mode });
  } catch (error) {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}
