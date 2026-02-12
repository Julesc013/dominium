import argparse
import json
import os
import sys


FUTURE_CASES_REL = os.path.join("data", "registries", "future_cases.json")
EXPERIENCE_REL = os.path.join("data", "registries", "experience_profiles.json")
LAW_REL = os.path.join("data", "registries", "law_profiles.json")
DOMAIN_REL = os.path.join("data", "registries", "domain_registry.json")
CONTROLX_POLICY_REL = os.path.join("data", "registries", "controlx_policy.json")


def _load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _scan_for_mode_flags(repo_root: str):
    roots = ("engine", "game", "client", "server", "launcher", "setup", "tools", "libs", "scripts")
    tokens = ("survival_mode", "creative_mode", "hardcore_mode", "spectator_mode")
    exts = (".c", ".cc", ".cpp", ".h", ".hpp", ".inl", ".py", ".json", ".schema")
    violations = []
    for rel_root in roots:
        abs_root = os.path.join(repo_root, rel_root)
        if not os.path.isdir(abs_root):
            continue
        for dirpath, dirnames, filenames in os.walk(abs_root):
            dirnames[:] = [name for name in dirnames if name not in {".git", ".vs", "out", "dist", "__pycache__", "cache"}]
            for filename in filenames:
                if not filename.lower().endswith(exts):
                    continue
                path = os.path.join(dirpath, filename)
                rel_norm = path.replace("\\", "/").lower()
                if "/tools/auditx/cache/" in rel_norm:
                    continue
                text = ""
                try:
                    text = open(path, "r", encoding="utf-8", errors="ignore").read().lower()
                except OSError:
                    continue
                for token in tokens:
                    if token in text:
                        violations.append("{} -> {}".format(path.replace("\\", "/"), token))
                        break
    return violations


