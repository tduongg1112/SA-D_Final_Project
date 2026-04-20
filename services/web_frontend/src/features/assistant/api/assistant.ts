import { useMutation, useQuery } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api/client";
import { getSessionKey } from "@/lib/api/session";
import type { AIRecommendationResponse, CartItem } from "@/lib/api/types";

interface AssistantChatPayload {
  message: string;
  context?: {
    query?: string;
    cart_product_slugs?: string[];
    cart_category_names?: string[];
  };
}

function buildCartRecommendationItems(items: CartItem[]) {
  return items.map((item) => ({
    product_id: item.product_id,
    product_slug: item.product_slug,
    product_name: item.product,
    category: item.category,
    brand: item.brand,
    quantity: item.quantity,
  }));
}

function cartRecommendationSignature(items: CartItem[]) {
  return items
    .map((item) => `${item.product_slug}:${item.quantity}`)
    .sort()
    .join("|");
}

export function useSearchRecommendations(query: string) {
  return useQuery({
    queryKey: ["ai", "search", query.trim()],
    queryFn: () =>
      apiRequest<AIRecommendationResponse>("/api/ai/recommend/search/", {
        method: "POST",
        body: {
          session_key: getSessionKey(),
          query,
          source: "search",
          top_k: 4,
        },
      }),
    enabled: Boolean(query.trim()),
  });
}

export function useCartRecommendations(items: CartItem[]) {
  return useQuery({
    queryKey: ["ai", "cart", cartRecommendationSignature(items)],
    queryFn: () =>
      apiRequest<AIRecommendationResponse>("/api/ai/recommend/cart/", {
        method: "POST",
        body: {
          session_key: getSessionKey(),
          items: buildCartRecommendationItems(items),
          top_k: 4,
        },
      }),
    enabled: items.length > 0,
  });
}

export function useAssistantChat() {
  return useMutation({
    mutationFn: ({ message, context }: AssistantChatPayload) =>
      apiRequest<AIRecommendationResponse>("/api/ai/chat/", {
        method: "POST",
        body: {
          session_key: getSessionKey(),
          message,
          source: "assistant",
          context: {
            query: context?.query,
            cart_product_slugs: context?.cart_product_slugs ?? [],
            cart_category_names: context?.cart_category_names ?? [],
          },
        },
      }),
  });
}
