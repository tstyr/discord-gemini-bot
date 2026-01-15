import { Sidebar } from "@/components/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen osu-bg-lines">
      {/* Background orbs */}
      <div className="fixed osu-orb w-96 h-96 bg-osu-pink/30 top-20 -right-48" />
      <div className="fixed osu-orb w-80 h-80 bg-osu-purple/20 bottom-20 left-20" />

      <Sidebar />
      <main className="ml-20 p-8">{children}</main>
    </div>
  );
}
