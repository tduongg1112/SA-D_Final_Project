import { CheckCircle2, CreditCard, MapPinned, PackageCheck } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import { useOrderDetail } from "@/features/orders/api/orders";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { PanelCard } from "@/components/ui/panel-card";
import { SkeletonBlock } from "@/components/ui/skeleton-block";
import { StatusBadge } from "@/components/ui/status-badge";
import { formatCurrency, formatTitleCase } from "@/lib/utils/format";
import { getStatusTone } from "@/lib/utils/status";

export function OrderDetailPage() {
  const navigate = useNavigate();
  const { orderId } = useParams();
  const { data: order, isLoading, error } = useOrderDetail(orderId);

  if (!orderId) {
    return (
      <EmptyState
        eyebrow="Order detail"
        title="No order identifier was provided."
        description="The order success route needs a valid order id to load real checkout, payment, and shipping state."
        action={<Button onClick={() => navigate("/products")}>Return to products</Button>}
      />
    );
  }

  if (isLoading) {
    return (
      <div className="grid gap-6">
        <SkeletonBlock className="min-h-[180px] rounded-[24px]" />
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
          <SkeletonBlock className="min-h-[320px] rounded-[24px]" />
          <SkeletonBlock className="min-h-[320px] rounded-[24px]" />
        </div>
      </div>
    );
  }

  if (error || !order) {
    const errorMessage = error instanceof Error ? error.message : "The selected order could not be loaded from the gateway.";
    return (
      <EmptyState
        eyebrow="Order detail"
        title="Order detail is unavailable."
        description={errorMessage}
        action={<Button onClick={() => navigate("/cart")}>Return to cart</Button>}
      />
    );
  }

  return (
    <div className="grid gap-6">
      <PanelCard
        eyebrow="Order success"
        title={`Order #${order.id} is confirmed.`}
        description="This page now reflects the real ordering, payment, and shipping read model through the gateway instead of a static receipt placeholder."
        icon={<CheckCircle2 size={18} strokeWidth={1.7} />}
      >
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="primary" onClick={() => navigate("/dashboard")}>
            Open dashboard
          </Button>
          <Button variant="secondary" onClick={() => navigate("/products")}>
            Return to products
          </Button>
        </div>
      </PanelCard>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="grid gap-6">
          <PanelCard
            eyebrow="Order summary"
            title={`Customer: ${order.customer_name}`}
            description="Status blocks stay compact, aligned, and directly tied to service data."
          >
            <div className="grid gap-4 md:grid-cols-2">
              {[
                { label: "Payment", value: order.payment_status ?? "Unavailable", icon: CreditCard, format: "status" as const },
                { label: "Shipping", value: order.shipping_status ?? "Unavailable", icon: PackageCheck, format: "status" as const },
                { label: "Tracking", value: order.tracking_code ?? "Pending", icon: MapPinned, format: "raw" as const },
                { label: "Customer", value: order.customer_email, icon: CheckCircle2, format: "raw" as const },
              ].map((item) => {
                const Icon = item.icon;
                const displayValue = item.format === "status" ? formatTitleCase(item.value) : item.value;
                return (
                  <div key={item.label} className="grid grid-cols-[32px_minmax(0,1fr)] gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4">
                    <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-[var(--color-accent)]">
                      <Icon size={18} strokeWidth={1.7} />
                    </span>
                    <div className="grid gap-1">
                      <span className="label-eyebrow">{item.label}</span>
                      <div className="flex flex-wrap items-center gap-2">
                        <strong className="text-[15px] font-medium text-[var(--color-text)]">{displayValue}</strong>
                        {(item.label === "Payment" || item.label === "Shipping") && item.value ? (
                          <StatusBadge tone={getStatusTone(item.value)}>{item.value}</StatusBadge>
                        ) : null}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </PanelCard>

          <PanelCard
            eyebrow="Order items"
            title={`${order.items.length} line items`}
            description="This section is already bound to the ordering-service read model."
          >
            <div className="grid gap-3">
              {order.items.map((item) => (
                <div key={`${item.product_id}-${item.product_name}`} className="grid gap-2 rounded-[18px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4">
                  <div className="flex items-center justify-between gap-3">
                    <strong className="block text-[16px] font-medium text-[var(--color-text)]">{item.product_name}</strong>
                    <StatusBadge tone="primary">Qty {item.quantity}</StatusBadge>
                  </div>
                  <div className="flex items-center justify-between gap-3 text-[14px] text-[var(--color-text-soft)]">
                    <span>{formatCurrency(item.unit_price)} each</span>
                    <strong className="text-[var(--color-text)]">{formatCurrency(item.line_total)}</strong>
                  </div>
                </div>
              ))}
            </div>
          </PanelCard>
        </div>

        <div className="grid gap-4">
          <PanelCard eyebrow="Checkout totals" title={formatCurrency(order.total)} description="These amounts are the stored order values after the shipping fee is applied.">
            <div className="grid gap-3">
              {[
                ["Subtotal", formatCurrency(order.subtotal)],
                ["Shipping fee", formatCurrency(order.shipping_fee)],
                ["Total", formatCurrency(order.total)],
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between gap-3 rounded-[18px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4 text-[15px]">
                  <span className="text-[var(--color-text-soft)]">{label}</span>
                  <strong className="text-[var(--color-text)]">{value}</strong>
                </div>
              ))}
            </div>
          </PanelCard>

          <PanelCard
            eyebrow="Shipping address"
            title={order.customer_phone}
            description={order.shipping_address}
            icon={<MapPinned size={18} strokeWidth={1.7} />}
          />

          <PanelCard
            eyebrow="Payment reference"
            title={order.payment_reference ?? "Pending sync"}
            description="Payment and shipping references are now visible in the rebuilt React UI so the end-to-end flow can be checked without opening service internals."
            icon={<CreditCard size={18} strokeWidth={1.7} />}
          />
        </div>
      </div>
    </div>
  );
}
