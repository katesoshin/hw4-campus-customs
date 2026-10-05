import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import type { Product } from "../types";

const SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"];

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api
      .getProduct(id)
      .then(setProduct)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load product"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="page"><p className="muted">Loading…</p></div>;
  if (error || !product)
    return (
      <div className="page">
        <p className="error-note">{error || "Product not found."}</p>
        <Link to="/products" className="link">← Back to the shop</Link>
      </div>
    );

  const sizes = [...product.sizes].sort((a, b) => SIZE_ORDER.indexOf(a.size) - SIZE_ORDER.indexOf(b.size));
  const anyStock = sizes.some((s) => s.quantity > 0);

  return (
    <div className="page">
      <Link to="/products" className="link back">← Back to the shop</Link>
      <div className="detail">
        <div className="detail-media">
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="detail-info">
          <p className="detail-type">{product.garment_type}</p>
          <h1 className="detail-name">{product.name}</h1>
          <p className="detail-price">${product.price.toFixed(2)}</p>
          <p className="detail-desc">{product.description}</p>

          <div className="detail-block">
            <h3>Colors</h3>
            <p>{product.colors.join(", ")}</p>
          </div>

          <div className="detail-block">
            <h3>Sizes {anyStock ? "" : <span className="badge badge-out">Sold out</span>}</h3>
            <div className="size-row">
              {sizes.map((s) => (
                <span
                  key={s.size}
                  className={`size-pill ${s.quantity > 0 ? "" : "size-out"}`}
                  title={s.quantity > 0 ? `${s.quantity} in stock` : "Out of stock"}
                >
                  {s.size}
                  <small>{s.quantity > 0 ? `${s.quantity}` : "0"}</small>
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
