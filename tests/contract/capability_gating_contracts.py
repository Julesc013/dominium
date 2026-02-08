import argparse
import hashlib
import json
import os
import re
import sys


CAPABILITY_SETS = [
    "CAPSET_WORLD_NONBIO",
    "CAPSET_WORLD_LIFE_NONINTELLIGENT",
    "CAPSET_WORLD_LIFE_INTELLIGENT",
    "CAPSET_WORLD_PRETOOL",
    "CAPSET_SOCIETY_INSTITUTIONS",
    "CAPSET_INFRASTRUCTURE_INDUSTRY",
    "CAPSET_FUTURE_AFFORDANCES",
]
EPISTEMIC_SCOPES = {
    "DOM_EPISTEMIC_SCOPE_OBS_ONLY",
    "DOM_EPISTEMIC_SCOPE_MEMORY_ONLY",
    "DOM_EPISTEMIC_SCOPE_PARTIAL",
    "DOM_EPISTEMIC_SCOPE_FULL",
}
REFUSE_CAPABILITY_MISSING = "REFUSE_CAPABILITY_MISSING"

SET_TO_CAPS = {
    "CAPSET_WORLD_NONBIO": [
        "dominium.capability.world.nonbio",
    ],
    "CAPSET_WORLD_LIFE_NONINTELLIGENT": [
        "dominium.capability.world.nonbio",
        "dominium.capability.world.life.nonintelligent",
    ],
    "CAPSET_WORLD_LIFE_INTELLIGENT": [
        "dominium.capability.world.nonbio",
        "dominium.capability.world.life.nonintelligent",
        "dominium.capability.world.life.intelligent",
    ],
    "CAPSET_WORLD_PRETOOL": [
        "dominium.capability.world.nonbio",
        "dominium.capability.world.life.nonintelligent",
        "dominium.capability.world.life.intelligent",
        "dominium.capability.world.pretool",
    ],
    "CAPSET_SOCIETY_INSTITUTIONS": [
        "dominium.capability.world.nonbio",
        "dominium.capability.world.life.nonintelligent",
        "dominium.capability.world.life.intelligent",
        "dominium.capability.world.pretool",
        "dominium.capability.society.institutions",
    ],
    "CAPSET_INFRASTRUCTURE_INDUSTRY": [
        "dominium.capability.world.nonbio",
        "dominium.capability.world.life.nonintelligent",
        "dominium.capability.world.life.intelligent",
        "dominium.capability.world.pretool",
        "dominium.capability.society.institutions",
        "dominium.capability.infrastructure.industry",
    ],
    "CAPSET_FUTURE_AFFORDANCES": [
        "dominium.capability.world.nonbio",
        "dominium.capability.world.life.nonintelligent",
        "dominium.capability.world.life.intelligent",
        "dominium.capability.world.pretool",
        "dominium.capability.society.institutions",
        "dominium.capability.infrastructure.industry",
        "dominium.capability.future.affordances",
    ],
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def hash_payload(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def parse_command_entries(path):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
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
                "scope": scope_match.group(1) if scope_match else "",
            }
        )
    return entries


