from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from typing import Any

from app_config import Settings
from knowledge_base import CATEGORY_KNOWLEDGE, PRODUCT_KNOWLEDGE
from text_utils import normalize_text, tokenize

if TYPE_CHECKING:
    from intelligence import DatasetStore


@dataclass
class GraphRebuildResult:
    status: str
    nodes_merged: int
    relationships_merged: int
    backend: str
    detail: str | None = None


@dataclass
class GraphContext:
    backend: str
    matched_category: str | None = None
    supporting_keywords: list[str] = field(default_factory=list)
    graph_product_slugs: list[str] = field(default_factory=list)
    related_categories: list[str] = field(default_factory=list)
    observed_intents: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


class GraphStore:
    def __init__(self, settings: Settings, dataset_store: "DatasetStore"):
        self.settings = settings
        self.dataset_store = dataset_store
        self.driver: Any | None = None
        self.backend = "graph_unavailable"
        self.load_error: str | None = None
        self._connect()

    def _connect(self) -> None:
        if not self.settings.neo4j_uri:
            self.load_error = "NEO4J_URI is not configured."
            return

        try:
            from neo4j import GraphDatabase
        except Exception as exc:
            self.load_error = f"Neo4j driver unavailable: {exc}"
            return

        try:
            self.driver = GraphDatabase.driver(
                self.settings.neo4j_uri,
                auth=(self.settings.neo4j_user, self.settings.neo4j_password),
            )
            self.driver.verify_connectivity()
            self.backend = "neo4j"
            self.load_error = None
        except Exception as exc:
            self.driver = None
            self.load_error = f"Neo4j connectivity failed: {exc}"

    @property
    def is_ready(self) -> bool:
        return self.driver is not None

    def summary(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "ready": self.is_ready,
            "uri": self.settings.neo4j_uri,
            "load_error": self.load_error,
        }

    def overview(self) -> dict[str, dict[str, int]]:
        if not self.driver:
            return {
                "node_counts": {},
                "relationship_counts": {},
            }

        node_rows = self._run(
            """
            MATCH (n)
            UNWIND labels(n) AS label
            RETURN label, count(*) AS count
            ORDER BY label ASC
            """
        )
        relationship_rows = self._run(
            """
            MATCH ()-[r]->()
            RETURN type(r) AS label, count(*) AS count
            ORDER BY label ASC
            """
        )
        return {
            "node_counts": {row["label"]: int(row["count"]) for row in node_rows},
            "relationship_counts": {row["label"]: int(row["count"]) for row in relationship_rows},
        }

    def _run(self, query: str, parameters: dict | None = None) -> list[dict]:
        if not self.driver:
            return []
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    def rebuild_graph(self) -> GraphRebuildResult:
        if not self.driver:
            return GraphRebuildResult(
                status="skipped",
                nodes_merged=0,
                relationships_merged=0,
                backend=self.backend,
                detail=self.load_error,
            )

        constraints = [
            "CREATE CONSTRAINT category_slug IF NOT EXISTS FOR (c:Category) REQUIRE c.slug IS UNIQUE",
            "CREATE CONSTRAINT product_slug IF NOT EXISTS FOR (p:Product) REQUIRE p.slug IS UNIQUE",
            "CREATE CONSTRAINT keyword_name IF NOT EXISTS FOR (k:Keyword) REQUIRE k.name IS UNIQUE",
            "CREATE CONSTRAINT intent_name IF NOT EXISTS FOR (i:Intent) REQUIRE i.name IS UNIQUE",
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT session_id IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE",
        ]
        for statement in constraints:
            self._run(statement)

        categories_payload = [
            {
                "slug": category["slug"],
                "name": category["name"],
                "keywords": category["keywords"],
                "related_categories": category["related_categories"],
            }
            for category in CATEGORY_KNOWLEDGE
        ]
        self._run(
            """
            UNWIND $categories AS category
            MERGE (c:Category {slug: category.slug})
            SET c.name = category.name,
                c.keywords = category.keywords
            """,
            {"categories": categories_payload},
        )

        products_payload = [
            {
                "id": product["id"],
                "slug": product["slug"],
                "name": product["name"],
                "brand": product["brand"],
                "category_slug": product["category_slug"],
                "category_name": product["category_name"],
                "short_description": product["short_description"],
                "summary": product["summary"],
                "price": product["price"],
                "featured": bool(product["featured"]),
                "accent_color": product["accent_color"],
                "tags": product["tags"],
                "complements": product["complements"],
            }
            for product in PRODUCT_KNOWLEDGE
        ]
        self._run(
            """
            UNWIND $products AS product
            MERGE (p:Product {slug: product.slug})
            SET p.product_id = product.id,
                p.name = product.name,
                p.brand = product.brand,
                p.short_description = product.short_description,
                p.summary = product.summary,
                p.price = product.price,
                p.featured = product.featured,
                p.accent_color = product.accent_color,
                p.tags = product.tags
            MERGE (c:Category {slug: product.category_slug})
            ON CREATE SET c.name = product.category_name
            MERGE (c)-[:CONTAINS]->(p)
            """,
            {"products": products_payload},
        )

        complement_edges = [
            {"source": product["slug"], "target": target}
            for product in PRODUCT_KNOWLEDGE
            for target in product["complements"]
        ]
        self._run(
            """
            UNWIND $edges AS edge
            MATCH (source:Product {slug: edge.source})
            MATCH (target:Product {slug: edge.target})
            MERGE (source)-[:COMPLEMENTS]->(target)
            """,
            {"edges": complement_edges},
        )

        related_edges = [
            {"source": category["slug"], "target": target}
            for category in CATEGORY_KNOWLEDGE
            for target in category["related_categories"]
        ]
        self._run(
            """
            UNWIND $edges AS edge
            MATCH (source:Category {slug: edge.source})
            MATCH (target:Category {slug: edge.target})
            MERGE (source)-[:RELATED_TO]->(target)
            """,
            {"edges": related_edges},
        )

        dataset_rows = [
            {
                "user_id": record["user_id"],
                "session_id": record["session_id"],
                "last_search_keyword": normalize_text(record["last_search_keyword"]),
                "dominant_category": record["dominant_category"],
                "target_label": record["target_label"],
                "search_count": int(record["search_count"]),
                "product_view_count": int(record["product_view_count"]),
                "detail_view_count": int(record["detail_view_count"]),
                "dwell_time_sec": int(record["dwell_time_sec"]),
                "add_wishlist_count": int(record["add_wishlist_count"]),
                "add_to_cart_count": int(record["add_to_cart_count"]),
                "remove_from_cart_count": int(record["remove_from_cart_count"]),
                "purchase_count": int(record["purchase_count"]),
            }
            for record in self.dataset_store.records
        ]
        self._run(
            """
            UNWIND $rows AS row
            MERGE (u:User {user_id: row.user_id})
            MERGE (s:Session {session_id: row.session_id})
            SET s.search_count = row.search_count,
                s.product_view_count = row.product_view_count,
                s.detail_view_count = row.detail_view_count,
                s.dwell_time_sec = row.dwell_time_sec,
                s.add_wishlist_count = row.add_wishlist_count,
                s.add_to_cart_count = row.add_to_cart_count,
                s.remove_from_cart_count = row.remove_from_cart_count,
                s.purchase_count = row.purchase_count
            MERGE (k:Keyword {name: row.last_search_keyword})
            MERGE (c:Category {slug: row.dominant_category})
            MERGE (i:Intent {name: row.target_label})
            MERGE (u)-[:HAS_SESSION]->(s)
            MERGE (s)-[searched:SEARCHED]->(k)
            SET searched.count = row.search_count
            MERGE (s)-[interest:INTERESTED_IN]->(c)
            SET interest.product_view_count = row.product_view_count,
                interest.detail_view_count = row.detail_view_count,
                interest.dwell_time_sec = row.dwell_time_sec,
                interest.add_wishlist_count = row.add_wishlist_count,
                interest.add_to_cart_count = row.add_to_cart_count,
                interest.remove_from_cart_count = row.remove_from_cart_count,
                interest.purchase_count = row.purchase_count
            MERGE (s)-[:HAS_INTENT]->(i)
            MERGE (k)-[:RELATES_TO]->(c)
            """,
            {"rows": dataset_rows},
        )

        node_estimate = len(CATEGORY_KNOWLEDGE) + len(PRODUCT_KNOWLEDGE) + len(dataset_rows) * 4
        relationship_estimate = len(complement_edges) + len(related_edges) + len(dataset_rows) * 5 + len(PRODUCT_KNOWLEDGE)
        return GraphRebuildResult(
            status="rebuilt",
            nodes_merged=node_estimate,
            relationships_merged=relationship_estimate,
            backend=self.backend,
            detail=f"Synced {len(dataset_rows)} behavior rows into KB_Graph.",
        )

    def retrieve(
        self,
        *,
        query: str = "",
        cart_slugs: list[str] | None = None,
        category_hints: list[str] | None = None,
        top_k: int = 4,
    ) -> GraphContext:
        if not self.driver:
            return GraphContext(backend=self.backend)

        cart_slugs = [slug for slug in (cart_slugs or []) if slug]
        category_hints = [hint for hint in (category_hints or []) if hint]
        query_terms = list(tokenize(query))
        matched_category = None
        supporting_keywords: list[str] = []
        related_categories: list[str] = []
        observed_intents: list[str] = []
        graph_product_slugs: list[str] = []
        evidence: list[str] = []

        if query_terms:
            keyword_rows = self._run(
                """
                MATCH (k:Keyword)-[:RELATES_TO]->(c:Category)
                WHERE any(term IN $terms WHERE toLower(k.name) CONTAINS term)
                RETURN c.slug AS category_slug,
                       c.name AS category_name,
                       collect(DISTINCT k.name)[0..4] AS keywords,
                       count(*) AS score
                ORDER BY score DESC
                LIMIT 1
                """,
                {"terms": query_terms},
            )
            if keyword_rows:
                top = keyword_rows[0]
                matched_category = top["category_slug"]
                supporting_keywords = top["keywords"] or []
                evidence.append(
                    f"Graph keyword matches point most strongly to {top['category_name']}."
                )

        if not matched_category and category_hints:
            for hint in category_hints:
                hint_slug = normalize_text(hint).replace(" ", "-")
                category_rows = self._run(
                    """
                    MATCH (c:Category)
                    WHERE c.slug = $hint OR toLower(c.name) = $hint_name
                    RETURN c.slug AS category_slug
                    LIMIT 1
                    """,
                    {"hint": hint_slug, "hint_name": normalize_text(hint)},
                )
                if category_rows:
                    matched_category = category_rows[0]["category_slug"]
                    evidence.append(f"Graph context re-used cart category {matched_category}.")
                    break

        if matched_category:
            product_rows = self._run(
                """
                MATCH (c:Category {slug: $category_slug})-[:CONTAINS]->(p:Product)
                RETURN p.slug AS slug, coalesce(p.featured, false) AS featured, p.name AS name
                ORDER BY featured DESC, name ASC
                LIMIT $top_k
                """,
                {"category_slug": matched_category, "top_k": int(top_k)},
            )
            graph_product_slugs.extend([row["slug"] for row in product_rows])

            related_rows = self._run(
                """
                MATCH (c:Category {slug: $category_slug})-[:RELATED_TO]->(related:Category)
                RETURN related.slug AS slug
                LIMIT 3
                """,
                {"category_slug": matched_category},
            )
            related_categories.extend([row["slug"] for row in related_rows])

            intent_rows = self._run(
                """
                MATCH (c:Category {slug: $category_slug})<-[:INTERESTED_IN]-(:Session)-[:HAS_INTENT]->(i:Intent)
                RETURN i.name AS intent, count(*) AS hits
                ORDER BY hits DESC
                LIMIT 3
                """,
                {"category_slug": matched_category},
            )
            observed_intents.extend([row["intent"] for row in intent_rows])
            if observed_intents:
                evidence.append(
                    "Observed intents in the graph for this category are "
                    + ", ".join(observed_intents)
                    + "."
                )

        if cart_slugs:
            complement_rows = self._run(
                """
                MATCH (source:Product)-[:COMPLEMENTS]->(target:Product)
                WHERE source.slug IN $cart_slugs
                RETURN target.slug AS slug
                LIMIT $top_k
                """,
                {"cart_slugs": cart_slugs, "top_k": int(top_k)},
            )
            complement_slugs = [row["slug"] for row in complement_rows]
            if complement_slugs:
                graph_product_slugs.extend(complement_slugs)
                evidence.append(
                    "Graph complement edges suggest "
                    + ", ".join(complement_slugs[:3])
                    + " for the current cart."
                )

        graph_product_slugs = list(dict.fromkeys(graph_product_slugs))
        related_categories = list(dict.fromkeys(related_categories))
        observed_intents = list(dict.fromkeys(observed_intents))
        supporting_keywords = list(dict.fromkeys(supporting_keywords))

        return GraphContext(
            backend=self.backend,
            matched_category=matched_category,
            supporting_keywords=supporting_keywords,
            graph_product_slugs=graph_product_slugs,
            related_categories=related_categories,
            observed_intents=observed_intents,
            evidence=evidence,
        )
