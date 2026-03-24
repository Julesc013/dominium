import argparse
import json
import os
import re
import sys


PLAN_REL = os.path.join("docs", "omega", "OMEGA_PLAN.md")
GATES_REL = os.path.join("docs", "omega", "OMEGA_GATES.md")
REGISTRY_REL = os.path.join("data", "registries", "omega_artifact_registry.json")

EXPECTED_PLAN_LINES = [
    "Ω-0 OMEGA_INDEX",
    "Ω-1 WORLDGEN-LOCK-0",
    "Ω-2 BASELINE-UNIVERSE-0",
    "Ω-3 MVP-GAMEPLAY-0",
    "Ω-4 DISASTER-TEST-0",
    "Ω-5 ECOSYSTEM-VERIFY-0",
    "Ω-6 UPDATE-CHANNEL-SIM-0",
    "Ω-7 TRUST-STRICT-VERIFY-0",
    "Ω-8 ARCHIVE-OFFLINE-VERIFY-0",
    "Ω-9 TOOLCHAIN-MATRIX-0",
    "Ω-10 DIST-FINAL-PLAN",
    "Ω-11 DIST-7 IMPLEMENTATION",
]

EXPECTED_GATE_SECTIONS = {
    "WORLDGEN-LOCK-0": [
        "NUMERIC-DISCIPLINE-0",
        "CONCURRENCY-CONTRACT-0",
    ],
    "BASELINE-UNIVERSE-0": [
        "WORLDGEN-LOCK-0",
        "STORE-GC-0",
        "MIGRATION-LIFECYCLE-0",
    ],
    "MVP-GAMEPLAY-0": [
        "BASELINE-UNIVERSE-0",
        "OBSERVABILITY-0",
    ],
    "DISASTER-TEST-0": [
        "UPDATE-MODEL-0",
        "TRUST-MODEL-0",
        "MIGRATION-LIFECYCLE-0",
    ],
    "ECOSYSTEM-VERIFY-0": [
        "COMPONENT-GRAPH-0",
        "DIST-REFINE-1",
        "UNIVERSAL-IDENTITY-0",
    ],
    "UPDATE-CHANNEL-SIM-0": [
        "RELEASE-INDEX-POLICY-0",
        "COMPONENT-GRAPH-0",
    ],
    "TRUST-STRICT-VERIFY-0": [
        "TRUST-MODEL-0",
    ],
    "ARCHIVE-OFFLINE-VERIFY-0": [
        "ARCHIVE-POLICY-0",
    ],
    "TOOLCHAIN-MATRIX-0": [
        "NUMERIC-DISCIPLINE-0",
        "CONCURRENCY-CONTRACT-0",
        "RELEASE-2",
    ],
    "DIST-FINAL-PLAN": [
        "All Ω-1..Ω-9 pass",
    ],
    "DIST-7 IMPLEMENTATION": [
        "DIST-FINAL-PLAN",
        "All previous gates pass",
    ],
}

PREREQ_EVIDENCE = {
    "NUMERIC-DISCIPLINE-0": os.path.join("docs", "audit", "NUMERIC_DISCIPLINE0_RETRO_AUDIT.md"),
    "CONCURRENCY-CONTRACT-0": os.path.join("docs", "audit", "CONCURRENCY_CONTRACT_BASELINE.md"),
    "STORE-GC-0": os.path.join("docs", "audit", "STORE_GC0_RETRO_AUDIT.md"),
    "MIGRATION-LIFECYCLE-0": os.path.join("docs", "audit", "MIGRATION_LIFECYCLE0_RETRO_AUDIT.md"),
    "OBSERVABILITY-0": os.path.join("docs", "audit", "OBSERVABILITY0_RETRO_AUDIT.md"),
    "UPDATE-MODEL-0": os.path.join("docs", "audit", "UPDATE_MODEL0_RETRO_AUDIT.md"),
    "TRUST-MODEL-0": os.path.join("docs", "audit", "TRUST_MODEL0_RETRO_AUDIT.md"),
    "COMPONENT-GRAPH-0": os.path.join("docs", "audit", "COMPONENT_GRAPH_BASELINE.md"),
    "DIST-REFINE-1": os.path.join("docs", "audit", "DIST_REFINE1_RETRO_AUDIT.md"),
    "UNIVERSAL-IDENTITY-0": os.path.join("docs", "audit", "UNIVERSAL_IDENTITY0_RETRO_AUDIT.md"),
    "RELEASE-INDEX-POLICY-0": os.path.join("docs", "audit", "RELEASE_INDEX_POLICY0_RETRO_AUDIT.md"),
    "ARCHIVE-POLICY-0": os.path.join("docs", "audit", "ARCHIVE_POLICY0_RETRO_AUDIT.md"),
    "RELEASE-2": os.path.join("docs", "audit", "RELEASE2_RETRO_AUDIT.md"),
}

