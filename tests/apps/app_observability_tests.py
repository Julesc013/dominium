import argparse
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_nonzero=False, expect_contains=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout
    if expect_nonzero:
        if result.returncode == 0:
            sys.stderr.write("FAIL: expected non-zero exit for {}\n".format(cmd))
            sys.stderr.write(output)
            return False
    elif expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--tools", required=True)
    args = parser.parse_args()

    ok = True

    ok = ok and run_cmd(
        [args.client, "--topology", "--format=json"],
        expect_contains=["\"core_info\"", "\"topology\"", "\"tree_id\""],
    )
    ok = ok and run_cmd(
        [args.client, "--topology", "--format=text"],
        expect_contains=["topology_tree=packages_tree"],
    )
    ok = ok and run_cmd(
        [args.tools, "inspect", "--format=json"],
        expect_contains=["\"topology\"", "\"snapshot\"", "\"events\""],
    )
    ok = ok and run_cmd(
        [args.tools, "validate", "--format=json"],
        expect_contains=["\"validate_status\"", "\"compat\""],
    )

    ok = ok and run_cmd(
        [args.client, "--snapshot"],
        expect_nonzero=True,
        expect_contains=["snapshot metadata unsupported"],
    )
    ok = ok and run_cmd(
        [args.client, "--events"],
        expect_nonzero=True,
        expect_contains=["event stream unsupported"],
    )
    ok = ok and run_cmd(
        [args.tools, "replay"],
        expect_nonzero=True,
        expect_contains=["replay unsupported"],
    )

    ok = ok and run_cmd(
        [args.client, "--topology", "--expect-engine-version=9.9.9"],
        expect_nonzero=True,
        expect_contains=["engine_version mismatch"],
    )

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
