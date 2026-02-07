import argparse
import hashlib
import json
import os
import re
import sys


STAGES = [
    "STAGE_0_NONBIO_WORLD",
    "STAGE_1_NONINTELLIGENT_LIFE",
    "STAGE_2_INTELLIGENT_PRE_TOOL",
    "STAGE_3_PRE_TOOL_WORLD",
    "STAGE_4_PRE_INDUSTRY",
    "STAGE_5_PRE_PRESENT",
    "STAGE_6_FUTURE",
]
EPISTEMIC_SCOPES = {
    "DOM_EPISTEMIC_SCOPE_OBS_ONLY",
    "DOM_EPISTEMIC_SCOPE_MEMORY_ONLY",
    "DOM_EPISTEMIC_SCOPE_PARTIAL",
    "DOM_EPISTEMIC_SCOPE_FULL",
}
REFUSE_STAGE_TOO_LOW = "REFUSE_CAPABILITY_STAGE_TOO_LOW"


def stage_rank(stage_id):
    if isinstance(stage_id, str) and stage_id.startswith("DOM_"):
        stage_id = stage_id[4:]
    try:
        return STAGES.index(stage_id)
    except ValueError:
        return -1


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def hash_payload(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def parse_command_entries(path):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
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
            "stage": stage_match.group(1) if stage_match else "",
            "scope": scope_match.group(1) if scope_match else "",
        })
    return entries


def load_world_fixtures(repo_root):
    fixture_roots = [
        ("STAGE_0_NONBIO_WORLD", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_0_nonbio", "world_stage.json")),
        ("STAGE_1_NONINTELLIGENT_LIFE", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_1_nonintelligent_life", "world_stage.json")),
        ("STAGE_2_INTELLIGENT_PRE_TOOL", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_2_intelligent_pre_tool", "world_stage.json")),
        ("STAGE_3_PRE_TOOL_WORLD", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_3_pre_tool_world", "world_stage.json")),
        ("STAGE_4_PRE_INDUSTRY", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_4_pre_industry", "world_stage.json")),
        ("STAGE_5_PRE_PRESENT", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_5_pre_present", "world_stage.json")),
        ("STAGE_6_FUTURE", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_6_future", "world_stage.json")),
    ]
    fixtures = []
    for expected_stage, path in fixture_roots:
        payload = load_json(path)
        record = payload.get("record", payload)
        fixtures.append({
            "expected": expected_stage,
            "path": path,
            "schema_id": payload.get("schema_id"),
            "schema_version": payload.get("schema_version"),
            "requires_stage": record.get("requires_stage"),
            "provides_stage": record.get("provides_stage"),
            "stage_features": record.get("stage_features"),
        })
    return fixtures


def parse_ui_bind_actions(path):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    action_re = re.compile(r"\{\s*\"[^\"]+\",\s*\"[^\"]+\",\s*\"([^\"]+)\"")
    return sorted({match.group(1) for match in action_re.finditer(text)})


def evaluate_pack_stage(world_stage, pack_requires_stage):
    world_rank = stage_rank(world_stage)
    pack_rank = stage_rank(pack_requires_stage)
    if world_rank < 0 or pack_rank < 0:
        return {"ok": False, "reason": "REFUSE_INVALID_STAGE"}
    if pack_rank > world_rank:
        return {"ok": False, "reason": REFUSE_STAGE_TOO_LOW}
    return {"ok": True, "reason": "ok"}


def main():
    parser = argparse.ArgumentParser(description="Capability-stage gating contracts.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []

    registry_path = os.path.join(repo_root, "libs", "appcore", "command", "command_registry.c")
    commands = parse_command_entries(registry_path)
    if not commands:
        violations.append("command registry entries missing")
    else:
        command_names = set()
        for command in commands:
            command_names.add(command["name"])
            if stage_rank(command["stage"]) < 0:
                violations.append("command missing valid required_stage: {}".format(command["name"]))
            if command["scope"] not in EPISTEMIC_SCOPES:
                violations.append("command missing valid epistemic_scope: {}".format(command["name"]))
            if command["scope"] == "DOM_EPISTEMIC_SCOPE_FULL" and command["app"] != "tools":
                violations.append("full epistemic scope must be tools-only: {}".format(command["name"]))

        ui_bind_path = os.path.join(repo_root, "libs", "appcore", "ui_bind", "ui_command_binding_table.c")
        for action in parse_ui_bind_actions(ui_bind_path):
            if action not in command_names:
                violations.append("ui binding action not in canonical command graph: {}".format(action))

        for rank, stage in enumerate(STAGES):
            allowed = sorted([cmd["name"] for cmd in commands if stage_rank(cmd["stage"]) <= rank])
            denied = sorted([cmd["name"] for cmd in commands if stage_rank(cmd["stage"]) > rank])
            if rank < len(STAGES) - 1 and not denied:
                violations.append("stage {} does not deny any higher-stage command".format(stage))
            digest_a = hash_payload({"stage": stage, "allowed": allowed, "denied": denied})
            digest_b = hash_payload({"stage": stage, "allowed": allowed, "denied": denied})
            if digest_a != digest_b:
                violations.append("non-deterministic command gating digest for {}".format(stage))

    fixtures = load_world_fixtures(repo_root)
    for fixture in fixtures:
        if fixture["schema_id"] != "dominium.schema.stage_declaration":
            violations.append("fixture schema_id mismatch: {}".format(fixture["path"]))
        if fixture["schema_version"] != "1.0.0":
            violations.append("fixture schema_version mismatch: {}".format(fixture["path"]))
        if fixture["requires_stage"] != fixture["expected"]:
            violations.append("fixture requires_stage mismatch: {}".format(fixture["path"]))
        if fixture["provides_stage"] != fixture["expected"]:
            violations.append("fixture provides_stage mismatch: {}".format(fixture["path"]))
        if not isinstance(fixture["stage_features"], list):
            violations.append("fixture stage_features missing list: {}".format(fixture["path"]))

    for stage in STAGES:
        world_rank = stage_rank(stage)
        for pack_stage in STAGES:
            result = evaluate_pack_stage(stage, pack_stage)
            if stage_rank(pack_stage) <= world_rank and not result["ok"]:
                violations.append("pack gating rejected compatible stage {} <= {}".format(pack_stage, stage))
            if stage_rank(pack_stage) > world_rank:
                if result["ok"] or result["reason"] != REFUSE_STAGE_TOO_LOW:
                    violations.append("pack gating allowed incompatible stage {} > {}".format(pack_stage, stage))

    if violations:
        for violation in sorted(set(violations)):
            print(violation)
        return 1

    print("Capability-stage gating contracts OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
