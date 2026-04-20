import { useQuery } from "@tanstack/react-query";

import { apiRequest, withQuery } from "@/lib/api/client";
import type { ProductDetailResponse, ProductListResponse } from "@/lib/api/types";

interface ProductsFilters {
  query?: string;
  category?: string;
}

export function productsQueryKey(filters: ProductsFilters = {}) {
  return ["products", filters.query ?? "", filters.category ?? ""] as const;
}

export function fetchProducts(filters: ProductsFilters = {}) {
  return apiRequest<ProductListResponse>(
    withQuery("/api/products/", {
      q: filters.query?.trim() || undefined,
      category: filters.category || undefined,
    }),
  );
}

export function fetchProductDetail(slug: string) {
  return apiRequest<ProductDetailResponse>(`/api/products/${slug}/`);
}

export function useProducts(filters: ProductsFilters = {}) {
  return useQuery({
    queryKey: productsQueryKey(filters),
    queryFn: () => fetchProducts(filters),
  });
}

export function useProductDetail(slug: string | undefined) {
  return useQuery({
    queryKey: ["product", slug],
    queryFn: () => fetchProductDetail(slug ?? ""),
    enabled: Boolean(slug),
  });
}
