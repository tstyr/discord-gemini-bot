// 共有型定義
export interface Guild {
  id: string;
  name: string;
  icon: string | null;
  memberCount: number;
}

export interface BotConfig {
  guildId: string;
  prefix: string;
  welcomeChannelId?: string;
  welcomeMessage?: string;
}

export interface User {
  id: string;
  username: string;
  avatar: string | null;
  discriminator: string;
}
