from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from graph_store import GraphContext, GraphStore
from knowledge_base import CATEGORY_KNOWLEDGE, PRODUCT_KNOWLEDGE, QUICK_PROMPTS
from model_loader import ArtifactModelBundle
from schemas import (
    BehaviorInput,
    ChatRequest,
    IntentPrediction,
    RecommendationProduct,
    RecommendationResponse,
    RetrievalContext,
    SearchRecommendationRequest,
    CartRecommendationRequest,
)
from text_utils import normalize_text, tokenize


BEHAVIOR_FEATURES = [
    "search_count",
    "product_view_count",
    "detail_view_count",
    "dwell_time_sec",
    "add_wishlist_count",
    "add_to_cart_count",
    "remove_from_cart_count",
    "purchase_count",
]

FEATURE_MAXIMA = {
    "search_count": 10,
    "product_view_count": 18,
    "detail_view_count": 10,
    "dwell_time_sec": 600,
    "add_wishlist_count": 4,
    "add_to_cart_count": 5,
    "remove_from_cart_count": 3,
    "purchase_count": 2,
}

FEATURE_WEIGHTS = {
    "search_count": 0.10,
    "product_view_count": 0.15,
    "detail_view_count": 0.15,
    "dwell_time_sec": 0.10,
    "add_wishlist_count": 0.10,
    "add_to_cart_count": 0.20,
    "remove_from_cart_count": -0.10,
    "purchase_count": 0.30,
}

def mean_feature(records: list[dict], feature: str) -> int:
    if not records:
        return 0
    return round(mean(int(record[feature]) for record in records))


@dataclass
class DatasetInsights:
    total_rows: int
    category_counts: Counter
    intent_counts: Counter
    keyword_records: dict[str, list[dict]]
    category_records: dict[str, list[dict]]


class DatasetStore:
    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path
        self.records: list[dict] = []
        self.insights = self._load()

    def _load(self) -> DatasetInsights:
        if not self.dataset_path.exists():
            return DatasetInsights(0, Counter(), Counter(), {}, {})

        keyword_records: dict[str, list[dict]] = defaultdict(list)
        category_records: dict[str, list[dict]] = defaultdict(list)
        category_counts: Counter = Counter()
        intent_counts: Counter = Counter()

        with self.dataset_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.records = list(reader)

        for record in self.records:
            keyword = normalize_text(record["last_search_keyword"])
            category = record["dominant_category"]
            keyword_records[keyword].append(record)
            category_records[category].append(record)
            category_counts[category] += 1
            intent_counts[record["target_label"]] += 1

        return DatasetInsights(
            total_rows=len(self.records),
            category_counts=category_counts,
            intent_counts=intent_counts,
            keyword_records=dict(keyword_records),
            category_records=dict(category_records),
        )

    def summarize_keyword(self, query: str) -> tuple[str | None, list[str], BehaviorInput | None]:
        query_terms = tokenize(query)
        if not query_terms:
            return None, [], None

        keyword_scores: list[tuple[int, str, list[dict]]] = []
        for keyword, records in self.insights.keyword_records.items():
            keyword_terms = tokenize(keyword)
            overlap = len(query_terms & keyword_terms)
            if overlap:
                keyword_scores.append((overlap, keyword, records))

        if not keyword_scores:
            return None, [], None

        keyword_scores.sort(key=lambda item: (-item[0], item[1]))
        top_keywords = [item[1] for item in keyword_scores[:3]]
        matched_records = []
        for _, _, records in keyword_scores[:5]:
            matched_records.extend(records)

        dominant_category = Counter(record["dominant_category"] for record in matched_records).most_common(1)[0][0]
        behaviors = BehaviorInput(
            **{
                feature: mean_feature(matched_records, feature)
                for feature in BEHAVIOR_FEATURES
            }
        )
        return dominant_category, top_keywords, behaviors

    def summarize_category(self, category_slug: str) -> BehaviorInput | None:
        records = self.insights.category_records.get(category_slug, [])
        if not records:
            return None
        return BehaviorInput(
            **{
                feature: mean_feature(records, feature)
                for feature in BEHAVIOR_FEATURES
            }
        )


