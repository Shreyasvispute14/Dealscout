export interface ProductOffer {
  id: string;
  product_name: string;
  category: string;
  source: string;
  seller: string;
  price: number;
  original_price: number | null;
  currency: string;
  rating: number | null;
  delivery: string | null;
  discount: number | null;
  product_url: string | null;
  mode: "demo" | "live";
  is_live: boolean;
  is_mocked: boolean;
  retrieved_at: string;
}

export interface SearchResponse {
  query: string;
  category: string;
  mode: "demo" | "live";
  results: ProductOffer[];
  best_deal_id: string | null;
  live_provider_available: boolean;
  notice: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

export interface LoginResponse {
  user: User;
  message: string;
}

export interface SearchLog {
  id: string;
  query: string;
  category: string;
  mode: "demo" | "live";
  result_count: number;
  best_price: number | null;
  searched_at: string;
}

export interface SourceCount {
  source: string;
  count: number;
}

export interface AnalyticsSummary {
  total_searches: number;
  unique_queries: number;
  average_results: number;
  top_query: string | null;
  source_counts: SourceCount[];
  recent_searches: SearchLog[];
}