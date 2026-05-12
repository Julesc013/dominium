"""Deterministic supervisor argument canonicalization helpers."""

from __future__ import annotations

import json
from typing import Iterable, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


def _token(value: object) -> str:
    return str(value or "").strip()


def _quote_arg(value: object) -> str:
    token = _token(value)
    if not token:
        return '""'
    if any(ch.isspace() for ch in token) or any(ch in token for ch in ('"', "\\", "=")):
        return json.dumps(token, ensure_ascii=True)
    return token


def canonicalize_flag_pairs(
    pairs: Iterable[tuple[object, object]],
    *,
    flag_order: Sequence[object] | None = None,
) -> list[str]:
    preferred = [_token(item) for item in list(flag_order or []) if _token(item)]
    preferred_rank = {flag: index for index, flag in enumerate(preferred)}
    normalized: list[tuple[str, str]] = []
    for raw_flag, raw_value in list(pairs or []):
        flag = _token(raw_flag)
        value = _token(raw_value)
        if not flag or not value:
            continue
        normalized.append((flag, value))
    normalized = sorted(
        normalized,
        key=lambda item: (
            preferred_rank.get(item[0], len(preferred_rank)),
            item[0],
            item[1],
        ),
    )
    out: list[str] = []
    for flag, value in normalized:
        out.extend([flag, value])
    return out


def canonicalize_args(
    *,
    positional: Sequence[object] | None = None,
    flag_pairs: Iterable[tuple[object, object]] | None = None,
    flag_order: Sequence[object] | None = None,
) -> dict:
    positionals = [_token(item) for item in list(positional or []) if _token(item)]
    args = positionals + canonicalize_flag_pairs(flag_pairs or (), flag_order=flag_order)
    argv_text = " ".join(_quote_arg(item) for item in args)
    payload = {
        "args": args,
        "argv_text": argv_text,
        "args_hash": canonical_sha256(args),
        "argv_text_hash": canonical_sha256({"argv_text": argv_text}),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def canonicalize_arg_map(
    *,
    positional: Sequence[object] | None = None,
    flag_map: Mapping[object, object] | None = None,
    flag_order: Sequence[object] | None = None,
) -> dict:
    pairs = [(key, value) for key, value in sorted(dict(flag_map or {}).items(), key=lambda item: _token(item[0]))]
    return canonicalize_args(positional=positional, flag_pairs=pairs, flag_order=flag_order)


__all__ = [
    "canonicalize_arg_map",
    "canonicalize_args",
    "canonicalize_flag_pairs",
]
