import argparse
import json
import os
import sys

from fab_lib import (
    add_issue,
    iter_numeric_map,
    load_json,
    load_units_table,
    make_refusal,
    validate_id,
    validate_quantity,
    validate_unit_annotations,
    REFUSAL_CAPABILITY,
    REFUSAL_INTEGRITY,
    REFUSAL_INVALID,
)


REQUIRED_TOP_KEYS = [
    "materials",
    "interfaces",
    "parts",
    "assemblies",
    "process_families",
    "instruments",
    "standards",
    "qualities",
    "batches",
    "hazards",
    "substances",
]


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def id_set(records, key):
    out = set()
    for rec in records:
        if isinstance(rec, dict):
            val = rec.get(key)
            if isinstance(val, str):
                out.add(val)
    return out


def id_tail(value):
    if not isinstance(value, str):
        return ""
    return value.split(".")[-1].lower()


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
    iface_id = None
    if isinstance(iface_ref, dict):
        iface_id = iface_ref.get("interface_id")
    if not isinstance(iface_id, str):
        iface_id = edge.get("interface_id") if isinstance(edge.get("interface_id"), str) else None
    meta = edge.get("metadata", {})
    from_id = meta.get("from_interface_id") if isinstance(meta, dict) else None
    to_id = meta.get("to_interface_id") if isinstance(meta, dict) else None
    return iface_id, from_id or iface_id, to_id or iface_id




def detect_cycle(node_ids, edges):
    adj = {node_id: [] for node_id in node_ids}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        src = edge.get("from_node_id")
        dst = edge.get("to_node_id")
        if src in adj and dst in adj:
            adj[src].append(dst)
    state = {node_id: 0 for node_id in node_ids}

    def dfs(node_id):
        if state[node_id] == 1:
            return True
        if state[node_id] == 2:
            return False
        state[node_id] = 1
        for nxt in adj.get(node_id, []):
            if dfs(nxt):
                return True
        state[node_id] = 2
        return False

    for node_id in node_ids:
        if dfs(node_id):
            return True
    return False


def cycle_policy_allows(value):
    if not isinstance(value, str):
        return False
    tail = id_tail(value)
    return tail in ("allow", "allowed", "permit", "permitted")


def validate_material(record, idx, issues, unit_table):
    path = f"materials[{idx}]"
    material_id = record.get("material_id")
    validate_id(material_id, issues, f"{path}.material_id")
    traits = record.get("traits", {})
    failure_params = record.get("failure_params", {})
    unit_annotations = record.get("unit_annotations", {})
    numeric_paths = iter_numeric_map(traits, "traits")
    numeric_paths.extend(iter_numeric_map(failure_params, "failure_params"))
    validate_unit_annotations(unit_annotations, numeric_paths, issues, unit_table)
    if "extensions" not in record:
        add_issue(issues, "extensions_missing", "extensions missing", f"{path}.extensions")


def validate_interface(record, idx, issues, unit_table):
    path = f"interfaces[{idx}]"
    interface_id = record.get("interface_id")
    validate_id(interface_id, issues, f"{path}.interface_id")
    validate_quantity(record.get("capacity"), f"{path}.capacity", issues, unit_table)
    if "unit_annotations" not in record:
        add_issue(issues, "unit_annotations_missing", "unit_annotations missing", f"{path}.unit_annotations")


def validate_part(record, idx, issues, unit_table):
    path = f"parts[{idx}]"
    part_id = record.get("part_id")
    validate_id(part_id, issues, f"{path}.part_id")
    material_ref = record.get("material_ref", {})
    if not isinstance(material_ref, dict) or "material_id" not in material_ref:
        add_issue(issues, "material_ref_missing", "material_ref missing", f"{path}.material_ref")
    validate_quantity(record.get("mass"), f"{path}.mass", issues, unit_table)
    validate_quantity(record.get("volume"), f"{path}.volume", issues, unit_table)
    if "unit_annotations" not in record:
        add_issue(issues, "unit_annotations_missing", "unit_annotations missing", f"{path}.unit_annotations")


def validate_assembly(record, idx, issues, unit_table):
    path = f"assemblies[{idx}]"
    assembly_id = record.get("assembly_id")
    validate_id(assembly_id, issues, f"{path}.assembly_id")
    unit_annotations = record.get("unit_annotations", {})
    throughput = record.get("throughput_limits", {})
    maintenance = record.get("maintenance", {})
    numeric_paths = iter_numeric_map(throughput, "throughput_limits")
    numeric_paths.extend(iter_numeric_map(maintenance, "maintenance"))
    validate_unit_annotations(unit_annotations, numeric_paths, issues, unit_table)


