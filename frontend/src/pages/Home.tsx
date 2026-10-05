import { Link } from "react-router-dom";

const categories = [
  { label: "Hoodies & Crewnecks", tag: "cozy fleece for the Quad", img: "/cat-hoodies.png" },
  { label: "Tees", tag: "everyday Bulldog basics", img: "/cat-tees.png" },
  { label: "Quarter-Zips", tag: "class-to-gameday layers", img: "/cat-quarterzips.png" },
  { label: "Jackets", tag: "New Haven-winter ready", img: "/cat-jackets.png" },
];

export default function Home() {
  return (
    <div className="page home">
      <section className="hero">
        <div className="hero-inner">
          <p className="hero-kicker">Officially licensed Yale merch · New Haven, CT</p>
          <h1 className="hero-title">
            Big Pride, <span className="accent">Big Yale.</span>
          </h1>
          <p className="hero-sub">
            Campus Customs is your home for Yale Bulldog Blue — hoodies, crewnecks, tees and
            more, made for students, families, and alumni who bleed blue. Classic comfort,
            classic Bulldog pride.
          </p>
          <div className="hero-cta">
            <Link to="/products" className="btn btn-primary btn-lg">Shop the collection</Link>
            <Link to="/about" className="btn btn-ghost btn-lg">Our story</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <h2 className="section-title">Shop by category</h2>
        <div className="cat-grid">
          {categories.map((c) => (
            <Link key={c.label} to="/products" className="cat-card">
              <div className="cat-thumb">
                <img src={c.img} alt={c.label} loading="lazy" />
              </div>
              <span className="cat-name">{c.label}</span>
              <span className="cat-tag">{c.tag}</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section band">
        <div className="band-inner">
          <h2 className="section-title">Need a hand picking something out?</h2>
          <p className="band-sub">
            Chat with Handsome Dan, our store mascot and helper in the corner. Ask about colors, sizes,
            prices, or what's in stock — honest answers, straight from our shelves.
          </p>
        </div>
      </section>
    </div>
  );
}
