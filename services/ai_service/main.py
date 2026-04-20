from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI

from app_config import settings
from catalog_client import CatalogClient
from graph_store import GraphStore
from intelligence import DatasetStore, RecommendationEngine
from model_loader import ArtifactModelBundle
from schemas import (
    BehaviorInput,
    ChatRequest,
    CartRecommendationRequest,
    GraphContextRequest,
    GraphRebuildResponse,
    GraphStatusResponse,
    IntentPrediction,
    RetrievalContext,
    SearchRecommendationRequest,
    SessionEventRequest,
    SessionEventResponse,
)


app = FastAPI(title="NovaMarket AI Service", version="2.0.0")

dataset_store = DatasetStore(Path(settings.dataset_path))
catalog_client = CatalogClient(settings)
artifact_bundle = ArtifactModelBundle.from_settings(settings)
graph_store = GraphStore(settings, dataset_store)
recommendation_engine = RecommendationEngine(
    dataset_store=dataset_store,
    max_recommendations=settings.max_recommendations,
    artifact_bundle=artifact_bundle,
    graph_store=graph_store,
)
SESSION_EVENTS: dict[str, list[dict]] = defaultdict(list)


if settings.neo4j_auto_sync:
    graph_store.rebuild_graph()


@app.on_event("shutdown")
def shutdown_resources():
    graph_store.close()


def remember_event(session_key: str, event_type: str, payload: dict) -> None:
    SESSION_EVENTS[session_key].append(
        {
            "event_type": event_type,
            "payload": payload,
            "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
        }
    )
    if len(SESSION_EVENTS[session_key]) > 20:
        SESSION_EVENTS[session_key] = SESSION_EVENTS[session_key][-20:]


def session_summary(session_key: str) -> str:
    events = SESSION_EVENTS.get(session_key, [])
    if not events:
        return ""
    last_events = ", ".join(event["event_type"] for event in events[-3:])
    return f"Recent session events include {last_events}."


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.service_name,
        "dataset_loaded": dataset_store.insights.total_rows,
        "session_memory": len(SESSION_EVENTS),
        "model": artifact_bundle.summary(),
        "graph": graph_store.summary(),
    }


@app.post("/api/ai/predict-intent/", response_model=IntentPrediction)
def predict_intent(payload: BehaviorInput):
    return recommendation_engine.intent_engine.predict(payload)


@app.post("/api/ai/recommend/search/")
async def recommend_for_search(payload: SearchRecommendationRequest):
    catalog = await catalog_client.fetch_catalog(query=payload.query)
    response = recommendation_engine.search_response(payload, catalog)
    remember_event(
        payload.session_key,
        "search_recommendation",
        {
            "query": payload.query,
            "matched_category": response.matched_category,
            "intent": response.predicted_intent.label,
        },
    )
    return response


@app.post("/api/ai/recommend/cart/")
async def recommend_for_cart(payload: CartRecommendationRequest):
    catalog = await catalog_client.fetch_catalog()
    response = recommendation_engine.cart_response(payload, catalog)
    remember_event(
        payload.session_key,
        "cart_recommendation",
        {
            "items": [item.model_dump() for item in payload.items],
            "matched_category": response.matched_category,
            "intent": response.predicted_intent.label,
        },
    )
    return response


@app.post("/api/ai/chat/")
async def ai_chat(payload: ChatRequest):
    catalog = await catalog_client.fetch_catalog(query=payload.context.query or payload.message)
    response = recommendation_engine.chat_response(
        payload,
        catalog,
        session_summary=session_summary(payload.session_key),
    )
    remember_event(
        payload.session_key,
        "chat_message",
        {
            "message": payload.message,
            "matched_category": response.matched_category,
            "intent": response.predicted_intent.label,
        },
    )
    return response


@app.post("/api/ai/events/", response_model=SessionEventResponse)
def store_session_event(payload: SessionEventRequest):
    remember_event(payload.session_key, payload.event_type, payload.payload)
    return SessionEventResponse(
        status="stored",
        session_key=payload.session_key,
        stored_events=len(SESSION_EVENTS[payload.session_key]),
    )


@app.post("/api/ai/graph/rebuild/", response_model=GraphRebuildResponse)
def rebuild_graph():
    result = graph_store.rebuild_graph()
    return GraphRebuildResponse(
        status=result.status,
        nodes_merged=result.nodes_merged,
        relationships_merged=result.relationships_merged,
        backend=result.backend,
        detail=result.detail,
    )


@app.get("/api/ai/graph/status/", response_model=GraphStatusResponse)
def graph_status():
    summary = graph_store.summary()
    overview = graph_store.overview()
    return GraphStatusResponse(
        backend=summary["backend"],
        ready=summary["ready"],
        uri=summary["uri"],
        load_error=summary["load_error"],
        node_counts=overview["node_counts"],
        relationship_counts=overview["relationship_counts"],
    )


@app.post("/api/ai/graph/context/", response_model=RetrievalContext)
def graph_context(payload: GraphContextRequest):
    context = recommendation_engine.graph_context(
        query=payload.query,
        cart_slugs=payload.cart_product_slugs,
        category_hints=payload.category_hints,
        top_k=payload.top_k,
    )
    return recommendation_engine.build_retrieval_context(context)
