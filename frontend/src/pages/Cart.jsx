import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext.jsx";

const formatPrice = (paise) => `₹${paise.toLocaleString("en-IN")}`;

export default function Cart() {
  const { items, total, loading, updateItem, removeItem, payNow } = useCart();
  const [paying, setPaying] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [error, setError] = useState(null);

  const handlePayNow = async () => {
    setPaying(true);
    setError(null);
    try {
      const order = await payNow();
      setConfirmation(order);
    } catch (err) {
      setError(err.message || "Payment failed. Please try again.");
    } finally {
      setPaying(false);
    }
  };

  if (confirmation) {
    return (
      <main className="page">
        <section className="receipt confirmation">
          <span className="eyebrow">order confirmed</span>
          <h2>Order #{confirmation.order_id}</h2>
          <p className="hero-sub">
            {confirmation.items.length} item{confirmation.items.length > 1 ? "s" : ""}{" "}
            &middot; {formatPrice(confirmation.total)} charged. Brewing excellence awaits.
          </p>
          <Link to="/" className="btn btn-solid">Continue Shopping</Link>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="page-heading">
        <span className="eyebrow">order receipt</span>
        <h1>Your Cart</h1>
      </section>

      {loading && <p className="status-text">Loading cart…</p>}

      {!loading && items.length === 0 && (
        <div className="empty-cart">
          <p>Your cart is empty. Time to go shopping.</p>
          <Link to="/" className="btn btn-outline">Browse the Catalog</Link>
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="receipt">
          <div className="receipt-rows">
            {items.map((item) => (
              <div className="receipt-row" key={item.product_id}>
                <div className="receipt-row-main">
                  <div className="receipt-item-info">
                    <span className="receipt-sku">{item.sku}</span>
                    <span className="receipt-name">{item.name}</span>
                  </div>
                  <span className="receipt-leader" />
                  <span className="receipt-subtotal">{formatPrice(item.subtotal)}</span>
                </div>

                <div className="receipt-row-controls">
                  <div className="qty-stepper">
                    <button
                      type="button"
                      aria-label={`Decrease quantity of ${item.name}`}
                      onClick={() => updateItem(item.product_id, item.quantity - 1)}
                    >
                      −
                    </button>
                    <span>{item.quantity}</span>
                    <button
                      type="button"
                      aria-label={`Increase quantity of ${item.name}`}
                      onClick={() => updateItem(item.product_id, item.quantity + 1)}
                    >
                      +
                    </button>
                  </div>
                  <span className="unit-price">{formatPrice(item.price)} each</span>
                  <button
                    type="button"
                    className="remove-btn"
                    onClick={() => removeItem(item.product_id)}
                    aria-label={`Remove ${item.name} from cart`}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="receipt-total">
            <span>Total</span>
            <span>{formatPrice(total)}</span>
          </div>

          {error && <p className="status-text status-error">{error}</p>}

          <button
            type="button"
            className="btn btn-solid btn-pay"
            onClick={handlePayNow}
            disabled={paying}
          >
            {paying ? "Processing…" : `Pay Now — ${formatPrice(total)}`}
          </button>
        </div>
      )}
    </main>
  );
}
