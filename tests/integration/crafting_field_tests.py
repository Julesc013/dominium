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


def main():
    parser = argparse.ArgumentParser(description="Crafting T10 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "crafting")

    fixtures = [
        "earth_like.craft",
        "asteroid_small.craft",
        "superflat_slab.craft",
        "oblique_spheroid.craft",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "crafting tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "crafting fixtures missing")

    for fixture in fixtures:
        fixture_path = os.path.join(fixture_root, fixture)
        ok = ok and require(os.path.isfile(fixture_path), "missing fixture {}".format(fixture_path))
        if not ok:
            return 1
        success, _output = run_cmd(
            [
                tool_path,
                "validate",
                "--fixture",
                fixture_path,
            ],
            expect_contains=[
                "DOMINIUM_CRAFTING_VALIDATE_V1",
                "provider_chain=materials->tools->conditions->crafting",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "earth_like.craft")
    success, output = run_cmd(
        [
            tool_path,
            "execute",
            "--fixture",
            base_fixture,
            "--recipe",
            "recipe.craft.basic_tool",
            "--temp",
            "0.5",
            "--humidity",
            "0.5",
            "--environment",
            "env.workshop",
            "--tick",
            "0",
            "--budget",
            "100",
        ],
        expect_contains=[
            "DOMINIUM_CRAFTING_EXECUTE_V1",
            "provider_chain=materials->tools->conditions->crafting",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "ok",
            "refusal_reason",
            "flags",
            "inputs_consumed",
            "outputs_produced",
            "byproducts_produced",
            "tool_damage",
            "inventory_count",
            "tool_count",
            "budget.used",
            "budget.max",
        ):
            ok = ok and require(key in data, "execute missing {}".format(key))
        ok = ok and require(data.get("ok") == "1", "expected ok=1 for craft execute")

    success, output = run_cmd(
        [
            tool_path,
            "execute",
            "--fixture",
            base_fixture,
            "--recipe",
            "recipe.craft.basic_tool",
            "--temp",
            "0.5",
            "--humidity",
            "0.5",
            "--environment",
            "env.workshop",
            "--tick",
            "0",
            "--budget",
            "0",
        ],
        expect_contains=["DOMINIUM_CRAFTING_EXECUTE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("ok") == "0", "expected ok=0 under zero budget")
        ok = ok and require(data.get("refusal_reason") == "1", "expected refusal_reason=1 (budget)")

    low_tool_fixture = os.path.join(fixture_root, "asteroid_small.craft")
    success, output = run_cmd(
        [
            tool_path,
            "execute",
            "--fixture",
            low_tool_fixture,
            "--recipe",
            "recipe.craft.basic_tool",
            "--temp",
            "0.5",
            "--humidity",
            "0.5",
            "--environment",
            "env.workshop",
            "--tick",
            "0",
            "--budget",
            "100",
        ],
        expect_contains=["DOMINIUM_CRAFTING_EXECUTE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("ok") == "0", "expected ok=0 for missing tool")
        ok = ok and require(data.get("refusal_reason") == "5", "expected refusal_reason=5 (policy)")

    success, output = run_cmd(
        [
            tool_path,
            "execute",
            "--fixture",
            base_fixture,
            "--recipe",
            "recipe.disassemble.basic_tool",
            "--tick",
            "10",
            "--budget",
            "100",
        ],
        expect_contains=["DOMINIUM_CRAFTING_EXECUTE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        flags = int(data.get("flags", "0"))
        ok = ok and require((flags & 16) != 0, "expected disassembly flag")
        ok = ok and require(data.get("ok") == "1", "expected ok=1 for disassembly")

    success, output = run_cmd(
        [
            tool_path,
            "core-sample",
            "--fixture",
            base_fixture,
            "--recipe",
            "recipe.craft.basic_tool",
            "--temp",
            "0.5",
            "--humidity",
            "0.5",
            "--environment",
            "env.workshop",
            "--tick",
            "0",
            "--steps",
            "4",
            "--budget",
            "100",
        ],
        expect_contains=["DOMINIUM_CRAFTING_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    sample_hash = None
    if success:
        data = parse_kv(output)
        ok = ok and require("sample_hash" in data, "core-sample missing sample_hash")
        sample_hash = data.get("sample_hash")

    success, output = run_cmd(
        [
            tool_path,
            "core-sample",
            "--fixture",
            base_fixture,
            "--recipe",
            "recipe.craft.basic_tool",
            "--temp",
            "0.5",
            "--humidity",
            "0.5",
            "--environment",
            "env.workshop",
            "--tick",
            "0",
            "--steps",
            "4",
            "--budget",
            "100",
        ],
        expect_contains=["DOMINIUM_CRAFTING_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    if success and sample_hash is not None:
        repeat_hash = parse_kv(output).get("sample_hash")
        ok = ok and require(repeat_hash == sample_hash, "determinism hash mismatch")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
