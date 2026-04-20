from __future__ import annotations

from typing import Any


class JsonUpdateMode:
    MERGE = "merge"
    REMOVE = "remove"
    OVERRIDE = "override"
    REWRITE = "rewrite"
    IGNORE = "ignore"

    @classmethod
    def choices(cls) -> list[str]:
        return [cls.MERGE, cls.REMOVE, cls.OVERRIDE, cls.IGNORE, cls.REWRITE]


def process_dict(d1: dict[str, Any], d2: dict[str, Any], mode: str) -> dict[str, Any]:
    if mode == JsonUpdateMode.MERGE:
        return merge_dicts(d1, d2)
    if mode == JsonUpdateMode.OVERRIDE:
        return override_dicts(d1, d2)
    if mode == JsonUpdateMode.REMOVE:
        return remove_dicts(d1, d2)
    raise ValueError(f"Unknown JsonUpdateMode: {mode}")


def merge_dicts(d1: dict[str, Any], d2: dict[str, Any]) -> dict[str, Any]:
    """Deep merge.

    - dicts merge recursively
    - other values from d2 override d1
    """
    result = d1.copy()

    for key, value in d2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def override_dicts(d1: dict[str, Any], d2: dict[str, Any]) -> dict[str, Any]:
    """Shallow override.

    values in d2 completely replace values in d1
    """
    result = d1.copy()
    result.update(d2)
    return result


def remove_dicts(d1: dict[str, Any], d2: dict[str, Any]) -> dict[str, Any]:
    """Remove keys in d1 if they appear in d2.

    If both values are dicts → remove recursively.
    """
    result = d1.copy()

    for key, value in d2.items():
        if key not in result:
            continue

        if isinstance(result[key], dict) and isinstance(value, dict):
            nested = remove_dicts(result[key], value)
            if nested:
                result[key] = nested
            else:
                del result[key]
        else:
            del result[key]

    return result
