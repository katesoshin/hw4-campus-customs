export interface SizeStock {
  size: string;
  quantity: number;
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  sizes: SizeStock[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  products?: Product[];
}

export interface ChatResponse {
  message: string;
  products: Product[];
}

export interface ChatHistoryItem {
  role: "user" | "assistant";
  message: string;
  products: Product[];
}

export interface PublicUser {
  id: number;
  name: string;
  email: string;
  first_name?: string | null;
}

export interface AuthResponse {
  token: string;
  user: PublicUser;
}
