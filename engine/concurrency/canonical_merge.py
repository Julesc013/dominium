"""Deterministic merge helpers for parallel derived and validation outputs."""

from __future__ import annotations

from typing import Callable, Mapping, Sequence


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def build_field_sort_key(
    field_names: Sequence[str],
    *,
    int_fields: Sequence[str] = (),
) -> Callable[[Mapping[str, object]], tuple]:
    ordered_fields = tuple(_token(field) for field in list(field_names or []) if _token(field))
    integer_fields = set(_token(field) for field in list(int_fields or []) if _token(field))

    def _key(row: Mapping[str, object]) -> tuple:
        row_map = _as_map(row)
        key_parts: list[object] = []
        for field_name in ordered_fields:
            if field_name in integer_fields:
                try:
                    key_parts.append(int(row_map.get(field_name, 0) or 0))
                except (TypeError, ValueError):
                    key_parts.append(0)
            else:
                key_parts.append(_token(row_map.get(field_name)))
        return tuple(key_parts)

    return _key


def canonicalize_parallel_mapping_rows(
    rows: Sequence[Mapping[str, object]] | None,
    *,
    key_fn: Callable[[Mapping[str, object]], tuple],
) -> list[dict]:
    return [
        dict(row)
        for row in sorted(
            (dict(item) for item in list(rows or []) if isinstance(item, Mapping)),
            key=key_fn,
        )
    ]


def canonical_merge_mapping_groups(
    row_groups: Sequence[Sequence[Mapping[str, object]]] | None,
    *,
    key_fn: Callable[[Mapping[str, object]], tuple],
) -> list[dict]:
    merged: list[dict] = []
    for group in list(row_groups or []):
        for row in list(group or []):
            if isinstance(row, Mapping):
                merged.append(dict(row))
    return canonicalize_parallel_mapping_rows(merged, key_fn=key_fn)


__all__ = [
    "build_field_sort_key",
    "canonical_merge_mapping_groups",
    "canonicalize_parallel_mapping_rows",
]