EXPECTED_OUTPUTS = {
    "WORLDGEN-LOCK-0": "worldgen_lock_baseline.json",
    "BASELINE-UNIVERSE-0": "baseline_universe_manifest.json",
    "MVP-GAMEPLAY-0": "gameplay_loop_baseline.json",
    "DISASTER-TEST-0": "disaster_suite_baseline.json",
    "ECOSYSTEM-VERIFY-0": "ecosystem_resolution_baseline.json",
    "UPDATE-CHANNEL-SIM-0": "update_sim_baseline.json",
    "TRUST-STRICT-VERIFY-0": "trust_suite_baseline.json",
    "ARCHIVE-OFFLINE-VERIFY-0": "archive_baseline.json",
    "TOOLCHAIN-MATRIX-0": "toolchain_matrix_reports",
    "DIST-FINAL-PLAN": "final_dist_signoff.json",
}


def _read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _require(condition, message):
    if condition:
        return True
    print(message)
    return False


def _normalize_stage_lines(text):
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Ω-"):
            lines.append(re.sub(r"\s+", " ", stripped))
    return lines


def _parse_gate_sections(text):
    sections = {}
    current = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current and line.startswith("- "):
            sections[current].append(line[2:].strip())
    return sections


def run_plan_exists(repo_root):
    plan_path = os.path.join(repo_root, PLAN_REL)
    if not _require(os.path.isfile(plan_path), "missing {}".format(PLAN_REL.replace("\\", "/"))):
        return 1

    text = _read_text(plan_path)
    checks = [
        _require("# Ω-Series: Ultimate MVP Finalization" in text, "missing omega plan title"),
        _require("## Objectives" in text, "missing objectives section"),
        _require("## Execution Order" in text, "missing execution order section"),
        _require("## Artifact Outputs" in text, "missing artifact outputs section"),
        _require("## Freeze Boundary" in text, "missing freeze boundary section"),
        _require("## Freeze Rules" in text, "missing freeze rules section"),
        _require("## Manual Intervention Boundaries" in text, "missing manual intervention boundaries section"),
        _require("## Stable vs Provisional Boundaries" in text, "missing stability boundary section"),
        _require("## Manual Polish Window" in text, "missing manual polish window section"),
        _require("docs/omega/OMEGA_GATES.md" in text, "omega plan missing gate map reference"),
        _require("data/registries/omega_artifact_registry.json" in text, "omega plan missing artifact registry reference"),
    ]

    stage_lines = _normalize_stage_lines(text)
    checks.append(_require(stage_lines == EXPECTED_PLAN_LINES, "execution order does not match authoritative omega order"))

    for required_line in (
        "No contract registry changes during Ω-series.",
        "No schema major version bumps during Ω-series.",
        "No changes to semantic compatibility ranges.",
        "No feature expansion.",
        "re-run convergence gate",
        "re-run worldgen lock verify",
        "re-run baseline universe verify",
        "re-run disaster suite",
    ):
        checks.append(_require(required_line in text, "omega plan missing required line: {}".format(required_line)))

    for output_name in sorted(EXPECTED_OUTPUTS.values()):
        checks.append(_require(output_name in text, "omega plan missing artifact output {}".format(output_name)))

    if not all(checks):
        return 1
    print("test_omega_plan_exists=ok")
    return 0


