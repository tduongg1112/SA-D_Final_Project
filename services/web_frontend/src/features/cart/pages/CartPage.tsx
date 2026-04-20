import { Minus, Plus, ShoppingBag, Truck, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useCartRecommendations } from "@/features/assistant/api/assistant";
import { RecommendationRail } from "@/features/assistant/components/RecommendationRail";
import { useCart, useClearCart, useRemoveCartItem, useUpdateCartItem } from "@/features/cart/api/cart";
import { useCheckout } from "@/features/orders/api/orders";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { PanelCard } from "@/components/ui/panel-card";
import { SkeletonBlock } from "@/components/ui/skeleton-block";
import { StatusBadge } from "@/components/ui/status-badge";
import { resolveProductMedia } from "@/lib/api/media";
import { getSessionKey } from "@/lib/api/session";
import { formatCurrency } from "@/lib/utils/format";

export function CartPage() {
  const navigate = useNavigate();
  const { data: cart, isLoading, error } = useCart();
  const updateItemMutation = useUpdateCartItem();
  const removeItemMutation = useRemoveCartItem();
  const clearCartMutation = useClearCart();
  const checkoutMutation = useCheckout();
  const cartRecommendations = useCartRecommendations(cart?.items ?? []);

  const isBusy =
    updateItemMutation.isPending ||
    removeItemMutation.isPending ||
    clearCartMutation.isPending ||
    checkoutMutation.isPending;
  const errorMessage = error instanceof Error ? error.message : "The cart could not be loaded from the gateway.";
  const checkoutErrorMessage =
    checkoutMutation.error instanceof Error ? checkoutMutation.error.message : "The checkout request did not complete.";
  const aiErrorMessage = cartRecommendations.error instanceof Error ? cartRecommendations.error.message : null;

  async function handleCheckout() {
    if (!cart || cart.items.length === 0) {
      return;
    }

    try {
      const sessionKey = getSessionKey();
      const order = await checkoutMutation.mutateAsync({
        customer_name: "NovaMarket Demo User",
        customer_email: `${sessionKey.slice(0, 12)}@demo.local`,
        customer_phone: "0123456789",
        shipping_address: "NovaMarket Demo Lane, Ho Chi Minh City",
        note: "Quick checkout from rebuilt React shell",
        items: cart.items.map((item) => ({
          product_id: item.product_id,
          product_name: item.product,
          unit_price: item.price,
          quantity: item.quantity,
          line_total: item.line_total,
        })),
      });

      try {
        await clearCartMutation.mutateAsync();
      } catch {
        // Keep the user on the successful order path even if cart cleanup fails.
      }
      navigate(`/orders/${order.id}`);
    } catch {
      return;
    }
  }

  return (
    <div className="grid gap-6">
      <PageHeader
        eyebrow="Quick checkout"
        title="Cart state is now running on the real cart service."
        description="This page keeps checkout lightweight: no manual shipping form, just the actual cart payload plus a one-click demo checkout that calls the ordering flow through the gateway."
        actions={
          <>
            <Button variant="secondary" size="lg" onClick={() => navigate("/products")}>
              Continue browsing
            </Button>
            <Button
              variant="primary"
              size="lg"
              disabled={!cart?.items.length || isBusy}
              onClick={() => {
                void handleCheckout();
              }}
            >
              {checkoutMutation.isPending ? "Placing order..." : "Place demo order"}
            </Button>
          </>
        }
      />

      {isLoading ? (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_360px]">
          <div className="grid gap-4">
            {Array.from({ length: 2 }).map((_, index) => (
              <PanelCard key={`cart-skeleton-${index}`} className="p-5">
                <div className="grid gap-5 md:grid-cols-[128px_minmax(0,1fr)_160px] md:items-center">
                  <SkeletonBlock className="h-28 rounded-[20px]" />
                  <div className="grid gap-3">
                    <SkeletonBlock className="h-6 w-28" />
                    <SkeletonBlock className="h-8 w-3/4" />
                    <SkeletonBlock className="h-16 w-full" />
                  </div>
                  <div className="grid gap-3">
                    <SkeletonBlock className="h-14 w-full" />
                    <SkeletonBlock className="h-10 w-24 justify-self-end" />
                  </div>
                </div>
              </PanelCard>
            ))}
          </div>
          <SkeletonBlock className="min-h-[280px] rounded-[24px]" />
        </div>
      ) : null}

      {!isLoading && error ? (
        <EmptyState
          icon={<ShoppingBag size={18} strokeWidth={1.7} />}
          eyebrow="Gateway status"
          title="Cart data is unavailable."
          description={errorMessage}
          action={<Button onClick={() => window.location.reload()}>Retry request</Button>}
        />
      ) : null}

      {!isLoading && !error && cart && cart.items.length === 0 ? (
        <EmptyState
          icon={<ShoppingBag size={18} strokeWidth={1.7} />}
          eyebrow="Empty cart"
          title="The cart is currently empty."
          description="Browse the catalog and add a few products. The session key is already managed behind the scenes, so cart state will persist through the gateway."
          action={<Button onClick={() => navigate("/products")}>Open products</Button>}
        />
      ) : null}

      {!isLoading && !error && cart && cart.items.length > 0 ? (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_360px]">
          <div className="grid gap-4">
            {cart.items.map((item) => {
              const media = resolveProductMedia({ slug: item.product_slug, name: item.product });

              return (
                <PanelCard key={item.id} className="p-5">
                  <div className="grid gap-5 md:grid-cols-[128px_minmax(0,1fr)_160px] md:items-center">
                    <div
                      className="overflow-hidden rounded-[20px] border border-[var(--color-border)]"
                      style={{
                        background: `linear-gradient(135deg, ${item.accent_color} 0%, #ffffff 100%)`,
                      }}
                    >
                      <img src={media.imageUrl} alt={media.imageAlt} className="h-28 w-full object-cover" />
                    </div>
                    <div className="grid gap-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="label-eyebrow">{item.category}</span>
                        <StatusBadge tone="primary">{item.brand}</StatusBadge>
                      </div>
                      <div className="grid gap-1">
                        <h3 className="text-[22px] font-semibold leading-[1.1] tracking-[-0.04em] text-[var(--color-text)]">
                          {item.product}
                        </h3>
                        <p className="text-[14px] leading-6 text-[var(--color-text-soft)]">{item.short_description}</p>
                      </div>
                    </div>
                    <div className="grid gap-3">
                      <div className="flex items-center justify-between rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-3 py-3">
                        <button
                          type="button"
                          disabled={isBusy}
                          aria-label={`Decrease quantity for ${item.product}`}
                          className="flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--color-border)] bg-white disabled:cursor-not-allowed disabled:opacity-50"
                          onClick={() => {
                            if (item.quantity === 1) {
                              removeItemMutation.mutate(item.id);
                              return;
                            }
                            updateItemMutation.mutate({ itemId: item.id, quantity: item.quantity - 1 });
                          }}
                        >
                          <Minus size={14} strokeWidth={1.8} />
                        </button>
                        <span className="text-[15px] font-medium text-[var(--color-text)]">{item.quantity}</span>
                        <button
                          type="button"
                          disabled={isBusy}
                          aria-label={`Increase quantity for ${item.product}`}
                          className="flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--color-border)] bg-white disabled:cursor-not-allowed disabled:opacity-50"
                          onClick={() => updateItemMutation.mutate({ itemId: item.id, quantity: item.quantity + 1 })}
                        >
                          <Plus size={14} strokeWidth={1.8} />
                        </button>
                      </div>
                      <div className="grid gap-1 text-right">
                        <span className="text-[13px] text-[var(--color-text-faint)]">
                          {item.quantity} x {formatCurrency(item.price)}
                        </span>
                        <strong className="text-[24px] font-semibold tracking-[-0.05em] text-[var(--color-text)]">
                          {formatCurrency(item.line_total)}
                        </strong>
                      </div>
                      <Button variant="ghost" className="justify-end gap-2 px-0" onClick={() => removeItemMutation.mutate(item.id)}>
                        <Trash2 size={14} strokeWidth={1.7} />
                        Remove
                      </Button>
                    </div>
                  </div>
                </PanelCard>
              );
            })}
          </div>

          <div className="grid gap-4">
            <PanelCard
              eyebrow="Summary"
              title={`${cart.item_count} items ready`}
              description="The checkout CTA now uses a compact demo payload so no visible shipping form is required."
            >
              <div className="grid gap-4">
                {[
                  ["Subtotal", formatCurrency(cart.subtotal)],
                  ["Shipping", formatCurrency(cart.shipping_fee)],
                  ["Total", formatCurrency(cart.total)],
                ].map(([label, value], index) => (
                  <div
                    key={label}
                    className={[
                      "flex items-center justify-between gap-3 py-1 text-[15px]",
                      index === 2 ? "border-t border-[var(--color-border)] pt-4 text-[var(--color-text)]" : "text-[var(--color-text-soft)]",
                    ].join(" ")}
                  >
                    <span>{label}</span>
                    <strong className="font-semibold text-[var(--color-text)]">{value}</strong>
                  </div>
                ))}
              </div>
              <div className="mt-5 grid gap-3">
                {checkoutMutation.isError ? (
                  <div className="rounded-[18px] border border-[#f1d0d0] bg-[#fbe8e8] px-4 py-3 text-[14px] leading-6 text-[#8b4545]">
                    {checkoutErrorMessage}
                  </div>
                ) : null}
                <Button
                  variant="primary"
                  size="lg"
                  className="w-full"
                  disabled={isBusy}
                  onClick={() => {
                    void handleCheckout();
                  }}
                >
                  {checkoutMutation.isPending ? "Placing order..." : "Submit checkout"}
                </Button>
                <Button variant="secondary" size="lg" className="w-full" disabled={isBusy} onClick={() => clearCartMutation.mutate()}>
                  Clear cart
                </Button>
              </div>
            </PanelCard>

            <RecommendationRail
              eyebrow="AI cart suggestions"
              title="Add-ons ranked for the current cart"
              description="This panel calls the AI service with the real cart payload, retrieves graph complements from Neo4j when available, and proposes complementary items for the checkout stage."
              data={cartRecommendations.data}
              isLoading={cartRecommendations.isLoading}
              errorMessage={aiErrorMessage}
              emptyTitle="Fill the cart to unlock recommendations"
              emptyDescription="Once the cart contains products, the AI service will suggest complementary items and explain the ranking."
            />

            <PanelCard
              eyebrow="Checkout note"
              title="No manual shipping form in this rebuild"
              description="This is intentionally a lightweight checkout. The frontend sends a small demo profile behind the scenes so the order, payment, and shipping services can still complete the integration flow."
              icon={<Truck size={18} strokeWidth={1.7} />}
            />
          </div>
        </div>
      ) : null}
    </div>
  );
}
