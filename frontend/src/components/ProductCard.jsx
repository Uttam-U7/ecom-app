import { useState } from "react";
import { useCart } from "../context/CartContext.jsx";
import { ICONS_BY_CATEGORY } from "./ProductIcons.jsx";

const formatPrice = (paise) => `₹${paise.toLocaleString("en-IN")}`;

export default function ProductCard({ product }) {
  const { addItem, createRazorpayOrder, verifyPayment } = useCart();
  const [addState, setAddState] = useState("idle"); // idle | adding | added
  const [orderState, setOrderState] = useState("idle"); // idle | ordering | confirmed | error
  const [orderId, setOrderId] = useState(null);
  const [orderError, setOrderError] = useState(null);

  const Icon = ICONS_BY_CATEGORY[product.category];

  const handleAdd = async () => {
    setAddState("adding");
    try {
      await addItem(product.id, 1);
      setAddState("added");
      setTimeout(() => setAddState("idle"), 1400);
    } catch {
      setAddState("idle");
    }
  };

  const handleOrder = async () => {
    setOrderState("ordering");
    setOrderError(null);
    try {
      const data = await createRazorpayOrder(product.id, 1);
      if (!window.Razorpay) throw new Error("Razorpay Checkout failed to load")

      const options = {
        key: data.key_id,
        amount: data.amount,
        currency: data.currency,
        name: "PayCom",
        description: `Payment for order ${data.order_id}`,
        order_id: data.order_id,
        handler: async (response) => {
          try {
            const verification = await verifyPayment(response);
            setOrderState("confirmed");
            setOrderId(verification.order_id);
          } catch (error) {
            setOrderError(error.message || "Payment verification failed");
            setOrderState("error");
          }
        },
        modal: {
          ondismiss: () => setOrderState((state) => state === "confirmed" ? state : "idle"),
        },
      };
      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (error) {
      console.error("Razorpay checkout failed", error);
      setOrderError(error.message || "Couldn't place that order. Try again.");
      setOrderState("error");
    }
  };

  return (
    <article className="product-card">
    

      <div className="product-body">
        <div className="product-heading">
          <span className="product-sku">{product.sku}</span>
          <h3 className="product-name">{product.name}</h3>
        </div>

        <p className="product-desc">{product.description}</p>

        <dl className="spec-plate">
          {Object.entries(product.specs).map(([label, value]) => (
            <div className="spec-item" key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>

        <div className="product-footer">
          <span className="product-price">{formatPrice(product.price)}</span>

          <div className="product-actions">
            <button
              type="button"
              className="btn btn-outline"
              onClick={handleAdd}
              disabled={addState !== "idle"}
            >
              {addState === "added" ? "Added ✓" : addState === "adding" ? "Adding…" : "Add to Cart"}
            </button>
            <button
              type="button"
              className="btn btn-solid"
              onClick={handleOrder}
              disabled={orderState !== "idle"}
            >
              {orderState === "ordering" ? "Placing…" : "Order Now"}
            </button>
          </div>
        </div>

        {orderState === "confirmed" && (
          <p className="order-confirm">Payment done successfully. Order #{orderId} placed.</p>
        )}
        {orderState === "error" && (
          <p className="order-error">{orderError || "Couldn't place that order. Try again."}</p>
        )}
      </div>
    </article>
  );
}
