import { Route, Server, ShieldCheck, TimerReset } from "lucide-react";

import { PanelCard } from "@/components/ui/panel-card";

const serviceCards = [
  "api-gateway",
  "product-service",
  "cart-service",
  "ordering-service",
  "payment-service",
  "shipping-service",
];

export function GatewayPage() {
  return (
    <div className="grid gap-6">
      <PanelCard
        eyebrow="Gateway operator view"
        title="Gateway visibility now lives inside the same React shell."
        description="This route will eventually surface health, routing, and service registry data from the gateway without breaking the product UI system."
        icon={<Route size={18} strokeWidth={1.7} />}
      />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <PanelCard eyebrow="Service map" title="Runtime cards" description="Each tile is a placeholder for gateway health data.">
          <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
            {serviceCards.map((service) => (
              <div key={service} className="grid gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4">
                <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-[var(--color-accent)]">
                  <Server size={18} strokeWidth={1.7} />
                </span>
                <strong className="text-[16px] font-medium text-[var(--color-text)]">{service}</strong>
                <span className="text-[13px] leading-6 text-[var(--color-text-faint)]">
                  Gateway-connected health snapshot placeholder
                </span>
              </div>
            ))}
          </div>
        </PanelCard>

        <div className="grid gap-4">
          <PanelCard eyebrow="Status" title="Healthy" description="UI placeholder for aggregated gateway health.">
            <div className="flex items-center gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4">
              <ShieldCheck size={18} strokeWidth={1.7} className="text-emerald-600" />
              <span className="text-[15px] text-[var(--color-text-soft)]">All tracked services can report into this panel later.</span>
            </div>
          </PanelCard>
          <PanelCard eyebrow="Latency" title="Trace surface" description="Reserved for response time and route metadata.">
            <div className="flex items-center gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4">
              <TimerReset size={18} strokeWidth={1.7} className="text-[var(--color-accent)]" />
              <span className="text-[15px] text-[var(--color-text-soft)]">Route timing, request ID, and service status will plug in here next.</span>
            </div>
          </PanelCard>
        </div>
      </div>
    </div>
  );
}
