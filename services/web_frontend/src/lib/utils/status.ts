export type StatusTone = "neutral" | "primary" | "success" | "warning";

export function getStatusTone(status: string | null | undefined): StatusTone {
  const value = (status ?? "").toLowerCase();

  if (["paid", "active", "delivered", "in stock", "success"].includes(value)) {
    return "success";
  }

  if (["preparing", "pending", "processing", "confirmed", "featured"].includes(value)) {
    return "primary";
  }

  if (["low stock", "draft", "warning"].includes(value)) {
    return "warning";
  }

  return "neutral";
}
