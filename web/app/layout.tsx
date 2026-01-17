import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Discord Bot Dashboard",
  description: "リアルタイム監視・管理ダッシュボード",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="bg-discord-darker text-white antialiased">{children}</body>
    </html>
  );
}
