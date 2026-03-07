import argparse
import hashlib
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.meta.profile import (
    apply_override,
    build_profile_binding_row,
    build_profile_row,
    normalize_profile_binding_rows,
    normalize_profile_rows,
    resolve_profile,
)


def _canonical_hash(payload) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _sample_profiles():
    rows = [
        build_profile_row(
            profile_id="physics.test_universe",
            profile_type="physics",
            version="1.0.0",
            overrides={"rule.test.override": "universe", "rule.test.guard": False},
        ),
        build_profile_row(
            profile_id="process.test_session",
            profile_type="process",
            version="1.0.0",
            overrides={"rule.test.override": "session", "rule.test.guard": True},
        ),
        build_profile_row(
            profile_id="epistemic.test_authority",
            profile_type="epistemic",
            version="1.0.0",
            overrides={"rule.test.override": "authority"},
        ),
        build_profile_row(
            profile_id="safety.test_system",
            profile_type="safety",
            version="1.0.0",
            overrides={"rule.test.override": "system"},
        ),
    ]
    return [dict(row) for row in normalize_profile_rows(rows)]


def _sample_bindings():
    rows = [
        build_profile_binding_row(
            binding_id="bind.universe",
            scope="universe",
            target_id="universe.test",
            profile_id="physics.test_universe",
            tick_applied=0,
        ),
        build_profile_binding_row(
            binding_id="bind.session",
            scope="session",
            target_id="session.test",
            profile_id="process.test_session",
            tick_applied=0,
        ),
        build_profile_binding_row(
            binding_id="bind.authority",
            scope="authority",
            target_id="authority.test",
            profile_id="epistemic.test_authority",
            tick_applied=0,
        ),
        build_profile_binding_row(
            binding_id="bind.system",
            scope="system",
            target_id="system.test",
            profile_id="safety.test_system",
            tick_applied=0,
        ),
    ]
    return [dict(row) for row in normalize_profile_binding_rows(rows)]


def case_profile_resolution_order_deterministic():
    profiles = _sample_profiles()
    bindings = _sample_bindings()
    context = {
        "universe_id": "universe.test",
        "session_id": "session.test",
        "authority_id": "authority.test",
        "system_id": "system.test",
    }
    first = resolve_profile(
        rule_id="rule.test.override",
        owner_context=context,
        profile_rows=list(profiles),
        profile_binding_rows=list(bindings),
    )
    second = resolve_profile(
        rule_id="rule.test.override",
        owner_context=context,
        profile_rows=list(reversed(profiles)),
        profile_binding_rows=list(reversed(bindings)),
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        print("profile resolution failed")
        return 1
    if first.get("effective_value") != "system":
        print("unexpected effective value {}".format(first.get("effective_value")))
        return 1
    if first.get("deterministic_fingerprint") != second.get("deterministic_fingerprint"):
        print("resolution fingerprint mismatch")
        return 1
    print("test_profile_resolution_order_deterministic=ok")
    return 0


def case_override_emits_exception_event():
    profiles = [
        build_profile_row(
            profile_id="physics.baseline",
            profile_type="physics",
            version="1.0.0",
            overrides={"rule.test.guard": False},
        ),
        build_profile_row(
            profile_id="process.override",
            profile_type="process",
            version="1.0.0",
            overrides={"rule.test.guard": True},
        ),
    ]
    bindings = [
        build_profile_binding_row(
            binding_id="bind.base",
            scope="universe",
            target_id="universe.test",
            profile_id="physics.baseline",
            tick_applied=0,
        ),
        build_profile_binding_row(
            binding_id="bind.overlay",
            scope="session",
            target_id="session.test",
            profile_id="process.override",
            tick_applied=0,
        ),
    ]
    result = apply_override(
        rule_id="rule.test.guard",
        owner_id="system.system.test",
        tick=42,
        owner_context={
            "universe_id": "universe.test",
            "session_id": "session.test",
        },
        profile_rows=profiles,
        profile_binding_rows=bindings,
        law_profile_row={"extensions": {"profile_override_allowed_rule_ids": ["rule.test.guard"]}},
        details={"justification": "unit-test"},
    )
    event = dict(result.get("exception_event") or {})
    if result.get("result") != "complete":
        print("apply_override refused")
        return 1
    if not result.get("override_active"):
        print("override should be active")
        return 1
    if not event or str(event.get("profile_id", "")).strip() != "process.override":
        print("missing or invalid exception event")
        return 1
    print("test_override_emits_exception_event=ok")
    return 0


def case_no_mode_flags_detected(repo_root: str):
    runtime_roots = ("src", "engine", "game", "client", "server", "launcher", "setup")
    source_exts = {".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp"}
    forbidden = ("creative_mode", "debug_mode", "godmode", "sandbox_mode", "debug_profile")
    violations = []
    for root_name in runtime_roots:
        abs_root = os.path.join(repo_root, root_name)
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(name for name in dirs if name not in {".git", "__pycache__", "build", "dist", "out", "legacy"})
            for name in sorted(files):
                if os.path.splitext(name)[1].lower() not in source_exts:
                    continue
                abs_path = os.path.join(walk_root, name)
                rel = abs_path.replace("\\", "/")
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read().lower()
                except OSError:
                    continue
                for token in forbidden:
                    if token in text:
                        violations.append("{} -> {}".format(rel, token))
                        break
    if violations:
        print("mode-like tokens detected in runtime paths:")
        for row in violations[:20]:
            print(row)
        return 1
    print("test_no_mode_flags_detected=ok")
    return 0


def case_profile_binding_hash_stable():
    first = build_profile_binding_row(
        binding_id="bind.hash",
        scope="session",
        target_id="session.hash",
        profile_id="process.default",
        tick_applied=5,
    )
    second = build_profile_binding_row(
        binding_id="bind.hash",
        scope="session",
        target_id="session.hash",
        profile_id="process.default",
        tick_applied=5,
    )
    if first.get("deterministic_fingerprint") != second.get("deterministic_fingerprint"):
        print("binding deterministic_fingerprint mismatch")
        return 1
    if _canonical_hash(first) != _canonical_hash(second):
        print("binding canonical hash mismatch")
        return 1
    print("test_profile_binding_hash_stable=ok")
    return 0


def case_cross_platform_profile_hash_match(repo_root: str):
    registry_path = os.path.join(repo_root, "data", "registries", "profile_registry.json")
    try:
        payload = json.load(open(registry_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        print("failed to load profile registry")
        return 1
    first = _canonical_hash(payload)
    second = _canonical_hash(json.loads(json.dumps(payload)))
    if first != second:
        print("canonical registry hash mismatch")
        return 1
    print("test_cross_platform_profile_hash_match=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="META-PROFILE0 profile override architecture tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--case",
        required=True,
        choices=(
            "profile_resolution_order_deterministic",
            "override_emits_exception_event",
            "no_mode_flags_detected",
            "profile_binding_hash_stable",
            "cross_platform_profile_hash_match",
        ),
    )
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "profile_resolution_order_deterministic":
        return case_profile_resolution_order_deterministic()
    if args.case == "override_emits_exception_event":
        return case_override_emits_exception_event()
    if args.case == "no_mode_flags_detected":
        return case_no_mode_flags_detected(repo_root)
    if args.case == "profile_binding_hash_stable":
        return case_profile_binding_hash_stable()
    return case_cross_platform_profile_hash_match(repo_root)


if __name__ == "__main__":
    sys.exit(main())
