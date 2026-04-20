import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api/client";
import type { CartResponse } from "@/lib/api/types";

export const cartQueryKey = ["cart"] as const;

interface AddToCartInput {
  productId: number;
  quantity?: number;
}

interface UpdateCartItemInput {
  itemId: number;
  quantity: number;
}

export function fetchCart() {
  return apiRequest<CartResponse>("/api/cart/");
}

export function useCart() {
  return useQuery({
    queryKey: cartQueryKey,
    queryFn: fetchCart,
  });
}

export function useAddToCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ productId, quantity = 1 }: AddToCartInput) =>
      apiRequest<CartResponse>("/api/cart/items/", {
        method: "POST",
        body: {
          product_id: productId,
          quantity,
        },
      }),
    onSuccess: (cart) => {
      queryClient.setQueryData(cartQueryKey, cart);
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdateCartItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, quantity }: UpdateCartItemInput) =>
      apiRequest<CartResponse>(`/api/cart/items/${itemId}/`, {
        method: "PATCH",
        body: { quantity },
      }),
    onSuccess: (cart) => {
      queryClient.setQueryData(cartQueryKey, cart);
    },
  });
}

export function useRemoveCartItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: number) =>
      apiRequest<CartResponse>(`/api/cart/items/${itemId}/remove/`, {
        method: "DELETE",
      }),
    onSuccess: (cart) => {
      queryClient.setQueryData(cartQueryKey, cart);
    },
  });
}

export function useClearCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      apiRequest<CartResponse>("/api/cart/clear/", {
        method: "POST",
      }),
    onSuccess: (cart) => {
      queryClient.setQueryData(cartQueryKey, cart);
    },
  });
}
