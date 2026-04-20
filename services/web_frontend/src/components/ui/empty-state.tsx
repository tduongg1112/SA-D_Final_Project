import type { ReactNode } from "react";

import { PanelCard } from "@/components/ui/panel-card";

interface EmptyStateProps {
  icon?: ReactNode;
  eyebrow?: string;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon, eyebrow, title, description, action }: EmptyStateProps) {
  return (
    <PanelCard eyebrow={eyebrow} title={title} description={description} icon={icon}>
      {action ? <div className="mt-1 flex flex-wrap items-center gap-3">{action}</div> : null}
    </PanelCard>
  );
}
