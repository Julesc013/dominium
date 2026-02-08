import argparse
import json
import os
import re
import sys


REQUIRED_DOCS = [
    os.path.join("docs", "architecture", "COMPLEXITY_AND_SCALE.md"),
    os.path.join("docs", "architecture", "COLLAPSE_EXPAND_SOLVERS.md"),
    os.path.join("docs", "architecture", "ARTIFACT_LIFECYCLE.md"),
    os.path.join("docs", "ui", "OBSERVATION_AND_INSPECTION.md"),
    os.path.join("docs", "knowledge", "BLUEPRINTS_AND_RESEARCH.md"),
    os.path.join("docs", "security", "CHEATING_AND_VERIFICATION.md"),
]

REQUIRED_SCHEMA_TOKENS = {
    os.path.join("schema", "observation.artifact.schema"): [
        "modality",
        "payload_type",
        "payload",
        "confidence",
        "provenance",
        "staleness",
        "epistemic_status",
        "reason_codes",
    ],
    os.path.join("schema", "memory.artifact.schema"): [
        "derived_from_observation_artifact_id",
        "decay_rules",
        "compression_rules",
        "error_allowance",
    ],
    os.path.join("schema", "knowledge.artifact.schema"): [
        "confidence",
        "provenance",
        "uncertainty_envelope",
    ],
    os.path.join("schema", "conformance.bundle.schema"): [
        "port_contracts",
        "tolerances",
        "allowed_solvers",
        "invariant_checks",
        "test_vectors",
    ],
}

REQUIRED_GUARD_TESTS = [
    os.path.join("tests", "integration", "freecam_epistemics_tests.py"),
    os.path.join("tests", "app", "scale1_collapse_expand_tests.py"),
]

SOLVER_REGISTRY = os.path.join("data", "registries", "solver_registry.json")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(errors, message):
    errors.append(message)


def check_solver_registry(path, errors):
    if not os.path.isfile(path):
        fail(errors, "missing solver registry: {}".format(path))
        return
    payload = read_json(path)
    if payload.get("schema_id") != "dominium.registry.solver_registry":
        fail(errors, "solver registry schema_id mismatch")
    if not SEMVER_RE.match(str(payload.get("schema_version", "")).strip()):
        fail(errors, "solver registry schema_version invalid")

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        fail(errors, "solver registry records missing or empty")
        return

    seen_solver_ids = set()
    for idx, record in enumerate(records):
        location = "solver registry record {}".format(idx)
        if not isinstance(record, dict):
            fail(errors, "{} invalid".format(location))
            continue

        solver_id = record.get("solver_id", "")
        if not isinstance(solver_id, str) or not solver_id:
            fail(errors, "{} missing solver_id".format(location))
            continue
        if not solver_id.startswith("solver."):
            fail(errors, "{} has non-namespaced solver_id '{}'".format(location, solver_id))
        if solver_id in seen_solver_ids:
            fail(errors, "{} duplicate solver_id '{}'".format(location, solver_id))
        seen_solver_ids.add(solver_id)

        if record.get("cost_class") not in ("low", "medium", "high", "critical"):
            fail(errors, "{} invalid cost_class for '{}'".format(location, solver_id))
        if record.get("resolution") not in ("macro", "micro", "hybrid"):
            fail(errors, "{} invalid resolution for '{}'".format(location, solver_id))

        guarantees = record.get("guarantees")
        if not isinstance(guarantees, list) or not guarantees:
            fail(errors, "{} guarantees missing for '{}'".format(location, solver_id))

        transitions = record.get("supports_transitions")
        if not isinstance(transitions, list):
            fail(errors, "{} supports_transitions missing for '{}'".format(location, solver_id))
        else:
            transition_set = set(transitions)
            if "collapse" not in transition_set or "expand" not in transition_set:
                fail(errors, "{} missing collapse/expand transitions for '{}'".format(location, solver_id))

        bounds = record.get("numeric_bounds")
        if not isinstance(bounds, dict):
            fail(errors, "{} numeric_bounds missing for '{}'".format(location, solver_id))
        else:
            if "max_error" not in bounds:
                fail(errors, "{} numeric_bounds.max_error missing for '{}'".format(location, solver_id))
            if bounds.get("bounded") is not True:
                fail(errors, "{} numeric_bounds.bounded must be true for '{}'".format(location, solver_id))

        refusal_codes = record.get("refusal_codes")
        if not isinstance(refusal_codes, list) or not refusal_codes:
            fail(errors, "{} refusal_codes missing for '{}'".format(location, solver_id))

        conformance_refs = record.get("conformance_bundle_refs")
        if not isinstance(conformance_refs, list) or not conformance_refs:
            fail(errors, "{} conformance_bundle_refs missing for '{}'".format(location, solver_id))


def main():
    parser = argparse.ArgumentParser(description="Universe complexity framework contract checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    errors = []

    for rel_path in REQUIRED_DOCS:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            fail(errors, "missing doc: {}".format(rel_path))

    for rel_path, tokens in REQUIRED_SCHEMA_TOKENS.items():
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            fail(errors, "missing schema: {}".format(rel_path))
            continue
        text = read_text(full_path)
        for token in tokens:
            if token not in text:
                fail(errors, "schema token '{}' missing in {}".format(token, rel_path))

    for rel_path in REQUIRED_GUARD_TESTS:
        if not os.path.isfile(os.path.join(repo_root, rel_path)):
            fail(errors, "missing guard test: {}".format(rel_path))

    check_solver_registry(os.path.join(repo_root, SOLVER_REGISTRY), errors)

    if errors:
        for item in errors:
            sys.stderr.write("FAIL: {}\n".format(item))
        return 1

    print("Universe complexity contracts OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
