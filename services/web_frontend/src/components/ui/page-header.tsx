import type { PropsWithChildren, ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface PageHeaderProps extends PropsWithChildren {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
  className?: string;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  className,
  children,
}: PageHeaderProps) {
  return (
    <section className={cn("grid gap-6 rounded-[32px] border border-[var(--color-border)] bg-white px-8 py-8 shadow-[var(--shadow-card)]", className)}>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-start">
        <div className="grid gap-3">
          <span className="label-eyebrow">{eyebrow}</span>
          <h1 className="max-w-[14ch] text-balance text-[40px] font-semibold leading-[0.98] tracking-[-0.055em] text-[var(--color-text)] md:text-[52px]">
            {title}
          </h1>
          <p className="max-w-[70ch] text-[16px] leading-7 text-[var(--color-text-soft)]">{description}</p>
        </div>
        {actions ? <div className="flex flex-wrap items-center gap-3 xl:justify-end">{actions}</div> : null}
      </div>
      {children}
    </section>
  );
}
