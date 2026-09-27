const BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed: ${res.status}`);
  }
  return data;
}

export const api = {
  getProducts: () => request("/products"),
  getCart: () => request("/cart"),
  addToCart: (productId, quantity = 1) =>
    request("/cart/add", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity }),
    }),
  updateCartItem: (productId, quantity) =>
    request("/cart/update", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity }),
    }),
  removeFromCart: (productId) =>
    request(`/cart/${productId}`, { method: "DELETE" }),
  checkout: () => request("/checkout", { method: "POST" }),
  orderNow: (productId, quantity = 1) =>
    request("/order-now", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity }),
    }),
};
