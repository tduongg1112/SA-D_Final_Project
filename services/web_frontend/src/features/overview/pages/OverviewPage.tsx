import { ArrowRight, ChartColumn, Package, Sparkles, Truck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { PanelCard } from "@/components/ui/panel-card";

const heroStats = [
  { label: "Service contracts", value: "6 core" },
  { label: "Primary shopper flow", value: "Browse -> checkout" },
  { label: "Layout rhythm", value: "4px rule" },
];

const journeyTiles = [
  {
    title: "Unified shopper shell",
    description: "Overview, products, cart, and order success all live under one sidebar-driven experience.",
    icon: Package,
  },
  {
    title: "Operational visibility",
    description: "Dashboard and gateway stay in the same design system instead of feeling like a separate admin product.",
    icon: ChartColumn,
  },
  {
    title: "AI-ready foundation",
    description: "Assistant and insight surfaces already have reserved routes in the navigation model.",
    icon: Sparkles,
  },
];

export function OverviewPage() {
  return (
    <div className="grid gap-6">
      <PageHeader
        eyebrow="Foundation phase"
        title="Sidebar-first frontend rebuilt from a clean slate."
        description="This first implementation step establishes the React app shell, navigation, routing, and visual tokens before any gateway or service data is wired in."
        actions={
          <>
            <Button variant="primary" size="lg" className="gap-2">
              Start products
              <ArrowRight size={18} strokeWidth={1.8} />
            </Button>
            <Button variant="secondary" size="lg">
              Review shell spec
            </Button>
          </>
        }
      >
        <div className="grid gap-4 md:grid-cols-3">
          {heroStats.map((item) => (
            <div
              key={item.label}
              className="rounded-[24px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-5 py-5"
            >
              <p className="label-eyebrow">{item.label}</p>
              <strong className="mt-3 block text-[28px] font-semibold tracking-[-0.05em] text-[var(--color-text)]">
                {item.value}
              </strong>
            </div>
          ))}
        </div>
      </PageHeader>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
        <PanelCard
          eyebrow="Build direction"
          title="Why the rebuild is now tractable"
          description="The route hierarchy, sidebar model, and card grammar are no longer mixed into Django templates. The shell is now a dedicated frontend concern."
          icon={<Truck size={18} strokeWidth={1.7} />}
        >
          <div className="grid gap-4 text-[15px] leading-7 text-[var(--color-text-soft)]">
            <p>
              The old UI has already been stripped back. This step establishes the frontend runtime with a durable structure:
              `AppShell`, `Sidebar`, `TopBar`, route groups, and reusable panel components.
            </p>
            <p>
              The next iteration can focus purely on connecting product, cart, order, dashboard, and gateway data without
              rethinking layout architecture again.
            </p>
          </div>
        </PanelCard>

        <PanelCard eyebrow="Immediate next" title="Implementation roadmap" description="The next build steps stay intentionally narrow.">
          <div className="grid gap-3">
            {[
              "Wire gateway-aware API client and query hooks.",
              "Replace placeholder product explorer with real product-service data.",
              "Implement cart and quick checkout against existing gateway contracts.",
              "Refactor gateway root to serve the new frontend app.",
            ].map((item, index) => (
              <div
                key={item}
                className="grid grid-cols-[32px_minmax(0,1fr)] items-start gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-[13px] font-semibold text-[var(--color-accent)]">
                  0{index + 1}
                </span>
                <p className="text-[15px] leading-6 text-[var(--color-text-soft)]">{item}</p>
              </div>
            ))}
          </div>
        </PanelCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        {journeyTiles.map((tile) => {
          const Icon = tile.icon;
          return (
            <PanelCard
              key={tile.title}
              eyebrow="Design principle"
              title={tile.title}
              description={tile.description}
              icon={<Icon size={18} strokeWidth={1.7} />}
            />
          );
        })}
      </div>
    </div>
  );
}
