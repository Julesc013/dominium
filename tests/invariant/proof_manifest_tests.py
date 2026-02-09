import argparse
import json
import os
import subprocess
import sys


def fail(message):
    sys.stderr.write("FAIL: {}\n".format(message))
    return 1


def parse_args():
    parser = argparse.ArgumentParser(description="RepoX/TestX proof manifest contract checks.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--manifest",
        default=os.path.join("build", "proof_manifests", "repox_proof_manifest.json"),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    repo_root = os.path.abspath(args.repo_root)
    manifest_path = os.path.join(repo_root, args.manifest)
    if not os.path.isfile(manifest_path):
        repox_script = os.path.join(repo_root, "scripts", "ci", "check_repox_rules.py")
        adapter = os.path.join(repo_root, "scripts", "dev", "env_tools.py")
        result = subprocess.run(
            [
                sys.executable,
                adapter,
                "--repo-root",
                repo_root,
                "run",
                "--",
                "python",
                repox_script,
                "--repo-root",
                repo_root,
                "--proof-manifest-out",
                args.manifest,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
        )
        if result.returncode != 0:
            return fail("unable to generate proof manifest:\n{}".format(result.stdout))
        if not os.path.isfile(manifest_path):
            return fail("proof manifest missing at {}".format(args.manifest.replace("\\", "/")))

    try:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return fail("invalid json in {}".format(args.manifest.replace("\\", "/")))

    if payload.get("schema_id") != "dominium.repox.proof_manifest":
        return fail("schema_id mismatch in proof manifest")
    if payload.get("schema_version") != "1.0.0":
        return fail("schema_version mismatch in proof manifest")

    required_tests = payload.get("required_tests")
    available_tests = payload.get("available_testx_tests")
    focused_subset = payload.get("focused_test_subset")
    if not isinstance(required_tests, list):
        return fail("required_tests must be a list")
    if not isinstance(available_tests, list):
        return fail("available_testx_tests must be a list")
    if not isinstance(focused_subset, list):
        return fail("focused_test_subset must be a list")

    available = set(available_tests)
    missing = sorted(test for test in required_tests if test not in available)
    if missing:
        return fail("required proof tests missing from TestX registration: {}".format(", ".join(missing)))

    subset_missing = sorted(test for test in focused_subset if test not in available)
    if subset_missing:
        return fail("focused_test_subset includes unknown tests: {}".format(", ".join(subset_missing)))

    required_caps = payload.get("required_capability_checks")
    required_refusals = payload.get("required_refusal_codes")
    if not isinstance(required_caps, list) or not required_caps:
        return fail("required_capability_checks must be a non-empty list")
    if not isinstance(required_refusals, list) or not required_refusals:
        return fail("required_refusal_codes must be a non-empty list")

    print("proof_manifest_contract=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
