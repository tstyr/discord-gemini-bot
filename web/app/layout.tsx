import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Discord Bot Dashboard",
  description: "AI Bot管理ダッシュボード",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen osu-bg-pattern">{children}</body>
    </html>
  );
}
