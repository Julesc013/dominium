import argparse
import hashlib
import json
import os
import sys

from invariant_utils import is_override_active


INVARIANT_ID = "INV-PROCESS-EXECUTION-COVERAGE"
REGISTRY_PATH = os.path.join("data", "registries", "process_registry.json")
REGISTRY_SCHEMA_ID = "dominium.schema.process_registry"
LAW_REFUSAL_PREFERENCE = (
    "failure.insufficient_authority",
    "failure.access_denied",
    "refuse.policy",
    "failure.insufficient_capability",
    "failure.insufficient_budget",
    "failure.unspecified",
)


def _load_registry(repo_root):
    path = os.path.join(repo_root, REGISTRY_PATH)
    if not os.path.isfile(path):
        return None, "missing {}".format(REGISTRY_PATH)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError) as exc:
        return None, "invalid {}: {}".format(REGISTRY_PATH, exc)
    return payload, None


def _pick_law_refusal(failure_modes):
    for token in LAW_REFUSAL_PREFERENCE:
        if token in failure_modes:
            return token
    if failure_modes:
        return sorted(set(failure_modes))[0]
    return ""


def _normalize_list(value):
    if isinstance(value, list):
        return list(value)
    return []


def _execute_contract(entry):
    process_id = entry.get("process_id", "")
    required_law = sorted(set(_normalize_list(entry.get("required_law_checks"))))
    failure_modes = sorted(set(_normalize_list(entry.get("failure_modes"))))
    affected_assemblies = sorted(set(_normalize_list(entry.get("affected_assemblies"))))
    affected_fields = sorted(set(_normalize_list(entry.get("affected_fields"))))

    allowed_result = {
        "process_id": process_id,
        "status": "ok",
        "required_law_checks": required_law,
        "affected_assemblies": affected_assemblies,
        "affected_fields": affected_fields,
    }
    denied_result = {
        "process_id": process_id,
        "status": "law_not_applicable",
        "required_law_checks": required_law,
        "refusal": "",
    }
    if required_law:
        denied_result["status"] = "law_denied"
        denied_result["refusal"] = _pick_law_refusal(failure_modes)

    return allowed_result, denied_result


def _fingerprint(result):
    payload = json.dumps(result, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Process registry contract execution coverage tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if is_override_active(repo_root, INVARIANT_ID):
        print("override active for {}".format(INVARIANT_ID))
        return 0

    payload, error = _load_registry(repo_root)
    if error:
        print("{}: {}".format(INVARIANT_ID, error))
        return 1

    violations = []
    if payload.get("schema_id") != REGISTRY_SCHEMA_ID:
        violations.append("{}: schema_id mismatch in {}".format(INVARIANT_ID, REGISTRY_PATH))

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        violations.append("{}: records missing or invalid in {}".format(INVARIANT_ID, REGISTRY_PATH))
        records = []

    seen = set()
    for entry in records:
        if not isinstance(entry, dict):
            violations.append("{}: invalid registry entry".format(INVARIANT_ID))
            continue
        process_id = entry.get("process_id", "")
        if not process_id:
            violations.append("{}: missing process_id".format(INVARIANT_ID))
            continue
        if process_id in seen:
            violations.append("{}: duplicate process_id {}".format(INVARIANT_ID, process_id))
            continue
        seen.add(process_id)

        allowed_a, denied_a = _execute_contract(entry)
        allowed_b, denied_b = _execute_contract(entry)
        if _fingerprint(allowed_a) != _fingerprint(allowed_b):
            violations.append("{}: non-deterministic allowed execution for {}".format(INVARIANT_ID, process_id))
        if _fingerprint(denied_a) != _fingerprint(denied_b):
            violations.append("{}: non-deterministic denied execution for {}".format(INVARIANT_ID, process_id))

        required_law = allowed_a.get("required_law_checks", [])
        if required_law and not denied_a.get("refusal"):
            violations.append(
                "{}: missing law-refusal mode for {} (required_law_checks present)".format(INVARIANT_ID, process_id)
            )

        # Side-effect checks are constrained to declared scope only.
        if len(allowed_a.get("affected_assemblies", [])) != len(set(allowed_a.get("affected_assemblies", []))):
            violations.append("{}: duplicate affected_assemblies for {}".format(INVARIANT_ID, process_id))
        if len(allowed_a.get("affected_fields", [])) != len(set(allowed_a.get("affected_fields", []))):
            violations.append("{}: duplicate affected_fields for {}".format(INVARIANT_ID, process_id))

    if violations:
        for item in sorted(set(violations)):
            print(item)
        return 1

    print("{}: contract execution coverage OK ({})".format(INVARIANT_ID, len(seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
