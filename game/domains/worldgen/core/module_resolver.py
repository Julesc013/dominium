"""Deterministic module DAG resolver for worldgen module registry entries."""

from __future__ import annotations

from typing import Dict, List, Tuple


def _refusal(reason_code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, str]) -> Dict[str, object]:
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": dict(sorted((relevant_ids or {}).items(), key=lambda item: str(item[0]))),
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": "$.module_order",
            }
        ],
    }


def _collect_active_entries(registry_payload: dict) -> Tuple[List[dict], Dict[str, object]]:
    if not isinstance(registry_payload, dict):
        return [], _refusal(
            "refusal.module_registry_invalid",
            "worldgen module registry must be an object",
            "Provide a valid module registry payload.",
            {"registry_id": "worldgen_module_registry"},
        )
    record = registry_payload.get("record")
    if not isinstance(record, dict):
        return [], _refusal(
            "refusal.module_registry_invalid",
            "worldgen module registry missing record object",
            "Provide a valid module registry record.entries list.",
            {"registry_id": "worldgen_module_registry"},
        )
    entries = record.get("entries")
    if not isinstance(entries, list):
        return [], _refusal(
            "refusal.module_registry_invalid",
            "worldgen module registry missing record.entries list",
            "Provide a valid module registry record.entries list.",
            {"registry_id": "worldgen_module_registry"},
        )
    active = []
    for row in entries:
        if not isinstance(row, dict):
            continue
        module_id = str(row.get("module_id", "")).strip()
        if not module_id:
            continue
        status = str(row.get("module_status", "active")).strip()
        if status == "deprecated":
            continue
        active.append(
            {
                "module_id": module_id,
                "module_status": status,
                "depends_on": sorted(
                    set(str(item).strip() for item in (row.get("depends_on") or []) if str(item).strip())
                ),
                "outputs": sorted(
                    set(str(item).strip() for item in (row.get("outputs") or []) if str(item).strip())
                ),
            }
        )
    return sorted(active, key=lambda item: str(item.get("module_id", ""))), {}


def resolve_worldgen_module_order(registry_payload: dict, include_experimental: bool = True) -> Dict[str, object]:
    """Resolve deterministic topological module order from worldgen module registry payload."""
    entries, entry_error = _collect_active_entries(registry_payload)
    if entry_error:
        return entry_error

    filtered = []
    for row in entries:
        status = str(row.get("module_status", "active")).strip()
        if status == "experimental" and not bool(include_experimental):
            continue
        filtered.append(dict(row))
    entries = sorted(filtered, key=lambda item: str(item.get("module_id", "")))

    module_map = {str(row.get("module_id", "")): dict(row) for row in entries}
    for row in entries:
        module_id = str(row.get("module_id", ""))
        for dep in row.get("depends_on") or []:
            if dep not in module_map:
                return _refusal(
                    "refusal.module_dependency_missing",
                    "module '{}' depends on missing module '{}'".format(module_id, dep),
                    "Declare dependency module in worldgen_module_registry.json or remove dependency.",
                    {"module_id": module_id, "dependency_module_id": dep},
                )

    incoming = {module_id: 0 for module_id in module_map}
    outgoing = {module_id: [] for module_id in module_map}
    for row in entries:
        module_id = str(row.get("module_id", ""))
        deps = sorted(set(row.get("depends_on") or []))
        incoming[module_id] = len(deps)
        for dep in deps:
            outgoing.setdefault(dep, []).append(module_id)

    queue = sorted(module_id for module_id, count in incoming.items() if int(count) == 0)
    order: List[str] = []
    while queue:
        current = queue.pop(0)
        order.append(current)
        for nxt in sorted(outgoing.get(current) or []):
            incoming[nxt] = int(incoming.get(nxt, 0)) - 1
            if int(incoming[nxt]) == 0:
                queue.append(nxt)
        queue = sorted(set(queue))

    if len(order) != len(module_map):
        remaining = sorted(module_id for module_id, count in incoming.items() if int(count) > 0)
        return _refusal(
            "refusal.module_dependency_cycle",
            "worldgen module dependency cycle detected",
            "Remove cyclic module dependencies in worldgen_module_registry.json.",
            {"remaining_modules": ",".join(remaining)},
        )

    output_to_module = {}
    for row in entries:
        module_id = str(row.get("module_id", ""))
        for output_key in row.get("outputs") or []:
            if output_key not in output_to_module:
                output_to_module[output_key] = []
            output_to_module[output_key].append(module_id)
    for key in sorted(output_to_module.keys()):
        output_to_module[key] = sorted(set(output_to_module[key]))

    return {
        "result": "complete",
        "module_order": order,
        "module_entries": entries,
        "module_output_map": output_to_module,
    }

