import { NavLink } from "react-router-dom";

import { navigationSections } from "@/lib/constants/navigation";
import { cn } from "@/lib/utils/cn";

export function Sidebar() {
  return (
    <aside className="grid gap-6 rounded-[32px] border border-[var(--color-border)] bg-[var(--color-surface)] p-5 shadow-[var(--shadow-card)]">
      <div className="grid gap-4 border-b border-[var(--color-border)] pb-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,_var(--color-accent)_0%,_var(--color-accent-soft)_100%)] text-white shadow-[0_20px_40px_rgba(47,109,246,0.24)]">
            <span className="text-lg font-semibold">N</span>
          </div>
          <div className="grid gap-1">
            <strong className="text-[16px] font-semibold tracking-[-0.03em] text-[var(--color-text)]">
              NovaMarket
            </strong>
            <span className="label-eyebrow">Frontend Alpha</span>
          </div>
        </div>
        <div className="rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4">
          <p className="label-eyebrow">Build phase</p>
          <p className="mt-2 text-[14px] leading-6 text-[var(--color-text-soft)]">
            Phase A foundation is active. The shell, navigation, and page hierarchy are now controlled in React.
          </p>
        </div>
      </div>

      <nav className="grid gap-5" aria-label="Primary sidebar">
        {navigationSections.map((section) => (
          <section key={section.title} className="grid gap-2">
            <span className="px-2 text-[12px] font-medium uppercase tracking-[0.16em] text-[var(--color-text-faint)]">
              {section.title}
            </span>
            <div className="grid gap-1.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      cn(
                        "group grid grid-cols-[32px_minmax(0,1fr)] items-center gap-3 rounded-2xl px-3 py-3 transition duration-150",
                        "hover:bg-[var(--color-surface-muted)]",
                        isActive
                          ? "bg-[var(--color-accent-soft)] text-[var(--color-accent)]"
                          : "text-[var(--color-text-soft)]",
                      )
                    }
                  >
                    <span className="flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--color-border)] bg-white text-current">
                      <Icon size={20} strokeWidth={1.6} />
                    </span>
                    <span className="grid gap-0.5">
                      <span className="text-[15px] font-medium leading-5 text-[var(--color-text)]">
                        {item.label}
                      </span>
                      <span className="text-[13px] leading-5 text-[var(--color-text-faint)]">
                        {item.description}
                      </span>
                    </span>
                  </NavLink>
                );
              })}
            </div>
          </section>
        ))}
      </nav>
    </aside>
  );
}
