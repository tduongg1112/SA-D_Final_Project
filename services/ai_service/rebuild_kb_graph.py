from __future__ import annotations

from pathlib import Path

from app_config import settings
from graph_store import GraphStore
from intelligence import DatasetStore


def main() -> None:
    dataset_store = DatasetStore(Path(settings.dataset_path))
    graph_store = GraphStore(settings, dataset_store)
    result = graph_store.rebuild_graph()
    print(
        {
            "status": result.status,
            "nodes_merged": result.nodes_merged,
            "relationships_merged": result.relationships_merged,
            "backend": result.backend,
            "detail": result.detail,
        }
    )
    graph_store.close()


if __name__ == "__main__":
    main()
