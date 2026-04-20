export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  absolute_url: string;
  category: Category;
  brand: string;
  short_description: string;
  description: string;
  price: string;
  stock_quantity: number;
  featured: boolean;
  status: string;
  status_label: string;
  accent_color: string;
  is_in_stock: boolean;
}

export interface ProductListResponse {
  items: Product[];
  categories: Category[];
}

export interface ProductDetailResponse {
  product: Product;
  related_products: Product[];
}

export interface CartItem {
  id: number;
  product_id: number;
  product: string;
  product_slug: string;
  category: string;
  brand: string;
  short_description: string;
  accent_color: string;
  quantity: number;
  price: string;
  line_total: string;
}

export interface CartResponse {
  session_key: string;
  item_count: number;
  subtotal: string;
  shipping_fee: string;
  total: string;
  items: CartItem[];
}

export interface OrderSummary {
  id: number;
  customer_name: string;
  total: string;
  status: string;
  payment_status: string | null;
  shipping_status: string | null;
}

export interface OrderDetail {
  id: number;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  shipping_address: string;
  subtotal: string;
  shipping_fee: string;
  total: string;
  status: string;
  payment_status: string | null;
  payment_reference: string | null;
  shipping_status: string | null;
  tracking_code: string | null;
  items: Array<{
    product_id: number | null;
    product_name: string;
    unit_price: string;
    quantity: number;
    line_total: string;
  }>;
}

export interface OrdersResponse {
  items: OrderSummary[];
}

export interface PaymentRecord {
  id: number;
  order_id: number;
  provider: string;
  amount: string;
  status: string;
  transaction_reference: string;
  created_at: string;
}

export interface PaymentsResponse {
  items: PaymentRecord[];
}

export interface ShipmentRecord {
  id: number;
  order_id: number;
  recipient_name: string;
  phone: string;
  address: string;
  method: string;
  status: string;
  tracking_code: string;
  created_at: string;
}

export interface ShipmentsResponse {
  items: ShipmentRecord[];
}

export interface CheckoutPayload {
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  shipping_address: string;
  note?: string;
  items: Array<{
    product_id: number;
    product_name: string;
    unit_price: string;
    quantity: number;
    line_total: string;
  }>;
}

export interface CheckoutResponse {
  id: number;
  status: string;
  payment_status: string | null;
  shipping_status: string | null;
}

export interface AIBehaviorSnapshot {
  search_count: number;
  product_view_count: number;
  detail_view_count: number;
  dwell_time_sec: number;
  add_wishlist_count: number;
  add_to_cart_count: number;
  remove_from_cart_count: number;
  purchase_count: number;
}

export interface AIIntentPrediction {
  label: string;
  score: number;
  confidence: number;
  explanation: string;
  feature_snapshot: AIBehaviorSnapshot;
}

export interface AIRecommendationProduct {
  id: number | null;
  slug: string;
  name: string;
  brand: string;
  category_name: string;
  category_slug: string;
  short_description: string;
  price: string;
  absolute_url: string;
  accent_color: string;
  featured: boolean;
  reason: string;
  score: number;
}

export interface AIRetrievalContext {
  backend: string;
  matched_category: string | null;
  supporting_keywords: string[];
  related_categories: string[];
  observed_intents: string[];
  retrieved_product_slugs: string[];
  retrieved_product_names: string[];
  evidence: string[];
}

export interface AIRecommendationResponse {
  answer: string;
  predicted_intent: AIIntentPrediction;
  matched_category: string | null;
  supporting_keywords: string[];
  retrieval_context: AIRetrievalContext;
  recommended_products: AIRecommendationProduct[];
  suggested_prompts: string[];
}
