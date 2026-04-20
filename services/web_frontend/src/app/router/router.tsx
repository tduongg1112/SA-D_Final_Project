import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "@/app/layouts/AppShell";
import { AssistantPage } from "@/features/assistant/pages/AssistantPage";
import { CartPage } from "@/features/cart/pages/CartPage";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
import { GatewayPage } from "@/features/gateway/pages/GatewayPage";
import { OrderDetailPage } from "@/features/orders/pages/OrderDetailPage";
import { OverviewPage } from "@/features/overview/pages/OverviewPage";
import { ProductDetailPage } from "@/features/products/pages/ProductDetailPage";
import { ProductsPage } from "@/features/products/pages/ProductsPage";
import { ServicesPage } from "@/features/services/pages/ServicesPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      {
        index: true,
        element: <OverviewPage />,
      },
      {
        path: "products",
        element: <ProductsPage />,
      },
      {
        path: "products/:slug",
        element: <ProductDetailPage />,
      },
      {
        path: "cart",
        element: <CartPage />,
      },
      {
        path: "orders/:orderId",
        element: <OrderDetailPage />,
      },
      {
        path: "dashboard",
        element: <DashboardPage />,
      },
      {
        path: "gateway",
        element: <GatewayPage />,
      },
      {
        path: "assistant",
        element: <AssistantPage />,
      },
      {
        path: "services",
        element: <ServicesPage />,
      },
      {
        path: "shell-spec",
        element: <OverviewPage />,
      },
    ],
  },
]);