def load_world_fixtures(repo_root):
    fixture_roots = [
        ("CAPSET_WORLD_NONBIO", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_0_nonbio", "world_stage.json")),
        ("CAPSET_WORLD_LIFE_NONINTELLIGENT", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_1_nonintelligent_life", "world_stage.json")),
        ("CAPSET_WORLD_LIFE_INTELLIGENT", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_2_intelligent_pre_tool", "world_stage.json")),
        ("CAPSET_WORLD_PRETOOL", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_3_pre_tool_world", "world_stage.json")),
        ("CAPSET_SOCIETY_INSTITUTIONS", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_4_pre_industry", "world_stage.json")),
        ("CAPSET_INFRASTRUCTURE_INDUSTRY", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_5_pre_present", "world_stage.json")),
        ("CAPSET_FUTURE_AFFORDANCES", os.path.join(repo_root, "tests", "fixtures", "worlds", "stage_6_future", "world_stage.json")),
    ]
    fixtures = []
    for expected_set, path in fixture_roots:
        payload = load_json(path)
        record = payload.get("record", payload)
        provides = []
        for item in record.get("provides_capabilities", []):
            cap_id = item.get("capability_id") if isinstance(item, dict) else item
            if isinstance(cap_id, str):
                provides.append(cap_id)
        fixtures.append(
            {
                "expected": expected_set,
                "path": path,
                "schema_id": payload.get("schema_id"),
                "schema_version": payload.get("schema_version"),
                "provides_capabilities": provides,
            }
        )
    return fixtures


def parse_ui_bind_actions(path):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    action_re = re.compile(r"\{\s*\"[^\"]+\",\s*\"[^\"]+\",\s*\"([^\"]+)\"")
    return sorted({match.group(1) for match in action_re.finditer(text)})


def evaluate_pack_capabilities(world_caps, pack_requires_caps):
    if set(pack_requires_caps).issubset(set(world_caps)):
        return {"ok": True, "reason": "ok"}
    return {"ok": False, "reason": REFUSE_CAPABILITY_MISSING}


def main():
    parser = argparse.ArgumentParser(description="Capability gating contracts.")
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
            if command["scope"] not in EPISTEMIC_SCOPES:
                violations.append("command missing valid epistemic_scope: {}".format(command["name"]))
            if command["scope"] == "DOM_EPISTEMIC_SCOPE_FULL" and command["app"] != "tools":
                violations.append("full epistemic scope must be tools-only: {}".format(command["name"]))

        ui_bind_path = os.path.join(repo_root, "libs", "appcore", "ui_bind", "ui_command_binding_table.c")
        for action in parse_ui_bind_actions(ui_bind_path):
            if action not in command_names:
                violations.append("ui binding action not in canonical command graph: {}".format(action))

        for capset in CAPABILITY_SETS:
            provided = SET_TO_CAPS[capset]
            allowed = sorted(
                [
                    cmd["name"]
                    for cmd in commands
                    if set(cmd["required_capabilities"]).issubset(set(provided))
                ]
            )
            denied = sorted(
                [
                    cmd["name"]
                    for cmd in commands
                    if not set(cmd["required_capabilities"]).issubset(set(provided))
                ]
            )
            if capset != "CAPSET_FUTURE_AFFORDANCES" and not denied:
                violations.append(
                    "capability set {} does not deny any higher requirement command".format(capset)
                )
            digest_a = hash_payload({"capset": capset, "allowed": allowed, "denied": denied})
            digest_b = hash_payload({"capset": capset, "allowed": allowed, "denied": denied})
            if digest_a != digest_b:
                violations.append("non-deterministic command gating digest for {}".format(capset))

    fixtures = load_world_fixtures(repo_root)
    for fixture in fixtures:
        if fixture["schema_id"] != "dominium.schema.capability_declaration":
            violations.append("fixture schema_id mismatch: {}".format(fixture["path"]))
        if fixture["schema_version"] != "1.0.0":
            violations.append("fixture schema_version mismatch: {}".format(fixture["path"]))
        if sorted(fixture["provides_capabilities"]) != sorted(SET_TO_CAPS.get(fixture["expected"], [])):
            violations.append("fixture provided_capabilities mismatch: {}".format(fixture["path"]))

    for world_set, world_caps in SET_TO_CAPS.items():
        for pack_set, pack_caps in SET_TO_CAPS.items():
            result = evaluate_pack_capabilities(world_caps, pack_caps)
            expected_ok = set(pack_caps).issubset(set(world_caps))
            if expected_ok and not result["ok"]:
                violations.append("pack gating rejected compatible set {} <= {}".format(pack_set, world_set))
            if not expected_ok and (result["ok"] or result["reason"] != REFUSE_CAPABILITY_MISSING):
                violations.append("pack gating allowed incompatible set {} > {}".format(pack_set, world_set))

    if violations:
        for violation in sorted(set(violations)):
            print(violation)
        return 1

    print("Capability gating contracts OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
