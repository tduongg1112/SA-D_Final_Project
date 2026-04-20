import { Activity, Box, CircleDollarSign, Truck } from "lucide-react";

import { useDashboardSnapshot } from "@/features/dashboard/api/dashboard";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { PanelCard } from "@/components/ui/panel-card";
import { SkeletonBlock } from "@/components/ui/skeleton-block";
import { StatusBadge } from "@/components/ui/status-badge";
import { formatCurrency, formatTitleCase } from "@/lib/utils/format";
import { getStatusTone } from "@/lib/utils/status";

export function DashboardPage() {
  const { data, isLoading, error } = useDashboardSnapshot();

  if (isLoading) {
    return (
      <div className="grid gap-6">
        <SkeletonBlock className="min-h-[220px] rounded-[32px]" />
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
          <div className="grid gap-6">
            <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <SkeletonBlock key={`metric-${index}`} className="min-h-[172px] rounded-[24px]" />
              ))}
            </div>
            <SkeletonBlock className="min-h-[320px] rounded-[24px]" />
          </div>
          <div className="grid gap-4">
            <SkeletonBlock className="min-h-[220px] rounded-[24px]" />
            <SkeletonBlock className="min-h-[220px] rounded-[24px]" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    const errorMessage = error instanceof Error ? error.message : "The dashboard could not aggregate gateway-backed service data.";
    return (
      <EmptyState
        eyebrow="Operator workspace"
        title="Dashboard data is unavailable."
        description={errorMessage}
      />
    );
  }

  const metrics = [
    {
      label: "Products",
      value: data.products.items.length.toString().padStart(2, "0"),
      detail: `${data.products.categories.length} categories`,
      icon: Box,
    },
    {
      label: "Orders",
      value: data.orders.items.length.toString().padStart(2, "0"),
      detail: "Recent gateway checkout records",
      icon: Activity,
    },
    {
      label: "Paid",
      value: data.payments.items.length.toString().padStart(2, "0"),
      detail: formatCurrency(data.grossRevenue),
      icon: CircleDollarSign,
    },
    {
      label: "Shipping",
      value: data.shipments.items.length.toString().padStart(2, "0"),
      detail: "Tracking state currently visible",
      icon: Truck,
    },
  ];

  return (
    <div className="grid gap-6">
      <PageHeader
        eyebrow="Operator workspace"
        title="Operations now read real service state."
        description="The dashboard aggregates products, orders, payments, and shipping through the gateway so the operator shell reflects the actual commerce flow instead of placeholder metrics."
      />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="grid gap-6">
          <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
            {metrics.map((metric) => {
              const Icon = metric.icon;
              return (
                <PanelCard
                  key={metric.label}
                  eyebrow={metric.label}
                  title={metric.value}
                  description={metric.detail}
                  icon={<Icon size={18} strokeWidth={1.7} />}
                  className="min-h-[172px]"
                />
              );
            })}
          </div>

          <PanelCard
            eyebrow="Recent orders"
            title="Gateway checkout stream"
            description="This table is now populated from the ordering service, with payment and shipping states already joined into each order summary."
          >
            <div className="grid gap-3">
              {data.orders.items.length === 0 ? (
                <div className="rounded-[18px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4 text-[15px] text-[var(--color-text-soft)]">
                  No orders have been placed yet from the rebuilt frontend flow.
                </div>
              ) : (
                data.orders.items.slice(0, 6).map((order) => (
                  <div
                    key={order.id}
                    className="grid gap-4 rounded-[18px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4 text-[14px] text-[var(--color-text-soft)] md:grid-cols-[88px_minmax(0,1fr)_120px_132px_140px]"
                  >
                    <span className="font-medium text-[var(--color-text)]">#{order.id}</span>
                    <span>{order.customer_name}</span>
                    <strong className="text-[var(--color-text)]">{formatCurrency(order.total)}</strong>
                    <StatusBadge tone={getStatusTone(order.payment_status)}>{formatTitleCase(order.payment_status)}</StatusBadge>
                    <StatusBadge tone={getStatusTone(order.shipping_status)}>{formatTitleCase(order.shipping_status)}</StatusBadge>
                  </div>
                ))
              )}
            </div>
          </PanelCard>
        </div>

        <div className="grid gap-4">
          <PanelCard
            eyebrow="Revenue snapshot"
            title={formatCurrency(data.grossRevenue)}
            description="Gross revenue here is derived from confirmed order totals already stored by the ordering service."
          >
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge tone="primary">{data.payments.items.length} payment records</StatusBadge>
              <StatusBadge tone="success">{data.shipments.items.length} shipment records</StatusBadge>
            </div>
          </PanelCard>

          <PanelCard
            eyebrow="Latest payment"
            title={data.payments.items[0]?.transaction_reference ?? "No payments yet"}
            description={
              data.payments.items[0]
                ? `${formatCurrency(data.payments.items[0].amount)} via ${data.payments.items[0].provider}`
                : "Once checkout runs through the ordering flow, the latest payment reference will appear here."
            }
          >
            {data.payments.items[0] ? (
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge tone={getStatusTone(data.payments.items[0].status)}>
                  {formatTitleCase(data.payments.items[0].status)}
                </StatusBadge>
              </div>
            ) : null}
          </PanelCard>

          <PanelCard
            eyebrow="Latest shipment"
            title={data.shipments.items[0]?.tracking_code ?? "No shipments yet"}
            description={
              data.shipments.items[0]
                ? data.shipments.items[0].address
                : "Shipment tracking will appear here after the quick checkout flow is exercised."
            }
          >
            {data.shipments.items[0] ? (
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge tone={getStatusTone(data.shipments.items[0].status)}>
                  {formatTitleCase(data.shipments.items[0].status)}
                </StatusBadge>
              </div>
            ) : null}
          </PanelCard>
        </div>
      </div>
    </div>
  );
}