def validate_process_family(record, idx, issues, unit_table):
    path = f"process_families[{idx}]"
    proc_id = record.get("process_family_id")
    validate_id(proc_id, issues, f"{path}.process_family_id")
    for key in ("inputs", "outputs", "wastes"):
        entries = normalize_list(record.get(key))
        for j, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            validate_quantity(entry.get("quantity"), f"{path}.{key}[{j}].quantity", issues, unit_table)
    if "unit_annotations" not in record:
        add_issue(issues, "unit_annotations_missing", "unit_annotations missing", f"{path}.unit_annotations")


def validate_instrument(record, idx, issues, unit_table):
    path = f"instruments[{idx}]"
    instrument_id = record.get("instrument_id")
    validate_id(instrument_id, issues, f"{path}.instrument_id")
    if "unit_annotations" not in record:
        add_issue(issues, "unit_annotations_missing", "unit_annotations missing", f"{path}.unit_annotations")


def validate_standard(record, idx, issues):
    path = f"standards[{idx}]"
    standard_id = record.get("standard_id")
    validate_id(standard_id, issues, f"{path}.standard_id")


def validate_quality(record, idx, issues):
    path = f"qualities[{idx}]"
    quality_id = record.get("quality_id")
    validate_id(quality_id, issues, f"{path}.quality_id")


def validate_batch(record, idx, issues, unit_table):
    path = f"batches[{idx}]"
    batch_id = record.get("batch_id")
    validate_id(batch_id, issues, f"{path}.batch_id")
    validate_quantity(record.get("quantity"), f"{path}.quantity", issues, unit_table)


def validate_hazard(record, idx, issues):
    path = f"hazards[{idx}]"
    hazard_id = record.get("hazard_id")
    validate_id(hazard_id, issues, f"{path}.hazard_id")


def validate_substance(record, idx, issues):
    path = f"substances[{idx}]"
    substance_id = record.get("substance_id")
    validate_id(substance_id, issues, f"{path}.substance_id")


def detect_pack_root(input_path):
    if not isinstance(input_path, str):
        return None
    norm = input_path.replace("\\", "/")
    if norm.endswith("/data/fab_pack.json"):
        return os.path.dirname(os.path.dirname(input_path))
    return None


def parse_maturity_label(text):
    if not isinstance(text, str):
        return None
    for raw in text.splitlines():
        line = raw.strip()
        if line.lower().startswith("maturity:"):
            value = line.split(":", 1)[1].strip()
            value = value.rstrip(".")
            return value.upper()
    return None


