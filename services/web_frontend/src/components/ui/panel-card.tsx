import type { PropsWithChildren, ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface PanelCardProps extends PropsWithChildren {
  eyebrow?: string;
  title?: string;
  description?: string;
  icon?: ReactNode;
  className?: string;
}

export function PanelCard({
  eyebrow,
  title,
  description,
  icon,
  className,
  children,
}: PanelCardProps) {
  return (
    <section
      className={cn(
        "rounded-[24px] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-[var(--shadow-card)]",
        className,
      )}
    >
      {(eyebrow || title || description || icon) && (
        <header className="mb-5 grid gap-3">
          {(eyebrow || icon) && (
            <div className="flex items-center gap-3">
              {icon ? (
                <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-accent)]">
                  {icon}
                </div>
              ) : null}
              {eyebrow ? <span className="label-eyebrow">{eyebrow}</span> : null}
            </div>
          )}
          {title ? <h2 className="text-balance text-[28px] font-semibold leading-[1.08] tracking-[-0.04em] text-[var(--color-text)]">{title}</h2> : null}
          {description ? <p className="max-w-[68ch] text-[15px] leading-7 text-[var(--color-text-soft)]">{description}</p> : null}
        </header>
      )}
      {children}
    </section>
  );
}
