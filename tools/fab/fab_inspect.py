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


def quantity_value(qty):
    if not isinstance(qty, dict):
        return None, None
    value = qty.get("value")
    unit = qty.get("unit")
    if not isinstance(value, int) or not isinstance(unit, str):
        return None, None
    return value, unit


def check_interface_compat(a, b):
    if not isinstance(a, dict) or not isinstance(b, dict):
        return "refused", make_refusal(*REFUSAL_INVALID, "invalid interface", {})
    type_a = parse_interface_type(a.get("interface_type"))
    type_b = parse_interface_type(b.get("interface_type"))
    if type_a == "unknown" or type_b == "unknown" or type_a != type_b:
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "interface type mismatch", {})
    dir_a = parse_directionality(a.get("directionality"))
    dir_b = parse_directionality(b.get("directionality"))
    if dir_a == "unknown" or dir_b == "unknown":
        return "refused", make_refusal(*REFUSAL_INVALID, "directionality invalid", {})
    if dir_a == "input" and dir_b == "input":
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "directionality clash", {})
    if dir_a == "output" and dir_b == "output":
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "directionality clash", {})
    val_a, unit_a = quantity_value(a.get("capacity"))
    val_b, unit_b = quantity_value(b.get("capacity"))
    if unit_a != unit_b:
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "capacity units mismatch", {})
    if val_a != val_b:
        if a.get("compatibility_rules", {}).get("allow_degraded") or b.get("compatibility_rules", {}).get("allow_degraded"):
            return "degraded", None
        return "refused", make_refusal(*REFUSAL_INTEGRITY, "capacity mismatch", {})
    return "compatible", None


def aggregate_assembly(assembly_id, assemblies, parts, interfaces, seen):
    if assembly_id in seen:
        return {"mass": 0, "volume": 0, "hosted": []}
    seen.add(assembly_id)
    assembly = assemblies.get(assembly_id)
    if not assembly:
        return {"mass": 0, "volume": 0, "hosted": []}
    total_mass = 0
    total_volume = 0
    hosted = []
    for proc in normalize_list(assembly.get("hosted_processes")):
        if isinstance(proc, dict):
            pid = proc.get("process_family_id")
        else:
            pid = proc
        if pid and pid not in hosted:
            hosted.append(pid)
    for node in normalize_list(assembly.get("nodes")):
        if not isinstance(node, dict):
            continue
        node_type = str(node.get("node_type", "")).lower()
        ref_id = node.get("ref_id")
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
        elif node_type == "subassembly":
            sub = aggregate_assembly(ref_id, assemblies, parts, interfaces, seen)
            total_mass += sub["mass"]
            total_volume += sub["volume"]
            for pid in sub["hosted"]:
                if pid not in hosted:
                    hosted.append(pid)
    hosted = sorted(hosted)
    return {"mass": total_mass, "volume": total_volume, "hosted": hosted}


def main():
    parser = argparse.ArgumentParser(description="Inspect FAB-0 data packs.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    _units = load_units_table(repo_root)
    data = load_json(args.input)

    materials = normalize_list(data.get("materials"))
    interfaces_list = normalize_list(data.get("interfaces"))
    parts_list = normalize_list(data.get("parts"))
    assemblies_list = normalize_list(data.get("assemblies"))

    interfaces = id_set(interfaces_list, "interface_id")
    parts = id_set(parts_list, "part_id")
    assemblies = id_set(assemblies_list, "assembly_id")

    assembly_summaries = []
    for assembly_id in sorted(assemblies.keys()):
        summary = aggregate_assembly(assembly_id, assemblies, parts, interfaces, set())
        assembly_summaries.append({
            "assembly_id": assembly_id,
            "total_mass": summary["mass"],
            "total_volume": summary["volume"],
            "hosted_processes": summary["hosted"],
        })

    edge_reports = []
    for assembly_id in sorted(assemblies.keys()):
        assembly = assemblies[assembly_id]
        for edge in normalize_list(assembly.get("edges")):
            if not isinstance(edge, dict):
                continue
            edge_id = edge.get("edge_id", "")
            iface_ref = edge.get("interface_ref", {})
            iface_id = iface_ref.get("interface_id") if isinstance(iface_ref, dict) else None
            iface = interfaces.get(iface_id) if iface_id else None
            if iface:
                compat, refusal = check_interface_compat(iface, iface)
            else:
                compat, refusal = "refused", make_refusal(*REFUSAL_INTEGRITY, "interface missing", {})
            edge_reports.append({
                "assembly_id": assembly_id,
                "edge_id": edge_id,
                "interface_id": iface_id,
                "compat": compat,
                "refusal": refusal,
            })

    edge_reports = sorted(edge_reports, key=lambda r: (r.get("assembly_id", ""), r.get("edge_id", "")))
    payload = {"assemblies": assembly_summaries, "edges": edge_reports}

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