def _scan_direct_tool_calls(repo_root: str):
    forbidden = ("check_repox_rules.py", "ctest", "tool_ui_bind")
    allowed_files = {
        "scripts/dev/gate.py",
        "scripts/dev/gate_shim.py",
        "scripts/dev/run_repox.py",
        "scripts/dev/run_testx.py",
        "scripts/ci/check_repox_rules.py",
        "scripts/dev/dev.py",
        "scripts/dev/env_tools_lib.py",
        "scripts/dev/testx_proof_engine.py",
        "scripts/repox/repox_release.py",
    }
    violations = []
    scripts_root = os.path.join(repo_root, "scripts")
    if not os.path.isdir(scripts_root):
        return violations
    for dirpath, dirnames, filenames in os.walk(scripts_root):
        dirnames[:] = [name for name in dirnames if name not in {".git", ".vs", "__pycache__"}]
        for filename in filenames:
            if not filename.lower().endswith((".py", ".ps1", ".bat", ".cmd", ".sh")):
                continue
            path = os.path.join(dirpath, filename)
            rel = path.replace("\\", "/")
            rel_norm = rel.replace(repo_root.replace("\\", "/") + "/", "")
            if rel_norm in allowed_files:
                continue
            text = ""
            try:
                text = open(path, "r", encoding="utf-8", errors="ignore").read().lower()
            except OSError:
                continue
            for token in forbidden:
                if token.lower() in text:
                    violations.append("{} -> {}".format(rel_norm, token))
                    break
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Systemic future-case constructibility stress suite.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    future_payload = _load_json(os.path.join(repo_root, FUTURE_CASES_REL))
    exp_payload = _load_json(os.path.join(repo_root, EXPERIENCE_REL))
    law_payload = _load_json(os.path.join(repo_root, LAW_REL))
    controlx_payload = _load_json(os.path.join(repo_root, CONTROLX_POLICY_REL))
    if future_payload is None:
        print("missing/invalid {}".format(FUTURE_CASES_REL.replace("\\", "/")))
        return 1
    if exp_payload is None:
        print("missing/invalid {}".format(EXPERIENCE_REL.replace("\\", "/")))
        return 1
    if law_payload is None:
        print("missing/invalid {}".format(LAW_REL.replace("\\", "/")))
        return 1
    if controlx_payload is None:
        print("missing/invalid {}".format(CONTROLX_POLICY_REL.replace("\\", "/")))
        return 1

    cases = ((future_payload.get("record") or {}).get("cases") or [])
    experiences = ((exp_payload.get("record") or {}).get("profiles") or [])
    laws = ((law_payload.get("record") or {}).get("profiles") or [])
    if not isinstance(cases, list) or not cases:
        print("future cases list missing/empty")
        return 1
    if not isinstance(experiences, list) or not isinstance(laws, list):
        print("experience/law registries invalid")
        return 1

    experience_ids = set()
    law_ids = set()
    ui_pack_ids = set()
    for row in experiences:
        if not isinstance(row, dict):
            continue
        exp_id = str(row.get("experience_id", "")).strip()
        if exp_id:
            experience_ids.add(exp_id)
        for pack_id in (row.get("ui_pack_ids") or []):
            pack_text = str(pack_id).strip()
            if pack_text:
                ui_pack_ids.add(pack_text)
    for row in laws:
        if isinstance(row, dict):
            law_id = str(row.get("law_profile_id", "")).strip()
            if law_id:
                law_ids.add(law_id)

    domain_ids = set()
    domain_payload = _load_json(os.path.join(repo_root, DOMAIN_REL))
    if isinstance(domain_payload, dict):
        for row in (domain_payload.get("records") or []):
            if isinstance(row, dict):
                domain_id = str(row.get("domain_id", "")).strip()
                if domain_id:
                    domain_ids.add(domain_id)

    violations = []
    for row in sorted(cases, key=lambda item: str(item.get("case_id", ""))):
        if not isinstance(row, dict):
            violations.append("case entry must be object")
            continue
        case_id = str(row.get("case_id", "")).strip()
        if not case_id:
            violations.append("case missing case_id")
            continue
        for exp_id in (row.get("required_experience_ids") or []):
            exp_text = str(exp_id).strip()
            if exp_text and exp_text not in experience_ids:
                violations.append("{} missing experience {}".format(case_id, exp_text))
        for law_id in (row.get("required_law_profile_ids") or []):
            law_text = str(law_id).strip()
            if law_text and law_text not in law_ids:
                violations.append("{} missing law profile {}".format(case_id, law_text))
        for pack_id in (row.get("required_ui_pack_ids") or []):
            pack_text = str(pack_id).strip()
            if pack_text and pack_text not in ui_pack_ids:
                violations.append("{} missing ui pack {}".format(case_id, pack_text))
        for capability in (row.get("required_capabilities") or []):
            cap_text = str(capability).strip()
            if "." not in cap_text:
                violations.append("{} capability must be namespaced: {}".format(case_id, cap_text))
        for domain_id in (row.get("optional_domain_ids") or []):
            dom_text = str(domain_id).strip()
            if domain_ids and dom_text and dom_text not in domain_ids:
                violations.append("{} optional domain not declared: {}".format(case_id, dom_text))

    mode_violations = _scan_for_mode_flags(repo_root)
    if mode_violations:
        violations.append("hardcoded mode flag tokens present")
        violations.extend(mode_violations[:16])

    gate_violations = _scan_direct_tool_calls(repo_root)
    if gate_violations:
        violations.append("direct tool invocations detected in scripts")
        violations.extend(gate_violations[:16])

    pattern_ids = set()
    for row in ((controlx_payload.get("record") or {}).get("forbidden_patterns") or []):
        if isinstance(row, dict):
            pattern_id = str(row.get("pattern_id", "")).strip()
            if pattern_id:
                pattern_ids.add(pattern_id)
    required_pattern_ids = (
        "controlx.forbid.stop_on_failure",
        "controlx.forbid.bypass",
        "controlx.forbid.raw_gate_calls",
    )
    for pattern_id in required_pattern_ids:
        if pattern_id not in pattern_ids:
            violations.append("controlx policy missing pattern_id '{}'".format(pattern_id))

    if violations:
        print("future-case stress suite failures:")
        for item in violations[:48]:
            print("- {}".format(item))
        return 1

    print("future-case stress suite OK ({})".format(len(cases)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
