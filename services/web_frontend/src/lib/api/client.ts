import { getSessionKey } from "@/lib/api/session";

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

interface ApiRequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  includeSession?: boolean;
}

function extractDetail(payload: unknown) {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = payload.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }

  return "The gateway request failed.";
}

function isBodyInit(body: ApiRequestOptions["body"]): body is BodyInit {
  return (
    typeof body === "string" ||
    body instanceof FormData ||
    body instanceof Blob ||
    body instanceof URLSearchParams ||
    body instanceof ArrayBuffer
  );
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}) {
  const { body, headers, includeSession = true, ...init } = options;
  const requestHeaders = new Headers(headers ?? {});
  requestHeaders.set("Accept", "application/json");

  if (includeSession) {
    requestHeaders.set("X-Session-Key", getSessionKey());
  }

  let requestBody: BodyInit | null | undefined = undefined;
  if (body !== undefined && body !== null) {
    if (isBodyInit(body)) {
      requestBody = body;
    } else {
      requestHeaders.set("Content-Type", "application/json");
      requestBody = JSON.stringify(body);
    }
  }

  const response = await fetch(path, {
    ...init,
    headers: requestHeaders,
    body: requestBody,
    credentials: "same-origin",
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    throw new ApiError(extractDetail(payload), response.status, payload);
  }

  return payload as T;
}

export function withQuery(path: string, params: Record<string, string | undefined>) {
  const url = new URL(path, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      url.searchParams.set(key, value);
    }
  });
  return `${url.pathname}${url.search}`;
}
