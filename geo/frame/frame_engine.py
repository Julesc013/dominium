"""Deterministic GEO-2 frame graph and position conversion helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from geo.kernel.geo_kernel import (
    _DEFAULT_METRIC_PROFILE_ID,
    _DEFAULT_TOPOLOGY_PROFILE_ID,
    _as_int,
    _as_map,
    _cache_lookup,
    _cache_store,
    _dimension_from_topology,
    _query_cache_key,
    _topology_row,
    geo_distance,
    geo_transform,
)


REFUSAL_GEO_FRAME_INVALID = "refusal.geo.frame_invalid"
REFUSAL_GEO_POSITION_INVALID = "refusal.geo.position_invalid"

_VALID_SCALE_CLASSES = {"galaxy", "system", "planet", "local"}
_VALID_TRANSFORM_KINDS = {"translate", "rotate", "scale", "chart_map_stub"}


def _refusal(*, refusal_code: str, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": str(refusal_code),
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _round_div_away_from_zero(numerator: int, denominator: int) -> int:
    if int(denominator) == 0:
        raise ValueError("denominator must be non-zero")
    n = int(numerator)
    d = int(denominator)
    sign = -1 if (n < 0) ^ (d < 0) else 1
    abs_n = abs(n)
    abs_d = abs(d)
    quotient = abs_n // abs_d
    remainder = abs_n % abs_d
    if remainder * 2 >= abs_d:
        quotient += 1
    return int(sign * quotient)


def _frame_id_token(value: object) -> str:
    if isinstance(value, Mapping):
        return str(value.get("frame_id", "")).strip()
    return str(value or "").strip()


def _normalize_vector(value: object, dimension: int) -> List[int]:
    if isinstance(value, list):
        coords = [int(_as_int(item, 0)) for item in value[:dimension]]
        while len(coords) < dimension:
            coords.append(0)
        return coords
    payload = _as_map(value)
    coords = payload.get("coords")
    if isinstance(coords, list):
        return _normalize_vector(coords, dimension)
    axis_labels = ("x", "y", "z", "w", "v", "u")
    out: List[int] = []
    for idx in range(int(dimension)):
        if idx < len(axis_labels):
            out.append(int(_as_int(payload.get(axis_labels[idx], 0), 0)))
        else:
            out.append(int(_as_int(payload.get("a{}".format(idx), 0), 0)))
    return out


def _frame_semantic_payload(row: Mapping[str, object]) -> dict:
    payload = _as_map(row)
    return {
        "frame_id": str(payload.get("frame_id", "")).strip(),
        "parent_frame_id": None
        if payload.get("parent_frame_id") in {None, ""}
        else str(payload.get("parent_frame_id", "")).strip() or None,
        "topology_profile_id": str(payload.get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID,
        "metric_profile_id": str(payload.get("metric_profile_id", "")).strip() or _DEFAULT_METRIC_PROFILE_ID,
        "chart_id": str(payload.get("chart_id", "")).strip() or "chart.global",
        "anchor_cell_key": _as_map(payload.get("anchor_cell_key")),
        "scale_class_id": str(payload.get("scale_class_id", "local")).strip() or "local",
    }


def normalize_frame_node(
    row: Mapping[str, object] | None,
    *,
    topology_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    payload = _frame_semantic_payload(_as_map(row))
    scale_class_id = str(payload.get("scale_class_id", "local")).strip().lower() or "local"
    if scale_class_id not in _VALID_SCALE_CLASSES:
        scale_class_id = "local"
    topology_profile_id = str(payload.get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    topology_row = _topology_row(topology_profile_id, registry_payload=topology_registry_payload)
    if not topology_row:
        topology_profile_id = _DEFAULT_TOPOLOGY_PROFILE_ID
    normalized = {
        "schema_version": "1.0.0",
        "frame_id": str(payload.get("frame_id", "")).strip(),
        "parent_frame_id": payload.get("parent_frame_id"),
        "topology_profile_id": topology_profile_id,
        "metric_profile_id": str(payload.get("metric_profile_id", "")).strip() or _DEFAULT_METRIC_PROFILE_ID,
        "chart_id": str(payload.get("chart_id", "")).strip() or "chart.global",
        "anchor_cell_key": _as_map(payload.get("anchor_cell_key")),
        "scale_class_id": scale_class_id,
        "deterministic_fingerprint": "",
        "extensions": _as_map(_as_map(row).get("extensions")),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def _transform_semantic_payload(row: Mapping[str, object]) -> dict:
    payload = _as_map(row)
    return {
        "from_frame_id": str(payload.get("from_frame_id", "")).strip(),
        "to_frame_id": str(payload.get("to_frame_id", "")).strip(),
        "transform_kind": str(payload.get("transform_kind", "translate")).strip().lower() or "translate",
        "parameters": _as_map(payload.get("parameters")),
    }


def normalize_frame_transform(row: Mapping[str, object] | None) -> dict:
    payload = _transform_semantic_payload(_as_map(row))
    transform_kind = str(payload.get("transform_kind", "translate")).strip().lower() or "translate"
    if transform_kind not in _VALID_TRANSFORM_KINDS:
        transform_kind = "translate"
    normalized = {
        "schema_version": "1.0.0",
        "from_frame_id": str(payload.get("from_frame_id", "")).strip(),
        "to_frame_id": str(payload.get("to_frame_id", "")).strip(),
        "transform_kind": transform_kind,
        "parameters": _as_map(payload.get("parameters")),
        "deterministic_fingerprint": "",
        "extensions": _as_map(_as_map(row).get("extensions")),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def build_position_ref(
    *,
    object_id: str,
    frame_id: str,
    local_position: Sequence[int],
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "object_id": str(object_id).strip(),
        "frame_id": str(frame_id).strip(),
        "local_position": [int(value) for value in list(local_position or [])],
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _frame_nodes_by_id(
    frame_nodes: object,
    *,
    topology_registry_payload: Mapping[str, object] | None = None,
) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(frame_nodes, list):
        frame_nodes = []
    for row in sorted(
        (dict(item) for item in frame_nodes if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("frame_id", "")),
            str(item.get("parent_frame_id", "")) if item.get("parent_frame_id") is not None else "",
        ),
    ):
        normalized = normalize_frame_node(row, topology_registry_payload=topology_registry_payload)
        frame_id = str(normalized.get("frame_id", "")).strip()
        if frame_id:
            out[frame_id] = normalized
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _frame_transforms_by_edge(frame_transform_rows: object) -> Dict[Tuple[str, str], dict]:
    out: Dict[Tuple[str, str], dict] = {}
    if not isinstance(frame_transform_rows, list):
        frame_transform_rows = []
    for row in sorted(
        (dict(item) for item in frame_transform_rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("from_frame_id", "")),
            str(item.get("to_frame_id", "")),
            str(item.get("transform_kind", "")),
        ),
    ):
        normalized = normalize_frame_transform(row)
        edge = (str(normalized.get("from_frame_id", "")).strip(), str(normalized.get("to_frame_id", "")).strip())
        if edge[0] and edge[1]:
            out[edge] = normalized
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def frame_graph_hash(
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    topology_registry_payload: Mapping[str, object] | None = None,
) -> str:
    nodes = _frame_nodes_by_id(frame_nodes, topology_registry_payload=topology_registry_payload)
    transforms = _frame_transforms_by_edge(frame_transform_rows)
    payload = {
        "frame_nodes": [_frame_semantic_payload(nodes[key]) for key in sorted(nodes.keys())],
        "frame_transforms": [
            _transform_semantic_payload(transforms[key])
            for key in sorted(transforms.keys(), key=lambda item: (str(item[0]), str(item[1])))
        ],
    }
    return canonical_sha256(payload)


def position_ref_hash(position_ref: Mapping[str, object] | None) -> str:
    payload = _as_map(position_ref)
    semantic = {
        "object_id": str(payload.get("object_id", "")).strip(),
        "frame_id": str(payload.get("frame_id", "")).strip(),
        "local_position": [int(_as_int(value, 0)) for value in list(payload.get("local_position") or [])],
    }
    return canonical_sha256(semantic)


def normalize_position_ref(
    row: Mapping[str, object] | None,
    *,
    frame_nodes: object = None,
    topology_registry_payload: Mapping[str, object] | None = None,
) -> dict | None:
    payload = _as_map(row)
    object_id = str(payload.get("object_id", "")).strip()
    frame_id = str(payload.get("frame_id", "")).strip()
    if not object_id or not frame_id:
        return None
    nodes = _frame_nodes_by_id(frame_nodes, topology_registry_payload=topology_registry_payload)
    frame_row = dict(nodes.get(frame_id) or {})
    topology_row = _topology_row(str(frame_row.get("topology_profile_id", "")), registry_payload=topology_registry_payload)
    dimension = max(
        len(list(payload.get("local_position") or [])),
        _dimension_from_topology(topology_row) if topology_row else 0,
        1,
    )
    return build_position_ref(
        object_id=object_id,
        frame_id=frame_id,
        local_position=_normalize_vector(payload.get("local_position"), dimension),
        extensions=_as_map(payload.get("extensions")),
    )


def _lineage(frame_id: str, nodes: Mapping[str, dict]) -> List[str] | None:
    out: List[str] = []
    visited = set()
    cursor = str(frame_id).strip()
    while cursor:
        if cursor in visited:
            return None
        row = dict(nodes.get(cursor) or {})
        if not row:
            return None
        visited.add(cursor)
        out.append(cursor)
        parent = row.get("parent_frame_id")
        cursor = str(parent).strip() if isinstance(parent, str) and str(parent).strip() else ""
    return out


def _lowest_common_ancestor(frame_a: str, frame_b: str, nodes: Mapping[str, dict]) -> str:
    lineage_a = _lineage(frame_a, nodes) or []
    lineage_b = set(_lineage(frame_b, nodes) or [])
    for token in lineage_a:
        if token in lineage_b:
            return token
    return ""


def _dimension_for_frame(
    frame_row: Mapping[str, object],
    *,
    topology_registry_payload: Mapping[str, object] | None = None,
) -> int:
    topology_row = _topology_row(str(_as_map(frame_row).get("topology_profile_id", "")), registry_payload=topology_registry_payload)
    return max(1, _dimension_from_topology(topology_row) if topology_row else 1)


def _translation_vector(parameters: Mapping[str, object], dimension: int) -> List[int]:
    params = _as_map(parameters)
    for key in ("translation", "translation_mm", "vector"):
        value = params.get(key)
        if value is not None:
            return _normalize_vector(value, dimension)
    return [0] * max(1, int(dimension))


def _scale_permille(parameters: Mapping[str, object]) -> int:
    params = _as_map(parameters)
    scale_permille = int(_as_int(params.get("scale_permille", params.get("value_permille", 1000)), 1000))
    return scale_permille if scale_permille != 0 else 1000


def _axis_order(parameters: Mapping[str, object], dimension: int) -> List[int]:
    params = _as_map(parameters)
    raw = params.get("axis_order")
    if not isinstance(raw, list):
        return list(range(int(dimension)))
    order = [int(_as_int(item, idx)) for idx, item in enumerate(raw[:dimension])]
    if sorted(order) != list(range(int(dimension))):
        return list(range(int(dimension)))
    return order


def _axis_signs(parameters: Mapping[str, object], dimension: int) -> List[int]:
    params = _as_map(parameters)
    raw = params.get("axis_signs")
    if not isinstance(raw, list):
        return [1] * int(dimension)
    signs = [1 if int(_as_int(item, 1)) >= 0 else -1 for item in raw[:dimension]]
    while len(signs) < int(dimension):
        signs.append(1)
    return signs


def _apply_translate(coords: Sequence[int], vector: Sequence[int], *, inverse: bool) -> List[int]:
    sign = -1 if inverse else 1
    return [int(coords[idx]) + (sign * int(vector[idx])) for idx in range(len(coords))]


def _apply_scale(coords: Sequence[int], scale_permille: int, *, inverse: bool) -> List[int]:
    if int(scale_permille) == 0:
        raise ValueError("scale_permille must be non-zero")
    if inverse:
        return [_round_div_away_from_zero(int(value) * 1000, int(scale_permille)) for value in coords]
    return [_round_div_away_from_zero(int(value) * int(scale_permille), 1000) for value in coords]


def _apply_rotate(coords: Sequence[int], parameters: Mapping[str, object], *, inverse: bool) -> List[int]:
    dimension = len(coords)
    order = _axis_order(parameters, dimension)
    signs = _axis_signs(parameters, dimension)
    if inverse:
        out = [0] * dimension
        for target_idx, source_idx in enumerate(order):
            out[source_idx] = int(coords[target_idx]) * int(signs[target_idx])
        return [int(value) for value in out]
    return [int(coords[order[idx]]) * int(signs[idx]) for idx in range(dimension)]


def _apply_chart_map(
    coords: Sequence[int],
    *,
    from_chart: str,
    to_chart: str,
) -> List[int]:
    transformed = geo_transform({"coords": [int(value) for value in coords]}, str(from_chart), str(to_chart))
    if str(transformed.get("result", "")) != "complete":
        raise ValueError(str(transformed.get("message", "chart transform failed")))
    payload = _as_map(transformed.get("position"))
    return [int(_as_int(value, 0)) for value in list(payload.get("coords") or [])]


def _apply_transform(
    coords: Sequence[int],
    transform_row: Mapping[str, object],
    *,
    from_frame_row: Mapping[str, object],
    to_frame_row: Mapping[str, object],
    inverse: bool,
) -> List[int]:
    dimension = max(len(coords), _dimension_for_frame(from_frame_row), _dimension_for_frame(to_frame_row))
    working = _normalize_vector(list(coords), dimension)
    transform_kind = str(_as_map(transform_row).get("transform_kind", "translate")).strip().lower() or "translate"
    parameters = _as_map(_as_map(transform_row).get("parameters"))
    if transform_kind == "translate":
        return _apply_translate(working, _translation_vector(parameters, dimension), inverse=inverse)
    if transform_kind == "scale":
        return _apply_scale(working, _scale_permille(parameters), inverse=inverse)
    if transform_kind == "rotate":
        return _apply_rotate(working, parameters, inverse=inverse)
    if inverse:
        return _apply_chart_map(
            working,
            from_chart=str(_as_map(to_frame_row).get("chart_id", "")),
            to_chart=str(_as_map(from_frame_row).get("chart_id", "")),
        )
    return _apply_chart_map(
        working,
        from_chart=str(_as_map(from_frame_row).get("chart_id", "")),
        to_chart=str(_as_map(to_frame_row).get("chart_id", "")),
    )


def _path_steps(
    *,
    from_frame_id: str,
    to_frame_id: str,
    frame_nodes: Mapping[str, dict],
    frame_transforms: Mapping[Tuple[str, str], dict],
) -> Tuple[str, List[str], List[dict]] | None:
    lca = _lowest_common_ancestor(from_frame_id, to_frame_id, frame_nodes)
    if not lca:
        return None
    path_ids: List[str] = []
    cursor = str(from_frame_id)
    while cursor:
        path_ids.append(cursor)
        if cursor == lca:
            break
        cursor = str(_as_map(frame_nodes.get(cursor)).get("parent_frame_id", "") or "").strip()
    tail_ids: List[str] = []
    cursor = str(to_frame_id)
    while cursor and cursor != lca:
        tail_ids.append(cursor)
        cursor = str(_as_map(frame_nodes.get(cursor)).get("parent_frame_id", "") or "").strip()
    path_ids.extend(reversed(tail_ids))

    up_steps: List[dict] = []
    cursor = str(from_frame_id)
    while cursor and cursor != lca:
        child_row = dict(frame_nodes.get(cursor) or {})
        parent_id = str(child_row.get("parent_frame_id", "") or "").strip()
        parent_row = dict(frame_nodes.get(parent_id) or {})
        transform_row = dict(frame_transforms.get((cursor, parent_id)) or {})
        if not transform_row:
            return None
        up_steps.append(
            {
                "direction": "forward",
                "from_frame_id": cursor,
                "to_frame_id": parent_id,
                "transform": transform_row,
                "from_frame": child_row,
                "to_frame": parent_row,
            }
        )
        cursor = parent_id

    reverse_edges: List[dict] = []
    cursor = str(to_frame_id)
    while cursor and cursor != lca:
        child_row = dict(frame_nodes.get(cursor) or {})
        parent_id = str(child_row.get("parent_frame_id", "") or "").strip()
        parent_row = dict(frame_nodes.get(parent_id) or {})
        transform_row = dict(frame_transforms.get((cursor, parent_id)) or {})
        if not transform_row:
            return None
        reverse_edges.append(
            {
                "direction": "inverse",
                "from_frame_id": parent_id,
                "to_frame_id": cursor,
                "transform": transform_row,
                "from_frame": parent_row,
                "to_frame": child_row,
            }
        )
        cursor = parent_id
    return lca, path_ids, up_steps + list(reversed(reverse_edges))


def frame_get_transform(
    from_frame: object,
    to_frame: object,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    from_frame_id = _frame_id_token(from_frame)
    to_frame_id = _frame_id_token(to_frame)
    if not from_frame_id or not to_frame_id:
        return _refusal(
            refusal_code=REFUSAL_GEO_FRAME_INVALID,
            message="from_frame and to_frame are required",
        )
    nodes = _frame_nodes_by_id(frame_nodes, topology_registry_payload=topology_registry_payload)
    transforms = _frame_transforms_by_edge(frame_transform_rows)
    if from_frame_id not in nodes or to_frame_id not in nodes:
        return _refusal(
            refusal_code=REFUSAL_GEO_FRAME_INVALID,
            message="frame_id is missing from frame graph",
            details={"from_frame_id": from_frame_id, "to_frame_id": to_frame_id},
        )
    version = str(graph_version or "").strip() or frame_graph_hash(
        frame_nodes=list(nodes.values()),
        frame_transform_rows=list(transforms.values()),
        topology_registry_payload=topology_registry_payload,
    )
    seed = {
        "query_kind": "frame_get_transform",
        "from_frame_id": from_frame_id,
        "to_frame_id": to_frame_id,
        "graph_version": version,
    }
    cache_key = _query_cache_key("frame_get_transform", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    if from_frame_id == to_frame_id:
        identity = {
            "result": "complete",
            "from_frame_id": from_frame_id,
            "to_frame_id": to_frame_id,
            "graph_version": version,
            "lca_frame_id": from_frame_id,
            "path_frame_ids": [from_frame_id],
            "transform_chain": [],
            "target_topology_profile_id": str(nodes[from_frame_id].get("topology_profile_id", "")),
            "target_metric_profile_id": str(nodes[from_frame_id].get("metric_profile_id", "")),
            "target_chart_id": str(nodes[from_frame_id].get("chart_id", "")),
            "deterministic_fingerprint": "",
        }
        identity["deterministic_fingerprint"] = canonical_sha256(dict(identity, deterministic_fingerprint=""))
        return _cache_store(cache_key, identity)

    path = _path_steps(
        from_frame_id=from_frame_id,
        to_frame_id=to_frame_id,
        frame_nodes=nodes,
        frame_transforms=transforms,
    )
    if path is None:
        return _refusal(
            refusal_code=REFUSAL_GEO_FRAME_INVALID,
            message="frame path or transform edge is missing",
            details={"from_frame_id": from_frame_id, "to_frame_id": to_frame_id},
        )
    lca_frame_id, path_frame_ids, transform_steps = path
    payload = {
        "result": "complete",
        "from_frame_id": from_frame_id,
        "to_frame_id": to_frame_id,
        "graph_version": version,
        "lca_frame_id": lca_frame_id,
        "path_frame_ids": list(path_frame_ids),
        "transform_chain": [
            {
                "direction": str(step.get("direction", "")),
                "from_frame_id": str(step.get("from_frame_id", "")),
                "to_frame_id": str(step.get("to_frame_id", "")),
                "transform": normalize_frame_transform(step.get("transform")),
            }
            for step in transform_steps
        ],
        "target_topology_profile_id": str(nodes[to_frame_id].get("topology_profile_id", "")),
        "target_metric_profile_id": str(nodes[to_frame_id].get("metric_profile_id", "")),
        "target_chart_id": str(nodes[to_frame_id].get("chart_id", "")),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


def position_to_frame(
    position_ref: Mapping[str, object] | None,
    target_frame_id: str,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    target_token = str(target_frame_id or "").strip()
    if not target_token:
        return _refusal(
            refusal_code=REFUSAL_GEO_FRAME_INVALID,
            message="target_frame_id is required",
        )
    nodes = _frame_nodes_by_id(frame_nodes, topology_registry_payload=topology_registry_payload)
    transforms = _frame_transforms_by_edge(frame_transform_rows)
    position_row = normalize_position_ref(
        position_ref,
        frame_nodes=list(nodes.values()),
        topology_registry_payload=topology_registry_payload,
    )
    if position_row is None:
        return _refusal(
            refusal_code=REFUSAL_GEO_POSITION_INVALID,
            message="position_ref is invalid",
        )
    source_frame_id = str(position_row.get("frame_id", "")).strip()
    if source_frame_id not in nodes or target_token not in nodes:
        return _refusal(
            refusal_code=REFUSAL_GEO_FRAME_INVALID,
            message="position_ref references missing frame node",
            details={"source_frame_id": source_frame_id, "target_frame_id": target_token},
        )
    version = str(graph_version or "").strip() or frame_graph_hash(
        frame_nodes=list(nodes.values()),
        frame_transform_rows=list(transforms.values()),
        topology_registry_payload=topology_registry_payload,
    )
    seed = {
        "query_kind": "position_to_frame",
        "position_ref_hash": position_ref_hash(position_row),
        "target_frame_id": target_token,
        "graph_version": version,
    }
    cache_key = _query_cache_key("position_to_frame", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    transform_payload = frame_get_transform(
        source_frame_id,
        target_token,
        frame_nodes=list(nodes.values()),
        frame_transform_rows=list(transforms.values()),
        graph_version=version,
        topology_registry_payload=topology_registry_payload,
    )
    if str(transform_payload.get("result", "")) != "complete":
        return transform_payload

    working_dimension = max(
        len(list(position_row.get("local_position") or [])),
        _dimension_for_frame(nodes[source_frame_id], topology_registry_payload=topology_registry_payload),
        _dimension_for_frame(nodes[target_token], topology_registry_payload=topology_registry_payload),
        1,
    )
    coords = _normalize_vector(position_row.get("local_position"), working_dimension)
    for step in list(transform_payload.get("transform_chain") or []):
        transform_row = normalize_frame_transform(_as_map(step).get("transform"))
        direction = str(_as_map(step).get("direction", "")).strip()
        from_frame_row = dict(nodes.get(str(step.get("from_frame_id", ""))) or {})
        to_frame_row = dict(nodes.get(str(step.get("to_frame_id", ""))) or {})
        try:
            coords = _apply_transform(
                coords,
                transform_row,
                from_frame_row=from_frame_row,
                to_frame_row=to_frame_row,
                inverse=(direction == "inverse"),
            )
        except ValueError as exc:
            return _refusal(
                refusal_code=REFUSAL_GEO_FRAME_INVALID,
                message="frame transform application failed",
                details={
                    "from_frame_id": str(step.get("from_frame_id", "")),
                    "to_frame_id": str(step.get("to_frame_id", "")),
                    "error": str(exc),
                },
            )

    target_dimension = _dimension_for_frame(nodes[target_token], topology_registry_payload=topology_registry_payload)
    converted = build_position_ref(
        object_id=str(position_row.get("object_id", "")),
        frame_id=target_token,
        local_position=_normalize_vector(coords, target_dimension),
        extensions={
            "source_frame_id": source_frame_id,
            "graph_version": version,
        },
    )
    payload = {
        "result": "complete",
        "graph_version": version,
        "source_position_ref": position_row,
        "target_position_ref": converted,
        "transform": transform_payload,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


def position_distance(
    pos_a_ref: Mapping[str, object] | None,
    pos_b_ref: Mapping[str, object] | None,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    nodes = _frame_nodes_by_id(frame_nodes, topology_registry_payload=topology_registry_payload)
    transforms = _frame_transforms_by_edge(frame_transform_rows)
    pos_a = normalize_position_ref(pos_a_ref, frame_nodes=list(nodes.values()), topology_registry_payload=topology_registry_payload)
    pos_b = normalize_position_ref(pos_b_ref, frame_nodes=list(nodes.values()), topology_registry_payload=topology_registry_payload)
    if pos_a is None or pos_b is None:
        return _refusal(
            refusal_code=REFUSAL_GEO_POSITION_INVALID,
            message="position_ref is invalid",
        )
    frame_a = str(pos_a.get("frame_id", "")).strip()
    frame_b = str(pos_b.get("frame_id", "")).strip()
    if frame_a not in nodes or frame_b not in nodes:
        return _refusal(
            refusal_code=REFUSAL_GEO_FRAME_INVALID,
            message="position_ref references missing frame node",
            details={"frame_a": frame_a, "frame_b": frame_b},
        )
    version = str(graph_version or "").strip() or frame_graph_hash(
        frame_nodes=list(nodes.values()),
        frame_transform_rows=list(transforms.values()),
        topology_registry_payload=topology_registry_payload,
    )
    seed = {
        "query_kind": "position_distance",
        "pos_a_hash": position_ref_hash(pos_a),
        "pos_b_hash": position_ref_hash(pos_b),
        "graph_version": version,
    }
    cache_key = _query_cache_key("position_distance", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    comparison_frame_id = _lowest_common_ancestor(frame_a, frame_b, nodes) or min(frame_a, frame_b)
    conv_a = position_to_frame(
        pos_a,
        comparison_frame_id,
        frame_nodes=list(nodes.values()),
        frame_transform_rows=list(transforms.values()),
        graph_version=version,
        topology_registry_payload=topology_registry_payload,
    )
    if str(conv_a.get("result", "")) != "complete":
        return conv_a
    conv_b = position_to_frame(
        pos_b,
        comparison_frame_id,
        frame_nodes=list(nodes.values()),
        frame_transform_rows=list(transforms.values()),
        graph_version=version,
        topology_registry_payload=topology_registry_payload,
    )
    if str(conv_b.get("result", "")) != "complete":
        return conv_b

    comparison_frame = dict(nodes.get(comparison_frame_id) or {})
    distance_result = geo_distance(
        {"coords": list((_as_map(conv_a.get("target_position_ref")).get("local_position") or []))},
        {"coords": list((_as_map(conv_b.get("target_position_ref")).get("local_position") or []))},
        str(comparison_frame.get("topology_profile_id", "")),
        str(comparison_frame.get("metric_profile_id", "")),
        topology_registry_payload=topology_registry_payload,
        metric_registry_payload=metric_registry_payload,
    )
    if str(distance_result.get("result", "")) != "complete":
        return distance_result
    payload = {
        "result": "complete",
        "graph_version": version,
        "comparison_frame_id": comparison_frame_id,
        "distance_mm": int(_as_int(distance_result.get("distance_mm", 0), 0)),
        "position_a_in_frame": _as_map(conv_a.get("target_position_ref")),
        "position_b_in_frame": _as_map(conv_b.get("target_position_ref")),
        "metric_query": distance_result,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


__all__ = [
    "REFUSAL_GEO_FRAME_INVALID",
    "REFUSAL_GEO_POSITION_INVALID",
    "build_position_ref",
    "frame_get_transform",
    "frame_graph_hash",
    "normalize_frame_node",
    "normalize_frame_transform",
    "normalize_position_ref",
    "position_distance",
    "position_ref_hash",
    "position_to_frame",
]
