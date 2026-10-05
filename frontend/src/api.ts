import type { AuthResponse, ChatHistoryItem, ChatResponse, Product, PublicUser } from "./types";

const TOKEN_KEY = "campus_customs_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, { ...options, headers: { ...headers, ...(options.headers || {}) } });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listProducts: () => request<Product[]>("/api/products"),
  getProduct: (id: string) => request<Product>(`/api/products/${id}`),
  register: (first_name: string, last_name: string, email: string, password: string) =>
    request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ first_name, last_name, email, password }),
    }),
  login: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<PublicUser>("/api/auth/me"),
  chat: (message: string, productId?: string) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, product_id: productId ?? null }),
    }),
  chatHistory: () => request<ChatHistoryItem[]>("/api/chat/history"),
};
