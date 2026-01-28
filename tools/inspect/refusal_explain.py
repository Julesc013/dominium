import argparse
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "distribution")))

from distribution_lib import discover_pack_manifests  # noqa: E402


SCHEMA_MAP = {
    "materials": "schema/material.schema",
    "interfaces": "schema/interface.schema",
    "parts": "schema/part.schema",
    "assemblies": "schema/assembly.schema",
    "process_families": "schema/process_family.schema",
    "instruments": "schema/instrument.schema",
    "standards": "schema/standard.schema",
    "qualities": "schema/quality.schema",
    "batches": "schema/batch_lot.schema",
    "hazards": "schema/hazard.schema",
    "substances": "schema/substance.schema",
}


SUGGESTION_MAP = {
    "id_shape": "Use lowercase reverse-DNS identifiers.",
    "unit_unknown": "Add the unit to the core units pack or correct the unit id.",
    "quantity_unit_missing": "Add a unit to the quantity field.",
    "quantity_value_missing": "Provide an integer value for the quantity field.",
    "quantity_overflow_missing": "Add overflow_behavior to the quantity field.",
    "unit_annotation_missing": "Add unit_annotations for all numeric fields.",
    "material_ref_missing": "Add the referenced material or fix the material_ref.",
    "ref_material_missing": "Add the referenced material or fix the material_ref.",
    "ref_interface_missing": "Ensure the interface exists and is referenced correctly.",
    "ref_part_missing": "Ensure the referenced part exists.",
    "ref_assembly_missing": "Ensure the referenced assembly exists.",
    "ref_process_missing": "Ensure the referenced process_family exists.",
    "ref_instrument_missing": "Ensure the referenced instrument exists.",
    "ref_standard_missing": "Ensure the referenced standard exists.",
    "ref_hazard_missing": "Ensure the referenced hazard exists.",
    "cycle_forbidden": "Remove the cycle or set a cycle_policy that allows it.",
    "maturity_missing": "Add a Maturity label to the pack docs/README.md.",
    "maturity_invalid": "Set Maturity to PARAMETRIC, STRUCTURAL, BOUNDED, or INCOMPLETE.",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_refusal_table(repo_root):
    candidates = [
        os.path.join(repo_root, "docs", "architecture", "REFUSAL_SEMANTICS.md"),
        os.path.join(repo_root, "docs", "arch", "REFUSAL_SEMANTICS.md"),
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        text = open(path, "r", encoding="utf-8", errors="replace").read()
        block_start = text.find("```refusal-codes")
        if block_start == -1:
            continue
        block_start = text.find("\n", block_start)
        block_end = text.find("```", block_start + 1)
        if block_end == -1:
            continue
        table = {}
        for raw in text[block_start:block_end].splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                continue
            try:
                code_id = int(parts[0])
            except ValueError:
                continue
            table[parts[1]] = {"code_id": code_id, "code": parts[1], "meaning": parts[2]}
        if table:
            return table
    return {}


def tokenize_path(path):
    tokens = []
    buf = ""
    i = 0
    while i < len(path):
        ch = path[i]
        if ch == ".":
            if buf:
                tokens.append(buf)
                buf = ""
            i += 1
            continue
        if ch == "[":
            if buf:
                tokens.append(buf)
                buf = ""
            end = path.find("]", i + 1)
            if end != -1:
                idx = path[i + 1:end]
                if idx.isdigit():
                    tokens.append(int(idx))
                i = end + 1
                continue
        buf += ch
        i += 1
    if buf:
        tokens.append(buf)
    return tokens


def extract_value(data, path):
    if not path:
        return None
    value = data
    for token in tokenize_path(path):
        if isinstance(token, int):
            if isinstance(value, list) and 0 <= token < len(value):
                value = value[token]
            else:
                return None
        else:
            if isinstance(value, dict) and token in value:
                value = value[token]
            else:
                return None
    return value


def schema_for_path(path):
    if not path:
        return None
    head = path.split(".", 1)[0]
    return SCHEMA_MAP.get(head)


def extract_refusal(payload):
    if isinstance(payload, dict) and isinstance(payload.get("refusal"), dict):
        return payload["refusal"]
    if isinstance(payload, dict) and "code" in payload:
        return payload
    return None


def extract_issues(payload):
    if isinstance(payload, dict):
        issues = payload.get("issues")
        if isinstance(issues, list):
            return issues
    return []


def build_capability_suggestions(repo_root, capability_id):
    if not capability_id:
        return []
    packs = discover_pack_manifests(["data/packs", "data/worldgen"], repo_root)
    providers = []
    for pack in packs:
        if capability_id in (pack.get("provides") or []):
            providers.append(pack.get("pack_id"))
    return sorted(set([p for p in providers if p]))


def main():
    parser = argparse.ArgumentParser(description="Explain refusal codes with data-side context.")
    parser.add_argument("--input", required=True, help="JSON file containing refusal or tool output.")
    parser.add_argument("--data", default=None, help="Optional data pack JSON for path/value lookup.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    payload = load_json(args.input)
    refusal = extract_refusal(payload) or {}
    issues = extract_issues(payload)
    data = load_json(args.data) if args.data else None

    table = load_refusal_table(repo_root)
    code = refusal.get("code")
    code_entry = table.get(code) if code else None

    explanations = []
    for issue in issues:
        path = issue.get("path")
        code = issue.get("code")
        entry = {
            "issue_code": code,
            "path": path,
            "schema_ref": schema_for_path(path),
            "value": extract_value(data, path) if data is not None else None,
            "suggestion": SUGGESTION_MAP.get(code),
        }
        explanations.append(entry)
    explanations = sorted(explanations, key=lambda e: (e.get("path") or "", e.get("issue_code") or ""))

    suggestions = []
    if refusal.get("code") == "REFUSE_CAPABILITY_MISSING":
        capability_id = refusal.get("details", {}).get("capability_id")
        providers = build_capability_suggestions(repo_root, capability_id)
        if providers:
            suggestions.append("Add a pack that provides {}: {}".format(capability_id, ", ".join(providers)))

    if code_entry and refusal.get("code_id") is None:
        refusal = dict(refusal)
        refusal["code_id"] = code_entry["code_id"]

    output = {
        "ok": True,
        "refusal": refusal,
        "meaning": code_entry.get("meaning") if code_entry else None,
        "explanations": explanations,
        "suggestions": suggestions,
    }

    if args.format == "json":
        print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("refusal_explain: {}".format(refusal.get("code") or "unknown"))
    if explanations:
        print("explanations={}".format(len(explanations)))
    if suggestions:
        print("suggestions={}".format(len(suggestions)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
