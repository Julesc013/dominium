import hashlib
import json
import os
import re


STAGES = [
    "STAGE_0_NONBIO_WORLD",
    "STAGE_1_NONINTELLIGENT_LIFE",
    "STAGE_2_INTELLIGENT_PRE_TOOL",
    "STAGE_3_PRE_TOOL_WORLD",
    "STAGE_4_PRE_INDUSTRY",
    "STAGE_5_PRE_PRESENT",
    "STAGE_6_FUTURE",
]

REFUSE_STAGE_TOO_LOW = "REFUSE_CAPABILITY_STAGE_TOO_LOW"
REFUSE_INVALID_STAGE = "REFUSE_INVALID_STAGE"

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


def stage_rank(stage_id):
    token = stage_id
    if isinstance(token, str) and token.startswith("DOM_"):
        token = token[4:]
    try:
        return STAGES.index(token)
    except ValueError:
        return -1


def hash_payload(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_stage_matrix(repo_root):
    matrix_path = os.path.join(repo_root, "tests", "testx", "STAGE_MATRIX.yaml")
    return load_json(matrix_path)


def stage_entry(matrix, stage_id):
    for entry in matrix.get("stages", []):
        if entry.get("stage_id") == stage_id:
            return entry
    return None


def parse_command_entries(repo_root):
    path = os.path.join(repo_root, "libs", "appcore", "command", "command_registry.c")
    text = open(path, "r", encoding="utf-8").read()
    entry_re = re.compile(r"\{\s*DOM_APP_CMD_[^}]+\}", re.DOTALL)
    name_re = re.compile(r"\{\s*DOM_APP_CMD_[^,]+,\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"")
    stage_re = re.compile(r"(DOM_STAGE_[A-Z0-9_]+)")
    scope_re = re.compile(r"(DOM_EPISTEMIC_SCOPE_[A-Z_]+)")

    entries = []
    for raw in entry_re.findall(text):
        name_match = name_re.search(raw)
        stage_match = stage_re.search(raw)
        scope_match = scope_re.search(raw)
        if not name_match:
            continue
        entries.append({
            "name": name_match.group(1),
            "app": name_match.group(2),
            "required_stage": stage_match.group(1) if stage_match else "",
            "epistemic_scope": scope_match.group(1) if scope_match else "",
        })
    return entries


def parse_ui_actions(repo_root):
    path = os.path.join(repo_root, "libs", "appcore", "ui_bind", "ui_command_binding_table.c")
    text = open(path, "r", encoding="utf-8").read()
    action_re = re.compile(r"\{\s*\"[^\"]+\",\s*\"[^\"]+\",\s*\"([^\"]+)\"")
    return sorted({match.group(1) for match in action_re.finditer(text)})


def command_surface(commands, stage_id):
    world_rank = stage_rank(stage_id)
    allowed = []
    denied = []
    for command in commands:
        command_rank = stage_rank(command["required_stage"])
        if command_rank < 0 or world_rank < 0:
            denied.append(command)
            continue
        if world_rank >= command_rank:
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


def evaluate_pack_stage(world_stage, pack_requires_stage):
    world_rank = stage_rank(world_stage)
    pack_rank = stage_rank(pack_requires_stage)
    if world_rank < 0 or pack_rank < 0:
        return {"ok": False, "reason": REFUSE_INVALID_STAGE}
    if pack_rank > world_rank:
        return {"ok": False, "reason": REFUSE_STAGE_TOO_LOW}
    return {"ok": True, "reason": "ok"}


def load_stage_fixture(repo_root, stage_id):
    matrix = load_stage_matrix(repo_root)
    entry = stage_entry(matrix, stage_id)
    if not entry:
        return None, None
    fixture_rel = entry.get("fixture")
    fixture_path = os.path.join(repo_root, fixture_rel)
    payload = load_json(fixture_path)
    record = payload.get("record", {})
    return entry, {
        "path": fixture_rel,
        "schema_id": payload.get("schema_id"),
        "schema_version": payload.get("schema_version"),
        "requires_stage": record.get("requires_stage"),
        "provides_stage": record.get("provides_stage"),
        "stage_features": record.get("stage_features"),
    }


def add_violation(violations, code, stage_id, message, fixture="", command="", pack="", expected="", actual=""):
    violations.append({
        "code": code,
        "stage": stage_id,
        "fixture": fixture,
        "command": command,
        "pack": pack,
        "expected": expected,
        "actual": actual,
        "message": message,
    })


def emit_violations(violations):
    for entry in violations:
        print(json.dumps(entry, sort_keys=True, ensure_ascii=True))

