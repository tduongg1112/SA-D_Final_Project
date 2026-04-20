import type { LucideIcon } from "lucide-react";
import {
  Bot,
  Boxes,
  ChartColumn,
  Compass,
  LayoutDashboard,
  Package,
  PanelLeft,
  Receipt,
  ServerCog,
  ShoppingCart,
  Sparkles,
} from "lucide-react";

export interface NavigationItem {
  label: string;
  path: string;
  icon: LucideIcon;
  description: string;
}

export interface NavigationSection {
  title: string;
  items: NavigationItem[];
}

export const navigationSections: NavigationSection[] = [
  {
    title: "Main",
    items: [
      {
        label: "Overview",
        path: "/",
        icon: Compass,
        description: "Landing and commerce summary",
      },
      {
        label: "Products",
        path: "/products",
        icon: Package,
        description: "Catalog explorer and browsing",
      },
      {
        label: "Cart",
        path: "/cart",
        icon: ShoppingCart,
        description: "Quick checkout workspace",
      },
      {
        label: "Orders",
        path: "/orders/demo-order",
        icon: Receipt,
        description: "Order success and status",
      },
    ],
  },
  {
    title: "Operations",
    items: [
      {
        label: "Dashboard",
        path: "/dashboard",
        icon: LayoutDashboard,
        description: "Operational view for staff",
      },
      {
        label: "Gateway",
        path: "/gateway",
        icon: ServerCog,
        description: "Routing and service visibility",
      },
      {
        label: "Services",
        path: "/services",
        icon: Boxes,
        description: "Bounded contexts and contracts",
      },
    ],
  },
  {
    title: "Future",
    items: [
      {
        label: "Assistant",
        path: "/assistant",
        icon: Bot,
        description: "AI-guided shopping shell",
      },
      {
        label: "Insights",
        path: "/assistant#insights",
        icon: Sparkles,
        description: "AI insight surface placeholder",
      },
      {
        label: "Shell",
        path: "/shell-spec",
        icon: PanelLeft,
        description: "Shell system specification view",
      },
    ],
  },
];
