import { Link } from "react-router-dom";
import type { Product } from "../types";

export default function ProductCard({ product, compact = false }: { product: Product; compact?: boolean }) {
  const anyStock = product.sizes.some((s) => s.quantity > 0);
  const short =
    product.description.length > 90 ? product.description.slice(0, 88).trimEnd() + "…" : product.description;

  return (
    <Link to={`/products/${product.product_id}`} className={`card ${compact ? "card-compact" : ""}`}>
      <div className="card-img-wrap">
        <img className="card-img" src={product.image_url} alt={product.name} loading="lazy" />
        {!anyStock && <span className="badge badge-out">Sold out</span>}
      </div>
      <div className="card-body">
        <h3 className="card-name">{product.name}</h3>
        {!compact && <p className="card-desc">{short}</p>}
        <div className="card-row">
          <span className="card-price">${product.price.toFixed(2)}</span>
          <span className="card-type">{product.garment_type}</span>
        </div>
      </div>
    </Link>
  );
}
