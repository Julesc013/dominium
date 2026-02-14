import argparse
import json
import os
import shutil
import sys
import tempfile


def _write(path: str, payload: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def _write_contract(repo_root: str) -> None:
    contract = {
        "schema_id": "dominium.schema.governance.derived_artifact_contract",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.governance.derived_artifacts",
            "registry_version": "1.0.0",
            "schema_version_ref": "dominium.schema.governance.derived_artifact_contract@1.0.0",
            "artifacts": [
                {
                    "artifact_id": "artifact.test.canonical",
                    "path": "docs/canonical.md",
                    "artifact_class": "CANONICAL",
                },
                {
                    "artifact_id": "artifact.test.run_meta",
                    "path": "docs/audit/run_meta.json",
                    "artifact_class": "RUN_META",
                },
                {
                    "artifact_id": "artifact.test.view",
                    "path": "docs/audit/view.md",
                    "artifact_class": "DERIVED_VIEW",
                },
            ],
        },
    }
    contract_path = os.path.join(repo_root, "data", "registries", "derived_artifacts.json")
    _write(contract_path, json.dumps(contract, indent=2, sort_keys=True) + "\n")


def _load_merkle(source_repo_root: str):
    if source_repo_root not in sys.path:
        sys.path.insert(0, source_repo_root)
    from tools.xstack.core import merkle_tree  # pylint: disable=import-error

    return merkle_tree


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: run-meta changes must not perturb canonical dep hash.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source_repo_root = os.path.abspath(args.repo_root)

    temp_root = tempfile.mkdtemp(prefix="repox_dep_hash_")
    try:
        _write_contract(temp_root)
        _write(os.path.join(temp_root, "docs", "canonical.md"), "canonical-v1\n")
        _write(os.path.join(temp_root, "docs", "audit", "run_meta.json"), "{\"generated_utc\":\"t0\"}\n")
        _write(os.path.join(temp_root, "docs", "audit", "view.md"), "view-v1\n")

        merkle_tree = _load_merkle(source_repo_root)
        opts = {
            "subtrees": ["docs"],
            "include_artifact_classes": ("CANONICAL",),
            "exclude_artifact_classes": ("RUN_META", "DERIVED_VIEW"),
            "extra_excluded_prefixes": ("docs/audit", "dist", "build", "tmp", ".xstack_cache"),
        }
        before = merkle_tree.compute_repo_state_hash(temp_root, **opts)
        before_hash = str(before.get("repo_state_hash", ""))
        if not before_hash:
            print("missing baseline repo_state_hash")
            return 1

        _write(os.path.join(temp_root, "docs", "audit", "run_meta.json"), "{\"generated_utc\":\"t1\"}\n")
        after_run_meta = merkle_tree.compute_repo_state_hash(temp_root, **opts)
        if str(after_run_meta.get("repo_state_hash", "")) != before_hash:
            print("run-meta edit changed canonical-only hash unexpectedly")
            return 1

        _write(os.path.join(temp_root, "docs", "canonical.md"), "canonical-v2\n")
        after_canonical = merkle_tree.compute_repo_state_hash(temp_root, **opts)
        if str(after_canonical.get("repo_state_hash", "")) == before_hash:
            print("canonical edit did not change canonical-only hash")
            return 1

        print("repox dep hash stability invariant OK")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
