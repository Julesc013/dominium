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


def validate_pack(data, repo_root):
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
        for j, node in enumerate(normalize_list(assembly.get("nodes"))):
            if not isinstance(node, dict):
                continue
            node_type = str(node.get("node_type", "")).lower()
            ref_id = node.get("ref_id")
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
            iface_ref = edge.get("interface_ref", {})
            iface_id = iface_ref.get("interface_id") if isinstance(iface_ref, dict) else None
            if iface_id and iface_id not in interface_ids:
                add_issue(issues, "ref_interface_missing", "interface reference missing", f"assemblies[{i}].edges[{j}]")
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

    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate FAB-0 data packs.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    data = load_json(args.input)
    issues = validate_pack(data, repo_root)
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
