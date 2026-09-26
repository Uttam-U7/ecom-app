import { createContext, useContext, useEffect, useState } from "react";

const CartContext = createContext(null);
const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

// Shared helper so every call handles non-2xx responses the same way.
// (fetch only rejects on network failure, not on a 4xx/5xx status, so
// this check is what turns a failed request into a thrown error.)
async function handleResponse(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed: ${res.status}`);
  }
  return data;
}

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const applyCart = (cart) => {
    setItems(cart.items || []);
    setTotal(cart.total || 0);
    setCount(cart.count || 0);
  };

  const refresh = async () => {
    try {
      const res = await fetch(`${BASE}/cart`);
      const cart = await handleResponse(res);
      applyCart(cart);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const addItem = async (productId, quantity = 1) => {
    const res = await fetch(`${BASE}/cart/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    const cart = await handleResponse(res);
    applyCart(cart);
  };

  const createRazorpayOrder = async (productId, quantity = 1) => {
    const res = await fetch(`${BASE}/create-order`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    return handleResponse(res);
  };

  const verifyPayment = async (payment) => {
    const res = await fetch(`${BASE}/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(payment),
    });
    return handleResponse(res);
  };

  const updateItem = async (productId, quantity) => {
    const res = await fetch(`${BASE}/cart/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    const cart = await handleResponse(res);
    applyCart(cart);
  };

  const removeItem = async (productId) => {
    const res = await fetch(`${BASE}/cart/${productId}`, { method: "DELETE" });
    const cart = await handleResponse(res);
    applyCart(cart);
  };

  const payNow = async () => {
    const orderRes = await fetch(`${BASE}/create-cart-order`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const order = await handleResponse(orderRes);

    if (!window.Razorpay) throw new Error("Razorpay Checkout failed to load");

    return new Promise((resolve, reject) => {
      let settled = false;
      const fail = (error) => {
        if (settled) return;
        settled = true;
        reject(error);
      };

      const razorpay = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "PayCom",
        description: "Payment for cart",
        order_id: order.order_id,
        handler: async (response) => {
          try {
            const verification = await verifyPayment(response);
            if (settled) return;
            settled = true;
            applyCart({ items: [], total: 0, count: 0 });
            resolve(verification);
          } catch (error) {
            fail(error);
          }
        },
        modal: { ondismiss: () => fail(new Error("Payment was cancelled")) },
      });

      razorpay.on("payment.failed", () => fail(new Error("Payment failed. Please try again.")));
      razorpay.open();
    });
  };

  const value = {
    items,
    total,
    count,
    loading,
    addItem,
    createRazorpayOrder,
    verifyPayment,
    updateItem,
    removeItem,
    payNow,
    refresh,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within a CartProvider");
  return ctx;
}
