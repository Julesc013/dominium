import hashlib
import json
import os
import re


CAPABILITY_SETS = [
    "CAPSET_WORLD_NONBIO",
    "CAPSET_WORLD_LIFE_NONINTELLIGENT",
    "CAPSET_WORLD_LIFE_INTELLIGENT",
    "CAPSET_WORLD_PRETOOL",
    "CAPSET_SOCIETY_INSTITUTIONS",
    "CAPSET_INFRASTRUCTURE_INDUSTRY",
    "CAPSET_FUTURE_AFFORDANCES",
]

REFUSE_CAPABILITY_MISSING = "REFUSE_CAPABILITY_MISSING"

EPISTEMIC_SCOPES = {
    "DOM_EPISTEMIC_SCOPE_OBS_ONLY",
    "DOM_EPISTEMIC_SCOPE_MEMORY_ONLY",
    "DOM_EPISTEMIC_SCOPE_PARTIAL",
    "DOM_EPISTEMIC_SCOPE_FULL",
}

FAMILY_COMMANDS = {
    "life": ("agents",),
    "tooling": ("agent-add",),
    "institutions": ("institution-create", "institution-list"),
    "industry": ("network-create", "network-list"),
    "future": ("ai",),
}


def hash_payload(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_capability_matrix(repo_root):
    matrix_path = os.path.join(repo_root, "tests", "testx", "CAPABILITY_MATRIX.yaml")
    return load_json(matrix_path)


def parse_command_entries(repo_root):
    path = os.path.join(repo_root, "libs", "appcore", "command", "command_registry.c")
    text = open(path, "r", encoding="utf-8").read()
    arr_re = re.compile(r"static const char\* (k_[A-Za-z0-9_]+)\[\] = \{([^}]*)\};")
    cap_arrays = {}
    for match in arr_re.finditer(text):
        cap_arrays[match.group(1)] = re.findall(r'"([^"]+)"', match.group(2))

    entry_re = re.compile(r"\{\s*DOM_APP_CMD_[^}]+\}", re.DOTALL)
    name_re = re.compile(r"\{\s*DOM_APP_CMD_[^,]+,\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"")
    scope_re = re.compile(r"(DOM_EPISTEMIC_SCOPE_[A-Z_]+)")
    cap_ref_re = re.compile(
        r",\s*(k_[A-Za-z0-9_]+)\s*,\s*(\d+)u\s*,\s*DOM_EPISTEMIC_SCOPE_[A-Z_]+"
    )

    entries = []
    for raw in entry_re.findall(text):
        name_match = name_re.search(raw)
        scope_match = scope_re.search(raw)
        cap_match = cap_ref_re.search(raw)
        if not name_match:
            continue
        cap_ref = cap_match.group(1) if cap_match else "k_required_caps_none"
        entries.append(
            {
                "name": name_match.group(1),
                "app": name_match.group(2),
                "required_capabilities": list(cap_arrays.get(cap_ref, [])),
                "epistemic_scope": scope_match.group(1) if scope_match else "",
            }
        )
    return entries


def parse_ui_actions(repo_root):
    path = os.path.join(repo_root, "libs", "appcore", "ui_bind", "ui_command_binding_table.c")
    text = open(path, "r", encoding="utf-8").read()
    action_re = re.compile(r"\{\s*\"[^\"]+\",\s*\"[^\"]+\",\s*\"([^\"]+)\"")
    return sorted({match.group(1) for match in action_re.finditer(text)})


def command_surface(commands, provided_capabilities):
    provided = set(provided_capabilities)
    allowed = []
    denied = []
    for command in commands:
        if set(command["required_capabilities"]).issubset(provided):
            allowed.append(command)
        else:
            denied.append(command)
    return allowed, denied


def family_status(allowed_commands):
    allowed_names = {command["name"] for command in allowed_commands}
    status = {}
    for family, names in FAMILY_COMMANDS.items():
        status[family] = any(name in allowed_names for name in names)
    return status


def evaluate_pack_capabilities(provided_capabilities, pack_requires_capabilities):
    if set(pack_requires_capabilities).issubset(set(provided_capabilities)):
        return {"ok": True, "reason": "ok"}
    return {"ok": False, "reason": REFUSE_CAPABILITY_MISSING}


def capability_entry(matrix, bundle_id):
    for entry in matrix.get("capability_sets", []):
        if entry.get("bundle_id") == bundle_id:
            return entry
    return None


def load_capability_fixture(repo_root, bundle_id):
    matrix = load_capability_matrix(repo_root)
    entry = capability_entry(matrix, bundle_id)
    if not entry:
        return None, None
    fixture_rel = entry.get("fixture")
    fixture_path = os.path.join(repo_root, fixture_rel)
    payload = load_json(fixture_path)
    record = payload.get("record", {})
    provides = []
    for item in record.get("provides_capabilities", []):
        cap_id = item.get("capability_id") if isinstance(item, dict) else item
        if isinstance(cap_id, str):
            provides.append(cap_id)
    return entry, {
        "path": fixture_rel,
        "schema_id": payload.get("schema_id"),
        "schema_version": payload.get("schema_version"),
        "provided_capabilities": provides,
    }


def add_violation(
    violations,
    code,
    bundle_id,
    message,
    fixture="",
    command="",
    pack="",
    expected="",
    actual="",
):
    violations.append(
        {
            "code": code,
            "capability_set": bundle_id,
            "fixture": fixture,
            "command": command,
            "pack": pack,
            "expected": expected,
            "actual": actual,
            "message": message,
        }
    )


def emit_violations(violations):
    for entry in violations:
        print(json.dumps(entry, sort_keys=True, ensure_ascii=True))
