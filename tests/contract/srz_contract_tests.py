import argparse
import os
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="SRZ-0 contract tests.")
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    required_docs = [
        "docs/architecture/SRZ_MODEL.md",
        "docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md",
        "docs/architecture/EPISTEMICS_MODEL.md",
        "docs/architecture/EPISTEMICS_AND_SCALED_MMO.md",
        "docs/ops/MMO_SCALING_PLAYBOOK.md",
    ]
    required_schemas = [
        "schema/srz.zone.schema",
        "schema/srz.assignment.schema",
        "schema/srz.policy.schema",
        "schema/process.log.schema",
        "schema/process.hashchain.schema",
        "schema/state.delta.schema",
    ]

    ok = True
    for rel_path in required_docs + required_schemas:
        path = os.path.join(repo_root, rel_path)
        ok = ok and require(os.path.isfile(path), "missing {}".format(rel_path))
        if not ok:
            return 1

    srz_doc = read_text(os.path.join(repo_root, "docs", "architecture", "SRZ_MODEL.md"))
    for token in ("server", "delegated", "dormant", "No other modes"):
        ok = ok and require(token in srz_doc, "SRZ_MODEL missing '{}'".format(token))

    zone_schema = read_text(os.path.join(repo_root, "schema", "srz.zone.schema"))
    for token in ("srz_zone", "mode", "verification_policy", "escalation_thresholds"):
        ok = ok and require(token in zone_schema, "srz.zone.schema missing '{}'".format(token))

    log_schema = read_text(os.path.join(repo_root, "schema", "process.log.schema"))
    for token in ("process_log", "chain_id", "delta_id", "epistemic_scope_ref"):
        ok = ok and require(token in log_schema, "process.log.schema missing '{}'".format(token))

    hash_schema = read_text(os.path.join(repo_root, "schema", "process.hashchain.schema"))
    ok = ok and require("process_hash_chain" in hash_schema, "process.hashchain.schema missing process_hash_chain")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
