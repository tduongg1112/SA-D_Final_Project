import { Outlet } from "react-router-dom";

import { Sidebar } from "@/components/shell/Sidebar";
import { TopBar } from "@/components/shell/TopBar";

export function AppShell() {
  return (
    <div className="min-h-screen bg-[var(--color-bg)]">
      <div className="mx-auto grid min-h-screen w-full max-w-[1640px] gap-4 p-4 lg:grid-cols-[280px_minmax(0,1fr)]">
        <Sidebar />
        <div className="grid min-h-full content-start gap-4">
          <TopBar />
          <main className="grid gap-6 pb-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