class IntentEngine:
    def __init__(self, artifact_bundle: ArtifactModelBundle | None = None):
        self.artifact_bundle = artifact_bundle

    def predict(self, behavior: BehaviorInput) -> IntentPrediction:
        if self.artifact_bundle and self.artifact_bundle.is_ready:
            artifact_prediction = self.artifact_bundle.predict(behavior)
            return IntentPrediction(
                label=artifact_prediction.label,
                score=artifact_prediction.score,
                confidence=artifact_prediction.confidence,
                explanation=artifact_prediction.explanation,
                feature_snapshot=behavior,
            )

        weighted_score = 0.0
        for feature in BEHAVIOR_FEATURES:
            value = getattr(behavior, feature)
            normalized = min(value / FEATURE_MAXIMA[feature], 1.0)
            weighted_score += normalized * FEATURE_WEIGHTS[feature]

        score = max(0.0, min(weighted_score, 1.0))
        if score >= 0.65:
            label = "high_intent"
            confidence = 0.72 + min((score - 0.65) * 0.9, 0.24)
        elif score >= 0.35:
            label = "medium_intent"
            confidence = 0.64 + min(abs(score - 0.50) * 0.5, 0.16)
        else:
            label = "low_intent"
            confidence = 0.70 + min((0.35 - score) * 0.8, 0.20)

        explanation = self._build_explanation(label=label, behavior=behavior)
        return IntentPrediction(
            label=label,
            score=round(score, 3),
            confidence=round(min(confidence, 0.96), 3),
            explanation=explanation,
            feature_snapshot=behavior,
        )

    def _build_explanation(self, label: str, behavior: BehaviorInput) -> str:
        if label == "high_intent":
            return (
                "Cart and purchase signals are strong, so the shopper looks close to conversion."
            )
        if label == "medium_intent":
            return (
                "Browsing depth is meaningful, but conversion signals are still moderate."
            )
        return (
            "The session is still exploratory with light browsing and no strong cart activity."
        )