def run_gates_consistent(repo_root):
    plan_path = os.path.join(repo_root, PLAN_REL)
    gates_path = os.path.join(repo_root, GATES_REL)
    for rel, path in ((PLAN_REL, plan_path), (GATES_REL, gates_path)):
        if not _require(os.path.isfile(path), "missing {}".format(rel.replace("\\", "/"))):
            return 1

    plan_text = _read_text(plan_path)
    gate_text = _read_text(gates_path)

    stage_tokens = []
    for line in _normalize_stage_lines(plan_text):
        parts = line.split(" ", 1)
        if len(parts) == 2:
            stage_tokens.append(parts[1])

    gate_sections = _parse_gate_sections(gate_text)
    checks = [
        _require(set(gate_sections.keys()) == set(EXPECTED_GATE_SECTIONS.keys()), "omega gate sections do not match expected stage set"),
        _require(set(stage_tokens[1:]) == set(EXPECTED_GATE_SECTIONS.keys()), "omega plan and gate map stage sets diverge"),
    ]

    for stage_name, expected_requires in EXPECTED_GATE_SECTIONS.items():
        actual_requires = gate_sections.get(stage_name, [])
        checks.append(
            _require(
                actual_requires == expected_requires,
                "gate requirements mismatch for {}: expected {} got {}".format(
                    stage_name, expected_requires, actual_requires
                ),
            )
        )

    for dep_name, rel_path in sorted(PREREQ_EVIDENCE.items()):
        abs_path = os.path.join(repo_root, rel_path)
        checks.append(_require(os.path.isfile(abs_path), "missing prerequisite evidence for {}: {}".format(dep_name, rel_path.replace("\\", "/"))))

    if not all(checks):
        return 1
    print("test_omega_gates_consistent=ok")
    return 0


def run_artifact_registry_complete(repo_root):
    registry_path = os.path.join(repo_root, REGISTRY_REL)
    if not _require(os.path.isfile(registry_path), "missing {}".format(REGISTRY_REL.replace("\\", "/"))):
        return 1

    try:
        payload = _load_json(registry_path)
    except (OSError, ValueError):
        print("invalid json {}".format(REGISTRY_REL.replace("\\", "/")))
        return 1

    record = payload.get("record") or {}
    outputs = record.get("expected_outputs") or []
    checks = [
        _require(payload.get("schema_id") == "dominium.schema.governance.omega_artifact_registry", "unexpected omega artifact registry schema_id"),
        _require(payload.get("schema_version") == "1.0.0", "unexpected omega artifact registry schema_version"),
        _require(record.get("registry_id") == "dominium.registry.governance.omega_artifact_registry", "unexpected omega artifact registry id"),
        _require(record.get("registry_version") == "1.0.0", "unexpected omega artifact registry version"),
        _require(isinstance(outputs, list), "omega artifact registry expected_outputs must be a list"),
        _require(record.get("extensions", {}).get("omega_11_note"), "omega artifact registry missing omega_11_note"),
    ]
    if not all(checks):
        return 1

    by_stage = {}
    seen_outputs = set()
    for row in outputs:
        if not isinstance(row, dict):
            print("omega artifact registry contains non-object output row")
            return 1
        stage_token = str(row.get("stage_token", "")).strip()
        output_name = str(row.get("output_name", "")).strip()
        if not stage_token or not output_name:
            print("omega artifact registry row missing stage_token or output_name")
            return 1
        if stage_token in by_stage:
            print("duplicate omega artifact registry stage_token {}".format(stage_token))
            return 1
        by_stage[stage_token] = output_name
        seen_outputs.add(output_name)

    checks = [
        _require(set(by_stage.keys()) == set(EXPECTED_OUTPUTS.keys()), "omega artifact registry stage coverage mismatch"),
        _require(seen_outputs == set(EXPECTED_OUTPUTS.values()), "omega artifact registry output set mismatch"),
    ]
    for stage_token, output_name in sorted(EXPECTED_OUTPUTS.items()):
        checks.append(
            _require(
                by_stage.get(stage_token) == output_name,
                "omega artifact registry mismatch for {}: expected {}".format(stage_token, output_name),
            )
        )

    if not all(checks):
        return 1
    print("test_omega_artifact_registry_complete=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Omega-series planning invariant tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--case",
        choices=("plan_exists", "gates_consistent", "artifact_registry_complete"),
        required=True,
    )
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "plan_exists":
        return run_plan_exists(repo_root)
    if args.case == "gates_consistent":
        return run_gates_consistent(repo_root)
    return run_artifact_registry_complete(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
