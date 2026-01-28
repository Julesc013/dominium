import argparse
import json
import os

from fab_lib import (
    load_json,
    load_units_table,
    make_refusal,
    REFUSAL_INTEGRITY,
    REFUSAL_INVALID,
)


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def id_set(records, key):
    out = {}
    for rec in records:
        if isinstance(rec, dict):
            val = rec.get(key)
            if isinstance(val, str):
                out[val] = rec
    return out


def id_tail(value):
    if not isinstance(value, str):
        return ""
    return value.split(".")[-1].lower()


def parse_directionality(value):
    tail = id_tail(value)
    if tail in ("input", "in"):
        return "input"
    if tail in ("output", "out"):
        return "output"
    if tail in ("bidirectional", "io", "both"):
        return "bidirectional"
    return "unknown"


def parse_interface_type(value):
    tail = id_tail(value)
    if tail in ("mechanical", "electrical", "fluid", "data", "thermal"):
        return tail
    return "unknown"


def hash32(value):
    if not isinstance(value, str):
        return 0
    h = 2166136261
    for ch in value.encode("utf-8"):
        h ^= ch
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def part_interface_ids(part):
    out = set()
    if not isinstance(part, dict):
        return out
    for ref in normalize_list(part.get("interfaces")):
        iface_id = None
        if isinstance(ref, dict):
            iface_id = ref.get("interface_id")
        elif isinstance(ref, str):
            iface_id = ref
        if isinstance(iface_id, str):
            out.add(iface_id)
    return out


def resolve_edge_interface_ids(edge):
    if not isinstance(edge, dict):
        return None, None, None
    iface_ref = edge.get("interface_ref", {})
    iface_id = iface_ref.get("interface_id") if isinstance(iface_ref, dict) else None
    if not isinstance(iface_id, str):
        iface_id = edge.get("interface_id") if isinstance(edge.get("interface_id"), str) else None
    meta = edge.get("metadata", {})
    from_id = meta.get("from_interface_id") if isinstance(meta, dict) else None
    to_id = meta.get("to_interface_id") if isinstance(meta, dict) else None
    return iface_id, from_id or iface_id, to_id or iface_id


def collect_assembly_interfaces(assembly_id, assemblies, parts, cache, stack):
    if assembly_id in cache:
        return cache[assembly_id]
    if assembly_id in stack:
        return set()
    assembly = assemblies.get(assembly_id)
    if not isinstance(assembly, dict):
        cache[assembly_id] = set()
        return cache[assembly_id]
    stack.add(assembly_id)
    out = set()
    for node in normalize_list(assembly.get("nodes")):
        if not isinstance(node, dict):
            continue
        node_type = str(node.get("node_type", "")).lower()
        ref_id = node.get("ref_id")
        if node_type == "part":
            out.update(part_interface_ids(parts.get(ref_id)))
        elif node_type == "subassembly":
            out.update(collect_assembly_interfaces(ref_id, assemblies, parts, cache, stack))
    stack.remove(assembly_id)
    cache[assembly_id] = out
    return out


def empty_capacity_totals():
    return {
        "mechanical": {"value": 0, "unit": None, "unit_mismatch": False},
        "electrical": {"value": 0, "unit": None, "unit_mismatch": False},
        "fluid": {"value": 0, "unit": None, "unit_mismatch": False},
        "data": {"value": 0, "unit": None, "unit_mismatch": False},
        "thermal": {"value": 0, "unit": None, "unit_mismatch": False},
    }


def add_capacity(bucket, value, unit):
    if bucket["unit"] is None:
        bucket["unit"] = unit
    if bucket["unit"] != unit:
        bucket["unit_mismatch"] = True
        return
    if isinstance(value, int):
        bucket["value"] += value


def quantity_value(qty):
    if not isinstance(qty, dict):
        return None, None
    value = qty.get("value")
    unit = qty.get("unit")
    if not isinstance(value, int) or not isinstance(unit, str):
        return None, None
    return value, unit


