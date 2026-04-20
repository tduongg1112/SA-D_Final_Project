import type { PropsWithChildren } from "react";

import { cn } from "@/lib/utils/cn";

type StatusTone = "neutral" | "primary" | "success" | "warning";

interface StatusBadgeProps extends PropsWithChildren {
  tone?: StatusTone;
  className?: string;
}

const toneClasses: Record<StatusTone, string> = {
  neutral: "border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text-faint)]",
  primary: "border-[var(--color-accent-soft)] bg-[var(--color-accent-soft)] text-[var(--color-accent)]",
  success: "border-[#d8f0df] bg-[var(--color-success-soft)] text-[var(--color-success)]",
  warning: "border-[#ffe4ab] bg-[var(--color-warning-soft)] text-[var(--color-warning)]",
};

export function StatusBadge({ tone = "neutral", className, children }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex h-8 items-center rounded-full border px-3 text-[12px] font-medium uppercase tracking-[0.12em]",
        toneClasses[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
