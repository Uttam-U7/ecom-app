import React, { useEffect, useState } from "react";
import { api } from "../api.js";
import ProductCard from "../components/ProductCard.jsx";

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const all_products = async () => {
    try{
      const products = await api.getProducts();
      setProducts(products)
    } catch (err) {
      setError("Couldn't load the catalog. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    all_products();
  }, []);

  return (
    <main className="page">
      <section className="hero">
        <span className="eyebrow">catalog no. 001–006</span>
        <h1>Gear specified to the gram, the degree, the second.</h1>
        <p className="hero-sub">
          Six tools for a slower, more precise cup — each one listed the way
          we'd want it listed: material, origin, weight, price. No filler.
        </p>
      </section>

      {loading && <p className="status-text">Loading catalog…</p>}
      {error && <p className="status-text status-error">{error}</p>}

      {!loading && !error && (
        <div className="product-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </main>
  );
}
