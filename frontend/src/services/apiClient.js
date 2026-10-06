export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export function backendNotConfigured() {
  throw new Error("This action will be available after backend integration.");
}

export async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}