def check_interface_compat(a, b):
    trace = {
        "from_interface_id": a.get("interface_id") if isinstance(a, dict) else None,
        "to_interface_id": b.get("interface_id") if isinstance(b, dict) else None,
        "from_type": None,
        "to_type": None,
        "from_directionality": None,
        "to_directionality": None,
        "from_capacity": None,
        "to_capacity": None,
        "allow_degraded": False,
    }
    if not isinstance(a, dict) or not isinstance(b, dict):
        return "refused", make_refusal(*REFUSAL_INVALID, "invalid interface", {}), trace
    type_a = parse_interface_type(a.get("interface_type"))
    type_b = parse_interface_type(b.get("interface_type"))
    trace["from_type"] = type_a
    trace["to_type"] = type_b
    if type_a == "unknown" or type_b == "unknown" or type_a != type_b:
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "interface type mismatch", {}), trace
    dir_a = parse_directionality(a.get("directionality"))
    dir_b = parse_directionality(b.get("directionality"))
    trace["from_directionality"] = dir_a
    trace["to_directionality"] = dir_b
    if dir_a == "unknown" or dir_b == "unknown":
        return "refused", make_refusal(*REFUSAL_INVALID, "directionality invalid", {}), trace
    if dir_a == "input" and dir_b == "input":
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "directionality clash", {}), trace
    if dir_a == "output" and dir_b == "output":
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "directionality clash", {}), trace
    val_a, unit_a = quantity_value(a.get("capacity"))
    val_b, unit_b = quantity_value(b.get("capacity"))
    trace["from_capacity"] = {"value": val_a, "unit": unit_a}
    trace["to_capacity"] = {"value": val_b, "unit": unit_b}
    if unit_a != unit_b:
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "capacity units mismatch", {}), trace
    if val_a != val_b:
        allow_degraded = a.get("compatibility_rules", {}).get("allow_degraded") or b.get("compatibility_rules", {}).get("allow_degraded")
        trace["allow_degraded"] = bool(allow_degraded)
        if allow_degraded:
            return "degraded", None, trace
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "capacity mismatch", {}), trace
    return "compatible", None, trace


def aggregate_assembly(assembly_id, assemblies, parts, interfaces, seen):
    if assembly_id in seen:
        return {"mass": 0, "volume": 0, "hosted": [], "capacities": empty_capacity_totals(), "breakdown": []}
    seen.add(assembly_id)
    assembly = assemblies.get(assembly_id)
    if not assembly:
        return {"mass": 0, "volume": 0, "hosted": [], "capacities": empty_capacity_totals(), "breakdown": []}
    total_mass = 0
    total_volume = 0
    hosted = []
    capacities = empty_capacity_totals()
    breakdown = []
    for proc in normalize_list(assembly.get("hosted_processes")):
        if isinstance(proc, dict):
            pid = proc.get("process_family_id")
        else:
            pid = proc
        if pid and pid not in hosted:
            hosted.append(pid)
    nodes = [node for node in normalize_list(assembly.get("nodes")) if isinstance(node, dict)]
    nodes = sorted(nodes, key=lambda n: n.get("node_id", ""))
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_type = str(node.get("node_type", "")).lower()
        ref_id = node.get("ref_id")
        node_id = node.get("node_id")
        if node_type == "part":
            part = parts.get(ref_id)
            if not part:
                continue
            mass_value, _unit = quantity_value(part.get("mass"))
            vol_value, _unit2 = quantity_value(part.get("volume"))
            if isinstance(mass_value, int):
                total_mass += mass_value
            if isinstance(vol_value, int):
                total_volume += vol_value
            iface_ids = sorted(part_interface_ids(part))
            for iface_id in iface_ids:
                iface = interfaces.get(iface_id)
                if not isinstance(iface, dict):
                    continue
                iface_type = parse_interface_type(iface.get("interface_type"))
                cap_value, cap_unit = quantity_value(iface.get("capacity"))
                if iface_type in capacities:
                    add_capacity(capacities[iface_type], cap_value, cap_unit)
            breakdown.append({
                "node_id": node_id,
                "node_type": node_type,
                "ref_id": ref_id,
                "mass": mass_value if isinstance(mass_value, int) else 0,
                "volume": vol_value if isinstance(vol_value, int) else 0,
                "interfaces": iface_ids,
            })
        elif node_type == "subassembly":
            sub = aggregate_assembly(ref_id, assemblies, parts, interfaces, seen)
            total_mass += sub["mass"]
            total_volume += sub["volume"]
            for pid in sub["hosted"]:
                if pid not in hosted:
                    hosted.append(pid)
            for key, bucket in sub["capacities"].items():
                if key in capacities:
                    add_capacity(capacities[key], bucket.get("value"), bucket.get("unit"))
                    if bucket.get("unit_mismatch"):
                        capacities[key]["unit_mismatch"] = True
            breakdown.append({
                "node_id": node_id,
                "node_type": node_type,
                "ref_id": ref_id,
                "mass": sub["mass"],
                "volume": sub["volume"],
                "interfaces": [],
            })
    hosted = sorted(hosted)
    breakdown = sorted(breakdown, key=lambda entry: entry.get("node_id", ""))
    return {"mass": total_mass, "volume": total_volume, "hosted": hosted, "capacities": capacities, "breakdown": breakdown}