class RecommendationEngine:
    def __init__(
        self,
        dataset_store: DatasetStore,
        max_recommendations: int = 4,
        artifact_bundle: ArtifactModelBundle | None = None,
        graph_store: GraphStore | None = None,
    ):
        self.dataset_store = dataset_store
        self.intent_engine = IntentEngine(artifact_bundle=artifact_bundle)
        self.graph_store = graph_store
        self.max_recommendations = max_recommendations
        self._category_map = {item["slug"]: item for item in CATEGORY_KNOWLEDGE}
        self._product_map = {item["slug"]: item for item in PRODUCT_KNOWLEDGE}

    def graph_context(
        self,
        *,
        query: str = "",
        cart_slugs: list[str] | None = None,
        category_hints: list[str] | None = None,
        top_k: int = 4,
    ) -> GraphContext:
        if not self.graph_store:
            return GraphContext(backend="graph_disabled")
        return self.graph_store.retrieve(
            query=query,
            cart_slugs=cart_slugs,
            category_hints=category_hints,
            top_k=top_k,
        )

    def infer_category(self, text: str, product_candidates: list[dict] | None = None) -> tuple[str | None, list[str]]:
        query_terms = tokenize(text)
        if not query_terms:
            return None, []

        score_by_category: defaultdict[str, int] = defaultdict(int)
        matched_keywords: list[str] = []

        for category in CATEGORY_KNOWLEDGE:
            for keyword in category["keywords"]:
                keyword_terms = tokenize(keyword)
                overlap = len(query_terms & keyword_terms)
                if overlap:
                    score_by_category[category["slug"]] += overlap
                    matched_keywords.append(keyword)

        for product in product_candidates or []:
            if product["category_slug"]:
                score_by_category[product["category_slug"]] += 2

        if not score_by_category:
            return None, []

        category_slug = max(score_by_category, key=score_by_category.get)
        supporting_keywords = list(dict.fromkeys(matched_keywords))[:4]
        return category_slug, supporting_keywords

    def build_retrieval_context(self, graph_context: GraphContext) -> RetrievalContext:
        retrieved_product_slugs = list(dict.fromkeys(graph_context.graph_product_slugs))
        retrieved_product_names = [
            self._product_map[slug]["name"]
            for slug in retrieved_product_slugs
            if slug in self._product_map
        ]
        return RetrievalContext(
            backend=graph_context.backend,
            matched_category=graph_context.matched_category,
            supporting_keywords=graph_context.supporting_keywords[:4],
            related_categories=graph_context.related_categories[:4],
            observed_intents=graph_context.observed_intents[:4],
            retrieved_product_slugs=retrieved_product_slugs[:6],
            retrieved_product_names=retrieved_product_names[:6],
            evidence=graph_context.evidence[:4],
        )

    def score_product(
        self,
        product: dict,
        *,
        query_terms: set[str],
        preferred_categories: list[str],
        exclude_slugs: set[str],
        boosted_slugs: set[str],
    ) -> tuple[float, str]:
        if product["slug"] in exclude_slugs:
            return -1.0, ""

        score = 0.0
        reasons: list[str] = []

        if product["category_slug"] in preferred_categories:
            score += 3.0
            reasons.append("strong category fit")

        searchable_text = " ".join(
            [
                product["name"],
                product["brand"],
                product["short_description"],
                product.get("summary", ""),
                " ".join(product.get("tags", [])),
            ]
        ).lower()
        matched_terms = [term for term in query_terms if term in searchable_text]
        if matched_terms:
            score += 1.6 + (0.35 * len(matched_terms))
            reasons.append(f"matches {', '.join(matched_terms[:3])}")

        if product.get("featured"):
            score += 0.6
            reasons.append("featured item")

        if product["slug"] in boosted_slugs:
            score += 2.2
            reasons.append("pairs well with current flow")

        reason = reasons[0] if reasons else "relevant product"
        return round(score, 3), reason

    def rank_products(
        self,
        products: list[dict],
        *,
        query_text: str = "",
        preferred_categories: list[str] | None = None,
        exclude_slugs: set[str] | None = None,
        boosted_slugs: set[str] | None = None,
        top_k: int | None = None,
    ) -> list[RecommendationProduct]:
        preferred_categories = preferred_categories or []
        exclude_slugs = exclude_slugs or set()
        boosted_slugs = boosted_slugs or set()
        query_terms = tokenize(query_text)
        top_k = top_k or self.max_recommendations

        scored_products: list[tuple[float, dict, str]] = []
        for product in products:
            score, reason = self.score_product(
                product,
                query_terms=query_terms,
                preferred_categories=preferred_categories,
                exclude_slugs=exclude_slugs,
                boosted_slugs=boosted_slugs,
            )
            if score < 0:
                continue
            scored_products.append((score, product, reason))

        scored_products.sort(
            key=lambda item: (
                -item[0],
                0 if item[1].get("featured") else 1,
                item[1]["name"],
            )
        )

        return [
            RecommendationProduct(
                id=product.get("id"),
                slug=product["slug"],
                name=product["name"],
                brand=product["brand"],
                category_name=product["category_name"],
                category_slug=product["category_slug"],
                short_description=product["short_description"],
                price=product["price"],
                absolute_url=product["absolute_url"],
                accent_color=product["accent_color"],
                featured=bool(product.get("featured", False)),
                reason=reason,
                score=round(score, 3),
            )
            for score, product, reason in scored_products[:top_k]
        ]

    def behavior_from_search(self, query: str, category_slug: str | None) -> BehaviorInput:
        keyword_category, _, keyword_behavior = self.dataset_store.summarize_keyword(query)
        if keyword_behavior:
            return keyword_behavior

        category_behavior = self.dataset_store.summarize_category(category_slug or "") if category_slug else None
        if category_behavior:
            return category_behavior

        term_count = max(len(tokenize(query)), 1)
        return BehaviorInput(
            search_count=min(6, 2 + term_count),
            product_view_count=min(10, 4 + (term_count * 2)),
            detail_view_count=min(5, 1 + term_count),
            dwell_time_sec=min(320, 90 + (term_count * 55)),
            add_wishlist_count=0,
            add_to_cart_count=0,
            remove_from_cart_count=0,
            purchase_count=0,
        )

    def behavior_from_cart(self, total_items: int, distinct_items: int) -> BehaviorInput:
        return BehaviorInput(
            search_count=min(8, 3 + distinct_items),
            product_view_count=min(16, 7 + (distinct_items * 3)),
            detail_view_count=min(8, 3 + (distinct_items * 2)),
            dwell_time_sec=min(580, 240 + (total_items * 55)),
            add_wishlist_count=min(3, 1 + (distinct_items // 2)),
            add_to_cart_count=min(5, max(2, total_items + (1 if distinct_items > 1 else 0))),
            remove_from_cart_count=0,
            purchase_count=1 if total_items >= 3 else 0,
        )

    def search_response(self, request: SearchRecommendationRequest, catalog: list[dict]) -> RecommendationResponse:
        keyword_category, supporting_keywords, keyword_behavior = self.dataset_store.summarize_keyword(request.query)
        inferred_category, inferred_keywords = self.infer_category(request.query, catalog)
        graph_context = self.graph_context(query=request.query, top_k=request.top_k)
        matched_category = graph_context.matched_category or keyword_category or inferred_category

        predicted_intent = self.intent_engine.predict(
            keyword_behavior or self.behavior_from_search(request.query, matched_category)
        )

        ranked_products = self.rank_products(
            catalog,
            query_text=request.query,
            preferred_categories=[matched_category] if matched_category else [],
            boosted_slugs=set(graph_context.graph_product_slugs),
            top_k=request.top_k,
        )

        answer = (
            f"AI matched the search to {matched_category or 'a broad product discovery flow'} "
            f"with {predicted_intent.label.replace('_', ' ')}."
        )
        if graph_context.evidence:
            answer += f" {graph_context.evidence[0]}"
        if ranked_products:
            answer += f" Start with {ranked_products[0].name}"
            if len(ranked_products) > 1:
                answer += f" and {ranked_products[1].name}"
            answer += "."

        return RecommendationResponse(
            answer=answer,
            predicted_intent=predicted_intent,
            matched_category=matched_category,
            supporting_keywords=list(
                dict.fromkeys(
                    supporting_keywords
                    + inferred_keywords
                    + graph_context.supporting_keywords
                )
            )[:4],
            retrieval_context=self.build_retrieval_context(graph_context),
            recommended_products=ranked_products,
            suggested_prompts=QUICK_PROMPTS[:3],
        )

    def cart_response(self, request: CartRecommendationRequest, catalog: list[dict]) -> RecommendationResponse:
        cart_slugs = {item.product_slug for item in request.items if item.product_slug}
        cart_categories = {
            normalize_text(item.category).replace(" ", "-")
            for item in request.items
            if item.category
        }
        resolved_categories = []
        for category in cart_categories:
            if category in self._category_map:
                resolved_categories.append(category)
            else:
                for known in CATEGORY_KNOWLEDGE:
                    if normalize_text(known["name"]).replace(" ", "-") == category:
                        resolved_categories.append(known["slug"])
                        break

        boosted_slugs = set()
        for slug in cart_slugs:
            product = self._product_map.get(slug)
            if product:
                boosted_slugs.update(product.get("complements", []))
                resolved_categories.extend(self._category_map.get(product["category_slug"], {}).get("related_categories", []))

        graph_context = self.graph_context(
            cart_slugs=[slug for slug in cart_slugs if slug],
            category_hints=resolved_categories,
            top_k=request.top_k,
        )
        boosted_slugs.update(graph_context.graph_product_slugs)
        resolved_categories.extend(graph_context.related_categories)

        distinct_items = len(request.items)
        total_items = sum(item.quantity for item in request.items)
        predicted_intent = self.intent_engine.predict(self.behavior_from_cart(total_items, distinct_items))

        ranked_products = self.rank_products(
            catalog,
            preferred_categories=list(dict.fromkeys(resolved_categories)),
            exclude_slugs={slug for slug in cart_slugs if slug},
            boosted_slugs=boosted_slugs,
            top_k=request.top_k,
        )

        answer = (
            f"The cart looks {predicted_intent.label.replace('_', ' ')}. "
            "These add-ons are ranked to pair with the current selection."
        )
        if graph_context.evidence:
            answer += f" {graph_context.evidence[0]}"

        return RecommendationResponse(
            answer=answer,
            predicted_intent=predicted_intent,
            matched_category=graph_context.matched_category or (resolved_categories[0] if resolved_categories else None),
            supporting_keywords=graph_context.supporting_keywords[:4],
            retrieval_context=self.build_retrieval_context(graph_context),
            recommended_products=ranked_products,
            suggested_prompts=QUICK_PROMPTS[1:],
        )

    def chat_response(
        self,
        request: ChatRequest,
        catalog: list[dict],
        session_summary: str = "",
    ) -> RecommendationResponse:
        preferred_categories = []
        if request.context.cart_category_names:
            for name in request.context.cart_category_names:
                slug, _ = self.infer_category(name, [])
                if slug:
                    preferred_categories.append(slug)

        inferred_category, inferred_keywords = self.infer_category(request.message, catalog)
        if inferred_category:
            preferred_categories.insert(0, inferred_category)

        boosted_slugs = set(request.context.cart_product_slugs)
        for slug in request.context.cart_product_slugs:
            product = self._product_map.get(slug)
            if product:
                boosted_slugs.update(product.get("complements", []))

        graph_context = self.graph_context(
            query=request.context.query or request.message,
            cart_slugs=request.context.cart_product_slugs,
            category_hints=preferred_categories,
            top_k=4,
        )
        boosted_slugs.update(graph_context.graph_product_slugs)
        if graph_context.matched_category:
            preferred_categories.insert(0, graph_context.matched_category)

        query_seed = request.context.query or request.message
        behavior = self.behavior_from_search(query_seed, graph_context.matched_category or inferred_category)
        if request.context.cart_product_slugs:
            behavior = self.behavior_from_cart(len(request.context.cart_product_slugs), len(request.context.cart_product_slugs))

        predicted_intent = self.intent_engine.predict(behavior)
        ranked_products = self.rank_products(
            catalog,
            query_text=request.message,
            preferred_categories=list(dict.fromkeys(preferred_categories)),
            exclude_slugs=set(),
            boosted_slugs=boosted_slugs,
            top_k=4,
        )

        opening = (
            f"I read this as a {predicted_intent.label.replace('_', ' ')} shopping request."
        )
        if graph_context.matched_category or inferred_category:
            opening += f" The strongest category fit is {graph_context.matched_category or inferred_category}."
        if graph_context.evidence:
            opening += " " + " ".join(graph_context.evidence[:2])
        if session_summary:
            opening += f" {session_summary}"
        if ranked_products:
            opening += (
                f" I would shortlist {ranked_products[0].name}"
                + (f", {ranked_products[1].name}" if len(ranked_products) > 1 else "")
                + " first."
            )

        return RecommendationResponse(
            answer=opening,
            predicted_intent=predicted_intent,
            matched_category=graph_context.matched_category or inferred_category,
            supporting_keywords=list(dict.fromkeys(inferred_keywords + graph_context.supporting_keywords))[:4],
            retrieval_context=self.build_retrieval_context(graph_context),
            recommended_products=ranked_products,
            suggested_prompts=QUICK_PROMPTS,
        )
