import { Route, Routes } from "react-router-dom";
import Chat from "./components/Chat";
import Navbar from "./components/Navbar";
import About from "./pages/About";
import CreateAccount from "./pages/CreateAccount";
import Home from "./pages/Home";
import Login from "./pages/Login";
import ProductDetail from "./pages/ProductDetail";
import Products from "./pages/Products";

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </main>
      <footer className="footer">
        <span>Campus Customs · Yale Bulldog Blue · 57 Broadway, New Haven, CT</span>
        <span className="footer-muted">Officially licensed Yale University merchandise</span>
      </footer>
      <Chat />
    </div>
  );
}
