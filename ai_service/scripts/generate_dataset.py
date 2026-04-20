from __future__ import annotations

import csv
import random
from collections.abc import Iterable
from pathlib import Path


SEED = 20260420

ROOT_DIR = Path(__file__).resolve().parents[2]
REPORT_DATASET_PATH = ROOT_DIR / "ai_service" / "data_user500.csv"
SERVICE_DATASET_PATH = ROOT_DIR / "services" / "ai_service" / "data" / "data_user500.csv"

FIELDNAMES = [
    "user_id",
    "session_id",
    "last_search_keyword",
    "dominant_category",
    "search_count",
    "product_view_count",
    "detail_view_count",
    "dwell_time_sec",
    "add_wishlist_count",
    "add_to_cart_count",
    "remove_from_cart_count",
    "purchase_count",
    "target_label",
]

CATEGORY_KEYWORDS = {
    "work-tech": [
        "laptop",
        "study laptop",
        "desk lamp",
        "office setup",
        "portable workstation",
        "coding laptop",
        "student device",
    ],
    "home-living": [
        "throw blanket",
        "diffuser",
        "cozy room",
        "sofa decor",
        "calm home",
        "bedside diffuser",
        "reading nook",
    ],
    "kitchen-dining": [
        "coffee press",
        "cutting board",
        "kitchen prep",
        "morning brew",
        "bamboo board",
        "home cafe",
        "meal prep",
    ],
    "wellness": [
        "yoga mat",
        "water bottle",
        "home workout",
        "hydration bottle",
        "stretching routine",
        "fitness gear",
        "daily wellness",
    ],
    "travel-everyday": [
        "travel bag",
        "weekender",
        "tote bag",
        "daily carry",
        "overnight bag",
        "commuter bag",
        "city trip bag",
    ],
    "beauty-care": [
        "skin care",
        "portable mirror",
        "starter skincare",
        "beauty routine",
        "travel mirror",
        "gentle skincare",
        "self care set",
    ],
}

INTENT_RANGES = {
    "low_intent": {
        "search_count": (1, 4),
        "product_view_count": (2, 7),
        "detail_view_count": (0, 2),
        "dwell_time_sec": (40, 160),
        "add_wishlist_count": (0, 1),
        "add_to_cart_count": (0, 0),
        "remove_from_cart_count": (0, 1),
        "purchase_count": (0, 0),
    },
    "medium_intent": {
        "search_count": (3, 7),
        "product_view_count": (5, 11),
        "detail_view_count": (2, 5),
        "dwell_time_sec": (140, 330),
        "add_wishlist_count": (0, 2),
        "add_to_cart_count": (1, 2),
        "remove_from_cart_count": (0, 1),
        "purchase_count": (0, 0),
    },
    "high_intent": {
        "search_count": (5, 9),
        "product_view_count": (9, 16),
        "detail_view_count": (4, 8),
        "dwell_time_sec": (300, 560),
        "add_wishlist_count": (1, 3),
        "add_to_cart_count": (2, 4),
        "remove_from_cart_count": (0, 1),
        "purchase_count": (1, 2),
    },
}

FIXED_ROWS = [
    ["U001", "S001", "laptop", "work-tech", 6, 12, 5, 410, 1, 2, 0, 1, "high_intent"],
    ["U002", "S002", "desk lamp", "work-tech", 4, 7, 3, 180, 1, 1, 0, 0, "medium_intent"],
    ["U003", "S003", "yoga mat", "wellness", 5, 9, 4, 320, 1, 2, 1, 1, "high_intent"],
    ["U004", "S004", "water bottle", "wellness", 3, 6, 2, 110, 0, 0, 0, 0, "low_intent"],
    ["U005", "S005", "travel bag", "travel-everyday", 7, 11, 6, 390, 2, 3, 0, 1, "high_intent"],
    ["U006", "S006", "tote bag", "travel-everyday", 4, 8, 3, 165, 1, 1, 1, 0, "medium_intent"],
    ["U007", "S007", "skin care", "beauty-care", 5, 10, 5, 300, 2, 2, 0, 0, "medium_intent"],
    ["U008", "S008", "coffee press", "kitchen-dining", 2, 5, 2, 95, 0, 0, 0, 0, "low_intent"],
    ["U009", "S009", "diffuser", "home-living", 6, 10, 4, 275, 1, 2, 0, 0, "medium_intent"],
    ["U010", "S010", "blanket", "home-living", 2, 4, 1, 70, 0, 0, 0, 0, "low_intent"],
    ["U011", "S011", "laptop for study", "work-tech", 8, 14, 7, 520, 2, 3, 0, 1, "high_intent"],
    ["U012", "S012", "portable mirror", "beauty-care", 3, 7, 3, 150, 0, 1, 0, 0, "medium_intent"],
    ["U013", "S013", "bamboo board", "kitchen-dining", 2, 6, 2, 105, 0, 0, 0, 0, "low_intent"],
    ["U014", "S014", "hydration bottle", "wellness", 4, 8, 4, 210, 1, 1, 0, 0, "medium_intent"],
    ["U015", "S015", "overnight bag", "travel-everyday", 6, 12, 6, 430, 1, 3, 0, 1, "high_intent"],
    ["U016", "S016", "calm diffuser", "home-living", 5, 9, 4, 260, 1, 1, 1, 0, "medium_intent"],
    ["U017", "S017", "desk setup", "work-tech", 3, 5, 2, 130, 0, 0, 0, 0, "low_intent"],
    ["U018", "S018", "yoga home workout", "wellness", 7, 13, 6, 470, 2, 2, 0, 1, "high_intent"],
    ["U019", "S019", "travel tote", "travel-everyday", 4, 7, 3, 175, 0, 1, 0, 0, "medium_intent"],
    ["U020", "S020", "starter skincare", "beauty-care", 6, 10, 5, 295, 2, 2, 0, 0, "medium_intent"],
]


def clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


def build_row_dict(raw_row: list[object]) -> dict[str, object]:
    return dict(zip(FIELDNAMES, raw_row, strict=True))


def choose_intent(index: int, rng: random.Random) -> str:
    pattern = index % 10
    if pattern in {0, 1, 5}:
        return "high_intent"
    if pattern in {2, 3, 6, 7}:
        return "medium_intent"
    return "low_intent"


def generate_behavior_value(
    ranges: dict[str, tuple[int, int]],
    feature: str,
    rng: random.Random,
    keyword: str,
) -> int:
    lower, upper = ranges[feature]
    value = rng.randint(lower, upper)

    keyword_length = len(keyword.split())
    if feature == "search_count":
        value += keyword_length // 2
    elif feature == "detail_view_count" and keyword_length > 1:
        value += 1
    elif feature == "dwell_time_sec" and keyword_length > 2:
        value += rng.randint(10, 35)

    return clamp(value, lower, upper)


def generate_rows() -> list[dict[str, object]]:
    rng = random.Random(SEED)
    rows = [build_row_dict(raw_row) for raw_row in FIXED_ROWS]

    categories = list(CATEGORY_KEYWORDS.keys())
    while len(rows) < 500:
        index = len(rows) + 1
        category = categories[(index - 1) % len(categories)]
        keyword = rng.choice(CATEGORY_KEYWORDS[category])
        intent = choose_intent(index, rng)
        ranges = INTENT_RANGES[intent]

        row = {
            "user_id": f"U{index:03d}",
            "session_id": f"S{index:03d}",
            "last_search_keyword": keyword,
            "dominant_category": category,
            "search_count": generate_behavior_value(ranges, "search_count", rng, keyword),
            "product_view_count": generate_behavior_value(ranges, "product_view_count", rng, keyword),
            "detail_view_count": generate_behavior_value(ranges, "detail_view_count", rng, keyword),
            "dwell_time_sec": generate_behavior_value(ranges, "dwell_time_sec", rng, keyword),
            "add_wishlist_count": generate_behavior_value(ranges, "add_wishlist_count", rng, keyword),
            "add_to_cart_count": generate_behavior_value(ranges, "add_to_cart_count", rng, keyword),
            "remove_from_cart_count": generate_behavior_value(ranges, "remove_from_cart_count", rng, keyword),
            "purchase_count": generate_behavior_value(ranges, "purchase_count", rng, keyword),
            "target_label": intent,
        }

        if row["purchase_count"] >= 1:
            row["add_to_cart_count"] = max(int(row["add_to_cart_count"]), 1)
            row["detail_view_count"] = max(int(row["detail_view_count"]), 3)
            row["product_view_count"] = max(int(row["product_view_count"]), int(row["detail_view_count"]) + 2)

        if row["add_to_cart_count"] == 0:
            row["purchase_count"] = 0

        if row["target_label"] == "low_intent":
            row["add_to_cart_count"] = 0
            row["purchase_count"] = 0
            row["detail_view_count"] = min(int(row["detail_view_count"]), 2)

        rows.append(row)

    return rows


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = generate_rows()
    write_csv(REPORT_DATASET_PATH, rows)
    write_csv(SERVICE_DATASET_PATH, rows)
    print(f"Generated {len(rows)} rows")
    print(f"- report dataset: {REPORT_DATASET_PATH}")
    print(f"- service dataset: {SERVICE_DATASET_PATH}")


if __name__ == "__main__":
    main()
