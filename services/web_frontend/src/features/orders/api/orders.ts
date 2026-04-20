import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api/client";
import type { CheckoutPayload, CheckoutResponse, OrderDetail, OrdersResponse } from "@/lib/api/types";

export const ordersQueryKey = ["orders"] as const;

export function fetchOrders() {
  return apiRequest<OrdersResponse>("/api/orders/");
}

export function fetchOrderDetail(orderId: number | string) {
  return apiRequest<OrderDetail>(`/api/orders/${orderId}/`);
}

export function useOrders() {
  return useQuery({
    queryKey: ordersQueryKey,
    queryFn: fetchOrders,
  });
}

export function useOrderDetail(orderId: string | undefined) {
  return useQuery({
    queryKey: ["orders", orderId],
    queryFn: () => fetchOrderDetail(orderId ?? ""),
    enabled: Boolean(orderId),
  });
}

export function useCheckout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CheckoutPayload) =>
      apiRequest<CheckoutResponse>("/api/orders/checkout/", {
        method: "POST",
        body: payload,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ordersQueryKey });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