def main():
    parser = argparse.ArgumentParser(description="Inspect FAB-0 data packs.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    _units = load_units_table(repo_root)
    data = load_json(args.input)

    materials = normalize_list(data.get("materials"))
    interfaces_list = normalize_list(data.get("interfaces"))
    parts_list = normalize_list(data.get("parts"))
    assemblies_list = normalize_list(data.get("assemblies"))
    process_families_list = normalize_list(data.get("process_families"))

    interfaces = id_set(interfaces_list, "interface_id")
    parts = id_set(parts_list, "part_id")
    assemblies = id_set(assemblies_list, "assembly_id")
    assembly_iface_cache = {}

    assembly_summaries = []
    for assembly_id in sorted(assemblies.keys()):
        summary = aggregate_assembly(assembly_id, assemblies, parts, interfaces, set())
        assembly_summaries.append({
            "assembly_id": assembly_id,
            "total_mass": summary["mass"],
            "total_volume": summary["volume"],
            "hosted_processes": summary["hosted"],
            "capacity_totals": summary["capacities"],
            "node_breakdown": summary["breakdown"],
        })

    edge_reports = []
    for assembly_id in sorted(assemblies.keys()):
        assembly = assemblies[assembly_id]
        node_map = {}
        for node in normalize_list(assembly.get("nodes")):
            if not isinstance(node, dict):
                continue
            node_id = node.get("node_id")
            if isinstance(node_id, str):
                node_map[node_id] = node
        for edge in normalize_list(assembly.get("edges")):
            if not isinstance(edge, dict):
                continue
            edge_id = edge.get("edge_id", "")
            iface_id, from_iface_id, to_iface_id = resolve_edge_interface_ids(edge)
            compat = "refused"
            refusal = None
            trace = {
                "from_interface_id": from_iface_id,
                "to_interface_id": to_iface_id,
            }

            from_node_id = edge.get("from_node_id")
            to_node_id = edge.get("to_node_id")
            from_node = node_map.get(from_node_id) if isinstance(from_node_id, str) else None
            to_node = node_map.get(to_node_id) if isinstance(to_node_id, str) else None

            if not iface_id:
                refusal = make_refusal(*REFUSAL_INVALID, "interface reference missing", {"edge_id": edge_id})
            else:
                iface_a = interfaces.get(from_iface_id) if from_iface_id else None
                iface_b = interfaces.get(to_iface_id) if to_iface_id else None
                if not iface_a or not iface_b:
                    refusal = make_refusal(*REFUSAL_INTEGRITY, "interface missing", {"edge_id": edge_id})
                else:
                    compat, refusal, trace = check_interface_compat(iface_a, iface_b)

            if compat != "refused":
                if isinstance(from_node, dict):
                    node_type = str(from_node.get("node_type", "")).lower()
                    ref_id = from_node.get("ref_id")
                    if node_type == "part":
                        iface_set = part_interface_ids(parts.get(ref_id))
                    elif node_type == "subassembly":
                        iface_set = collect_assembly_interfaces(ref_id, assemblies, parts,
                                                                assembly_iface_cache, set())
                    else:
                        iface_set = set()
                    if from_iface_id and iface_set and from_iface_id not in iface_set:
                        compat = "refused"
                        refusal = make_refusal(*REFUSAL_INTEGRITY, "from-node interface missing",
                                               {"edge_id": edge_id, "from_interface_id": from_iface_id})
                if isinstance(to_node, dict) and compat != "refused":
                    node_type = str(to_node.get("node_type", "")).lower()
                    ref_id = to_node.get("ref_id")
                    if node_type == "part":
                        iface_set = part_interface_ids(parts.get(ref_id))
                    elif node_type == "subassembly":
                        iface_set = collect_assembly_interfaces(ref_id, assemblies, parts,
                                                                assembly_iface_cache, set())
                    else:
                        iface_set = set()
                    if to_iface_id and iface_set and to_iface_id not in iface_set:
                        compat = "refused"
                        refusal = make_refusal(*REFUSAL_INTEGRITY, "to-node interface missing",
                                               {"edge_id": edge_id, "to_interface_id": to_iface_id})
            edge_reports.append({
                "assembly_id": assembly_id,
                "edge_id": edge_id,
                "interface_id": iface_id,
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "from_interface_id": from_iface_id,
                "to_interface_id": to_iface_id,
                "compat": compat,
                "refusal": refusal,
                "trace": trace,
            })

    edge_reports = sorted(edge_reports, key=lambda r: (r.get("assembly_id", ""), r.get("edge_id", "")))
    payload = {"assemblies": assembly_summaries, "edges": edge_reports}

    if args.seed is not None:
        base_seed = int(args.seed)
        process_seeds = []
        for proc in process_families_list:
            if not isinstance(proc, dict):
                continue
            pid = proc.get("process_family_id")
            if not isinstance(pid, str):
                continue
            seed = base_seed ^ hash32(pid)
            process_seeds.append({
                "process_family_id": pid,
                "base_seed": base_seed,
                "seed": seed,
            })
        process_seeds = sorted(process_seeds, key=lambda entry: entry.get("process_family_id", ""))
        payload["process_seeds"] = process_seeds

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("fab_inspect: assemblies={}".format(len(assembly_summaries)))
    for entry in assembly_summaries:
        print("{assembly_id} mass={total_mass} volume={total_volume}".format(**entry))
    for edge in edge_reports:
        print("{assembly_id}:{edge_id} {compat}".format(**edge))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
