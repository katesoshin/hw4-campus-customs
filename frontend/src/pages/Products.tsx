import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { useChatResults } from "../chatResults";
import ProductCard from "../components/ProductCard";
import type { Product } from "../types";

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("featured");
  const [inStockOnly, setInStockOnly] = useState(false);
  const { results: chatResults, query: chatQuery, clear } = useChatResults();

  useEffect(() => {
    api
      .listProducts()
      .then(setProducts)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load products"))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = products;
    if (q) {
      list = list.filter((p) =>
        [p.name, p.garment_type, p.description, ...p.colors, ...p.search_tags].join(" ").toLowerCase().includes(q)
      );
    }
    if (inStockOnly) {
      list = list.filter((p) => p.sizes.some((s) => s.quantity > 0));
    }
    const sorted = [...list];
    if (sort === "price-asc") sorted.sort((a, b) => a.price - b.price);
    else if (sort === "price-desc") sorted.sort((a, b) => b.price - a.price);
    else if (sort === "name") sorted.sort((a, b) => a.name.localeCompare(b.name));
    return sorted;
  }, [products, query, sort, inStockOnly]);

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">The Shop</h1>
          <p className="page-sub">Officially licensed Yale apparel from Campus Customs.</p>
        </div>
        <div className="shop-controls">
          <input
            className="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search — navy hoodie, quarter-zip, Harvard-Yale…"
          />
          <select className="sort" value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort products">
            <option value="featured">Featured</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
            <option value="name">Name: A–Z</option>
          </select>
          <label className="stock-toggle">
            <input type="checkbox" checked={inStockOnly} onChange={(e) => setInStockOnly(e.target.checked)} />
            In stock only
          </label>
        </div>
      </div>

      {chatResults.length > 0 && (
        <section className="spotlight" id="spotlight">
          <div className="section-head">
            <h2 className="section-title">
              Handsome Dan found {chatResults.length} match{chatResults.length === 1 ? "" : "es"}
              {chatQuery ? <span className="spotlight-q"> for “{chatQuery}”</span> : null}
            </h2>
            <button className="link" onClick={clear}>Clear</button>
          </div>
          <div className="grid">
            {chatResults.map((p) => (
              <ProductCard key={`chat-${p.product_id}`} product={p} />
            ))}
          </div>
        </section>
      )}

      {loading && <p className="muted">Loading products…</p>}
      {error && <p className="error-note">Couldn't load products: {error}. Is the backend running on :8000?</p>}

      {!loading && !error && (
        <>
          <p className="count">{filtered.length} item{filtered.length === 1 ? "" : "s"}</p>
          <div className="grid">
            {filtered.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
          {filtered.length === 0 && <p className="empty">No items match "{query}".</p>}
        </>
      )}
    </div>
  );
}
