import { Box, Search, ShoppingCart, SlidersHorizontal, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { useSearchRecommendations } from "@/features/assistant/api/assistant";
import { RecommendationRail } from "@/features/assistant/components/RecommendationRail";
import { useAddToCart } from "@/features/cart/api/cart";
import { useProducts } from "@/features/products/api/products";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { PanelCard } from "@/components/ui/panel-card";
import { SkeletonBlock } from "@/components/ui/skeleton-block";
import { StatusBadge } from "@/components/ui/status-badge";
import { TextField } from "@/components/ui/text-field";
import { resolveProductMedia } from "@/lib/api/media";
import { formatCurrency } from "@/lib/utils/format";
import { getStatusTone } from "@/lib/utils/status";

export function ProductsPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [draftQuery, setDraftQuery] = useState(searchParams.get("q") ?? "");

  const activeQuery = searchParams.get("q") ?? "";
  const activeCategory = searchParams.get("category") ?? "";
  const { data, isLoading, isFetching, error } = useProducts({
    query: activeQuery,
    category: activeCategory,
  });
  const aiSearch = useSearchRecommendations(activeQuery);
  const addToCartMutation = useAddToCart();

  useEffect(() => {
    setDraftQuery(activeQuery);
  }, [activeQuery]);

  const categories = data?.categories ?? [];
  const products = data?.items ?? [];
  const pendingProductId = addToCartMutation.isPending ? addToCartMutation.variables?.productId : null;
  const errorMessage = error instanceof Error ? error.message : "The product explorer could not reach the gateway.";
  const aiErrorMessage = aiSearch.error instanceof Error ? aiSearch.error.message : null;

  function applyFilters(nextQuery: string, nextCategory: string) {
    const nextParams = new URLSearchParams();
    if (nextQuery.trim()) {
      nextParams.set("q", nextQuery.trim());
    }
    if (nextCategory) {
      nextParams.set("category", nextCategory);
    }
    setSearchParams(nextParams);
  }

  function resetFilters() {
    setDraftQuery("");
    setSearchParams(new URLSearchParams());
  }

  return (
    <div className="grid gap-6">
      <PageHeader
        eyebrow="Product explorer"
        title="Browse real products through the new shell."
        description="This screen now reads the catalog from the gateway, keeps filters in the URL, and uses the new card system with real product media."
        actions={
          <>
            <Button variant="secondary" size="lg" className="gap-2" onClick={() => navigate("/cart")}>
              <ShoppingCart size={18} strokeWidth={1.7} />
              Open cart
            </Button>
            <Button variant="primary" size="lg" className="gap-2" onClick={() => navigate("/dashboard")}>
              <Sparkles size={18} strokeWidth={1.7} />
              Operator view
            </Button>
          </>
        }
      >
        <div className="grid gap-4">
          <form
            className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-center"
            onSubmit={(event) => {
              event.preventDefault();
              applyFilters(draftQuery, activeCategory);
            }}
          >
            <TextField
              type="search"
              value={draftQuery}
              onChange={(event) => setDraftQuery(event.target.value)}
              placeholder="Search products, brands, or use cases"
              icon={<Search size={18} strokeWidth={1.75} />}
            />
            <div className="flex flex-wrap items-center gap-3">
              <Button variant="secondary" className="gap-2" onClick={resetFilters}>
                <SlidersHorizontal size={16} strokeWidth={1.7} />
                Reset filters
              </Button>
              <Button variant="primary" type="submit">
                Apply search
              </Button>
            </div>
          </form>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => applyFilters(activeQuery, "")}
              className="rounded-full"
            >
              <StatusBadge tone={activeCategory ? "neutral" : "primary"}>All</StatusBadge>
            </button>
            {categories.map((category) => (
              <button
                key={category.slug}
                type="button"
                onClick={() => applyFilters(activeQuery, category.slug)}
                className="rounded-full"
              >
                <StatusBadge tone={activeCategory === category.slug ? "primary" : "neutral"}>{category.name}</StatusBadge>
              </button>
            ))}
          </div>
        </div>
      </PageHeader>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="grid gap-5 md:grid-cols-2 2xl:grid-cols-3">
          {isLoading
            ? Array.from({ length: 6 }).map((_, index) => (
                <PanelCard key={`product-skeleton-${index}`} className="grid grid-rows-[208px_auto_1fr_auto] gap-5 overflow-hidden p-0">
                  <SkeletonBlock className="rounded-none rounded-t-[24px]" />
                  <div className="px-6">
                    <SkeletonBlock className="h-8 w-28 rounded-full" />
                  </div>
                  <div className="grid gap-3 px-6">
                    <SkeletonBlock className="h-10 w-3/4" />
                    <SkeletonBlock className="h-16 w-full" />
                  </div>
                  <div className="grid gap-3 border-t border-[var(--color-border)] px-6 py-5">
                    <SkeletonBlock className="h-10 w-24" />
                    <div className="grid gap-3 md:grid-cols-2">
                      <SkeletonBlock className="h-11 w-full" />
                      <SkeletonBlock className="h-11 w-full" />
                    </div>
                  </div>
                </PanelCard>
              ))
            : null}

          {!isLoading && error ? (
            <div className="md:col-span-2 2xl:col-span-3">
              <EmptyState
                icon={<Box size={18} strokeWidth={1.7} />}
                eyebrow="Gateway status"
                title="Catalog data is not loading."
                description={errorMessage}
                action={<Button onClick={() => window.location.reload()}>Retry request</Button>}
              />
            </div>
          ) : null}

          {!isLoading && !error && products.length === 0 ? (
            <div className="md:col-span-2 2xl:col-span-3">
              <EmptyState
                icon={<Search size={18} strokeWidth={1.7} />}
                eyebrow="No results"
                title="No products match the current filter."
                description="The gateway responded successfully, but the current query or category filter returned an empty list."
                action={<Button onClick={resetFilters}>Clear search</Button>}
              />
            </div>
          ) : null}

          {!isLoading && !error
            ? products.map((product) => {
                const media = resolveProductMedia(product);

                return (
                  <PanelCard
                    key={product.slug}
                    className="grid grid-rows-[208px_auto_1fr_auto] gap-5 overflow-hidden p-0"
                  >
                    <div
                      className="rounded-t-[24px] border-b border-[var(--color-border)] p-5"
                      style={{
                        background: `linear-gradient(135deg, ${product.accent_color} 0%, #ffffff 100%)`,
                      }}
                    >
                      <div className="h-full overflow-hidden rounded-[20px] border border-white/70 bg-white/80">
                        <img
                          src={media.imageUrl}
                          alt={media.imageAlt}
                          className="h-full min-h-[168px] w-full object-cover"
                        />
                      </div>
                    </div>
                    <div className="flex items-center justify-between gap-3 px-6">
                      <span className="label-eyebrow">{product.category.name}</span>
                      <StatusBadge tone={getStatusTone(product.is_in_stock ? "in stock" : product.status_label)}>
                        {product.is_in_stock ? "In stock" : product.status_label}
                      </StatusBadge>
                    </div>
                    <div className="grid content-start gap-3 px-6">
                      <div className="grid gap-1">
                        <h3 className="text-[22px] font-semibold leading-[1.12] tracking-[-0.04em] text-[var(--color-text)]">
                          {product.name}
                        </h3>
                        <span className="text-[13px] font-medium uppercase tracking-[0.12em] text-[var(--color-text-faint)]">
                          {product.brand}
                        </span>
                      </div>
                      <p className="text-[15px] leading-7 text-[var(--color-text-soft)]">{product.short_description}</p>
                    </div>
                    <div className="grid gap-4 border-t border-[var(--color-border)] px-6 py-5">
                      <div className="flex items-end justify-between gap-3">
                        <div className="grid gap-1">
                          <strong className="text-[28px] font-semibold leading-none tracking-[-0.05em] text-[var(--color-text)]">
                            {formatCurrency(product.price)}
                          </strong>
                          <span className="text-[13px] text-[var(--color-text-faint)]">{product.stock_quantity} units available</span>
                        </div>
                        {product.featured ? <StatusBadge tone="primary">Featured</StatusBadge> : null}
                      </div>
                      <div className="grid gap-3 md:grid-cols-2">
                        <Button variant="secondary" onClick={() => navigate(`/products/${product.slug}`)}>
                          Preview
                        </Button>
                        <Button
                          variant="primary"
                          disabled={!product.is_in_stock || addToCartMutation.isPending}
                          onClick={() =>
                            addToCartMutation.mutate({
                              productId: product.id,
                              quantity: 1,
                            })
                          }
                        >
                          {pendingProductId === product.id ? "Adding..." : "Add to cart"}
                        </Button>
                      </div>
                    </div>
                  </PanelCard>
                );
              })
            : null}
        </div>

        <div className="grid gap-4">
          <PanelCard
            eyebrow="Catalog snapshot"
            title={`${products.length} live products`}
            description="The product explorer now uses gateway-backed data instead of placeholder cards."
          >
            <div className="grid gap-4">
              <div className="grid gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4">
                <span className="label-eyebrow">Filters</span>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge tone={activeQuery ? "primary" : "neutral"}>
                    {activeQuery ? `Query: ${activeQuery}` : "No keyword"}
                  </StatusBadge>
                  <StatusBadge tone={activeCategory ? "primary" : "neutral"}>
                    {activeCategory || "All categories"}
                  </StatusBadge>
                  {isFetching ? <StatusBadge tone="warning">Refreshing</StatusBadge> : null}
                </div>
              </div>
              <div className="grid gap-3 text-[15px] leading-7 text-[var(--color-text-soft)]">
                <p>The URL now carries the search state so refreshes and deep-links stay predictable.</p>
                <p>Every card keeps a consistent image, metadata, price, and action rhythm even with real API payloads.</p>
                <p>The next shopper step can now build on real cart and order contracts without rewiring catalog layout again.</p>
              </div>
            </div>
          </PanelCard>

          <RecommendationRail
            eyebrow="AI suggestions"
            title="Search-aware recommendations"
            description="The AI service reads the active search term, retrieves graph context from Neo4j when available, and ranks a shortlist without replacing the raw catalog response."
            data={aiSearch.data}
            isLoading={aiSearch.isLoading}
            errorMessage={aiErrorMessage}
            emptyTitle="Search to activate AI ranking"
            emptyDescription="Submit a keyword from the product explorer and this rail will show intent-aware recommendations."
          />
        </div>
      </div>
    </div>
  );
}
