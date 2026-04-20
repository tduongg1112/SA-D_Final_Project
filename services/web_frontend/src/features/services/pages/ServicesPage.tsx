import { Boxes, Database, Router } from "lucide-react";

import { PanelCard } from "@/components/ui/panel-card";

const services = [
  {
    title: "Product context",
    description: "Browse, search, category, and product detail data owned by product-service.",
  },
  {
    title: "Cart context",
    description: "Cart state, quantities, and subtotal progression owned by cart-service.",
  },
  {
    title: "Ordering context",
    description: "Checkout orchestration and order lifecycle owned by ordering-service.",
  },
  {
    title: "Payment context",
    description: "Payment records and status owned by payment-service.",
  },
  {
    title: "Shipping context",
    description: "Shipment preparation and delivery state owned by shipping-service.",
  },
  {
    title: "Gateway context",
    description: "Public routing, aggregation, and edge orchestration owned by api-gateway.",
  },
];

export function ServicesPage() {
  return (
    <div className="grid gap-6">
      <PanelCard
        eyebrow="Service map"
        title="The frontend now has a route dedicated to architectural context."
        description="This page can evolve into a developer-facing overview or operator contract reference without polluting shopper pages."
        icon={<Router size={18} strokeWidth={1.7} />}
      />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <PanelCard eyebrow="Bounded contexts" title="Service ownership tiles" description="A layout scaffold for context documentation inside the product shell.">
          <div className="grid gap-4 md:grid-cols-2">
            {services.map((service) => (
              <div key={service.title} className="grid gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4">
                <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-[var(--color-accent)]">
                  <Boxes size={18} strokeWidth={1.7} />
                </span>
                <strong className="text-[16px] font-medium text-[var(--color-text)]">{service.title}</strong>
                <p className="text-[14px] leading-6 text-[var(--color-text-soft)]">{service.description}</p>
              </div>
            ))}
          </div>
        </PanelCard>

        <PanelCard eyebrow="Data boundary" title="Database per service" description="The UI plan stays aligned with the microservices decomposition already present in the repo.">
          <div className="flex items-start gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4">
            <Database size={18} strokeWidth={1.7} className="mt-1 shrink-0 text-[var(--color-accent)]" />
            <p className="text-[15px] leading-7 text-[var(--color-text-soft)]">
              This view is a good place to surface contract summaries later, especially before the AI service starts reading
              product, cart, and order context through the gateway.
            </p>
          </div>
        </PanelCard>
      </div>
    </div>
  );
}
