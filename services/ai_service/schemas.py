from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BehaviorInput(BaseModel):
    search_count: int = Field(ge=0)
    product_view_count: int = Field(ge=0)
    detail_view_count: int = Field(ge=0)
    dwell_time_sec: int = Field(ge=0)
    add_wishlist_count: int = Field(ge=0)
    add_to_cart_count: int = Field(ge=0)
    remove_from_cart_count: int = Field(ge=0)
    purchase_count: int = Field(ge=0)


class IntentPrediction(BaseModel):
    label: str
    score: float
    confidence: float
    explanation: str
    feature_snapshot: BehaviorInput


class SearchRecommendationRequest(BaseModel):
    session_key: str
    query: str = ""
    source: str = "search"
    top_k: int = Field(default=4, ge=1, le=8)


class CartRecommendationItem(BaseModel):
    product_id: int | None = None
    product_slug: str | None = None
    product_name: str | None = None
    category: str | None = None
    brand: str | None = None
    quantity: int = Field(default=1, ge=1)


class CartRecommendationRequest(BaseModel):
    session_key: str
    items: list[CartRecommendationItem]
    top_k: int = Field(default=4, ge=1, le=8)


class ChatContext(BaseModel):
    query: str | None = None
    cart_product_slugs: list[str] = Field(default_factory=list)
    cart_category_names: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    session_key: str
    message: str
    source: str = "assistant"
    context: ChatContext = Field(default_factory=ChatContext)


class SessionEventRequest(BaseModel):
    session_key: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class RetrievalContext(BaseModel):
    backend: str
    matched_category: str | None = None
    supporting_keywords: list[str] = Field(default_factory=list)
    related_categories: list[str] = Field(default_factory=list)
    observed_intents: list[str] = Field(default_factory=list)
    retrieved_product_slugs: list[str] = Field(default_factory=list)
    retrieved_product_names: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class RecommendationProduct(BaseModel):
    id: int | None = None
    slug: str
    name: str
    brand: str
    category_name: str
    category_slug: str
    short_description: str
    price: str
    absolute_url: str
    accent_color: str
    featured: bool = False
    reason: str
    score: float


class RecommendationResponse(BaseModel):
    answer: str
    predicted_intent: IntentPrediction
    matched_category: str | None = None
    supporting_keywords: list[str] = Field(default_factory=list)
    retrieval_context: RetrievalContext
    recommended_products: list[RecommendationProduct] = Field(default_factory=list)
    suggested_prompts: list[str] = Field(default_factory=list)


class SessionEventResponse(BaseModel):
    status: str
    session_key: str
    stored_events: int


class GraphRebuildResponse(BaseModel):
    status: str
    nodes_merged: int
    relationships_merged: int
    backend: str
    detail: str | None = None


class GraphContextRequest(BaseModel):
    query: str = ""
    cart_product_slugs: list[str] = Field(default_factory=list)
    category_hints: list[str] = Field(default_factory=list)
    top_k: int = Field(default=4, ge=1, le=8)


class GraphStatusResponse(BaseModel):
    backend: str
    ready: bool
    uri: str
    load_error: str | None = None
    node_counts: dict[str, int] = Field(default_factory=dict)
    relationship_counts: dict[str, int] = Field(default_factory=dict)
