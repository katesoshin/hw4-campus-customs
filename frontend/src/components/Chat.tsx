import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { useChatResults } from "../chatResults";
import type { ChatMessage } from "../types";
import Markdown from "./Markdown";
import ProductCard from "./ProductCard";

const MASCOT = "/handsome-dan.webp";

const GREETING: ChatMessage = {
  role: "assistant",
  text: "Hi! I'm Handsome Dan, the Campus Customs helper. Ask me about Yale hoodies, tees, prices, or sizes — I'll pull up matches for you. Big Pride, Big Yale!",
};

export default function Chat() {
  const { user } = useAuth();
  const { setResults } = useChatResults();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const bodyRef = useRef<HTMLDivElement>(null);

  // The product being viewed (if on a detail page), passed as page context so "this" resolves.
  const viewingId = location.pathname.match(/^\/products\/(.+)$/)?.[1];

  // Memory: load saved history when a shopper signs in; reset to greeting on sign-out.
  useEffect(() => {
    if (!user) {
      setMessages([GREETING]);
      return;
    }
    api
      .chatHistory()
      .then((items) => {
        const restored = items.map<ChatMessage>((it) => ({
          role: it.role,
          text: it.message,
          products: it.products,
        }));
        setMessages(restored.length ? restored : [GREETING]);
      })
      .catch(() => setMessages([GREETING]));
  }, [user]);

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, open]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setBusy(true);
    try {
      const res = await api.chat(text, viewingId);
      setMessages((m) => [...m, { role: "assistant", text: res.message, products: res.products }]);
      // Problem 7: surface the agent's matches as product cards on the Shop page.
      if (res.products.length > 0) {
        setResults(text, res.products);
        navigate("/products");
      }
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: `Sorry — I hit a snag: ${err instanceof Error ? err.message : "unknown error"}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button className={`chat-fab ${open ? "chat-fab-open" : ""}`} onClick={() => setOpen((o) => !o)} aria-label="Open chat">
        <img className="fab-dan" src={MASCOT} alt="Chat with Handsome Dan" />
      </button>

      {open && (
        <div className="chat-panel" role="dialog" aria-label="Campus Customs chat">
          <div className="chat-head">
            <img className="head-dan" src={MASCOT} alt="Handsome Dan" />
            <div className="chat-head-text">
              <strong>Handsome Dan</strong>
              <span className="chat-status">Campus Customs helper</span>
            </div>
            <button className="chat-x" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
          </div>

          <div className="chat-body" ref={bodyRef}>
            {messages.map((m, i) => (
              <div key={i} className={`bubble-row ${m.role}`}>
                <div className={`bubble ${m.role}`}>
                  {m.role === "assistant" ? <Markdown text={m.text} /> : m.text}
                </div>
                {m.products && m.products.length > 0 && (
                  <div className="chat-products">
                    {m.products.map((p) => (
                      <ProductCard key={p.product_id} product={p} compact />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {busy && (
              <div className="bubble-row assistant">
                <div className="bubble assistant typing"><span></span><span></span><span></span></div>
              </div>
            )}
          </div>

          <form className="chat-input" onSubmit={send}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={user ? "Ask about merch…" : "Ask about merch…"}
              disabled={busy}
            />
            <button className="btn btn-primary" type="submit" disabled={busy || !input.trim()}>Send</button>
          </form>
        </div>
      )}
    </>
  );
}