def validate_maturity(pack_root, issues):
    if not pack_root:
        return
    readme = os.path.join(pack_root, "docs", "README.md")
    if not os.path.isfile(readme):
        add_issue(issues, "maturity_missing", "maturity label missing (docs/README.md)", "docs/README.md")
        return
    with open(readme, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    maturity = parse_maturity_label(text)
    if maturity not in ("PARAMETRIC", "STRUCTURAL", "BOUNDED", "INCOMPLETE"):
        add_issue(issues, "maturity_invalid", "maturity label invalid or missing", "docs/README.md")


def validate_pack(data, repo_root, pack_root=None):
    issues = []
    unit_table = load_units_table(repo_root)

    if not isinstance(data, dict):
        add_issue(issues, "pack_type", "pack must be object", "pack")
        return issues

    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            add_issue(issues, "pack_key_missing", f"missing key {key}", key)

    materials = normalize_list(data.get("materials"))
    interfaces = normalize_list(data.get("interfaces"))
    parts = normalize_list(data.get("parts"))
    assemblies = normalize_list(data.get("assemblies"))
    process_families = normalize_list(data.get("process_families"))
    instruments = normalize_list(data.get("instruments"))
    standards = normalize_list(data.get("standards"))
    qualities = normalize_list(data.get("qualities"))
    batches = normalize_list(data.get("batches"))
    hazards = normalize_list(data.get("hazards"))
    substances = normalize_list(data.get("substances"))

    part_map = {part.get("part_id"): part for part in parts if isinstance(part, dict)}

    for i, rec in enumerate(materials):
        if isinstance(rec, dict):
            validate_material(rec, i, issues, unit_table)
    for i, rec in enumerate(interfaces):
        if isinstance(rec, dict):
            validate_interface(rec, i, issues, unit_table)
    for i, rec in enumerate(parts):
        if isinstance(rec, dict):
            validate_part(rec, i, issues, unit_table)
    for i, rec in enumerate(assemblies):
        if isinstance(rec, dict):
            validate_assembly(rec, i, issues, unit_table)
    for i, rec in enumerate(process_families):
        if isinstance(rec, dict):
            validate_process_family(rec, i, issues, unit_table)
    for i, rec in enumerate(instruments):
        if isinstance(rec, dict):
            validate_instrument(rec, i, issues, unit_table)
    for i, rec in enumerate(standards):
        if isinstance(rec, dict):
            validate_standard(rec, i, issues)
    for i, rec in enumerate(qualities):
        if isinstance(rec, dict):
            validate_quality(rec, i, issues)
    for i, rec in enumerate(batches):
        if isinstance(rec, dict):
            validate_batch(rec, i, issues, unit_table)
    for i, rec in enumerate(hazards):
        if isinstance(rec, dict):
            validate_hazard(rec, i, issues)
    for i, rec in enumerate(substances):
        if isinstance(rec, dict):
            validate_substance(rec, i, issues)

    # Cross-reference validation
    material_ids = id_set(materials, "material_id")
    interface_ids = id_set(interfaces, "interface_id")
    process_ids = id_set(process_families, "process_family_id")
    instrument_ids = id_set(instruments, "instrument_id")
    standard_ids = id_set(standards, "standard_id")
    hazard_ids = id_set(hazards, "hazard_id")

    for i, part in enumerate(parts):
        if not isinstance(part, dict):
            continue
        material_ref = part.get("material_ref", {})
        mat_id = material_ref.get("material_id") if isinstance(material_ref, dict) else None
        if mat_id and mat_id not in material_ids:
            add_issue(issues, "ref_material_missing", "material reference missing", f"parts[{i}].material_ref")
        for j, ref in enumerate(normalize_list(part.get("interfaces"))):
            if isinstance(ref, dict):
                iface_id = ref.get("interface_id")
                if iface_id and iface_id not in interface_ids:
                    add_issue(issues, "ref_interface_missing", "interface reference missing", f"parts[{i}].interfaces[{j}]")

    for i, assembly in enumerate(assemblies):
        if not isinstance(assembly, dict):
            continue
        node_map = {}
        for j, node in enumerate(normalize_list(assembly.get("nodes"))):
            if not isinstance(node, dict):
                continue
            node_type = str(node.get("node_type", "")).lower()
            ref_id = node.get("ref_id")
            node_id = node.get("node_id")
            if isinstance(node_id, str):
                node_map[node_id] = node
            if node_type == "part":
                if ref_id not in id_set(parts, "part_id"):
                    add_issue(issues, "ref_part_missing", "part reference missing", f"assemblies[{i}].nodes[{j}]")
            elif node_type == "subassembly":
                if ref_id not in id_set(assemblies, "assembly_id"):
                    add_issue(issues, "ref_assembly_missing", "assembly reference missing", f"assemblies[{i}].nodes[{j}]")
            else:
                add_issue(issues, "node_type_invalid", "node_type must be part or subassembly", f"assemblies[{i}].nodes[{j}]")
        for j, edge in enumerate(normalize_list(assembly.get("edges"))):
            if not isinstance(edge, dict):
                continue
            from_node_id = edge.get("from_node_id")
            to_node_id = edge.get("to_node_id")
            if from_node_id and from_node_id not in node_map:
                add_issue(issues, "ref_node_missing", "edge from-node missing", f"assemblies[{i}].edges[{j}].from_node_id")
            if to_node_id and to_node_id not in node_map:
                add_issue(issues, "ref_node_missing", "edge to-node missing", f"assemblies[{i}].edges[{j}].to_node_id")

            iface_id, from_iface_id, to_iface_id = resolve_edge_interface_ids(edge)
            for label, iface in (("interface_id", iface_id),
                                 ("from_interface_id", from_iface_id),
                                 ("to_interface_id", to_iface_id)):
                if iface and iface not in interface_ids:
                    add_issue(issues, "ref_interface_missing", "interface reference missing",
                              f"assemblies[{i}].edges[{j}].{label}")

            if isinstance(from_node_id, str) and from_iface_id:
                node = node_map.get(from_node_id)
                node_type = str(node.get("node_type", "")).lower() if isinstance(node, dict) else ""
                ref_id = node.get("ref_id") if isinstance(node, dict) else None
                if node_type == "part":
                    iface_set = part_interface_ids(part_map.get(ref_id))
                else:
                    iface_set = set()
                if from_iface_id and iface_set and from_iface_id not in iface_set:
                    add_issue(issues, "ref_interface_missing", "interface missing on from-node",
                              f"assemblies[{i}].edges[{j}].from_node_id")

            if isinstance(to_node_id, str) and to_iface_id:
                node = node_map.get(to_node_id)
                node_type = str(node.get("node_type", "")).lower() if isinstance(node, dict) else ""
                ref_id = node.get("ref_id") if isinstance(node, dict) else None
                if node_type == "part":
                    iface_set = part_interface_ids(part_map.get(ref_id))
                else:
                    iface_set = set()
                if to_iface_id and iface_set and to_iface_id not in iface_set:
                    add_issue(issues, "ref_interface_missing", "interface missing on to-node",
                              f"assemblies[{i}].edges[{j}].to_node_id")

        node_ids = list(node_map.keys())
        edges = normalize_list(assembly.get("edges"))
        extensions = assembly.get("extensions", {}) if isinstance(assembly.get("extensions"), dict) else {}
        cycle_policy = extensions.get("cycle_policy")
        if cycle_policy is not None and not cycle_policy_allows(cycle_policy) and id_tail(cycle_policy) not in (
                "forbid", "forbidden", "deny", "denied"):
            add_issue(issues, "cycle_policy_invalid", "cycle_policy invalid", f"assemblies[{i}].extensions.cycle_policy")
        if node_ids and detect_cycle(node_ids, edges) and not cycle_policy_allows(cycle_policy):
            add_issue(issues, "cycle_forbidden", "assembly contains forbidden cycle", f"assemblies[{i}].edges")
        for j, proc in enumerate(normalize_list(assembly.get("hosted_processes"))):
            if isinstance(proc, dict):
                proc_id = proc.get("process_family_id")
                if proc_id and proc_id not in process_ids:
                    add_issue(issues, "ref_process_missing", "process_family reference missing", f"assemblies[{i}].hosted_processes[{j}]")

    for i, proc in enumerate(process_families):
        if not isinstance(proc, dict):
            continue
        for j, inst in enumerate(normalize_list(proc.get("required_instruments"))):
            inst_id = inst.get("instrument_id") if isinstance(inst, dict) else inst
            if inst_id and inst_id not in instrument_ids:
                add_issue(issues, "ref_instrument_missing", "instrument reference missing", f"process_families[{i}].required_instruments[{j}]")
        for j, std in enumerate(normalize_list(proc.get("required_standards"))):
            std_id = std.get("standard_id") if isinstance(std, dict) else std
            if std_id and std_id not in standard_ids:
                add_issue(issues, "ref_standard_missing", "standard reference missing", f"process_families[{i}].required_standards[{j}]")

    for i, inst in enumerate(instruments):
        if not isinstance(inst, dict):
            continue
        for j, std in enumerate(normalize_list(inst.get("required_standards"))):
            std_id = std.get("standard_id") if isinstance(std, dict) else std
            if std_id and std_id not in standard_ids:
                add_issue(issues, "ref_standard_missing", "standard reference missing", f"instruments[{i}].required_standards[{j}]")

    for i, sub in enumerate(substances):
        if not isinstance(sub, dict):
            continue
        for j, haz in enumerate(normalize_list(sub.get("hazards"))):
            haz_id = haz.get("hazard_id") if isinstance(haz, dict) else haz
            if haz_id and haz_id not in hazard_ids:
                add_issue(issues, "ref_hazard_missing", "hazard reference missing", f"substances[{i}].hazards[{j}]")

    validate_maturity(pack_root, issues)
    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate FAB-0 data packs.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--pack-root", default=None,
                        help="Optional pack root to enforce maturity labels (docs/README.md).")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    data = load_json(args.input)
    pack_root = args.pack_root or detect_pack_root(args.input)
    issues = validate_pack(data, repo_root, pack_root=pack_root)
    issues = sorted(issues, key=lambda item: (item.get("path", ""), item.get("code", "")))

    ok = len(issues) == 0
    if ok:
        payload = {"ok": True, "issues": []}
    else:
        integrity = any(issue["code"].startswith("ref_") for issue in issues)
        code_id, code = REFUSAL_INTEGRITY if integrity else REFUSAL_INVALID
        payload = {"ok": False,
                   "issues": issues,
                   "refusal": make_refusal(code_id, code, "fab validation failed", {})}

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0 if ok else 2

    if ok:
        print("fab_validate: ok")
        return 0
    print("fab_validate: failed")
    for issue in issues:
        print("{code} {path} {message}".format(**issue))
    return 2


if __name__ == "__main__":
    sys.exit(main())
