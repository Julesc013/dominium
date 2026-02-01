import argparse
import os
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_contains=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout or ""
    if expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False, output
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False, output
    return True, output


def parse_kv(output):
    data = {}
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def resolve(tool_path, fixture_path):
    return run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            fixture_path,
            "--region",
            "srz.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "300",
        ],
        expect_contains=["DOMINIUM_SRZ_RESOLVE_V1"],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="SRZ-0 determinism tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "srz")

    baseline = os.path.join(fixture_root, "baseline.srz")
    shuffled = os.path.join(fixture_root, "shuffled.srz")

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "srz tool missing")
    ok = ok and require(os.path.isfile(baseline), "baseline fixture missing")
    ok = ok and require(os.path.isfile(shuffled), "shuffled fixture missing")
    if not ok:
        return 1

    success, output = resolve(tool_path, baseline)
    ok = ok and success
    hash_a = None
    if success:
        hash_a = parse_kv(output).get("resolve_hash")
        ok = ok and require(hash_a is not None, "missing resolve_hash baseline")

    success, output = resolve(tool_path, baseline)
    ok = ok and success
    if success and hash_a is not None:
        hash_b = parse_kv(output).get("resolve_hash")
        ok = ok and require(hash_b == hash_a, "baseline resolve hash drift")

    success, output = resolve(tool_path, shuffled)
    ok = ok and success
    if success and hash_a is not None:
        hash_c = parse_kv(output).get("resolve_hash")
        ok = ok and require(hash_c == hash_a, "ordering invariance hash mismatch")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
