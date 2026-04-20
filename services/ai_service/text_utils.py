from __future__ import annotations

import re


def normalize_text(value: str) -> str:
    value = value.lower().strip()
    return re.sub(r"[^a-z0-9\s-]+", " ", value)


def tokenize(value: str) -> set[str]:
    return {token for token in normalize_text(value).replace("-", " ").split() if token}
