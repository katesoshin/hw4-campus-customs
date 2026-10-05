import { createContext, useContext, useState, type ReactNode } from "react";
import type { Product } from "./types";

// Shared state so the chat widget can push matching products onto the page (the Shop),
// where they render as product cards. This is the front-end side of the Problem 7 contract:
// agent returns structured matches -> chat stores them here -> the Shop renders them.
interface ChatResultsValue {
  results: Product[];
  query: string | null;
  setResults: (query: string, products: Product[]) => void;
  clear: () => void;
}

const ChatResultsContext = createContext<ChatResultsValue | null>(null);

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResultsState] = useState<Product[]>([]);
  const [query, setQuery] = useState<string | null>(null);

  function setResults(q: string, products: Product[]) {
    setQuery(q);
    setResultsState(products);
  }
  function clear() {
    setQuery(null);
    setResultsState([]);
  }

  return (
    <ChatResultsContext.Provider value={{ results, query, setResults, clear }}>
      {children}
    </ChatResultsContext.Provider>
  );
}

export function useChatResults() {
  const ctx = useContext(ChatResultsContext);
  if (!ctx) throw new Error("useChatResults must be used within ChatResultsProvider");
  return ctx;
}
