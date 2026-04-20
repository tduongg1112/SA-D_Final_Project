import { ArrowLeft, BadgeInfo, Package, ShieldCheck, ShoppingCart, Sparkles } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import { useAddToCart } from "@/features/cart/api/cart";
import { useProductDetail } from "@/features/products/api/products";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { PanelCard } from "@/components/ui/panel-card";
import { SkeletonBlock } from "@/components/ui/skeleton-block";
import { StatusBadge } from "@/components/ui/status-badge";
import { resolveProductMedia } from "@/lib/api/media";
import { formatCurrency, formatTitleCase } from "@/lib/utils/format";
import { getStatusTone } from "@/lib/utils/status";

export function ProductDetailPage() {
  const navigate = useNavigate();
  const { slug } = useParams();
  const { data, isLoading, error } = useProductDetail(slug);
  const addToCartMutation = useAddToCart();

  if (!slug) {
    return (
      <EmptyState
        eyebrow="Product detail"
        title="No product was selected."
        description="The detail route opened without a valid product slug."
        action={<Button onClick={() => navigate("/products")}>Back to products</Button>}
      />
    );
  }

  if (isLoading) {
    return (
      <div className="grid gap-6">
        <PanelCard eyebrow="Product detail" title="Loading product payload" description="The page grammar is ready and waiting for the gateway response.">
          <div className="flex flex-wrap items-center gap-3">
            <SkeletonBlock className="h-12 w-40" />
            <SkeletonBlock className="h-12 w-36" />
          </div>
        </PanelCard>
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(360px,0.92fr)]">
          <SkeletonBlock className="min-h-[420px] rounded-[24px]" />
          <SkeletonBlock className="min-h-[420px] rounded-[24px]" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    const errorMessage = error instanceof Error ? error.message : "The selected product could not be loaded from the gateway.";
    return (
      <EmptyState
        eyebrow="Product detail"
        title="Product detail is unavailable."
        description={errorMessage}
        action={<Button onClick={() => navigate("/products")}>Return to products</Button>}
      />
    );
  }

  const { product, related_products: relatedProducts } = data;
  const media = resolveProductMedia(product);
  const pendingProductId = addToCartMutation.isPending ? addToCartMutation.variables?.productId : null;

  return (
    <div className="grid gap-6">
      <PanelCard
        eyebrow="Product detail"
        title={product.name}
        description="The detail page now reads the real product payload, keeps summary spacing disciplined, and reuses the same media + action hierarchy as the catalog grid."
      >
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="secondary" className="gap-2" onClick={() => navigate(-1)}>
            <ArrowLeft size={16} strokeWidth={1.7} />
            Back to products
          </Button>
          <Button
            variant="primary"
            className="gap-2"
            disabled={!product.is_in_stock || addToCartMutation.isPending}
            onClick={() => addToCartMutation.mutate({ productId: product.id })}
          >
            <ShoppingCart size={16} strokeWidth={1.7} />
            {pendingProductId === product.id ? "Adding..." : "Add to cart"}
          </Button>
        </div>
      </PanelCard>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(360px,0.92fr)]">
        <PanelCard className="min-h-[420px] overflow-hidden p-5">
          <div
            className="grid h-full gap-4 rounded-[24px] border border-white/70 p-4"
            style={{
              background: `linear-gradient(135deg, ${product.accent_color} 0%, #ffffff 100%)`,
            }}
          >
            <div className="overflow-hidden rounded-[20px] border border-white/80 bg-white/80">
              <img src={media.imageUrl} alt={media.imageAlt} className="h-[320px] w-full object-cover" />
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {[
                { label: "Brand", value: product.brand, icon: Sparkles },
                { label: "Category", value: product.category.name, icon: Package },
                { label: "Status", value: product.is_in_stock ? "In stock" : product.status_label, icon: ShieldCheck },
              ].map((item) => {
                const Icon = item.icon;

                return (
                  <div
                    key={item.label}
                    className="grid grid-cols-[32px_minmax(0,1fr)] gap-3 rounded-[20px] border border-white/80 bg-white/70 p-4 backdrop-blur-sm"
                  >
                    <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-[var(--color-accent)]">
                      <Icon size={18} strokeWidth={1.7} />
                    </span>
                    <div className="grid gap-1">
                      <span className="label-eyebrow">{item.label}</span>
                      <strong className="text-[15px] font-medium text-[var(--color-text)]">{item.value}</strong>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </PanelCard>

        <div className="grid gap-6">
          <PanelCard eyebrow="Summary" title={formatCurrency(product.price)} description={product.short_description}>
            <div className="grid gap-4">
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge tone={getStatusTone(product.status_label)}>{product.status_label}</StatusBadge>
                <StatusBadge tone={product.featured ? "primary" : "neutral"}>
                  {product.featured ? "Featured" : "Standard"}
                </StatusBadge>
                <StatusBadge tone={product.is_in_stock ? "success" : "warning"}>
                  {product.stock_quantity} in stock
                </StatusBadge>
              </div>
              <p className="text-[15px] leading-7 text-[var(--color-text-soft)]">{product.description}</p>
              <div className="grid gap-3 md:grid-cols-2">
                {[
                  { icon: BadgeInfo, label: "Route", value: `/api/products/${product.slug}/` },
                  { icon: BadgeInfo, label: "Display status", value: formatTitleCase(product.status) },
                  { icon: Package, label: "Category slug", value: product.category.slug },
                  { icon: ShieldCheck, label: "Absolute URL", value: product.absolute_url },
                ].map((item) => {
                  const Icon = item.icon;
                  return (
                    <div
                      key={item.label}
                      className="grid grid-cols-[32px_minmax(0,1fr)] items-start gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4"
                    >
                      <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-[var(--color-accent)]">
                        <Icon size={18} strokeWidth={1.7} />
                      </span>
                      <div className="grid gap-1">
                        <span className="label-eyebrow">{item.label}</span>
                        <strong className="break-all text-[15px] font-medium text-[var(--color-text)]">{item.value}</strong>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </PanelCard>

          <PanelCard
            eyebrow="Related products"
            title={`${relatedProducts.length} more from this category`}
            description="Related products are already coming from the product service contract, so later recommendation work can build on a real product graph."
          >
            <div className="grid gap-3">
              {relatedProducts.length === 0 ? (
                <div className="rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4 text-[15px] text-[var(--color-text-soft)]">
                  No related products were returned for this category yet.
                </div>
              ) : (
                relatedProducts.map((item) => (
                  <button
                    key={item.slug}
                    type="button"
                    onClick={() => navigate(`/products/${item.slug}`)}
                    className="grid gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4 text-left transition hover:border-[var(--color-border-strong)] hover:bg-white"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <strong className="text-[16px] font-medium text-[var(--color-text)]">{item.name}</strong>
                      <StatusBadge tone={item.featured ? "primary" : "neutral"}>
                        {item.featured ? "Featured" : "Related"}
                      </StatusBadge>
                    </div>
                    <p className="text-[14px] leading-6 text-[var(--color-text-soft)]">{item.short_description}</p>
                  </button>
                ))
              )}
            </div>
          </PanelCard>
        </div>
      </div>
    </div>
  );
}
