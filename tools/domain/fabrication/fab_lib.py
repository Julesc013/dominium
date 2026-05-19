import json
import os
import re


REVERSE_DNS_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9][a-z0-9_-]*)+$")


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_units_table(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "UNIT_SYSTEM_POLICY.md")
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    start = text.find("```units")
    if start == -1:
        return {}
    start = text.find("\n", start)
    end = text.find("```", start + 1)
    if end == -1:
        return {}
    units = {}
    for raw_line in text[start:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 4:
            continue
        unit_id = parts[0]
        try:
            scale = int(parts[3])
        except Exception:
            scale = 1
        units[unit_id] = scale
    return units


def is_reverse_dns(identifier):
    if not isinstance(identifier, str):
        return False
    if not identifier.isascii():
        return False
    if identifier != identifier.lower():
        return False
    return REVERSE_DNS_RE.match(identifier) is not None


def add_issue(issues, code, message, path):
    issues.append({"code": code, "message": message, "path": path})


def is_number(value):
    if isinstance(value, bool):
        return False
    return isinstance(value, int)


def validate_quantity(value, path, issues, unit_table):
    if not isinstance(value, dict):
        add_issue(issues, "quantity_type", "quantity must be object", path)
        return
    if "value" not in value:
        add_issue(issues, "quantity_value_missing", "quantity value missing", path)
    if "unit" not in value:
        add_issue(issues, "quantity_unit_missing", "quantity unit missing", path)
    if "overflow_behavior" not in value:
        add_issue(issues, "quantity_overflow_missing", "overflow behavior missing", path)
    if "value" in value and not is_number(value.get("value")):
        add_issue(issues, "quantity_value_type", "quantity value must be integer", path)
    unit_id = value.get("unit")
    if isinstance(unit_id, str) and unit_table and unit_id not in unit_table:
        add_issue(issues, "unit_unknown", "unknown unit id", path)


def iter_numeric_map(value, prefix):
    if not isinstance(value, dict):
        return []
    out = []
    for key, val in value.items():
        if is_number(val):
            out.append((f"{prefix}.{key}", val))
    return out


def validate_unit_annotations(unit_annotations, numeric_paths, issues, unit_table):
    if not isinstance(unit_annotations, dict):
        add_issue(issues, "unit_annotations_type", "unit_annotations must be object", "unit_annotations")
        return
    for path, _value in numeric_paths:
        entry = unit_annotations.get(path)
        if not isinstance(entry, dict):
            add_issue(issues, "unit_annotation_missing", "unit annotation missing", path)
            continue
        unit_id = entry.get("unit")
        if not isinstance(unit_id, str):
            add_issue(issues, "unit_annotation_unit", "unit annotation missing unit", path)
            continue
        if unit_table and unit_id not in unit_table:
            add_issue(issues, "unit_unknown", "unknown unit id", path)
        if "scale" not in entry:
            add_issue(issues, "unit_annotation_scale", "unit annotation missing scale", path)
        if "overflow_behavior" not in entry:
            add_issue(issues, "unit_annotation_overflow", "unit annotation missing overflow behavior", path)


def validate_id(identifier, issues, path):
    if not is_reverse_dns(identifier):
        add_issue(issues, "id_shape", "identifier must be lowercase reverse-dns", path)


def make_refusal(code_id, code, message, details=None):
    return {
        "code_id": code_id,
        "code": code,
        "message": message,
        "details": details or {},
        "explanation_classification": "PUBLIC"
    }


REFUSAL_INVALID = (1, "REFUSE_INVALID_INTENT")
REFUSAL_INTEGRITY = (5, "REFUSE_INTEGRITY_VIOLATION")
REFUSAL_CAPABILITY = (3, "REFUSE_CAPABILITY_MISSING")
