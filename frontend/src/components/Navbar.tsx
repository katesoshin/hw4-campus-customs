import { NavLink } from "react-router-dom";
import { useAuth } from "../auth";

const links = [
  { to: "/", label: "Home", end: true },
  { to: "/products", label: "Products" },
  { to: "/about", label: "About Us" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <header className="nav">
      <div className="nav-inner">
        <NavLink to="/" className="brand">
          <span className="brand-mark">CC</span>
          <span className="brand-text">
            <span className="brand-name">Campus Customs</span>
            <span className="brand-tag">Yale Bulldog Blue</span>
          </span>
        </NavLink>

        <nav className="nav-links">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className="nav-auth">
          {user ? (
            <>
              <span className="nav-hi">Hi, {user.first_name || user.name}</span>
              <button className="btn btn-ghost" onClick={logout}>Sign out</button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn btn-ghost">Log In</NavLink>
              <NavLink to="/create-account" className="btn btn-primary">Create account</NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
