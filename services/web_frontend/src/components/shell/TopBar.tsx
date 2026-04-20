import { Bell, Search, Settings2 } from "lucide-react";
import { useLocation } from "react-router-dom";

import { Button } from "@/components/ui/button";

const pageNames: Record<string, string> = {
  "/": "Overview",
  "/products": "Products",
  "/cart": "Cart",
  "/dashboard": "Dashboard",
  "/gateway": "Gateway",
  "/services": "Services",
  "/assistant": "Assistant",
  "/shell-spec": "Shell Spec",
};

function resolveLabel(pathname: string) {
  if (pathname.startsWith("/products/")) return "Product Detail";
  if (pathname.startsWith("/orders/")) return "Order Detail";
  return pageNames[pathname] ?? "Workspace";
}

export function TopBar() {
  const location = useLocation();

  return (
    <header className="grid gap-4 rounded-[28px] border border-[var(--color-border)] bg-white p-5 shadow-[var(--shadow-card)] lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
      <div className="grid gap-2">
        <span className="label-eyebrow">NovaMarket Product Shell</span>
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-[24px] font-semibold leading-[1.04] tracking-[-0.04em] text-[var(--color-text)]">
            {resolveLabel(location.pathname)}
          </h2>
          <span className="rounded-full border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-3 py-1.5 text-[12px] font-medium uppercase tracking-[0.14em] text-[var(--color-text-faint)]">
            React foundation
          </span>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-[minmax(280px,360px)_auto] md:items-center">
        <label className="flex h-12 items-center gap-3 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 text-[var(--color-text-faint)]">
          <Search size={18} strokeWidth={1.75} />
          <input
            type="search"
            placeholder="Search products, routes, or services"
            className="w-full border-none bg-transparent text-[15px] text-[var(--color-text)] outline-none placeholder:text-[var(--color-text-faint)]"
          />
        </label>

        <div className="flex flex-wrap items-center gap-3 md:justify-end">
          <Button variant="ghost" className="px-0 text-[var(--color-text-faint)] hover:bg-transparent">
            <Bell size={20} strokeWidth={1.7} />
          </Button>
          <Button variant="secondary" className="gap-2">
            <Settings2 size={18} strokeWidth={1.7} />
            Shell settings
          </Button>
        </div>
      </div>
    </header>
  );
}
