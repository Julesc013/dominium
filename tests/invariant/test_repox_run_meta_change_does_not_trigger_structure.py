import argparse
import json
import os
import shutil
import sys
import tempfile


def _write(path: str, content: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def _write_contract(repo_root: str) -> None:
    payload = {
        "schema_id": "dominium.schema.governance.derived_artifact_contract",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.governance.derived_artifacts",
            "registry_version": "1.0.0",
            "schema_version_ref": "dominium.schema.governance.derived_artifact_contract@1.0.0",
            "artifacts": [
                {
                    "artifact_id": "artifact.structure.ruleset",
                    "path": "repo/repox/rulesets/core.json",
                    "artifact_class": "CANONICAL",
                    "canonical_hash_required": True,
                    "used_for_gating": True,
                },
                {
                    "artifact_id": "artifact.structure.script",
                    "path": "scripts/ci/check_repox_rules.py",
                    "artifact_class": "CANONICAL",
                    "canonical_hash_required": True,
                    "used_for_gating": True,
                },
                {
                    "artifact_id": "artifact.repox.profile",
                    "path": "docs/audit/repox/REPOX_PROFILE.json",
                    "artifact_class": "RUN_META",
                    "canonical_hash_required": False,
                    "used_for_gating": False,
                },
            ],
        },
    }
    _write(
        os.path.join(repo_root, "data", "registries", "derived_artifacts.json"),
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
    )


def _load_repox(source_repo_root: str):
    ci_dir = os.path.join(source_repo_root, "scripts", "ci")
    if ci_dir not in sys.path:
        sys.path.insert(0, ci_dir)
    import check_repox_rules as repox  # pylint: disable=import-error

    return repox


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: run-meta edits must not invalidate repox.structure.* dep hashes.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source_repo_root = os.path.abspath(args.repo_root)
    repox = _load_repox(source_repo_root)

    temp_root = tempfile.mkdtemp(prefix="repox_scope_")
    try:
        _write_contract(temp_root)
        _write(os.path.join(temp_root, "repo", "repox", "rulesets", "core.json"), "{\n  \"rules\": []\n}\n")
        _write(os.path.join(temp_root, "scripts", "ci", "check_repox_rules.py"), "# synthetic\n")
        _write(os.path.join(temp_root, "docs", "audit", "repox", "REPOX_PROFILE.json"), "{\"generated_utc\":\"t0\"}\n")

        scope = ("repo", "scripts")
        classes = ("CANONICAL",)
        roots_before = repox._load_merkle_roots(  # pylint: disable=protected-access
            temp_root,
            subtrees=scope,
            include_artifact_classes=classes,
            exclude_artifact_classes=("RUN_META", "DERIVED_VIEW"),
            extra_excluded_prefixes=repox.STRUCTURE_SCOPE_EXCLUDED_PREFIXES,  # pylint: disable=protected-access
        )
        dep_before = repox._group_dep_hash(roots_before, scope)  # pylint: disable=protected-access
        if not dep_before:
            print("missing baseline dep hash")
            return 1

        def _no_violations():
            return []

        repox._run_check_group(  # pylint: disable=protected-access
            repo_root=temp_root,
            group_id="repox.structure.ruleset.synthetic",
            scope_subtrees=scope,
            artifact_classes=classes,
            profile="STRICT",
            impacted_roots={"repo", "scripts"},
            roots=roots_before,
            checks=[_no_violations],
        )

        _write(os.path.join(temp_root, "docs", "audit", "repox", "REPOX_PROFILE.json"), "{\"generated_utc\":\"t1\"}\n")
        roots_after = repox._load_merkle_roots(  # pylint: disable=protected-access
            temp_root,
            subtrees=scope,
            include_artifact_classes=classes,
            exclude_artifact_classes=("RUN_META", "DERIVED_VIEW"),
            extra_excluded_prefixes=repox.STRUCTURE_SCOPE_EXCLUDED_PREFIXES,  # pylint: disable=protected-access
        )
        dep_after = repox._group_dep_hash(roots_after, scope)  # pylint: disable=protected-access
        if dep_after != dep_before:
            print("run-meta change invalidated structure dep hash")
            return 1

        def _must_not_execute():
            raise RuntimeError("structure check executed unexpectedly")

        warm = repox._run_check_group(  # pylint: disable=protected-access
            repo_root=temp_root,
            group_id="repox.structure.ruleset.synthetic",
            scope_subtrees=scope,
            artifact_classes=classes,
            profile="STRICT",
            impacted_roots={"docs"},
            roots=roots_after,
            checks=[_must_not_execute],
        )
        if not bool(warm.get("cache_hit")):
            print("expected cached skip for run-meta-only change")
            return 1

        print("repox run-meta isolation invariant OK")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
