const STORAGE_KEY = "novamarket.gateway-session";

function generateSessionKey() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `nova-${crypto.randomUUID()}`;
  }

  return `nova-${Math.random().toString(36).slice(2)}-${Date.now()}`;
}

export function getSessionKey() {
  if (typeof window === "undefined") {
    return "nova-build-session";
  }

  const existing = window.localStorage.getItem(STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const nextValue = generateSessionKey();
  window.localStorage.setItem(STORAGE_KEY, nextValue);
  return nextValue;
}
