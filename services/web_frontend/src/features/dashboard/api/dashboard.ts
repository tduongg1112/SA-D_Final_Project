import { useQuery } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api/client";
import type {
  OrdersResponse,
  PaymentsResponse,
  ProductListResponse,
  ShipmentsResponse,
} from "@/lib/api/types";

export interface DashboardSnapshot {
  products: ProductListResponse;
  orders: OrdersResponse;
  payments: PaymentsResponse;
  shipments: ShipmentsResponse;
  grossRevenue: number;
}

async function fetchDashboardSnapshot(): Promise<DashboardSnapshot> {
  const [products, orders, payments, shipments] = await Promise.all([
    apiRequest<ProductListResponse>("/api/products/"),
    apiRequest<OrdersResponse>("/api/orders/"),
    apiRequest<PaymentsResponse>("/api/payments/"),
    apiRequest<ShipmentsResponse>("/api/shipping/"),
  ]);

  const grossRevenue = orders.items.reduce((total, order) => total + Number.parseFloat(order.total), 0);

  return {
    products,
    orders,
    payments,
    shipments,
    grossRevenue,
  };
}

export function useDashboardSnapshot() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboardSnapshot,
  });
}
